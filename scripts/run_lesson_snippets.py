"""Ejecuta los bloques ```python de las lecciones y falla si alguno lanza una excepción.

Uso: uv run python scripts/run_lesson_snippets.py [carpeta-de-lecciones]
     (por defecto, todas las lecciones)

Se omiten los bloques que no pueden ejecutarse aquí: los marcados con un comentario que contiene
"no se ejecuta" y los que importan paquetes externos o necesitan claves.
Los bloques de una misma lección comparten espacio de nombres, en orden (como en un cuaderno),
para que un fragmento pueda usar lo definido en el anterior.
"""

import contextlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "public" / "py"))

SKIP = (
    "no se ejecuta",
    "import tiktoken",
    "import anthropic",
    "import openai",
    "from pydantic",
    "import pydantic",
    "from langgraph",
    "from langchain",
    "from openai",
    "from anthropic",
    "import mcp",
    "from mcp",
    "import torch",
    "import faiss",
    "from sentence_transformers",
    "import qdrant",
    "from qdrant",
)
BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)

base = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "src" / "content" / "lessons"
failures = 0
ran = 0
for mdx in sorted(base.rglob("*.mdx")):
    namespace: dict = {"__name__": "__main__"}
    for i, block in enumerate(BLOCK.findall(mdx.read_text(encoding="utf-8")), 1):
        if any(marker in block for marker in SKIP):
            continue
        ran += 1
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(block, f"{mdx.name}#{i}", "exec"), namespace)  # noqa: S102
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"FALLA {mdx.relative_to(ROOT)} bloque {i}: {type(e).__name__}: {e}")
print(f"{ran} bloques ejecutados, {failures} fallos")
sys.exit(1 if failures else 0)
