# Guía de contenido

Cómo escribir lecciones, quizzes y laboratorios. Complementa `PLAN.md` (§8 y §9). Las reglas marcadas con **[CI]** las comprueba `pnpm validate` o el esquema Zod y rompen la integración si se incumplen.

## 1. Estructura de una lección

Archivo: `src/content/lessons/<modulo>/<NN-slug>.mdx`. El id de la lección es `<modulo>/<NN-slug>`.

Orden de secciones (los títulos pueden variar, salvo los marcados):

1. **Intuición**: el problema que resuelve, con un ejemplo concreto (usa el corpus ficticio de Nimbus Logística cuando encaje).
2. **Cómo funciona**: explicación técnica, fórmulas (KaTeX) y al menos un diagrama por módulo.
3. **En código**: fragmento mínimo de Python. Si es ejecutable, debe ejecutarse **de verdad** antes de publicarlo y su salida comentada debe coincidir. Si requiere paquetes externos o claves, dilo en un comentario (`# no se ejecuta en el navegador`).
4. **`## … Trade-offs …`** **[CI]**: cuándo usarlo y cuándo no.
5. **`## Errores comunes …`** **[CI]**: fallos típicos en producción.
6. **`<Callout type="entrevista">`** **[CI]**: 2–3 preguntas típicas con pista de respuesta.
7. **`<KeyTakeaways>`** **[CI]**: ideas clave.
8. Fuentes y mini-quiz: se renderizan solos desde el frontmatter y el YAML del quiz.

Longitud **[CI]**: mínimo 1.500 palabras sin contar bloques de código (máximo recomendado 3.000). No rellenes: si falta, añade profundidad útil (casos, métricas, errores reales), no paja.

## 2. Frontmatter

Lo valida el esquema Zod de `src/content.config.ts` **[CI]**. Reglas adicionales de `validate-content.mjs` **[CI]**:

- `module` coincide con la carpeta y existe en `src/content/modules/`.
- `order` único dentro del módulo; `prerequisites` apuntan a lecciones existentes.
- `sources`: mínimo 2, URLs no repetidas, `lastReviewed` no futura.
- `volatility: high` exige al menos un `<Snapshot date="AAAA-MM">`.

## 3. Fuentes y veracidad

- **Antes de redactar**, consulta fuentes primarias del tema con búsqueda web (papers, especificaciones, documentación oficial, blogs de ingeniería de los laboratorios). No te fíes solo de tu memoria.
- **Verifica cada referencia**: abre la página y comprueba título, autores y año. Nunca inventes URLs, autores ni títulos. Si no puedes verificar una referencia, no la pongas.
- **Cifras**: toda cifra debe venir de una fuente citada o de un cálculo reproducible que puedas enseñar (código o tabla). Si calculas algo, ejecuta el cálculo y usa el resultado, no una estimación mental.
- **Lo que cambia con el tiempo** (versiones, precios, nombres de modelos, límites, benchmarks) va en un `<Snapshot date="AAAA-MM">` con la fecha de verificación. El resto de la lección debe ser estable.
- **Atribuye las cifras de proveedor** ("según la documentación de X", "en sus pruebas") en lugar de presentarlas como constantes.
- **No presentes como hecho lo que no hayas verificado.** Si es opinión o práctica habitual sin fuente, dilo ("una regla práctica…", "suele…").
- Registra las fuentes nuevas en `docs/SOURCES.md`.

## 4. Estilo

- Español claro y directo; términos técnicos en inglés cuando así se usan en la industria. La primera vez, en cursiva y con equivalente: "fragmentación (_chunking_)".
- Sin emojis decorativos ni relleno. Frases cortas. Un ejemplo concreto antes que una definición abstracta.
- Tablas para comparar; listas para enumerar; prosa para explicar.
- Las "Preguntas típicas" van en cursiva y entre comillas, con una **Pista** de la respuesta esperada, no la respuesta completa.

## 5. Componentes MDX

