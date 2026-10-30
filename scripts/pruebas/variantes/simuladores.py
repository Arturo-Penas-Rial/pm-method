#!/usr/bin/env python3
"""Simuladores locales de los modelos opcionales de pm-kb (docs/PM-KB.md §8, §9, §11.3 y §12): NO son los modelos
reales. Hablan el mismo protocolo HTTP que usa `pm-kb/pmkb/modelos.py`, para probar sin red el camino completo
(indexar con vectores, búsqueda híbrida, re-ranqueo y "Preguntar" con respuesta citada) y sus fallas.

Uso:  python3 scripts/pruebas/variantes/simuladores.py [--puerto 0] [--retardo 3]
Imprime una línea «SIMULADOR http://127.0.0.1:<puerto>» y atiende hasta que se lo detiene. Solo biblioteca estándar.

Protocolos (formas según la documentación pública; TEI verificado contra su docs/openapi.json 1.9.4 el 2026-10-29):
  POST /embed           TEI: {"inputs": str | [str], "truncate"?, "normalize"?} → [[float, …], …]
  POST /rerank          TEI: {"query", "texts": [str], "truncate"?} → [{"index", "score"}, …] (de mayor a menor)
  POST /v1/embeddings   compatible con OpenAI (también TEI y Ollama): {"model", "input"} → {"object": "list",
                        "data": [{"object": "embedding", "index", "embedding"}], "model", "usage"}
  POST /v1/messages     API de Anthropic: cabeceras x-api-key y anthropic-version; {"model", "max_tokens", "system",
                        "messages", "temperature"} → {"type": "message", "content": [{"type": "text", "text"}], …};
                        401 authentication_error con otra clave, 404 not_found_error con un modelo desconocido
  POST /v1/chat/completions  compatible con OpenAI: → {"choices": [{"message": {"role", "content"}}]}
  GET  /registro        lo que recibió (ruta, modelo, parámetros y si llegaron las cabeceras; nunca el valor de una clave)
  POST /falla/…         500 en cualquier ruta (servidor que responde con error)
La clave esperada se lee de la variable de entorno PMKB_SIM_CLAVE (la genera la prueba en cada corrida; nunca va a un
archivo). Modelos de respuesta: «sim-respuesta» (cita la evidencia), «sim-cita-invalida» (agrega una cita [99]),
«sim-sin-citas» (no cita) y «sim-lento» (tarda --retardo segundos); cualquier otro → 404.

Vectores: bolsa de palabras normalizada (L2) en dimensión fija (DIM) con raíces de 5 letras y una tabla corta de
conceptos (sinónimos y traducciones que no están en los sinónimos de pm-kb), para que la búsqueda híbrida tenga algo
que medir: una consulta sin términos del corpus puede recuperar por concepto lo que BM25 solo no trae. Determinista.
Re-ranqueo: fracción de los rasgos de la consulta (raíz o concepto) presentes en el texto, más una bonificación pequeña
que decrece con el largo del texto (favorece textos breves que cubren la consulta; distinto del BM25 de pm-kb).
"""
import argparse, hashlib, json, math, os, re, sys, threading, time, unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DIM = 256
MODELOS_RESPUESTA = ("sim-respuesta", "sim-cita-invalida", "sim-sin-citas", "sim-lento")
# concepto → palabras (sin tildes) que lo expresan; ninguna pareja está en pmkb/sinonimos.py ni en el glosario de texto.py
CONCEPTOS = {
    "c-mensajeria": ("sms", "mensajeria", "mensaje", "mensajes", "texting", "notificacion", "notificaciones", "whatsapp"),
    "c-caida": ("caida", "caidas", "outage", "apagon", "interrupcion", "corte", "downtime"),
    "c-gremio": ("sindicato", "gremio", "union", "gremial", "sindical"),
    "c-dinero": ("costo", "costos", "dinero", "plata", "gasto", "gastos", "money", "spend"),
    "c-identidad": ("biometria", "biometrica", "huella", "fingerprint", "biometrics", "identidad"),
    "c-lento": ("lentitud", "lento", "timeout", "latencia", "sluggish", "slowness"),
    "c-padron": ("padron", "registry", "censo"),
}
_CONCEPTO = {p: c for c, ps in CONCEPTOS.items() for p in ps}


