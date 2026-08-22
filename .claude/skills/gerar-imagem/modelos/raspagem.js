/* raspagem.js — vídeo raspado pela rolagem, sem autoplay.
 *
 * Acha todo <video data-raspa> e prende o tempo dele à posição na tela:
 * o vídeo está inteiro abaixo da dobra = primeiro quadro; o centro dele
 * cruza a tela = o tempo avança junto; parou a rolagem = congelou.
 * Rolagem é o único relógio — o vídeo nunca dá play de verdade.
 *
 * Como ligar:
 *   <video data-raspa src="v.mp4" poster="v.webp"
 *          muted playsinline preload="auto" disablepictureinpicture></video>
 *   <script src="raspagem.js"></script>
 *
 * Nunca coloque autoplay, loop ou controls — os três brigam com isto.
 *
 * O vídeo precisa ter TODO quadro como quadro-chave (ffmpeg -g 1), senão
 * cada mexida no scroll custa centenas de quadros de decodificação e a
 * raspagem trava. A receita completa está na skill, em referencias/video.md.
 */
(function () {
  'use strict';

  /* respeitar quem pediu menos movimento: tudo desligado, fica o poster */
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var vids = [].slice.call(document.querySelectorAll('video[data-raspa]'));
  if (!vids.length) return;

  vids.forEach(function (v) {
    /* garantias, caso a marcação tenha esquecido: sem muted o iOS recusa
       manipular o tempo, e um play() perdido viraria autoplay por acidente */
    v.muted = true;
    v.pause();
    v.removeAttribute('autoplay');
    v.removeAttribute('loop');
  });

  var agendado = false;

  function passo() {
    agendado = false;
    var altura = innerHeight || document.documentElement.clientHeight;
    vids.forEach(function (v) {
      var d = v.duration;
      if (!d || !isFinite(d)) return;             /* metadados ainda não chegaram */
      var r = v.getBoundingClientRect();
      if (r.bottom < -altura || r.top > altura * 2) return;  /* longe da tela: não mexe */
      /* progresso 0→1 conforme o vídeo atravessa a janela, de entrar por
         baixo até sair por cima — o percurso inteiro vira a linha do tempo */
      var p = (altura - r.top) / (altura + r.height);
      p = Math.max(0, Math.min(1, p));
      /* 0.999 e não 1: currentTime = duration em alguns navegadores dispara
         'ended' e pinta o controle nativo de replay por cima do quadro */
      var t = p * d * 0.999;
      if (Math.abs(v.currentTime - t) > 0.02) {
        try { v.currentTime = t; } catch (e) { /* ainda sem dados suficientes */ }
      }
    });
  }

  function pedir() {
    /* um quadro por rolagem, nunca mais que isso — e nada roda com a página parada */
    if (!agendado) {
      agendado = true;
      requestAnimationFrame(passo);
    }
  }

  addEventListener('scroll', pedir, { passive: true });
  addEventListener('resize', pedir, { passive: true });

  /* posição inicial certa, inclusive quando a página abre já rolada,
     e de novo quando os metadados de cada vídeo chegarem */
  vids.forEach(function (v) {
    v.addEventListener('loadedmetadata', pedir);
  });
  pedir();
})();
