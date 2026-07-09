# Guía de puesta en marcha — para David

Esta guía te lleva paso a paso desde "tengo unos archivos" hasta "el torneo corre solo cada lunes". Está pensada para que NO necesites saber programar. Ve a tu ritmo; no hace falta hacerlo todo de golpe.

---

## FASE A — Probarlo en tu ordenador (sin gastar nada)

El sistema ya funciona en "modo simulado" (con IAs de mentira), así que puedes verlo girar antes de tener ninguna clave.

1. **Instala Python** (si no lo tienes). Descárgalo de python.org. Al instalar, marca la casilla "Add Python to PATH".

2. **Abre una terminal** en la carpeta `alpha-artificial`.

3. **Instala las librerías** (las herramientas que usa el programa):
   ```
   pip install -r requirements.txt
   ```

4. **Ejecuta el motor**:
   ```
   python torneo.py
   ```

Si todo va bien, verás cómo baja los precios reales y las 5 IAs (de mentira) toman su decisión, y se creará el archivo `dades/decisions.csv`. Eso significa que **el sistema entero funciona**.

---

## FASE B — Conseguir las claves API (una a una, sin prisa)

Una "clave API" es como una contraseña que deja a tu programa hablar con cada IA. Cada empresa te da la suya desde su web. Suele costar un poco de dinero por uso (en tu caso, céntimos: tu documento estima 2-5 €/mes en total).

Empieza por UNA, la que quieras (Claude o GPT son las más fáciles):

- **Claude (Anthropic):** entra en console.anthropic.com → crea cuenta → "API Keys" → crea una.
- **GPT (OpenAI):** platform.openai.com → "API keys" → crea una.
- **Gemini (Google):** aistudio.google.com → "Get API key".
- **DeepSeek:** platform.deepseek.com → "API keys".
- **Mistral:** console.mistral.ai → "API keys".

⚠️ Una clave API es secreta. NUNCA la pongas en un archivo que subas a internet. Aquí ya está todo preparado para guardarlas de forma segura (mira el archivo `secrets.example.txt`).

Cuando tengas una clave, conectarla ya NO necesita programar nada: el código de las cinco empresas ya está escrito (archivo `connectors_ia.py`). Solo tienes que:

1. Copiar `secrets.example.txt` como `secrets.txt` y pegar ahí tu clave.
2. En `config.py`, poner `actiu: True` en ese modelo.
3. Cuando quieras jugar de verdad, cambiar `MODE_SIMULAT = False` en `torneo.py`.

La web tiene una sección "Configuració d'APIs" que te enseña el estado de cada conexión y los enlaces para conseguir cada clave.

---

## FASE C — Subirlo a GitHub

GitHub es la nube gratuita donde vivirá el proyecto y desde donde se ejecutará solo.

1. Crea una cuenta en github.com (gratis).
2. Crea un repositorio nuevo (puede ser privado).
3. Sube esta carpeta `alpha-artificial`.

Cuando llegues aquí, te guío con los detalles (es más fácil de lo que parece).

---

## FASE D — Que corra solo cada lunes

Una vez en GitHub, se activa la automatización (un archivo que ya te dejaré preparado en `.github/workflows/`). A partir de ahí, GitHub ejecuta el torneo cada lunes a las 08:00 sin que toques nada, ni con tu ordenador apagado.

---

## La web pública

La web vive en la carpeta `web/`. Para verla en tu ordenador:

```
python -m http.server 8099 --directory web
```

y abre http://localhost:8099 en el navegador.

Mientras el torneo no empiece, enseña datos de DEMOSTRACIÓN (lo pone arriba a la derecha). Cuando el torneo real tenga historial, ejecuta `python generar_web.py` después de cada ronda y la web pasará sola a "DADES REALS". Para publicarla gratis: GitHub Pages (activando Pages sobre la carpeta `web/` del repositorio).

⚠️ Los datos que hay ahora en `dades/` son de prueba. El día que empiece el torneo de verdad, borra el contenido de `dades/` para empezar de cero.

---

## ¿Dónde estás ahora?

✅ Estructura del proyecto creada
✅ Motor funcionando (con memoria entre semanas y reglas reales)
✅ Conectores de las 5 IAs escritos y PROBADOS con tus claves
✅ Titulares de actualidad conectados (WSJ, CNBC, MarketWatch — idénticos para las 5)
✅ Web completa funcionando
✅ Las 5 IAs activadas y `MODE_SIMULAT = False`: el torneo está ARMADO
✅ Repositorio git creado y workflows de automatización escritos
⬜ Subir a GitHub, poner los Secrets y encender los robots  ← **tu siguiente paso: sigue GUIA_GITHUB.md**

A partir de ahí, cada lunes a las 09:30 la ronda corre sola y la web se actualiza sola.
