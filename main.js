/* ─────────────────────────────────────────
   BSC CIP ACID 350 — main.js
   ───────────────────────────────────────── */

(() => {
  'use strict';

  /* ── Navbar scroll state ─────────────── */
  const navbar = document.getElementById('navbar');
  let lastScroll = 0;

  function onScroll() {
    const scrollY = window.scrollY;
    navbar.classList.toggle('scrolled', scrollY > 60);
    lastScroll = scrollY;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── Hamburger menu ──────────────────── */
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });

  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });

  /* ── Parallax backgrounds ────────────── */
  const parallaxMap = [
    { el: document.getElementById('heroBg'),      speed: 0.45 },
    { el: document.getElementById('aplicacaoBg'), speed: 0.25 },
    { el: document.getElementById('ctaBg'),       speed: 0.3  },
  ];

  function updateParallax() {
    const scrollY = window.scrollY;
    parallaxMap.forEach(({ el, speed }) => {
      if (!el) return;
      const rect   = el.parentElement.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const offset = (window.innerHeight / 2 - center) * speed;
      el.style.transform = `translateY(${offset}px)`;
    });
  }
  window.addEventListener('scroll', updateParallax, { passive: true });
  updateParallax();

  /* ── Reveal on scroll ────────────────── */
  const revealEls = document.querySelectorAll('.reveal');

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger cards inside grids
        const siblings = entry.target.parentElement.querySelectorAll('.reveal');
        let delay = 0;
        siblings.forEach((sib, idx) => {
          if (sib === entry.target) delay = idx * 80;
        });
        setTimeout(() => {
          entry.target.classList.add('visible');
          // Animate progress bars when card reveals
          entry.target.querySelectorAll('.bcard-fill').forEach(bar => {
            bar.style.width = bar.style.width; // trigger reflow
          });
        }, delay);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => revealObserver.observe(el));

  /* ── Progress bars animate on reveal ── */
  const barObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.bcard-fill').forEach(fill => {
          const target = fill.style.width;
          fill.style.width = '0';
          requestAnimationFrame(() => {
            fill.style.transition = 'width 1.2s ease .2s';
            fill.style.width = target;
          });
        });
        barObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  document.querySelectorAll('.beneficio-card').forEach(c => barObserver.observe(c));

  /* ── 3-D tilt on product card ────────── */
  const prod3d = document.querySelector('.produto-3d');
  if (prod3d) {
    prod3d.addEventListener('mousemove', (e) => {
      const rect = prod3d.getBoundingClientRect();
      const cx   = rect.left + rect.width  / 2;
      const cy   = rect.top  + rect.height / 2;
      const rx   = ((e.clientY - cy) / (rect.height / 2)) * 10;
      const ry   = ((e.clientX - cx) / (rect.width  / 2)) * -10;
      prod3d.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) scale(1.04)`;
    });
    prod3d.addEventListener('mouseleave', () => {
      prod3d.style.transform = 'perspective(800px) rotateY(-8deg) rotateX(4deg)';
    });
  }

  /* ── Contact form ────────────────────── */
  const form        = document.getElementById('contactForm');
  const formSuccess = document.getElementById('formSuccess');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.textContent = 'Enviando…';
      btn.disabled = true;
      setTimeout(() => {
        formSuccess.classList.add('show');
        form.reset();
        btn.textContent = 'Enviar Solicitação';
        btn.disabled = false;
      }, 1200);
    });
  }

  /* ── Smooth active-section highlight ── */
  const sections = document.querySelectorAll('section[id]');
  const navAs    = document.querySelectorAll('.nav-links a[href^="#"]');

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navAs.forEach(a => {
          a.style.fontWeight = a.getAttribute('href') === `#${id}` ? '700' : '';
        });
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => sectionObserver.observe(s));

})();
