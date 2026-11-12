#!/usr/bin/env python3
"""Genera matias/Planillas-Matias.xlsx y matias/recordatorios-matias.ics desde matias/datos.json.

Uso:  python3 matias/herramientas/generar.py      (necesita: pip install openpyxl)
Volver a correrlo cada vez que se cambie datos.json.
"""
import json
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

BASE = Path(__file__).resolve().parent.parent
D = json.loads((BASE / "datos.json").read_text(encoding="utf-8"))
PROD = {p["id"]: p for p in D["productos"]}

NEGRO, ROJO, CREMA = "232323", "D42200", "F0E7D8"
fino = Side(style="thin", color="B8AC98")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
CAB = Font(bold=True, color="FFFFFF", size=12)
CAB_FILL = PatternFill("solid", fgColor=NEGRO)
EDIT_FILL = PatternFill("solid", fgColor="FFF6D6")  # celdas para completar
TIT = Font(bold=True, size=16, color=ROJO)


def titulo(ws, texto, sub=None, ancho=6):
    ws["A1"] = texto
    ws["A1"].font = TIT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ancho)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="5F5B6B")
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ancho)


def cabecera(ws, fila, cols, anchos):
    for i, (c, w) in enumerate(zip(cols, anchos), start=1):
        cel = ws.cell(row=fila, column=i, value=c)
        cel.font, cel.fill, cel.border = CAB, CAB_FILL, BORDE
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[cel.column_letter].width = w
    ws.row_dimensions[fila].height = 30


def grilla(ws, desde, hasta, ncols, editables=()):
    for r in range(desde, hasta + 1):
        ws.row_dimensions[r].height = 24
        for c in range(1, ncols + 1):
            cel = ws.cell(row=r, column=c)
            cel.border = BORDE
            cel.alignment = Alignment(vertical="center", wrap_text=True)
            if c in editables:
                cel.fill = EDIT_FILL


def hoja_presupuesto(wb, kit):
    ws = wb.create_sheet(("Presu " + kit["id"])[:31])
    titulo(ws, "Martín Color · Presupuesto orientativo", kit["nombre"])
    ws["A3"], ws["A4"] = "Cliente:", "Piezas:"
    for c in ("A3", "A4"):
        ws[c].font = Font(bold=True)
    for c in ("B3", "B4"):
        ws[c].fill = EDIT_FILL
    ws.merge_cells("B3:F3")
    ws.merge_cells("B4:F4")
    cabecera(ws, 6, ["Código", "Producto", "Color", "Cantidad", "Precio unidad $\n(Infogestión)", "Subtotal $"],
             [12, 44, 18, 11, 16, 15])
    fila = 7
    for pid, cant in kit["lineas"]:
        p = PROD[pid]
        ws.cell(row=fila, column=1, value=p["codigo"])
        ws.cell(row=fila, column=2, value=p["nombre"] + (" (verificar código)" if p.get("verificar") else ""))
        ws.cell(row=fila, column=4, value=cant)
        ws.cell(row=fila, column=6, value=f"=D{fila}*E{fila}")
        fila += 1
    extra_hasta = fila + 3  # filas libres para agregar productos
    for r in range(fila, extra_hasta + 1):
        ws.cell(row=r, column=6, value=f'=IF(E{r}="","",D{r}*E{r})')
    grilla(ws, 7, extra_hasta, 6, editables=(3, 4, 5))
    for r in range(7, extra_hasta + 1):
        ws.cell(row=r, column=5).number_format = '"$" #,##0'
        ws.cell(row=r, column=6).number_format = '"$" #,##0'
    t = extra_hasta + 1
    ws.cell(row=t, column=5, value="TOTAL").font = Font(bold=True, size=14)
    tot = ws.cell(row=t, column=6, value=f"=SUM(F7:F{extra_hasta})")
    tot.font, tot.number_format = Font(bold=True, size=14, color=ROJO), '"$" #,##0'
    ws.cell(row=t + 2, column=1, value="Precios con IVA. Válido por 7 días. Cantidades para 2 o 3 piezas: si son más, subir litros.") \
        .font = Font(italic=True, color="5F5B6B")
    ws.cell(row=t + 3, column=1, value="Solo completar las celdas AMARILLAS. El subtotal y el total se calculan solos.") \
        .font = Font(bold=True, color=ROJO)
    ws.print_options.horizontalCentered = True
    ws.page_setup.fitToWidth = 1


def hoja_tabla(wb, nombre, tit, sub, cols, anchos, filas=25, validar=None):
    ws = wb.create_sheet(nombre)
    titulo(ws, tit, sub, len(cols))
    cabecera(ws, 4, cols, anchos)
    grilla(ws, 5, 4 + filas, len(cols), editables=range(1, len(cols) + 1))
    if validar:
        col, opciones = validar
        dv = DataValidation(type="list", formula1='"' + ",".join(opciones) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}5:{col}{4 + filas}")
    ws.freeze_panes = "A5"
    return ws


