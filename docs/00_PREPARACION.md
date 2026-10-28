# 00 · Preparación: seis pasos (hazlos antes de la sesión 1)

Son los mismos seis pasos de la presentación. Tiempo: 20–30 minutos. Si algo no funciona, manda a quien imparte el
taller la salida completa del paso 6 **antes** de la sesión (no contiene tu token).

> En Windows los comandos usan `python` en lugar de `python3`, y las variables se ponen con `$env:NOMBRE="..."`.
> Después de instalar algo, **abre una terminal nueva** para que se reconozca.

## Paso 1 · Python 3.10 o más reciente

| Sistema | Qué hacer |
|---|---|
| **macOS** | Descarga el instalador de https://www.python.org/downloads (botón amarillo) y ábrelo. Si usas Homebrew: `brew install python`. El Python 3.9 que trae macOS **no sirve**. |
| **Windows** | Descarga el instalador de https://www.python.org/downloads. En la primera pantalla marca **«Add python.exe to PATH»**. O en PowerShell: `winget install -e --id Python.Python.3.13` |
| **Linux** | Ubuntu 24.04 ya lo trae (3.12). Si no: `sudo apt install python3` |

Comprueba: `python3 --version` (Windows: `python --version`) → 3.10 o más.

No necesitas instalar paquetes: las herramientas del repo usan solo la biblioteca estándar.

## Paso 2 · Node.js 22.19 o más reciente

pi lo requiere. Cualquier instalador **LTS** de https://nodejs.org cumple (la LTS actual es la 24).

| Sistema | Qué hacer |
|---|---|
| **macOS** | Instalador LTS de nodejs.org. O con Homebrew: `brew install node` |
| **Windows** | Instalador LTS (.msi) de nodejs.org. O en PowerShell: `winget install -e --id OpenJS.NodeJS.LTS` |
| **Linux** | Con nvm: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash`, cierra y abre la terminal, y luego `nvm install --lts` |

Comprueba: `node --version` → v22.19 o más.

## Paso 3 · pi, el agente

| Sistema | Qué hacer |
|---|---|
| **macOS y Linux** | `curl -fsSL https://pi.dev/install.sh \| sh` |
| **Windows** (PowerShell) | `powershell -c "irm https://pi.dev/install.ps1 \| iex"` |
| **Cualquiera** (alternativa con npm, que viene con Node) | `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` |

Comprueba: `pi --version`. Para actualizar más adelante: `pi update`.

## Paso 4 · Token de INEGI (gratuito)

1. Entra a https://www.inegi.org.mx/app/desarrolladores/generaToken/Usuarios/token_Verify
2. Escribe **tu** correo y envía. INEGI te manda el token por correo (revisa spam; puede tardar).
3. Guárdalo en la terminal, **no en un archivo**:

```
export INEGI_TOKEN="pega-aquí-tu-token"        # macOS y Linux
$env:INEGI_TOKEN="pega-aquí-tu-token"          # Windows (PowerShell)
```

Cada terminal nueva hay que repetirlo (o ponerlo en el perfil de tu terminal). Un token por persona: no lo compartas.

## Paso 5 · Conectar pi a un proveedor gratuito

pi necesita un modelo de lenguaje. Recomendamos **Google Gemini** (plan gratuito, sin tarjeta):

1. Entra a https://aistudio.google.com/apikey con tu cuenta de Google.
2. Pulsa **«Create API key»** y copia la clave.
3. Dásela a pi de una de dos formas:
   - **Opción A, variable en la terminal:** `export GEMINI_API_KEY="pega-aquí-tu-clave"` (Windows: `$env:GEMINI_API_KEY="..."`).
   - **Opción B, dentro de pi:** abre `pi`, escribe `/login`, elige Google y pega la clave cuando la pida.
4. Dentro de pi escribe `/model` y elige **`gemini-3.6-flash`** (el probado en el taller). Si no aparece en la lista,
   actualiza pi (`pi update`). Alternativas: `gemini-3.8-flash`, `gemini-3.5-flash-lite`. **Evita** los modelos «Pro» y
   «Argon»: son de pago.