def _plano(t):
    return unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()


def rasgos(texto):
    """Raíces de 5 letras y conceptos de un texto (palabras de 3 o más letras)."""
    out = []
    for w in re.findall(r"[a-z0-9]{3,}", _plano(texto)):
        out.append("r:" + w[:5])
        if w in _CONCEPTO:
            out += [_CONCEPTO[w]] * 2          # el concepto pesa el doble que la raíz
    return out


def vector(texto):
    v = [0.0] * DIM
    for r in rasgos(texto):
        h = hashlib.sha256(r.encode()).digest()
        v[int.from_bytes(h[:4], "big") % DIM] += 1.0 if h[4] % 2 else -1.0
    n = math.sqrt(sum(x * x for x in v))
    if not n:
        v[0] = 1.0; return v
    return [round(x / n, 6) for x in v]


def puntaje(consulta, texto):
    q = set(rasgos(consulta))
    palabras = re.findall(r"[a-z0-9]{3,}", _plano(texto))
    t = set(rasgos(texto))
    if not q:
        return 0.0
    return round(len(q & t) / len(q) + 0.2 / (1 + math.log(1 + len(palabras))), 6)


def _evidencia(mensajes):
    """[(n, título)] de la evidencia numerada que arma pm-kb en el último mensaje del usuario."""
    ultimo = next((m.get("content", "") for m in reversed(mensajes or []) if m.get("role") == "user"), "")
    if isinstance(ultimo, list):
        ultimo = " ".join(b.get("text", "") for b in ultimo if isinstance(b, dict))
    return [(int(n), t.strip()) for n, t in re.findall(r"(?m)^\[(\d+)\] (.+?) \(", ultimo)]


def redactar(modelo, mensajes):
    ev = _evidencia(mensajes)
    if not ev:
        return "No hay evidencia suficiente: la pregunta no trae evidencia numerada."
    partes = [f"{t[:80]} [{n}]" for n, t in ev[:2]]
    if modelo == "sim-sin-citas":
        return "Según la evidencia, " + " y ".join(t[:80] for _, t in ev[:2]) + "."
    txt = "Según la evidencia: " + "; ".join(partes) + "."
    if modelo == "sim-cita-invalida":
        txt += " También lo confirma el acta [99]."
    return txt


class Estado:
    def __init__(self, retardo):
        self.registro, self.lock, self.retardo = [], threading.Lock(), retardo

    def anotar(self, x):
        with self.lock:
            self.registro.append(x)