Disponibles sin importar (se inyectan en `src/pages/teoria/[...slug].astro`):

| Componente                                                     | Uso                                                                         |
| -------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `<Callout type="nota\|consejo\|aviso\|peligro\|entrevista" title="…">` | Notas destacadas. `entrevista` es obligatorio una vez por lección.         |
| `<Snapshot date="AAAA-MM">`                                    | Información que caduca. Siempre con fecha.                                  |
| `<Diagram caption="…" code={`…`} />`                           | Diagrama Mermaid. La `caption` es también el texto accesible.               |
| `<KeyTakeaways>`                                               | Cierre con las ideas clave (lista).                                         |

Fórmulas: `$…$` en línea y `$$…$$` en bloque (KaTeX).

### Trampas de MDX que ya nos han mordido

- **Líneas en blanco dentro de componentes.** Para que el contenido de un `<Callout>`, `<Snapshot>` o `<KeyTakeaways>` se interprete como Markdown (listas, negritas), deja una línea en blanco después de la etiqueta de apertura y antes de la de cierre.
- **Llaves y `<` en prosa.** En MDX, `{…}` es una expresión y `<` abre una etiqueta. Fuera de código, evita escribirlos sueltos; ponlos en `` `código en línea` `` o en un bloque de código. Dentro de `$…$` las llaves sí son seguras.
- **Código Mermaid en `code={`…`}`**: usa una plantilla literal (acentos graves). No incluyas acentos graves dentro del diagrama.
- **Tablas anchas**: se desplazan horizontalmente en móvil, pero mantén las celdas breves.
- **Bloques de código con `{{…}}`** (marcadores de plantilla) son seguros dentro de ``` ```.

## 6. Quizzes

Archivo: `src/content/quizzes/<modulo>/<NN-slug>.yaml` (mismo id que la lección). Esquema en `src/content.config.ts` **[CI]**.

- 6–10 preguntas por lección, mezcla de tipos (`single`, `multiple`, `truefalse`, `order`, `code-output`) y dificultades (1–3).
- Ids **únicos globales** **[CI]**; por convención con el patrón `<modulo>-<NN>-q<k>` (el patrón no se comprueba).
- `explanation` **[CI, mínimo 40 caracteres]** justifica la correcta **y** por qué las otras no lo son.
- `ref` apunta a un ancla real de la lección **[CI]** (el slug del encabezado, p. ej. `#la-ventana-de-contexto`).
- **Verdadero/falso equilibradas** **[CI]**: si un módulo tiene 4 o más, ninguna respuesta puede superar el 80 %. Redacta unas como afirmaciones ciertas y otras como falsas; si todas son falsas, se acierta sin saber.
- El Markdown de prompts, opciones y explicaciones se renderiza en build, pero el **HTML crudo se escapa**: escribe `<documents>` entre acentos graves o aparecerá literal de todos modos. No hay KaTeX en las preguntas.
- Las opciones **se barajan** al mostrarlas (salvo en verdadero/falso): **no te refieras a ellas por su posición** ("la primera opción", "las tres primeras", "todas las anteriores") **[CI]**. Describe su contenido.
- Los tipos `order` no llevan `answer`: `options` ya está en el orden correcto.
- Los distractores deben ser plausibles (errores reales), no absurdos. Evita "todas las anteriores".
- Cada pregunta evalúa comprensión, no memoria de una cifra de un `Snapshot`.

## 7. Laboratorios

Se definen en la fase F3. Cada lab: `index.mdx`, `starter.py`, `solution.py`, `test_lab.py` con ≥ 4 tests (al menos uno oculto) y mensajes de error en español. `tests/labs/test_all_labs.py` exige que la solución pase y el starter falle **[CI]**.

## 8. Antes de abrir un PR de contenido

```powershell
pnpm validate    # referencias cruzadas, estructura y longitud
pnpm check       # tipos y esquemas
pnpm build; pnpm test:e2e
```

Revisa visualmente la lección en `pnpm dev` (claro y oscuro, y a 390 px de ancho).
