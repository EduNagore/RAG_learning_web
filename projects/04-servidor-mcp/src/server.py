"""Servidor MCP: expone la búsqueda del índice como herramienta.

API comprobada en el README del SDK de Python (2026-10-06): `from mcp.server import MCPServer`,
`@mcp.tool()` y funciones con anotaciones de tipo. Para arrancarlo, el README muestra
`uv run mcp dev server.py`; consulta ahí cómo servirlo por stdio o HTTP en tu versión.
"""

from mcp.server import MCPServer

mcp = MCPServer("rag-docs")


@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> list[dict]:
    """Busca en la documentación y devuelve fragmentos con su identificador y fuente.

    TODO 1: conecta con el recuperador del proyecto 1 (o un BM25 sencillo).
    TODO 2: valida `top_k` (1 a 10) y devuelve un error claro si se sale de rango.
    TODO 3: filtra por los permisos de quien llama (¿cómo se identifica al cliente?).
    """
    raise NotImplementedError("Implementa search_docs")


if __name__ == "__main__":
    # TODO: arranca el servidor según el README del SDK para tu versión.
    raise SystemExit("Completa el arranque del servidor")
