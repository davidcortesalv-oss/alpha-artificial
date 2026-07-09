# CLAUDE.md — Contexto del proyecto ALPHA ARTIFICIAL

> Este archivo lo lee Claude Code automáticamente al abrir la carpeta. Le da todo el contexto que necesita. Si trabajas en la web del torneo, lee esto primero.

## Qué es este proyecto

Es el sistema de un Treball de Recerca (TR) de Bachillerato llamado **ALPHA ARTIFICIAL**, de David Cortés (Monlau, 2026-27). El TR responde a la pregunta: **¿puede una IA batir al mercado?**

El experimento: cinco modelos de IA (GPT, Claude, Gemini, DeepSeek, Mistral) reciben cada uno 10.000 € virtuales y los gestionan durante 5 meses invirtiendo en ETFs reales. Una vez por semana (lunes) cada IA decide si mantiene o reajusta su cartera. Compiten contra el índice S&P 500 (gestión pasiva), que es el verdadero rival a batir. El autor (David) participa fuera de competición, no en el ranking oficial.

Hay dos preguntas de investigación: (1) ¿bate alguna IA al índice? (2) ¿muestran las IAs sesgos conductuales humanos (pánico, sobreoperar, exceso de confianza) al decidir? — economía conductual, Kahneman.

## Importante sobre el autor

David **no programa**. Explícale las cosas en castellano y de forma sencilla. El código puede llevar comentarios en castellano. Todo lo que sea **público o visible (la web, sus textos, botones, títulos) debe ir en CATALÀ**, porque el TR se entrega en catalán.

## Cómo funciona el motor (ya construido)

- `config.py` — todas las reglas y datos: capital (10.000 €), comisión (0,1%), máximo 40% por ETF, los 5 modelos y el universo de ~20 ETFs reales (con ticker, nombre y categoría).
- `torneo.py` — el motor. Cada ronda baja precios reales (yfinance), monta un briefing idéntico para las 5 IAs, recoge su decisión en JSON, valida reglas y guarda en CSV. Ahora mismo en `MODE_SIMULAT = True` (IAs de mentira, para probar gratis).
- `prompts/prompt_setmanal.txt` — las instrucciones que recibe cada IA.
- `dades/` — el historial en CSV (esta es la fuente de datos de la web).

## La forma de los datos (lee de aquí, NO te la inventes)

La web debe leer los CSV de la carpeta `dades/`. Estructura actual:

**`dades/decisions.csv`** — una fila por decisión de cada IA cada semana:
```
data, setmana, model, decisio, nivell_risc, confianca, valor_cartera, justificacio
```
- `model`: uno de gpt / claude / gemini / deepseek / mistral
- `decisio`: "mantenir" o "reajustar"
- `nivell_risc`: conservador / moderat / agressiu
- `confianca`: 1-10
- `valor_cartera`: valor en € de la cartera esa semana
- `justificacio`: texto en catalán del porqué de la decisión

(Habrá más CSV a medida que crezca el motor, p. ej. `carteres.csv` con la composición actual. Si necesitas un dato que no existe aún, dilo en vez de inventarlo.)

Los nombres legibles de los modelos y de los ETFs están en `config.py` (MODELS y UNIVERS_ETFS). Úsalos.

## Qué debe mostrar la web

1. **Ranking en directo** — clasificación de las 5 IAs + el índice S&P 500 + David (fuera de ranking, marcado aparte), ordenado por rentabilidad. Es el corazón de la página.
2. **Gráfica de evolución** — línea temporal con el valor de cada cartera semana a semana.
3. **Detalle por IA** — al hacer clic en una IA: su cartera actual, su historial de decisiones y sus justificaciones escritas.
4. **Análisis de sesgos conductuales** — sección que resuma patrones: quién sobreopera, quién muestra más confianza antes de perder, etc.
5. **Lista de ETFs disponibles** — el universo de inversión (de `config.py`), con nombre y categoría.

## Decisiones ya cerradas (no cambiar)

- Duración: 5 meses. Sin fecha exacta de inicio ("aquest estiu").
- 1 decisión por semana, NO diaria.
- David participa fuera de competición, NO es "experto".
- Las 5 IAs reciben información idéntica (control de variables).

## Decisiones libres para Claude Code

- **Tecnología de la web**: elige tú. Opción natural y recomendada por el diseño original: Streamlit (Python, lee los CSV directamente, hosting gratis, encaja con el motor). Pero si ves mejor otra cosa, propónla con sus pros y contras.
- **Estética**: libertad. Como referencia, la presentación del TR usa fondo negro (#070707) + ámbar (#ffb000) + crema, estilo terminal/editorial. Puedes seguir esa línea para coherencia de marca, o proponer un dashboard financiero limpio. Lo importante: que se vea TODO con claridad y que impresione (la web es pública y se enseñará).

## Estado y siguiente paso

El motor funciona en modo simulado. La web puede empezar a construirse ya con datos de ejemplo/simulados y conectarse a los datos reales cuando el torneo arranque. Genera datos de ejemplo realistas si hace falta para ver la web funcionando.
