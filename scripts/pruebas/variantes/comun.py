"""Utilidades de la suite de variantes (scripts/pruebas/variantes/): ejecución de scripts con un intérprete y un entorno
dados, registro de comprobaciones, omisiones observadas e invariantes comunes (sin traza, JSON válido, ids únicos,
huella de BMAD). Solo biblioteca estándar; compatible con Python 3.9."""
import csv, hashlib, json, os, re, shutil, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
FIX = os.path.join(RAIZ, "scripts", "pruebas", "fixtures")
SITIO = os.path.join(AQUI, "sitio")          # sitecustomize de prueba (bloqueador de imports y plazo SMTP corto)
S = os.path.join(RAIZ, "skills", "pm-estado-proyecto", "scripts")
SCR = {
    "nuevo": os.path.join(S, "nuevo_proyecto.py"), "estado": os.path.join(S, "estado.py"), "registro": os.path.join(S, "registro.py"),
    "sanidad": os.path.join(S, "sanidad.py"), "puertas": os.path.join(S, "puertas.py"), "especificacion": os.path.join(S, "especificacion.py"),
    "exportar": os.path.join(S, "exportar.py"), "evm": os.path.join(S, "evm.py"),
    "bmad": os.path.join(RAIZ, "skills", "pm-bmad-puente", "scripts", "bmad.py"),
    "paquete": os.path.join(RAIZ, "skills", "pm-exportar", "scripts", "paquete.py"),
    "decision": os.path.join(RAIZ, "skills", "pm-direccion-decisiones", "scripts", "decision.py"),
    "riesgos": os.path.join(RAIZ, "skills", "pm-riesgos", "scripts", "riesgos.py"),
    "envios": os.path.join(RAIZ, "skills", "pm-integraciones", "scripts", "envios.py"),
    "interesados": os.path.join(RAIZ, "skills", "pm-interesados", "scripts", "interesados.py"),
    "guardian": os.path.join(RAIZ, "hooks", "guardian.py"), "inicio": os.path.join(RAIZ, "hooks", "inicio.py"),
    "idioma": os.path.join(RAIZ, "hooks", "idioma.py"),
}
PY39 = os.environ.get("PM_PYTHON39") or "/tmp/py39/bin/python"


def interpretes():
    """{'3.9': ruta|None, '3.13': ruta} — 3.13 es el intérprete que corre la suite (o PM_PYTHON313)."""
    py39 = PY39 if os.path.exists(PY39) else (shutil.which("python3.9") or None)
    return {"3.9": py39, "3.13": os.environ.get("PM_PYTHON313") or sys.executable}


