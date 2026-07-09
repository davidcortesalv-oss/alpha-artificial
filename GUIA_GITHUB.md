# Automatización en GitHub — 10 minutos y te olvidas

Todo el trabajo técnico ya está hecho: el repositorio git está creado en tu
ordenador, los robots de GitHub (workflows) están escritos y el motor está
ARMADO en modo real. Solo faltan los pasos que necesitan TU cuenta.
Hazlos una vez y el torneo correrá solo cada lunes.

---

## Paso 1 — Crea la cuenta y el repositorio (3 min)

1. Entra en **github.com** y crea una cuenta (gratis) si no la tienes.
2. Arriba a la derecha: **+** → **New repository**.
3. Rellena SOLO esto:
   - Repository name: `alpha-artificial`
   - Visibilidad: **Public** (necesario para que la web y la automatización sean gratis)
   - NO marques "Add a README" ni nada más.
4. Botón verde **Create repository**. Te saldrá una página con comandos: ignórala y sigue aquí.

## Paso 2 — Sube el proyecto (2 min)

Abre una terminal en la carpeta `alpha-artificial` y pega estos dos comandos
(cambia `TU-USUARIO` por tu nombre de usuario de GitHub):

```
git remote add origin https://github.com/TU-USUARIO/alpha-artificial.git
git push -u origin main
```

La primera vez se abrirá una ventana del navegador para iniciar sesión.
Acepta y listo: el código ya está en GitHub.

⚠️ Tranquilo: el archivo `secrets.txt` con tus claves NO se sube nunca
(está bloqueado por `.gitignore`; lo hemos comprobado).

## Paso 3 — Pon las 5 claves como "Secrets" (3 min)

En tu repositorio de GitHub:

1. **Settings** → menú izquierdo **Secrets and variables** → **Actions**.
2. Botón **New repository secret**. Crea estos 5, uno a uno.
   El "Name" tiene que ser EXACTAMENTE este; el "Secret" es la clave que
   tienes en tu `secrets.txt`:

   | Name | Secret |
   |---|---|
   | `OPENAI_API_KEY` | tu clave de OpenAI |
   | `ANTHROPIC_API_KEY` | tu clave de Anthropic |
   | `GOOGLE_API_KEY` | tu clave de Google |
   | `DEEPSEEK_API_KEY` | tu clave de DeepSeek |
   | `MISTRAL_API_KEY` | tu clave de Mistral |

## Paso 4 — Enciende los robots (1 min)

1. Pestaña **Actions** del repositorio. Si sale un botón verde
   "I understand my workflows, go ahead and enable them", púlsalo.
2. Verás dos workflows: **"Ronda setmanal del torneig"** y **"Publicar la web"**.

## Paso 5 — La primera ronda (cuando TÚ quieras)

- Opción A (recomendada): no hagas nada. El lunes a las 09:30 (hora española
  de verano) se ejecutará sola la primera ronda oficial.
- Opción B: lánzala ya a mano: Actions → "Ronda setmanal del torneig" →
  **Run workflow** → botón verde.

Después de cada ronda, el robot guarda los resultados y publica la web sola.

## Tu web pública

En un par de minutos tras la primera ejecución de "Publicar la web":

```
https://TU-USUARIO.github.io/alpha-artificial/
```

(La dirección exacta también sale en Settings → Pages.)
Mientras no haya rondas oficiales, la web enseña la DEMOSTRACIÓ;
con la primera ronda pasará sola a "DADES REALS".

---

## Preguntas rápidas

**¿Cómo PAUSO el torneo?** Actions → "Ronda setmanal del torneig" → menú
"···" → **Disable workflow**. (Y "Enable" para reanudarlo.)

**¿Cuánto cuesta?** GitHub: 0 €. Las IAs: unos céntimos por semana
(solo se les llama una vez cada lunes).

**¿Y si un lunes falla una IA?** El motor reintenta hasta 5 veces; si aun
así no responde, esa IA queda como "mantenir" esa semana con el motivo
apuntado, y el torneo sigue. Nada se rompe.

**¿Tengo que tener el ordenador encendido?** No. Todo corre en los
servidores de GitHub.
