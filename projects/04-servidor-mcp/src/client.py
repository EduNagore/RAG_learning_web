"""Cliente MCP de ejemplo.

API comprobada en el README del SDK (2026-10-06): `from mcp import Client` y
`async with Client(<destino>) as client: await client.call_tool(nombre, argumentos)`.
El README documenta el destino HTTP (`http://localhost:8000/mcp`) y menciona que el cliente
también puede lanzar un servidor local como subproceso stdio o usar un transporte propio.
"""

import asyncio

from mcp import Client


async def main(target: str) -> None:
    async with Client(target) as client:
        result = await client.call_tool("search_docs", {"query": "plazo de devolución", "top_k": 3})
        # TODO: comprueba que un top_k inválido devuelve un error que el cliente puede mostrar
        # (distingue error de herramienta y error de protocolo).
        print(result.structured_content)


if __name__ == "__main__":
    asyncio.run(main("http://localhost:8000/mcp"))
