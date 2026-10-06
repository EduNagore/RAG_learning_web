# Proyecto 4: Servidor MCP propio

Guía completa en la web del curso: `/proyectos/04-servidor-mcp/`.

## Objetivo

Exponer tu índice de RAG como herramienta MCP (y, como extensión, los documentos como recursos) con el SDK oficial de Python, y consumirlo desde un cliente MCP. Aplica lo aprendido sobre diseño de herramientas, errores y seguridad.

## Puesta en marcha

```bash
uv sync
cp .env.example .env
```

El SDK `mcp` se comprobó en PyPI (2.3, 2026-10-06) y en su README (`MCPServer`, `@mcp.tool()`, `Client`, `call_tool`). Es una API joven que cambia entre versiones mayores: antes de seguir, lee el README de tu versión.

## Qué hay que completar

`src/server.py` (la herramienta `search_docs` y el arranque) y `src/client.py` (el cliente y las comprobaciones de error).

## Criterios de evaluación

- La descripción de la herramienta explica cuándo usarla; los argumentos están tipados y validados.
- Los errores de herramienta son informativos y se distinguen de los errores de protocolo.
- El servidor no devuelve contenido sin comprobar los permisos de quien llama.
- Pruebas automáticas del servidor con un cliente MCP.

## Extensiones

Recursos y plantillas de prompt, autorización, límites de uso y registro de llamadas; conectar el servidor al proyecto 3 como herramienta de búsqueda.
