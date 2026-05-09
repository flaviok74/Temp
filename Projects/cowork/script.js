/* ============================================
   EKOQUIM Financial Services
   Interactions · Parallax · Charts · Counters
   ============================================ */

(function () {
    'use strict';

    const PALETTE = {
        navy:    '#0D2818',   /* deep forest */
        navy2:   '#1B4332',   /* forest */
        blue:    '#2D6A4F',   /* primary green */
        blueSoft:'#40916C',   /* mid green */
        gold:    '#52B788',   /* vibrant accent green */
        goldSoft:'#95D5B2',   /* sage highlight */
        ink:     '#1A1D1F',   /* near-black */
        gray:    '#4A525A',   /* mid gray */
        graySoft:'#B7BCC2',   /* light gray */
    };

    // ========= NAV ON SCROLL =========
    const nav = document.querySelector('.nav');
    const onScroll = () => {
        nav.classList.toggle('scrolled', window.scrollY > 40);
        applyParallax();
    };
    window.addEventListener('scroll', onScroll, { passive: true });

    // ========= PARALLAX =========
    const parallaxEls = document.querySelectorAll('[data-parallax]');
    function applyParallax() {
        const y = window.scrollY;
        parallaxEls.forEach(el => {
            const speed = parseFloat(el.dataset.parallax) || 0.2;
            const rect = el.getBoundingClientRect();
            const offsetTop = rect.top + y;
            const relative = y - offsetTop;
            const translate = relative * speed;
            el.style.transform = `translate3d(0, ${translate}px, 0)`;
        });
    }
    applyParallax();

    // ========= REVEAL ON SCROLL =========
    const revealTargets = document.querySelectorAll(
        '.section, .pillar, .chart-card, .timeline-item, .summary-callout, .kpi-banner, .cta-card'
    );
    revealTargets.forEach(el => el.classList.add('reveal'));

    const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in');
                io.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    revealTargets.forEach(el => io.observe(el));

    // ========= COUNTERS =========
    const counters = document.querySelectorAll('.stat-num[data-count]');
    const countObs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
            const target = parseInt(el.dataset.count, 10);
            const duration = 1400;
            const start = performance.now();
            const ease = t => 1 - Math.pow(1 - t, 3);
            function tick(now) {
                const p = Math.min((now - start) / duration, 1);
                el.textContent = Math.round(ease(p) * target);
                if (p < 1) requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
            countObs.unobserve(el);
        });
    }, { threshold: 0.6 });
    counters.forEach(c => countObs.observe(c));

    // ========= CHART.JS GLOBALS =========
    if (typeof Chart === 'undefined') return;

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.font.weight = '600';
    Chart.defaults.color = '#1F3243';
    Chart.defaults.borderColor = 'rgba(11, 27, 43, 0.1)';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.padding = 18;
    Chart.defaults.plugins.legend.labels.font = { size: 13, weight: '600' };
    Chart.defaults.plugins.tooltip.backgroundColor = PALETTE.navy;
    Chart.defaults.plugins.tooltip.titleFont = { weight: '700', size: 13 };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 13, weight: '500' };
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.boxPadding = 6;

    // ========= EXHIBIT 1 — Cost decomposition (stacked bar) =========
    const ctxCost = document.getElementById('chartCost');
    if (ctxCost) {
        new Chart(ctxCost, {
            type: 'bar',
            data: {
                labels: ['Operação tradicional', 'Operação Ekoquim'],
                datasets: [
                    {
                        label: 'CIF (preço base)',
                        data: [62, 62],
                        backgroundColor: PALETTE.navy,
                        borderRadius: 4,
                        stack: 's'
                    },
                    {
                        label: 'Tributos federais',
                        data: [18, 18],
                        backgroundColor: PALETTE.navy2,
                        borderRadius: 4,
                        stack: 's'
                    },
                    {
                        label: 'ICMS',
                        data: [12, 8],
                        backgroundColor: PALETTE.blue,
                        borderRadius: 4,
                        stack: 's'
                    },
                    {
                        label: 'Custo cambial',
                        data: [5, 1.5],
                        backgroundColor: PALETTE.gold,
                        borderRadius: 4,
                        stack: 's'
                    },
                    {
                        label: 'Logística e armazém',
                        data: [3, 2.5],
                        backgroundColor: PALETTE.goldSoft,
                        borderRadius: 4,
                        stack: 's'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: {
                        stacked: true,
                        max: 110,
                        ticks: { callback: v => v + '%' },
                        grid: { color: 'rgba(11,27,43,0.05)' }
                    },
                    y: { stacked: true, grid: { display: false } }
                },
                plugins: {
                    legend: { position: 'bottom', align: 'start' }
                }
            }
        });
    }

    // ========= EXHIBIT 2 — USD/BRL volatility (line) =========
    const ctxHedge = document.getElementById('chartHedge');
    if (ctxHedge) {
        const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        const semHedge = [100, 102.4, 105.8, 103.2, 108.5, 112.7, 109.4, 115.2, 118.9, 114.6, 117.3, 121.5];
        const comHedge = labels.map(() => 100);

        const grad = ctxHedge.getContext('2d').createLinearGradient(0, 0, 0, 320);
        grad.addColorStop(0, 'rgba(34, 81, 255, 0.25)');
        grad.addColorStop(1, 'rgba(34, 81, 255, 0)');

        new Chart(ctxHedge, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Sem hedge (PTAX real)',
                        data: semHedge,
                        borderColor: PALETTE.blue,
                        backgroundColor: grad,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        borderWidth: 2.5,
                    },
                    {
                        label: 'Com hedge Ekoquim (NDF travado)',
                        data: comHedge,
                        borderColor: PALETTE.gold,
                        borderDash: [6, 6],
                        backgroundColor: 'transparent',
                        tension: 0,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        borderWidth: 2.5,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: {
                        beginAtZero: false,
                        suggestedMin: 95, suggestedMax: 125,
                        ticks: { callback: v => v.toFixed(0) },
                        grid: { color: 'rgba(11,27,43,0.05)' }
                    },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { position: 'bottom', align: 'start' } }
            }
        });
    }

    // ========= EXHIBIT 3 — Cash flow comparison (grouped bars) =========
    const ctxCash = document.getElementById('chartCash');
    if (ctxCash) {
        const labels = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6', 'Mês 7', 'Mês 8', 'Mês 9', 'Mês 10', 'Mês 11', 'Mês 12'];
        // Capital de giro disponível (USD mil) ao longo dos meses
        const aVista   = [0, 80, 160, 250, 340, 430, 530, 630, 740, 850, 970, 1100];
        const dias180  = [500, 580, 670, 760, 360, 450, 540, 640, 750, 860, 980, 1100];
        const dias365  = [950, 1040, 1130, 1230, 1320, 1410, 1510, 1610, 1710, 1810, 1900, 1100];

        new Chart(ctxCash, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Pagamento à vista',
                        data: aVista,
                        backgroundColor: 'rgba(11, 27, 43, 0.55)',
                        borderRadius: 3,
                        borderSkipped: false,
                    },
                    {
                        label: 'Financiamento 180 dias',
                        data: dias180,
                        backgroundColor: PALETTE.blue,
                        borderRadius: 3,
                        borderSkipped: false,
                    },
                    {
                        label: 'Financiamento Ekoquim 365 dias',
                        data: dias365,
                        backgroundColor: PALETTE.gold,
                        borderRadius: 3,
                        borderSkipped: false,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        ticks: { callback: v => 'USD ' + (v >= 1000 ? (v/1000).toFixed(1) + 'M' : v + 'k') },
                        grid: { color: 'rgba(11,27,43,0.05)' }
                    },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { position: 'bottom', align: 'start' } }
            }
        });
    }

    // ========= EXHIBIT 4 — Donut: composição da economia =========
    const ctxDonut = document.getElementById('chartDonut');
    if (ctxDonut) {
        new Chart(ctxDonut, {
            type: 'doughnut',
            data: {
                labels: [
                    'Benefício tributário SC',
                    'Hedge cambial',
                    'Câmbio sem taxas',
                    'Capital de giro liberado',
                ],
                datasets: [{
                    data: [42, 28, 12, 18],
                    backgroundColor: [
                        PALETTE.blue,
                        PALETTE.gold,
                        PALETTE.navy2,
                        PALETTE.goldSoft,
                    ],
                    borderColor: '#fff',
                    borderWidth: 3,
                    hoverOffset: 12,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: {
                    legend: { position: 'bottom', align: 'center' },
                    tooltip: {
                        callbacks: { label: (c) => ` ${c.label}: ${c.parsed}%` }
                    }
                }
            }
        });
    }

    // ========= SMOOTH ANCHORS WITH OFFSET =========
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const id = a.getAttribute('href');
            if (id.length > 1) {
                const target = document.querySelector(id);
                if (target) {
                    e.preventDefault();
                    const offset = 70;
                    const top = target.getBoundingClientRect().top + window.scrollY - offset;
                    window.scrollTo({ top, behavior: 'smooth' });
                }
            }
        });
    });

})();