def manejador(estado):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _enviar(self, codigo, datos):
            b = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            if self.path == "/registro":
                with estado.lock:
                    return self._enviar(200, list(estado.registro))
            if self.path == "/salud":
                return self._enviar(200, {"ok": True})
            self._enviar(404, {"error": "ruta desconocida"})

        def do_DELETE(self):
            if self.path == "/registro":
                with estado.lock:
                    estado.registro.clear()
                return self._enviar(200, {"ok": True})
            self._enviar(404, {"error": "ruta desconocida"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                c = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                return self._enviar(400, {"error": "JSON inválido"})
            p = self.path.rstrip("/")
            nota = {"ruta": p, "modelo": c.get("model"), "x_api_key": bool(self.headers.get("x-api-key")),
                    "anthropic_version": self.headers.get("anthropic-version"), "authorization": bool(self.headers.get("authorization")),
                    "max_tokens": c.get("max_tokens"), "temperature": c.get("temperature"), "claves": sorted(c)}
            if p.startswith("/falla/"):
                estado.anotar(nota); return self._enviar(500, {"error": "falla simulada", "error_type": "backend"})
            if p == "/embed":
                xs = c.get("inputs"); xs = [xs] if isinstance(xs, str) else xs
                if not isinstance(xs, list):
                    return self._enviar(422, {"error": "inputs", "error_type": "validation"})
                nota["n"] = len(xs); estado.anotar(nota)
                return self._enviar(200, [vector(x) for x in xs])
            if p == "/rerank":
                ts = c.get("texts") or []
                ps = [{"index": i, "score": puntaje(c.get("query", ""), t)} for i, t in enumerate(ts)]
                nota.update(n=len(ts), consulta=c.get("query"), puntajes=[(t[:120], x["score"]) for t, x in zip(ts, ps)])
                estado.anotar(nota)
                return self._enviar(200, sorted(ps, key=lambda x: (-x["score"], x["index"])))
            if p == "/v1/embeddings":
                xs = c.get("input"); xs = [xs] if isinstance(xs, str) else xs
                nota["n"] = len(xs or []); estado.anotar(nota)
                return self._enviar(200, {"object": "list", "model": c.get("model") or "sim-vectores",
                                          "data": [{"object": "embedding", "index": i, "embedding": vector(x)} for i, x in enumerate(xs or [])],
                                          "usage": {"prompt_tokens": 0, "total_tokens": 0}})
            clave = os.environ.get("PMKB_SIM_CLAVE", "")
            if p == "/v1/messages":
                estado.anotar(nota)
                if not clave or self.headers.get("x-api-key") != clave:
                    return self._enviar(401, {"type": "error", "error": {"type": "authentication_error", "message": "invalid x-api-key"}})
                if c.get("model") not in MODELOS_RESPUESTA:
                    return self._enviar(404, {"type": "error", "error": {"type": "not_found_error", "message": f"model: {c.get('model')}"}})
                if c.get("model") == "sim-lento":
                    time.sleep(estado.retardo)
                txt = redactar(c["model"], c.get("messages"))
                return self._enviar(200, {"id": "msg_simulado", "type": "message", "role": "assistant", "model": c["model"],
                                          "content": [{"type": "text", "text": txt}], "stop_reason": "end_turn",
                                          "usage": {"input_tokens": 0, "output_tokens": 0}})
            if p == "/v1/chat/completions":
                estado.anotar(nota)
                if clave and self.headers.get("authorization") != f"Bearer {clave}":
                    return self._enviar(401, {"error": {"message": "Incorrect API key provided", "type": "invalid_request_error"}})
                if c.get("model") not in MODELOS_RESPUESTA:
                    return self._enviar(404, {"error": {"message": f"The model `{c.get('model')}` does not exist", "type": "invalid_request_error"}})
                if c.get("model") == "sim-lento":
                    time.sleep(estado.retardo)
                msgs = [m for m in c.get("messages") or [] if m.get("role") != "system"]
                return self._enviar(200, {"id": "chatcmpl-simulado", "object": "chat.completion", "model": c["model"],
                                          "choices": [{"index": 0, "message": {"role": "assistant", "content": redactar(c["model"], msgs)}, "finish_reason": "stop"}]})
            estado.anotar(nota)
            self._enviar(404, {"error": "ruta desconocida"})
    return H


def arrancar(puerto=0, retardo=3.0):
    """Servidor en un hilo (para usarlo dentro de un proceso): (url, servidor, estado)."""
    est = Estado(retardo)
    s = ThreadingHTTPServer(("127.0.0.1", puerto), manejador(est))
    s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{s.server_address[1]}", s, est


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.splitlines()[1:]))
    ap.add_argument("--puerto", type=int, default=0); ap.add_argument("--retardo", type=float, default=3.0)
    a = ap.parse_args()
    url, s, _ = arrancar(a.puerto, a.retardo)
    print(f"SIMULADOR {url}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        s.shutdown()


if __name__ == "__main__":
    main()
