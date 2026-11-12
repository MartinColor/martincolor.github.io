# Asistente de Matías

Página: **https://martincolor.github.io/matias/** (no aparece en Google ni tiene enlace desde la web pública).

| Archivo | Para qué |
|---|---|
| `index.html` | La app del celular: Hoy · Presupuesto · Planillas · Productos |
| `datos.json` | **Todo lo editable**: productos, kits de presupuesto, tareas y horarios, listas de planillas, fichas |
| `Planillas-Matias.xlsx` | Las mismas planillas en Excel (celdas amarillas = completar) |
| `recordatorios-matias.ics` | Alarmas para el calendario del celular |
| `pc3/` | **El asistente de la PC3** (Claude de escritorio): instrucciones, equivalencias, presupuesto, productos, avisos. Ver `pc3/LEEME.md` |
| `asistente-matias-pc3.zip` | La carpeta `pc3/` lista para bajar y descomprimir en la PC3 |
| `herramientas/generar.py` | Regenera el Excel, el .ics, `pc3/productos.md` y el .zip desde `datos.json` |
| `herramientas/telegram_recordatorio.py` | Lo usa el bot de Telegram |

## Cambiar algo
Editar `datos.json` (códigos, cantidades, tareas, horas). Después:
```
pip install openpyxl
python3 matias/herramientas/generar.py
```
Si se cambia o agrega una **hora** de recordatorio, agregar también su línea `cron` en
`.github/workflows/recordatorios-matias.yml` (en UTC: hora de Uruguay + 3).

## Activar los avisos por Telegram (una sola vez)
1. Matías instala Telegram.
2. Desde Telegram, hablar con **@BotFather** → `/newbot` → nombre «Asistente de Matías». Te da un **token**.
3. Matías abre el bot nuevo y le manda «hola».
4. En el navegador abrir `https://api.telegram.org/bot<TOKEN>/getUpdates` y copiar el número de `"chat":{"id": ...}`.
5. En GitHub → este repositorio → Settings → Secrets and variables → Actions → New repository secret:
   `TELEGRAM_BOT_TOKEN` = el token, `TELEGRAM_CHAT_ID` = el número.
6. Actions → «Recordatorios de Matías» → Run workflow (sin hora) → le llega un mensaje de prueba.

Notas: los avisos programados de GitHub pueden llegar unos minutos tarde (a veces 10–15).
Por eso conviene **también** cargar las alarmas del calendario (`recordatorios-matias.ics`), que suenan a la hora exacta.
GitHub pausa los workflows programados si el repositorio pasa 60 días sin cambios: si dejan de llegar, entrar a Actions y reactivarlo.