Modelos de texto gratuitos según la página de precios de Google (27 de octubre de 2026): `gemini-3.8-flash`,
`gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite` y `gemini-3-flash-preview`. Google ya no publica
los límites del plan gratuito por modelo: los ves en AI Studio con tu clave; son por proyecto y se reinician a
medianoche, hora del Pacífico.

**Si ves «too many requests» (error 429):** es el cupo por minuto del plan gratuito; un agente hace varias llamadas
seguidas por pregunta y lo alcanza fácil. La carpeta del taller trae `.pi/settings.json` con reintentos automáticos:
pi espera (5, 10, 20, 40… segundos) y vuelve a intentar hasta 6 veces, así que verás un aviso de reintento en lugar de
un error. Se carga solo si abres pi con `-a` (como todo lo del repo). Si aun así falla, cambia a `gemini-3.5-flash-lite`
con la misma clave (`/model`).

Otros proveedores sin tarjeta (si Gemini no te funciona):

| Proveedor | Dónde se crea la clave | Variable que lee pi | Nota |
|---|---|---|---|
| Groq | https://console.groq.com/keys | `GROQ_API_KEY` | Para agentes: `openai/gpt-oss-120b`. Pocos tokens por minuto (8 mil en la tabla oficial): un agente avanza lento |
| OpenRouter (modelos `:free`) | https://openrouter.ai/keys | `OPENROUTER_API_KEY` | Solo 50 solicitudes al día sin créditos: no alcanza para el taller |

Cerebras no está en la lista porque pide un método de pago para activar la cuenta.

Crea **tu propia** cuenta y clave; no compartas claves ni las pegues en archivos. Los planes gratuitos tienen límites de
uso que cambian seguido y pueden usar tus conversaciones para mejorar el producto: **no subas datos personales ni
información sensible**. Aquí solo usamos datos públicos de INEGI.

Comprueba: `pi -p "Responde solo con la palabra: listo"` → debe responder «listo».

## Paso 6 · Descargar el material del taller y pasar el diagnóstico

El material está en un repositorio: **`<URL del repo>`** (te la damos junto con esta guía).

1. Descárgalo al Escritorio, de una de dos formas:
   - **Sin git (lo más simple):** en la página del repositorio, botón **Code → Download ZIP**; descomprime el ZIP en
     el Escritorio. La carpeta se llamará como el repositorio (a veces con `-main` al final): renómbrala a
     `taller-agentes-economia`.
   - **Con git:** `cd Desktop` y luego `git clone <URL del repo> taller-agentes-economia`
2. Entra a la carpeta y corre el diagnóstico:

```
cd taller-agentes-economia
python3 herramientas/doctor.py --red --modelo
```

Cada línea sale como `[OK]` o `[FALTA]` con qué hacer. Revisa Python, Node, pi, token, skills, credencial del modelo,
la herramienta de INEGI, la API de INEGI y una respuesta del modelo. Nunca muestra tu token.

Para ver el agente: `pi -a -ns` (confía en los archivos de la carpeta; en la sesión 1 trabajamos sin skills).

**Plan B.** Si no puedes descargar el repositorio, pide el archivo `instalar_taller.py`: guárdalo en el Escritorio y
corre `cd Desktop` y `python3 instalar_taller.py`. Crea la misma carpeta con todo el material y corre el diagnóstico,
sin internet ni git.

**Sin internet o sin token:** `INEGI_OFFLINE=1 python3 herramientas/inegi.py ficha 910392` usa respuestas guardadas.
La primera vez que uses `ficha`, `buscar` o `validar` con red, el programa descarga unos 8 MB de catálogos a `.cache/`.

## Lista de verificación

- [ ] `python3 --version` ≥ 3.10
- [ ] `node --version` ≥ 22.19 y `pi --version` responde
- [ ] `INEGI_TOKEN` exportado
- [ ] Clave de un proveedor conectada (`/login` o variable) y `pi -p "..."` responde
- [ ] `python3 herramientas/doctor.py --red --modelo` sin ningún `[FALTA]`
