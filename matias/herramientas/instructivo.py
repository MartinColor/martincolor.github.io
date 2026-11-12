#!/usr/bin/env python3
"""Genera matias/instalar-pc3.html: el instructivo para armar el asistente de Matías en la PC3,
con el texto de cada archivo de matias/pc3/ listo para copiar y pegar en el Bloc de notas.

Uso:  python3 matias/herramientas/instructivo.py [--sin-esqueleto RUTA]
"""
import html
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PC3 = BASE / "pc3"
ARCHIVOS = [
    ("CLAUDE.md", "Las instrucciones principales: quién es Matías, cómo hablarle, horario, Álvaro y Martín."),
    ("equivalencias.md", "Cuánto material lleva cada pieza (fondo, color, barniz, masilla, lijas)."),
    ("presupuesto.md", "Cómo armar el presupuesto con los precios de Infogestión."),
    ("avisos.md", "Avisos en Google Calendar, rutina fija y laboratorio de punta en blanco."),
    ("productos.md", "Qué decirle al cliente de cada producto."),
    ("precios-guardados.md", "Una tabla vacía donde el asistente anota los precios que va buscando."),
]

CSS = """
:root{
  /* Instructivo de una sola columna: pasos numerados de verdad (es un orden a seguir) y, en el paso 2, una tarjeta por archivo con su botón Copiar. */
  --bg:#f3eee6; --hoja:#fffdf9; --tinta:#1f1d1c; --suave:#5b5650; --linea:#ddd3c4;
  --rojo:#c81e00; --negro:#232323; --codigo:#f6f1e9; --ok:#1d6b36;
  --f-tit:"Michroma","Arial Black",sans-serif; --f-txt:"Montserrat",Arial,sans-serif; --f-mono:"JetBrains Mono",Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#181716; --hoja:#22201f; --tinta:#f0e9df; --suave:#b5ada3; --linea:#3d3935; --rojo:#ff6a4d; --codigo:#1b1a19; --ok:#7fd497; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#181716; --hoja:#22201f; --tinta:#f0e9df; --suave:#b5ada3; --linea:#3d3935; --rojo:#ff6a4d; --codigo:#1b1a19; --ok:#7fd497; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--tinta);font:500 17px/1.6 var(--f-txt);margin:0}
.wrap{max-width:820px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:28px}
h1,h2,h3{font-family:var(--f-tit);font-weight:400;line-height:1.25;margin:0;text-wrap:balance}
h1{font-size:clamp(24px,4.5vw,34px)} h1 em{font-style:normal;color:var(--rojo)}
h2{font-size:19px} h3{font-size:15px;font-family:var(--f-mono);font-weight:700;letter-spacing:0}
p,ol,ul{margin:0}
.cab{display:grid;gap:10px;border-bottom:3px solid var(--negro);padding-bottom:20px}
.cab .sub{color:var(--suave);max-width:62ch}
.etq{font:700 12px/1 var(--f-txt);letter-spacing:.14em;text-transform:uppercase;color:var(--rojo)}
.paso{display:grid;grid-template-columns:48px 1fr;gap:16px}
.num{width:48px;height:48px;border-radius:50%;background:var(--negro);color:#fff;display:grid;place-items:center;font:800 20px/1 var(--f-txt)}
.cuerpo{display:grid;gap:12px;min-width:0}
.cuerpo ol,.cuerpo ul{padding-left:22px;display:grid;gap:6px}
kbd,.k{font:600 14px/1 var(--f-mono);background:var(--codigo);border:1px solid var(--linea);border-bottom-width:2px;border-radius:6px;padding:3px 7px;white-space:nowrap}
.ojo{border:2px solid var(--rojo);border-radius:12px;padding:12px 14px;font-size:15px}
.ojo b{color:var(--rojo)}
.archivo{background:var(--hoja);border:1px solid var(--linea);border-radius:12px;overflow:hidden}
.archivo header{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--linea);flex-wrap:wrap}
.archivo header div{min-width:0;display:grid;gap:2px}
.archivo header p{font-size:14px;color:var(--suave)}
.copiar{font:700 15px/1 var(--f-txt);background:var(--rojo);color:#fff;border:0;border-radius:10px;padding:12px 18px;cursor:pointer;min-height:46px}
.copiar.hecho{background:var(--ok)}
.copiar:focus-visible{outline:3px solid var(--tinta);outline-offset:2px}
details summary{cursor:pointer;padding:10px 14px;font-size:14px;color:var(--suave)}
pre{margin:0;padding:14px;background:var(--codigo);font:13px/1.55 var(--f-mono);white-space:pre-wrap;word-break:break-word;max-height:420px;overflow:auto;border-top:1px solid var(--linea)}
.pruebas{display:grid;gap:8px}
.pruebas li{background:var(--hoja);border:1px solid var(--linea);border-radius:10px;padding:10px 12px;list-style:none}
.pruebas li b{display:block;font-size:13px;color:var(--suave);font-weight:600}
.pruebas{padding:0!important}
@media (max-width:480px){.paso{grid-template-columns:1fr}.num{width:40px;height:40px;font-size:17px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
document.querySelectorAll('.copiar').forEach(function(b){
  b.addEventListener('click',function(){
    var pre=document.getElementById(b.dataset.para), t=pre.textContent, txt=b.textContent;
    function listo(){b.textContent='¡Copiado! Ahora pegalo';b.classList.add('hecho');setTimeout(function(){b.textContent=txt;b.classList.remove('hecho')},2500)}
    function seleccionar(){pre.closest('details').open=true;var r=document.createRange();r.selectNodeContents(pre);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Apretá Ctrl + C'}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(listo,seleccionar)}else seleccionar();
  });
});
"""


