"""Clientes HTTP mínimos (biblioteca estándar) de los modelos opcionales: vectores, re-ranqueo y respuesta citada.

- Vectores: Text Embeddings Inference (`POST /embed` con {"inputs": [...], "truncate": true}) o una API compatible con
  OpenAI (`POST /embeddings` con {"model", "input"}; sirve también para Ollama en `http://host:11434/v1`).
- Re-ranqueo: TEI `POST /rerank` con {"query", "texts", "truncate": true} → [{"index", "score"}].
- Respuesta: API de Anthropic (`POST /v1/messages`) o compatible con OpenAI (`POST /chat/completions`).
Formas de las API según su documentación pública [verificar en la versión que se despliegue].
"""
import json, urllib.request, urllib.error

TIEMPO = 60


def _post(url, cuerpo, cabeceras=None, tiempo=TIEMPO):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", **(cabeceras or {})})
    try:
        with urllib.request.urlopen(req, timeout=tiempo) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as x:
        detalle = x.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"{url} respondió {x.code}: {detalle}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as x:
        raise RuntimeError(f"{url} no responde ({x})") from None


def vectores(cfg, textos, lote=32):
    out = []
    for i in range(0, len(textos), lote):
        parte = textos[i:i + lote]
        if cfg["tipo"] == "openai":
            r = _post(cfg["url"] + "/embeddings", {"model": cfg["modelo"], "input": parte})
            out += [d["embedding"] for d in sorted(r["data"], key=lambda d: d["index"])]
        else:
            out += _post(cfg["url"] + "/embed", {"inputs": parte, "truncate": True})
    return out


def reranquear(cfg, consulta, textos):
    """Índices de `textos` ordenados por relevancia."""
    r = _post(cfg["url"] + "/rerank", {"query": consulta, "texts": textos, "truncate": True})
    return [d["index"] for d in sorted(r, key=lambda d: -d["score"])]


def responder(cfg, sistema, mensajes, max_tokens=900):
    """Texto de la respuesta del modelo configurado. `mensajes` = [{"role": "user"|"assistant", "content": str}]."""
    if cfg["tipo"] == "anthropic":
        if not cfg["clave"]:
            raise RuntimeError("falta la clave de la API (variable de entorno indicada en PMKB_LLM_CLAVE_VAR)")
        r = _post(cfg["url"] + "/v1/messages",
                  {"model": cfg["modelo"], "max_tokens": max_tokens, "system": sistema, "messages": mensajes, "temperature": 0},
                  {"x-api-key": cfg["clave"], "anthropic-version": "2023-06-01"})
        return "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
    cab = {"Authorization": f"Bearer {cfg['clave']}"} if cfg["clave"] else {}
    r = _post(cfg["url"] + "/chat/completions",
              {"model": cfg["modelo"], "temperature": 0, "max_tokens": max_tokens,
               "messages": [{"role": "system", "content": sistema}] + mensajes}, cab)
    return r["choices"][0]["message"]["content"]
