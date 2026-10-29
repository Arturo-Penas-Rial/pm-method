"""Regenera pm-kb/requirements.txt con versiones fijadas y hashes sha256 de PyPI (pip --require-hashes).

Entrada: la lista "paquete==versión" completa (directas y transitivas), p. ej. el `pip freeze` de un entorno limpio con
las directas instaladas y `-c` a las versiones de docker/requirements.txt (las comunes deben coincidir).
Toma solo ruedas instalables en los dos caminos: CPython 3.12 (Ubuntu 24.04, WSL2) y 3.14 (Ubuntu 26.04, Docker) en
manylinux x86_64 y aarch64, más ruedas puras o abi3. Falla si una combinación queda sin rueda.
Uso: python3 pm-kb/regenerar_requisitos.py congelado.txt > pm-kb/requirements.txt
"""
import json, re, sys, urllib.request

PY = ["cp312", "cp314"]
ARQ = ["x86_64", "aarch64"]
DIRECTAS = {"psycopg", "psycopg-binary", "starlette", "uvicorn", "markitdown"}


def norm(n):
    return re.sub(r"[-_.]+", "-", n).lower()


def sirve(nombre, py, arq):
    m = re.match(r".+?-[^-]+-(?:\d[^-]*-)?([^-]+)-([^-]+)-([^-]+)\.whl$", nombre)
    if not m:
        return False
    pyt, abi, plat = m.groups()
    if plat == "any":
        return pyt.startswith("py3") or pyt in ("py2.py3",) or pyt == py
    if not (plat.startswith("manylinux") and plat.endswith(arq)) and not any(p.startswith("manylinux") and p.endswith(arq) for p in plat.split(".")):
        return False
    if abi == "none" and any(t.startswith("py3") for t in pyt.split(".")):
        return True
    if abi == "abi3":
        tags = [int(t[2:]) for t in pyt.split(".") if t.startswith("cp3")]
        return bool(tags) and min(tags) <= int(py[2:])
    return py in pyt.split(".")


def main():
    pares = [l.strip().split("==") for l in open(sys.argv[1], encoding="utf-8") if "==" in l and not l.startswith("#")]
    salida, faltan = [], []
    for nombre, version in sorted(pares, key=lambda p: (norm(p[0]) not in DIRECTAS, norm(p[0]))):
        d = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{nombre}/{version}/json", timeout=60))
        ruedas = [f for f in d["urls"] if f["packagetype"] == "bdist_wheel"]
        usadas = {}
        for py in PY:
            for arq in ARQ:
                ok = [f for f in ruedas if sirve(f["filename"], py, arq)]
                if not ok:
                    faltan.append(f"{nombre}=={version} sin rueda para {py} {arq}")
                for f in ok:
                    usadas[f["filename"]] = f["digests"]["sha256"]
        hashes = sorted(set(usadas.values()))
        salida.append(f"{norm(nombre)}=={version} \\\n" + " \\\n".join(f"    --hash=sha256:{h}" for h in hashes))
    if faltan:
        sys.exit("\n".join(faltan))
    print("# Dependencias de pm-kb (docs/PM-KB.md §7). Versiones fijadas con hash: pip install --require-hashes --only-binary=:all:")
    print("# Ruedas de CPython 3.12 y 3.14, manylinux x86_64 y aarch64, o puras. Regenerar: pm-kb/regenerar_requisitos.py.")
    print("# Directas: psycopg[binary] (LGPL-3.0, como biblioteca), starlette y uvicorn (BSD-3-Clause), markitdown[docx,pptx,xlsx,pdf] (MIT).")
    print("\n".join(salida))


if __name__ == "__main__":
    main()
