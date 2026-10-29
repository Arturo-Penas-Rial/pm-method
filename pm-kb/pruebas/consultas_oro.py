"""Consultas de oro de la búsqueda (E2E-1, proyecto portal-socios): aciertos@5 y MRR@5. docs/PM-KB.md §12.

Un acierto es una unidad con alguno de los ids esperados o que contiene todos los términos de un grupo "todo"
(sin tildes ni mayúsculas). Uso: python3 -m pruebas.consultas_oro --proyecto portal-socios [--minimo 11]
"""
import argparse, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pmkb import config  # noqa: E402
from pmkb.busqueda import Sesion  # noqa: E402

CONSULTAS = [
    ("Q01", "riesgos de integracion con el padron", "sin tildes",
     [{"id": "R-001"}, {"todo": ["padron", "entorno de pruebas", "riesgo"]}]),
    ("Q02", "¿Qué pasó con el proveedor de SMS?", "pregunta natural",
     [{"id": "R-003"}, {"id": "C-005"}, {"id": "D-018"}, {"id": "A-005"}, {"todo": ["proveedor de sms", "caida"]}]),
    ("Q03", "cambios rechazados", "flexión (texto: rechazado)",
     [{"id": "C-003"}, {"todo": ["licencias", "rechaz"]}]),
    ("Q04", "¿por qué no se aprobó la compra de licencias para diseño?", "pregunta natural",
     [{"id": "C-003"}, {"todo": ["licencias", "reserva"]}]),
    ("Q05", "nueva regulación que exige biometria", "sinónimo (norma) y sin tilde",
     [{"id": "R-007"}, {"id": "C-004"}, {"id": "D-016"}, {"todo": ["biometria", "norma"]}]),
    ("Q06", "resistencia de los operadores a la bandeja unica", "sin tilde",
     [{"id": "R-002"}, {"id": "A-002"}, {"todo": ["operadores", "bandeja"]}]),
    ("Q07", "lentitud al consultar saldos", "sinónimo (timeout)",
     [{"id": "I-002"}, {"todo": ["saldos", "nfr-3"]}]),
    ("Q08", "lecciones aprendidas sobre el entorno de pruebas", "flexión (lección)",
     [{"id": "L-001"}, {"todo": ["exigir el entorno de pruebas"]}]),
    ("Q09", "¿cuánto queda de la reserva de riesgo?", "pregunta natural",
     [{"id": "D-019"}, {"todo": ["remanente", "reserva"]}, {"todo": ["94 %", "reserva"]}]),
    ("Q10", "¿quién aprobó el caso de negocio?", "sinónimo (business case)",
     [{"id": "D-010"}, {"id": "D-017"}, {"todo": ["business-case", "aprob"]}, {"todo": ["business case", "aprob"]},
      {"todo": ["caso de negocio", "aprob"]}]),
    ("Q11", "rotacion de programadores del proveedor", "sinónimo (desarrolladores)",
     [{"id": "R-005"}, {"todo": ["rota", "desarrolladores"]}]),
    ("Q12", "la revisión de riesgos que se postergó", "flexión (postergar)",
     [{"id": "L-002"}, {"todo": ["revision de riesgos", "posterg"]}]),
    ("Q13", "¿qué hacer si falla la demostración en vivo?", "documento (guion), sinónimo (demo)",
     [{"todo": ["plan b"]}]),
    ("Q14", "¿qué dijo el sindicato en la ronda de riesgos?", "transcripción",
     [{"todo": ["sindicato", "bandeja"]}]),
    ("Q15", "protección de datos personales en las constancias", "conocimiento implícito (Ley 18.331)",
     [{"id": "R-004"}, {"todo": ["18.331"]}]),
]


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def acierta(r, esperados, texto):
    t = norm(texto + " " + r["titulo"])
    for e in esperados:
        if "id" in e and r["id"] == e["id"]:
            return True
        if "todo" in e and all(norm(x) in t for x in e["todo"]):
            return True
    return False


def evaluar(sesion, proyecto, k=5):
    filas = []
    for qid, q, clase, esp in CONSULTAS:
        r = sesion.buscar(q, proyecto=proyecto, k=k, max_tokens=10000, extracto=5000)
        rango = next((n for n, x in enumerate(r["resultados"], 1) if acierta(x, esp, x["extracto"].replace("«", "").replace("»", ""))), 0)
        filas.append((qid, q, clase, rango, [x["id"] for x in r["resultados"]]))
    aciertos = sum(1 for f in filas if f[3])
    mrr = sum(1 / f[3] for f in filas if f[3]) / len(filas)
    return filas, aciertos, mrr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--proyecto", default="portal-socios"); ap.add_argument("--minimo", type=int, default=0)
    a = ap.parse_args()
    filas, aciertos, mrr = evaluar(Sesion(config.conectar(), "*", True), a.proyecto)
    for qid, q, clase, rango, ids in filas:
        print(f"{qid} {'OK ' if rango else '-- '} rango {rango or '—'} · {q} ({clase}) · top: {', '.join(ids[:5])}")
    print(f"aciertos@5 {aciertos}/{len(filas)} · MRR@5 {mrr:.2f}")
    sys.exit(0 if aciertos >= a.minimo else 1)


if __name__ == "__main__":
    main()