def hoja_lista(wb, nombre, tit, sub, items, cols, anchos, validar=None):
    ws = wb.create_sheet(nombre)
    titulo(ws, tit, sub, len(cols))
    cabecera(ws, 4, cols, anchos)
    for i, it in enumerate(items, start=5):
        ws.cell(row=i, column=1, value=it)
    hasta = 4 + len(items) + 4
    grilla(ws, 5, hasta, len(cols), editables=range(2, len(cols) + 1))
    if validar:
        dv = DataValidation(type="list", formula1='"' + ",".join(validar) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        for c in range(2, len(cols) + 1):
            letra = ws.cell(row=4, column=c).column_letter
            dv.add(f"{letra}5:{letra}{hasta}")
    ws.freeze_panes = "B5"


def excel():
    wb = Workbook()
    wb.remove(wb.active)
    for k in D["kits"]:
        hoja_presupuesto(wb, k)
    hoja_tabla(wb, "Reparto", "Planilla de reparto", "Fecha: ____/____   Salida 11:10",
               ["Hora", "Cliente", "Dirección", "Qué lleva", "Cobrar $", "Cómo pagó", "Entregado"],
               [8, 24, 26, 32, 12, 14, 12], validar=("G", ["Sí", "No"]))
    hoja_tabla(wb, "Mercadería", "Control de mercadería", "Anotar TODO lo que entra y lo que sale",
               ["Fecha", "Entra / Sale", "Producto", "Cantidad", "Proveedor / cliente", "Nota (roto, falta, sobra)"],
               [12, 12, 36, 10, 22, 30], filas=40, validar=("B", ["ENTRA", "SALE"]))
    semana = ["Martes", "Jueves", "Martes", "Jueves"]
    hoja_lista(wb, "Básicos auto", "Control de básicos automotriz", "Martes y jueves. Poner: HAY / POCO / NO HAY",
               D["planillas"]["basicos"], ["Producto"] + [f"{d}\n__/__" for d in semana], [34, 13, 13, 13, 13],
               validar=["HAY", "POCO", "NO HAY"])
    hoja_lista(wb, "Compras local", "Compras de insumos del local", "Viernes. Marcar con X lo que falta",
               D["planillas"]["compras"], ["Insumo", "Falta (X)", "Cantidad", "Comprado (X)"], [30, 12, 12, 14])
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    hoja_lista(wb, "Limpieza", "Limpieza del local", "Semana del ____/____. Poner ✔ cuando está hecho",
               D["planillas"]["limpieza"], ["Tarea"] + dias, [30] + [8] * 6)
    hoja_lista(wb, "Laboratorio", "Laboratorio de Martín", "Lunes, miércoles y viernes. Poner ✔",
               D["planillas"]["laboratorio"], ["Qué revisar", "Lun", "Mié", "Vie"], [30, 10, 10, 10])
    # Rutina
    ws = wb.create_sheet("Mi rutina")
    titulo(ws, "La rutina de Matías", "Lo que toca cada día (también te llega al celular)", 3)
    cabecera(ws, 4, ["Hora", "Días", "Qué hacer"], [9, 22, 80])
    nombres = {1: "Lun", 2: "Mar", 3: "Mié", 4: "Jue", 5: "Vie", 6: "Sáb", 7: "Dom"}
    rs = sorted(D["recordatorios"], key=lambda r: (r["dias"] == [6], r["hora"]))
    for i, r in enumerate(rs, start=5):
        ws.cell(row=i, column=1, value=r["hora"])
        ws.cell(row=i, column=2, value=" ".join(nombres[d] for d in r["dias"]))
        ws.cell(row=i, column=3, value=r["texto"])
        ws.row_dimensions[i].height = 15 * (r["texto"].count("\n") + 1) + 6
    grilla(ws, 5, 4 + len(rs), 3)
    for i in range(5, 5 + len(rs)):
        ws.row_dimensions[i].height = 15 * (ws.cell(row=i, column=3).value.count("\n") + 1) + 6
    wb.move_sheet("Mi rutina", offset=-(len(wb.sheetnames) - 1))
    wb.active = 0
    wb.save(BASE / "Planillas-Matias.xlsx")


def ics():
    byday = {1: "MO", 2: "TU", 3: "WE", 4: "TH", 5: "FR", 6: "SA", 7: "SU"}
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())

    def esc(s):
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def plegar(linea):  # RFC 5545: líneas de máx. 75 octetos
        b = linea.encode("utf-8")
        out, cur = [], b""
        for ch in linea:
            e = ch.encode("utf-8")
            if len(cur) + len(e) > (75 if not out else 74):
                out.append(cur.decode("utf-8"))
                cur = b""
            cur += e
        out.append(cur.decode("utf-8"))
        return "\r\n ".join(out)

    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Martin Color//Asistente de Matias//ES", "CALSCALE:GREGORIAN",
         "X-WR-CALNAME:Matías · Martín Color", "X-WR-TIMEZONE:America/Montevideo",
         "BEGIN:VTIMEZONE", "TZID:America/Montevideo", "BEGIN:STANDARD", "DTSTART:19700101T000000",
         "TZOFFSETFROM:-0300", "TZOFFSETTO:-0300", "TZNAME:-03", "END:STANDARD", "END:VTIMEZONE"]
    for r in D["recordatorios"]:
        primero = min(r["dias"])
        d0 = lunes + timedelta(days=primero - 1)
        hh, mm = r["hora"].split(":")
        L += ["BEGIN:VEVENT", f"UID:matias-{r['id']}@martincolor.github.io",
              f"DTSTAMP:{hoy:%Y%m%d}T000000Z",
              f"DTSTART;TZID=America/Montevideo:{d0:%Y%m%d}T{hh}{mm}00",
              "DURATION:PT15M",
              "RRULE:FREQ=WEEKLY;BYDAY=" + ",".join(byday[d] for d in r["dias"]),
              plegar("SUMMARY:" + esc(r["titulo"])),
              plegar("DESCRIPTION:" + esc(r["texto"])),
              "BEGIN:VALARM", "ACTION:DISPLAY", plegar("DESCRIPTION:" + esc(r["titulo"])), "TRIGGER:PT0M", "END:VALARM",
              "END:VEVENT"]
    L.append("END:VCALENDAR")
    (BASE / "recordatorios-matias.ics").write_text("\r\n".join(L) + "\r\n", encoding="utf-8", newline="")


if __name__ == "__main__":
    excel()
    ics()
    print("Listo: Planillas-Matias.xlsx y recordatorios-matias.ics")
