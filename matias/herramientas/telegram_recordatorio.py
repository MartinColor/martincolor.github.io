#!/usr/bin/env python3
"""Manda a Matías por Telegram el recordatorio que toca ahora.

Lo corre GitHub Actions (.github/workflows/recordatorios-matias.yml). Sin dependencias externas.
Variables de entorno:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID  (secrets del repositorio; si faltan, no hace nada)
  CRON     la expresión cron que disparó el workflow, en UTC (ej: "10 14 * * 1-5")
  PRUEBA   si es "1", manda un mensaje de prueba
  HORA     (opcional) hora de Uruguay HH:MM a simular, para probar a mano
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

UY = timezone(timedelta(hours=-3))  # Uruguay no tiene horario de verano desde 2015
DATOS = json.loads((Path(__file__).resolve().parent.parent / "datos.json").read_text(encoding="utf-8"))


def enviar(token, chat, texto):
    datos = urllib.parse.urlencode({"chat_id": chat, "text": texto}).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos, timeout=20) as r:
        r.read()


def hora_del_cron(cron):
    minuto, hora = cron.split()[:2]
    t = datetime(2000, 1, 3, int(hora), int(minuto), tzinfo=timezone.utc).astimezone(UY)
    return f"{t:%H:%M}"


def main():
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("Faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID: no se manda nada.")
        return 0
    if os.environ.get("PRUEBA") == "1":
        enviar(token, chat, "👋 Hola Matías, soy tu Asistente de Martín Color. Desde ahora te aviso acá lo que toca en el día.")
        print("Mensaje de prueba enviado.")
        return 0

    ahora = datetime.now(UY)
    hora = os.environ.get("HORA") or (hora_del_cron(os.environ["CRON"]) if os.environ.get("CRON") else None)
    if not hora:
        print("Sin CRON ni HORA: no se sabe qué recordatorio mandar.")
        return 1
    dia = ahora.isoweekday()
    toca = [r for r in DATOS["recordatorios"] if r["hora"] == hora and dia in r["dias"]]
    if not toca:
        print(f"Nada para las {hora} del día {dia}.")
        return 0
    for r in toca:
        enviar(token, chat, f"⏰ {r['hora']} · {r['titulo']}\n\n{r['texto']}")
        print(f"Enviado: {r['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
