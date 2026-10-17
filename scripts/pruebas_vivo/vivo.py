#!/usr/bin/env python3
"""Arnés de pruebas EN VIVO: ejecuta Claude Code real (claude -p) con el plugin cargado y analiza qué hizo el modelo.
Live test harness: runs real Claude Code with the plugin and inspects the stream of events.

Requisitos: CLI `claude` autenticada. Costo: cada escenario consume tokens del modelo.
Uso como biblioteca:
    from vivo import Sesion
    s = Sesion(cwd="/tmp/x", plugin="/ruta/pm-method")
    r = s.turno("/pm-method:pm-estado")          # primer turno
    r2 = s.turno("Aprobado por el Ejecutivo")      # continúa la misma sesión (--resume)
    r.skills, r.agentes, r.bash, r.negaciones, r.texto, r.costo
Uso por línea de comandos (un turno):
    python3 vivo.py --cwd /tmp/x "/pm-method:pm-ayuda"
"""
import argparse, json, os, subprocess, sys, time

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Resultado:
    def __init__(self):
        self.skills, self.agentes, self.bash, self.escrituras, self.herramientas = [], [], [], [], []
        self.negaciones, self.hooks, self.texto, self.errores = [], [], [], []
        self.costo, self.turnos, self.session_id, self.subtipo, self.crudo = 0.0, 0, None, None, []
    def resumen(self):
        return {"skills": self.skills, "agentes": self.agentes, "bash": [b[:160] for b in self.bash], "escrituras": self.escrituras,
                "negaciones": self.negaciones, "costo_usd": round(self.costo or 0, 4), "turnos": self.turnos, "fin": self.subtipo,
                "texto_final": (self.texto[-1][:1500] if self.texto else "")}

def analizar(lineas):
    r = Resultado()
    for l in lineas:
        try: d = json.loads(l)
        except Exception: continue
        r.crudo.append(d)
        t = d.get("type")
        if t == "system" and d.get("subtype") == "init":
            r.session_id = d.get("session_id")
        elif t == "system" and d.get("subtype") == "hook_response":
            r.hooks.append({"hook": d.get("hook_name"), "stdout": (d.get("stdout") or "")[:600], "exit": d.get("exit_code")})
            if "permissionDecision" in (d.get("stdout") or "") and '"deny"' in (d.get("stdout") or ""):
                r.negaciones.append((d.get("stdout") or "")[:300])
        elif t in ("assistant", "user"):
            msg = d.get("message") or {}
            for c in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if c.get("type") == "tool_use":
                    n, inp = c.get("name"), c.get("input") or {}
                    r.herramientas.append(n)
                    if n == "Skill": r.skills.append(inp.get("skill") or inp.get("command") or str(inp)[:80])
                    elif n in ("Agent", "Task"): r.agentes.append(inp.get("subagent_type") or inp.get("agent") or "?")
                    elif n == "Bash": r.bash.append(inp.get("command", ""))
                    elif n in ("Write", "Edit", "MultiEdit"): r.escrituras.append(inp.get("file_path", ""))
                elif c.get("type") == "text" and t == "assistant" and not d.get("parent_tool_use_id"):
                    r.texto.append(c.get("text", ""))
                elif c.get("type") == "tool_result" and c.get("is_error"):
                    cont = c.get("content"); r.errores.append(str(cont)[:300])
        elif t == "result":
            r.costo, r.turnos, r.subtipo = d.get("total_cost_usd") or 0, d.get("num_turns"), d.get("subtype")
            r.session_id = d.get("session_id") or r.session_id
            if d.get("result"): r.texto.append(d.get("result"))
    return r

class Sesion:
    def __init__(self, cwd, plugin=RAIZ, max_turns=40, timeout=1500, modelo=None, extra=None, registro=None):
        self.cwd, self.plugin, self.max_turns, self.timeout, self.modelo = cwd, plugin, max_turns, timeout, modelo
        self.extra, self.session_id, self.registro = extra or [], None, registro
        os.makedirs(cwd, exist_ok=True)

    def turno(self, prompt, max_turns=None):
        cmd = ["claude", "-p", prompt, "--plugin-dir", self.plugin, "--output-format", "stream-json", "--verbose",
               "--max-turns", str(max_turns or self.max_turns), "--dangerously-skip-permissions"] + self.extra
        if self.modelo: cmd += ["--model", self.modelo]
        if self.session_id: cmd += ["--resume", self.session_id]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, timeout=self.timeout, stdin=subprocess.DEVNULL)
        r = analizar(p.stdout.splitlines())
        r.segundos = round(time.time() - t0, 1)
        if r.session_id: self.session_id = r.session_id
        if self.registro:
            with open(self.registro, "a", encoding="utf-8") as f:
                f.write(json.dumps({"prompt": prompt, "cwd": self.cwd, **r.resumen(), "segundos": r.segundos}, ensure_ascii=False) + "\n")
        return r

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("prompt"); ap.add_argument("--cwd", default=os.getcwd()); ap.add_argument("--max-turns", type=int, default=20)
    a = ap.parse_args()
    r = Sesion(a.cwd).turno(a.prompt, a.max_turns)
    print(json.dumps(r.resumen(), ensure_ascii=False, indent=2))