def version_de(py):
    try:
        return subprocess.run([py, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


class Registro:
    """Comprobaciones, omisiones observadas y bitácora de comandos de una unidad (celda o nivel)."""
    def __init__(self, nivel, unidad, carpeta=None):
        self.nivel, self.unidad, self.carpeta = nivel, unidad, carpeta
        self.checks, self.omisiones, self.trazas, self.log, self.notas = [], [], [], [], []
        self.esperadas, self.celda = [], None      # omisiones esperadas (manifiesto) y ejes, si es una celda de la matriz
        self.t0 = time.time()
        if carpeta: os.makedirs(carpeta, exist_ok=True)

    def check(self, nombre, cond, detalle=""):
        self.checks.append({"comprobacion": nombre, "ok": bool(cond), "detalle": "" if cond else str(detalle)[:800]})
        print(f"  {'OK   ' if cond else 'FALLO'} [{self.unidad}] {nombre}" + (f" — {str(detalle)[:400]}" if detalle and not cond else ""), flush=True)
        return bool(cond)

    def omitir(self, clave, motivo):
        if clave not in [o["clave"] for o in self.omisiones]:
            self.omisiones.append({"clave": clave, "motivo": motivo})

    def resumen(self):
        return {"nivel": self.nivel, "unidad": self.unidad, "ok": sum(c["ok"] for c in self.checks),
                "fallo": sum(not c["ok"] for c in self.checks), "checks": self.checks, "omisiones": self.omisiones,
                "trazas": self.trazas, "notas": self.notas, "esperadas": self.esperadas, "celda": self.celda, "duracion_s": round(time.time() - self.t0, 1)}

    def guardar_log(self):
        if not self.carpeta: return
        with open(os.path.join(self.carpeta, "comandos.log"), "w", encoding="utf-8") as fh:
            for x in self.log:
                fh.write(f"$ {x['cmd']}\n(cwd {x['cwd']} · código {x['rc']} · {x['s']} s)\n{x['out']}\n{x['err']}\n\n")


class Ejecutor:
    """Corre scripts con un intérprete y un entorno fijos; anota cada comando y detecta trazas de Python."""
    def __init__(self, reg, py, env_extra=None, cwd=None):
        self.reg, self.py, self.cwd = reg, py, cwd
        base = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING", "PYTHONPATH", "PM_SIN_DEPS")}
        self.env = {**base, **{k: v for k, v in (env_extra or {}).items() if v is not None}}

    def __call__(self, clave, *args, ok=(0,), entrada=None, cwd=None, timeout=300, paso=""):
        script = SCR.get(clave, clave)
        cmd = [self.py, script] + [str(a) for a in args]
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=cwd or self.cwd, capture_output=True, input=entrada, env=self.env, timeout=timeout)
            out, err, rc = r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace"), r.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", f"(sin respuesta en {timeout} s)", -9
        vis = " ".join([os.path.basename(script)] + [str(a) for a in args])
        self.reg.log.append({"cmd": vis, "cwd": cwd or self.cwd, "rc": rc, "s": round(time.time() - t0, 1), "out": out[-4000:], "err": err[-3000:]})
        res = Res(vis, rc, out, err)
        if "Traceback (most recent call last)" in out + err:
            self.reg.trazas.append({"paso": paso or vis, "comando": vis, "cola": (err or out)[-600:]})
            self.reg.check(f"{paso or vis}: sin traza de Python", False, (err or out)[-400:])
        if ok is not None and rc not in ok:
            self.reg.check(f"{paso or vis}: código {rc} (esperado {'/'.join(map(str, ok))})", False, (err + out)[-500:])
        return res


class Res:
    def __init__(self, cmd, rc, out, err): self.cmd, self.rc, self.out, self.err = cmd, rc, out, err
    @property
    def todo(self): return self.out + "\n" + self.err
    def json(self):
        try: return json.loads(self.out)
        except ValueError: return None


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as fh: return list(csv.DictReader(fh))


def ids_repetidos(proyecto):
    """{registro: [ids repetidos]} de todos los registros CSV del proyecto."""
    out = {}
    regs = os.path.join(proyecto, "03-control", "registros")
    for f in sorted(os.listdir(regs)) if os.path.isdir(regs) else []:
        if not f.endswith(".csv"): continue
        ids = [x.get("id", "") for x in leer_csv(os.path.join(regs, f))]
        rep = sorted({i for i in ids if i and ids.count(i) > 1})
        if rep: out[f] = rep
    return out


def huella(raiz, carpetas=("_bmad", "_bmad-output", ".bmad-core", "docs")):
    """sha256 de cada archivo de las carpetas de BMAD (solo lectura para pm-method)."""
    out = {}
    for c in carpetas:
        base = os.path.join(raiz, c)
        for d, _, fs in os.walk(base):
            for f in fs:
                p = os.path.join(d, f)
                with open(p, "rb") as fh: out[os.path.relpath(p, raiz)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def idioma_de(texto):
    """Heurística del hook de idioma (hooks/idioma.py), importada por ruta."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("pm_idioma_hook", SCR["idioma"])
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.idioma_de(texto)


def escribir(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as fh: fh.write(texto)
