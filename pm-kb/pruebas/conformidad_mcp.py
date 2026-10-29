"""Conformidad de pm-kb con el SDK oficial de MCP para Python (el que usa Hermes Agent): stdio y HTTP.

Requiere el SDK en un entorno aparte (no es dependencia de pm-kb): python3 -m venv /tmp/mcp && /tmp/mcp/bin/pip install mcp==2.3.0
  /tmp/mcp/bin/python pm-kb/pruebas/conformidad_mcp.py stdio            # usa ~/.local/bin/pm-kb mcp
  /tmp/mcp/bin/python pm-kb/pruebas/conformidad_mcp.py http <token> [url]
Necesita un proyecto indexado que contenga C-003 (p. ej. el portal-socios del caso E2E-1).
"""
import asyncio, os, sys
import httpx2
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

async def probar(r, w, nombre):
    async with ClientSession(r, w) as s:
        ini = await s.initialize()
        tools = await s.list_tools()
        res = await s.call_tool("buscar", {"consulta": "licencias de diseño", "k": 2})
        txt = res.content[0].text
        print(f"{nombre}: protocolo {ini.protocol_version} · {len(tools.tools)} herramientas · isError {res.is_error} · C-003 en resultado: {'C-003' in txt}")
        res = await s.call_tool("ficha", {"id": "no-existe"})
        print(f"{nombre}: ficha inexistente → isError {res.is_error}: {res.content[0].text[:60]}")

async def main():
    modo = sys.argv[1]
    if modo == "stdio":
        p = StdioServerParameters(command=os.path.expanduser("~/.local/bin/pm-kb") if os.path.exists(os.path.expanduser("~/.local/bin/pm-kb")) else str(__import__("pathlib").Path(__file__).resolve().parents[1] / "pm-kb"), args=["mcp"],
                                  env={k: v for k, v in os.environ.items() if k.startswith("PMKB_") or k in ("PATH", "HOME")})
        async with stdio_client(p) as (r, w):
            await probar(r, w, "stdio")
    else:
        async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {sys.argv[2]}"}) as c:
            async with streamable_http_client(sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8765/mcp", http_client=c) as t:
                await probar(t[0], t[1], "http")

asyncio.run(main())
