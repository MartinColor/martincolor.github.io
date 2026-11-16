/* Brillo HDR para pantallas que lo soportan (iPhone y celulares nuevos).
   Pone un video HDR chiquito de color detrás de botones, carteles y descuentos.
   En pantallas sin HDR no hace nada: la página queda igual. */
(() => {
  const forzar = /[?&]hdr=1/.test(location.search);
  if (!forzar && !(window.matchMedia && matchMedia('(dynamic-range: high)').matches)) return;
  const prueba = document.createElement('video');
  if (!forzar && !prueba.canPlayType('video/mp4; codecs="hvc1"')) return;

  // [selector, color, modo]  modo: fill = todo el fondo brilla · ring = borde de neón · lines = líneas arriba y abajo
  const REGLAS = [
    ['.btn-wa, .pc-wa-btn, .wa-fab', 'verde', 'fill'],
    ['.btn-mp, .pc-mp-btn', 'azul', 'fill'],
    ['.btn-cel', 'celeste', 'fill'],
    ['.cinta-mc, .au-marq', 'rojo', 'fill'],
    ['.pct > div, .memb-card, .mc-card', 'rojo', 'ring'],
    ['.cartel', 'celeste', 'lines'],
    // fichas técnicas y etiquetas que tienen que llamar la atención
    ['.dur, .sello, .techo', 'celeste', 'fill'],
    ['.ft-links a, .desc', 'celeste', 'under'],
    ['.au-cod, .au-n', 'azul', 'fill'],
    ['.ult, .mc-40', 'rojo', 'fill'],
  ];

  const css = document.createElement('style');
  css.textContent = `
.hdr-on{isolation:isolate}
.hdr-on>video.hdr-v{position:absolute;pointer-events:none;object-fit:cover;z-index:-2;opacity:0;transition:opacity .4s}
.hdr-on.hdr-ok>video.hdr-v{opacity:1}
.hdr-fill{overflow:hidden}
.hdr-fill>video.hdr-v{inset:0;width:100%;height:100%;border-radius:inherit}
.hdr-fill.hdr-ok{background:transparent!important}
.hdr-ring>video.hdr-v{inset:0;width:100%;height:100%;border-radius:inherit}
.hdr-ring.hdr-ok{background:transparent!important;border-color:transparent!important}
.hdr-ring.hdr-ok::after{content:"";position:absolute;inset:3px;border-radius:inherit;background:var(--hdr-bg);z-index:-1;pointer-events:none}
.hdr-lines>video.hdr-v{left:0;width:100%;height:3px}
.hdr-lines>video.hdr-v.top{top:0}.hdr-lines>video.hdr-v.bot{bottom:0}
.hdr-lines.hdr-ok{border-color:transparent!important}
.hdr-under>video.hdr-v{left:0;bottom:-3px;width:100%;height:3px}
.hdr-under{overflow:visible}
.hdr-under.hdr-ok{border-bottom-color:transparent!important}`;
  document.head.appendChild(css);

  const vistos = new Set();
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => {
    e.target.querySelectorAll(':scope>video.hdr-v').forEach(v => { if (e.isIntersecting) v.play().catch(() => {}); else v.pause(); });
  }), { rootMargin: '200px' }) : null;

  const claro = c => { const m = c.match(/\d+(\.\d+)?/g); if (!m) return false; const [r, g, b, a = 1] = m.map(Number); return a > 0.5 && r + g + b > 600; };

  function video(color, extra) {
    const v = document.createElement('video');
    v.className = 'hdr-v' + (extra ? ' ' + extra : '');
    v.src = (/hdrtest=1/.test(location.search) ? '/hdr-test-' : '/hdr/') + color + '.mp4';
    v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true;
    v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
    return v;
  }

  function aplicar(el, color, modo) {
    if (vistos.has(el)) return;
    const cs = getComputedStyle(el);
    if (modo === 'fill' && claro(cs.backgroundColor)) return; // botones blancos: no
    vistos.add(el);
    if (cs.position === 'static') el.style.position = 'relative';
    el.classList.add('hdr-on', 'hdr-' + modo);
    if (modo === 'ring') el.style.setProperty('--hdr-bg', cs.backgroundColor);
    const vs = modo === 'lines' ? [video(color, 'top'), video(color, 'bot')] : [video(color)];
    let listo = false;
    vs.forEach(v => {
      v.addEventListener('playing', () => { if (!listo) { listo = true; el.classList.add('hdr-ok'); } }, { once: true });
      el.prepend(v);
      v.play().catch(() => {});
    });
    if (io) io.observe(el);
  }

  function correr() { REGLAS.forEach(([s, c, m]) => document.querySelectorAll(s).forEach(el => aplicar(el, c, m))); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', correr); else correr();
  window.addEventListener('load', correr);
  setTimeout(correr, 2000);
})();
