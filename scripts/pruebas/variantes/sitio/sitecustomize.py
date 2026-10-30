"""sitecustomize de la suite de variantes (solo pruebas; se activa poniendo esta carpeta en PYTHONPATH).

- PM_SIN_DEPS=yaml,docx,openpyxl,matplotlib,playwright: esos imports fallan con ModuleNotFoundError, como si los
  paquetes no estuvieran instalados (perfil de dependencias mínimas, sin desinstalar nada ni salir a la red).
- PM_PRUEBA_SMTP_PLAZO=N: smtplib usa un plazo de N segundos (el script fija 30) para probar un servidor que no responde
  sin esperar medio minuto.
Al terminar, carga el sitecustomize que esta carpeta tapa, si existe."""
import os, sys

_bloqueados = {x.strip() for x in os.environ.get("PM_SIN_DEPS", "").split(",") if x.strip()}
if _bloqueados:
    class _Bloqueador:
        def find_spec(self, nombre, ruta=None, objetivo=None):
            if nombre.split(".")[0] in _bloqueados:
                raise ModuleNotFoundError(f"No module named '{nombre}' (bloqueado por PM_SIN_DEPS)", name=nombre)
            return None
        def find_module(self, nombre, ruta=None):   # Python < 3.4 / compatibilidad
            return None
    sys.meta_path.insert(0, _Bloqueador())
    import importlib.util as _iu        # como sin el paquete: find_spec devuelve None (sanidad INS-01 lo usa así)
    _find_spec = _iu.find_spec
    def _find_spec_bloqueado(nombre, paquete=None):
        if nombre.split(".")[0] in _bloqueados: return None
        return _find_spec(nombre, paquete)
    _iu.find_spec = _find_spec_bloqueado

_plazo = os.environ.get("PM_PRUEBA_SMTP_PLAZO")
if _plazo:
    import smtplib
    _ini_smtp = smtplib.SMTP.__init__
    def _con_plazo(self, host="", port=0, local_hostname=None, timeout=None, *a, **k):
        return _ini_smtp(self, host, port, local_hostname, float(_plazo), *a, **k)
    smtplib.SMTP.__init__ = _con_plazo

# sitecustomize tapado por esta carpeta (p. ej. el de la distribución)
_aqui = os.path.dirname(os.path.abspath(__file__))
for _p in sys.path:
    _c = os.path.join(_p, "sitecustomize.py")
    if _p and os.path.abspath(_p) != _aqui and os.path.isfile(_c):
        try:
            with open(_c, encoding="utf-8") as _fh: exec(compile(_fh.read(), _c, "exec"), {"__name__": "sitecustomize", "__file__": _c})
        except Exception:
            pass
        break
