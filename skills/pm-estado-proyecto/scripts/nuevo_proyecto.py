#!/usr/bin/env python3
"""Crea la carpeta de un proyecto, sus registros CSV y su estado.json inicial.
Create a project folder, its CSV registers and its initial estado.json.

Uso / Usage:
  python3 nuevo_proyecto.py --ruta ./mi-proyecto --nombre "Proyecto Faro" --idioma es \
      --enfoque hibrido --ejecutivo "Nombre" --gestor "Nombre" [--fecha AAAA-MM-DD]
--fecha fija la fecha de creación (creado, actualizado e inicio de la etapa 0) para recorridos con fechas simuladas o
proyectos que se registran después de empezar; por defecto, hoy.
"""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import esquema as E

DIARIO = {
    "es": "# Diario del proyecto · Daily log\n\n| fecha | entrada | responsable | seguimiento |\n|---|---|---|---|\n",
    "en": "# Daily log · Diario del proyecto\n\n| date | entry | owner | follow-up |\n|---|---|---|---|\n",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruta", required=True)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--idioma", default="es", choices=["es", "en"])
    ap.add_argument("--enfoque", default="predictivo", choices=["predictivo", "agil", "hibrido"])
    ap.add_argument("--ejecutivo", default="")
    ap.add_argument("--gestor", default="")
    ap.add_argument("--fecha", help="fecha de creación AAAA-MM-DD (defecto: hoy)")
    a = ap.parse_args()
    t = lambda es, en: E.t(a.idioma, es, en)
    if a.fecha:
        try: datetime.date.fromisoformat(a.fecha)
        except ValueError: sys.exit(t(f"--fecha debe tener el formato AAAA-MM-DD: {a.fecha}", f"--fecha must be YYYY-MM-DD: {a.fecha}"))

    if os.path.exists(os.path.join(a.ruta, "estado.json")):
        sys.exit(t("Ya existe estado.json en esa ruta; no se sobrescribe.", "estado.json already exists there; not overwritten."))
    for c in E.CARPETAS:
        os.makedirs(os.path.join(a.ruta, c), exist_ok=True)
    with E.bloqueo(a.ruta, nuevo=True):   # dos creaciones simultáneas en la misma ruta: la segunda no pisa a la primera
        if os.path.exists(os.path.join(a.ruta, "estado.json")):
            sys.exit(t("Ya existe estado.json en esa ruta; no se sobrescribe.", "estado.json already exists there; not overwritten."))
        for reg, spec in E.REGISTROS.items():
            if not spec.get("opcional"): E.asegurar_registro(a.ruta, reg)   # los opcionales se crean al primer uso
        diario = os.path.join(a.ruta, "03-control", "registros", "diario.md")
        if not os.path.exists(diario):
            open(diario, "w", encoding="utf-8").write(DIARIO[a.idioma])

        estado = E.estado_inicial(a.nombre, a.idioma, a.enfoque, a.ejecutivo, a.gestor)
        if a.fecha:
            estado["creado"] = estado["actualizado"] = estado["etapa_actual"]["inicio"] = a.fecha
        E.escribir_json(os.path.join(a.ruta, "estado.json"), estado)
    print(t(f"Proyecto creado en {a.ruta} · enfoque de entrega: {a.enfoque} · siguiente: estado.py siguiente",
            f"Project created in {a.ruta} · delivery approach: {a.enfoque} · next: estado.py siguiente"))

if __name__ == "__main__":
    main()