def cuerpo():
    tarjetas = []
    for i, (nombre, que) in enumerate(ARCHIVOS):
        texto = (PC3 / nombre).read_text(encoding="utf-8")
        tarjetas.append(f"""
      <article class="archivo">
        <header><div><h3>{nombre}</h3><p>{html.escape(que)}</p></div>
          <button class="copiar" type="button" data-para="f{i}">Copiar texto</button></header>
        <details><summary>Ver el texto</summary><pre id="f{i}">{html.escape(texto)}</pre></details>
      </article>""")
    return f"""<title>Asistente de Matías · PC3</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header class="cab">
    <span class="etq">Martín Color · Instructivo</span>
    <h1>Armar el asistente de <em>Matías</em> en la PC3</h1>
    <p class="sub">Se arma igual que los de Francis y Álvaro. Tarda unos 20 minutos. No hace falta bajar nada: los archivos se crean copiando y pegando en el Bloc de notas.</p>
  </header>

  <section class="paso"><div class="num">1</div><div class="cuerpo">
    <h2>Crear la carpeta</h2>
    <ol>
      <li>En el Escritorio de la PC3: clic derecho → <span class="k">Nuevo</span> → <span class="k">Carpeta</span>.</li>
      <li>Nombre: <span class="k">Asistente Matias</span> (sin tilde).</li>
      <li>Adentro de esa carpeta, creá dos carpetas más: <span class="k">presupuestos</span> y <span class="k">fichas</span>.</li>
    </ol>
  </div></section>

  <section class="paso"><div class="num">2</div><div class="cuerpo">
    <h2>Crear los 6 archivos</h2>
    <p>Para <b>cada</b> archivo de abajo:</p>
    <ol>
      <li>Tocá <b>Copiar texto</b>.</li>
      <li>Abrí el <b>Bloc de notas</b> (tecla Windows, escribí «bloc» y Enter) y pegá con <kbd>Ctrl</kbd> + <kbd>V</kbd>.</li>
      <li><span class="k">Archivo</span> → <span class="k">Guardar como</span> → entrá a la carpeta <span class="k">Asistente Matias</span>.</li>
      <li>Abajo, en <b>Tipo</b>, elegí <span class="k">Todos los archivos (*.*)</span> y en <b>Codificación</b> <span class="k">UTF-8</span>.</li>
      <li>En <b>Nombre</b> escribí el nombre <b>exacto</b> (por ejemplo <span class="k">CLAUDE.md</span>) y Guardar.</li>
    </ol>
    <p class="ojo"><b>Ojo:</b> si no elegís «Todos los archivos», Windows le agrega «.txt» al final y queda mal. El nombre tiene que terminar en <b>.md</b>.</p>
    {''.join(tarjetas)}
  </div></section>

  <section class="paso"><div class="num">3</div><div class="cuerpo">
    <h2>Abrir Claude con la carpeta</h2>
    <ol>
      <li>Abrí la app <b>Claude</b> en la PC3 y entrá con la cuenta de Matías.</li>
      <li>Igual que en las PC de Francis y Álvaro, elegí trabajar sobre la carpeta <span class="k">Asistente Matias</span> del Escritorio.</li>
      <li>Si la app tiene un lugar para <b>instrucciones</b> (de la carpeta o del proyecto), pegá ahí también el texto de <span class="k">CLAUDE.md</span>.</li>
      <li>Primer mensaje para el asistente:
        <pre style="border:1px solid var(--linea);border-radius:10px">Leé todos los archivos de esta carpeta, empezando por CLAUDE.md. Esas son tus instrucciones para ayudar a Matías.</pre></li>
    </ol>
  </div></section>

  <section class="paso"><div class="num">4</div><div class="cuerpo">
    <h2>Conectar Google Calendar</h2>
    <ol>
      <li>En Claude: <span class="k">Configuración</span> → <span class="k">Conectores</span> → <span class="k">Google Calendar</span> → Conectar.</li>
      <li>Entrá con la cuenta de Google de <b>Matías</b>.</li>
      <li>En el celular de Matías: app <b>Google Calendar</b> con la misma cuenta y las <b>notificaciones prendidas</b>.</li>
      <li>Escribile al asistente: <span class="k">cargá la rutina</span>. Crea los avisos fijos de toda la semana.</li>
    </ol>
  </div></section>

  <section class="paso"><div class="num">5</div><div class="cuerpo">
    <h2>Infogestión y fichas técnicas</h2>
    <ul>
      <li>Dejá <b>Infogestión abierto</b> en la PC3. Lo mejor es un usuario que <b>solo pueda consultar</b> (sin facturar ni cambiar precios).</li>
      <li>Si el asistente no puede entrar a Infogestión, no pasa nada: le pide a Matías que le dicte los precios.</li>
      <li>Poné los PDF de las fichas técnicas PPG (Deltron, barniz B21.11, fondo P41.04, F351, poliuretano, masilla) en la carpeta <span class="k">fichas</span>.</li>
    </ul>
  </div></section>

  <section class="paso"><div class="num">6</div><div class="cuerpo">
    <h2>Probarlo</h2>
    <p>Escribile estas cosas y fijate que conteste corto, de vos y sin palabras en inglés:</p>
    <ul class="pruebas">
      <li><b>Cantidades</b>bo, cuanto llevo para pintar paragolpe guardabarro y capot en base poliester</li>
      <li><b>Presupuesto</b>haceme un presupuesto de 1 litro de fondo, 1 litro de barniz y 1 kilo de masilla para 3 piezas</li>
      <li><b>Qué hago</b>termine el laboratorio, que hago ahora</li>
      <li><b>Aviso</b>avisame a las 3 que lo llamo a Juan por el gris del Gol</li>
      <li><b>Producto</b>la epoxi F351 sirve para un porton afuera?</li>
    </ul>
    <p>Respuestas que tienen que salir: 1 L de fondo, 800 g de color, 1 L de barniz + ½ L de catalizador · «hablá con Álvaro» · un aviso a las 15:00 · «no, la F351 es para adentro».</p>
  </div></section>

  <section class="paso"><div class="num">7</div><div class="cuerpo">
    <h2>Cambiar algo después</h2>
    <p>Abrí el archivo con el Bloc de notas, cambiá y guardá. Por ejemplo: cantidades en <span class="k">equivalencias.md</span>, códigos en <span class="k">presupuesto.md</span>, horarios y tareas en <span class="k">avisos.md</span>, tono y reglas en <span class="k">CLAUDE.md</span>. Después decile al asistente: «volvé a leer los archivos».</p>
  </div></section>
</div>
<script>{JS}</script>
"""


if __name__ == "__main__":
    c = cuerpo()
    if len(sys.argv) == 3 and sys.argv[1] == "--sin-esqueleto":
        Path(sys.argv[2]).write_text(c, encoding="utf-8")
    pagina = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
              '<meta name="robots" content="noindex,nofollow"></head><body>\n' + c + "\n</body></html>\n")
    (BASE / "instalar-pc3.html").write_text(pagina, encoding="utf-8")
    print("Listo: instalar-pc3.html")
