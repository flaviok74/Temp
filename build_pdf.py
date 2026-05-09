"""
Build a print-ready PDF of the Ekoquim Financial Services report.
Uses matplotlib to render the 4 exhibits as static images, then
WeasyPrint to compose a multi-page A4 PDF with the same green/gray
palette and Fraunces/Manrope typography as the web landing page.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from weasyprint import HTML, CSS

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(OUT_DIR, "pdf-assets")
os.makedirs(CHART_DIR, exist_ok=True)

# Ekoquim palette
GREEN_900 = "#0D2818"
GREEN_800 = "#1B4332"
GREEN_700 = "#2D5A3F"
GREEN_600 = "#40916C"
GREEN_500 = "#52B788"
GREEN_400 = "#74C69D"
GREEN_300 = "#95D5B2"
GREEN_200 = "#B7E4C7"
GRAY_900  = "#1A1D1F"
GRAY_700  = "#4A525A"
GRAY_500  = "#6B7280"
GRAY_300  = "#D4D7DB"
PAPER     = "#F1EFE9"

# Common matplotlib style
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": GRAY_300,
    "axes.linewidth": 0.6,
    "axes.labelcolor": GRAY_700,
    "xtick.color": GRAY_700,
    "ytick.color": GRAY_700,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#EAE7DD",
    "grid.linewidth": 0.5,
})


def save(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return os.path.basename(path)


# ---------- Exhibit 1: Cost decomposition (horizontal stacked bars) ----------
def chart_cost():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    fig.patch.set_facecolor("white")
    categories = ["Operação\ntradicional", "Operação\nEkoquim"]

    segments = [
        ("CIF (preço base)",        [62, 62],   GREEN_900),
        ("Tributos federais",        [18, 18],   GREEN_700),
        ("ICMS",                     [12,  8],   GREEN_500),
        ("Custo cambial",            [ 5, 1.5],  GREEN_300),
        ("Logística e armazém",      [ 3, 2.5],  GREEN_200),
    ]

    left = np.zeros(2)
    for label, vals, color in segments:
        ax.barh(categories, vals, left=left, color=color, label=label,
                height=0.55, edgecolor="white", linewidth=1.2)
        left += np.array(vals)

    ax.set_xlim(0, 110)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x)}%"))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32),
              ncol=3, frameon=False, fontsize=9)
    ax.set_axisbelow(True)
    ax.grid(axis="y", visible=False)
    return save(fig, "exhibit1.png")


# ---------- Exhibit 2: USD/BRL volatility (line) ----------
def chart_hedge():
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    no_hedge = [100, 102.4, 105.8, 103.2, 108.5, 112.7,
                109.4, 115.2, 118.9, 114.6, 117.3, 121.5]
    with_hedge = [100] * 12

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    fig.patch.set_facecolor("white")

    ax.fill_between(months, no_hedge, 100, alpha=0.18, color=GREEN_700)
    ax.plot(months, no_hedge, color=GREEN_700, linewidth=2.4,
            marker="o", markersize=4, label="Sem hedge (PTAX real)")
    ax.plot(months, with_hedge, color=GREEN_500, linewidth=2.2,
            linestyle=(0, (5, 4)), label="Com hedge Ekoquim (NDF travado)")

    ax.set_ylim(95, 125)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28),
              ncol=2, frameon=False, fontsize=9)
    return save(fig, "exhibit2.png")


# ---------- Exhibit 3: Capital de giro liberado (grouped bars) ----------
def chart_cash():
    months = [f"M{i}" for i in range(1, 13)]
    a_vista  = [   0,   80,  160,  250,  340,  430,  530,  630,  740,  850,  970, 1100]
    d180     = [ 500,  580,  670,  760,  360,  450,  540,  640,  750,  860,  980, 1100]
    d365     = [ 950, 1040, 1130, 1230, 1320, 1410, 1510, 1610, 1710, 1810, 1900, 1100]

    x = np.arange(len(months))
    w = 0.27

    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    fig.patch.set_facecolor("white")
    ax.bar(x - w, a_vista, w, color=GREEN_900, label="Pagamento à vista")
    ax.bar(x,     d180,    w, color=GREEN_600, label="Financiamento 180 dias")
    ax.bar(x + w, d365,    w, color=GREEN_300, label="Financiamento Ekoquim 365 dias")

    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: f"USD {v/1000:.1f}M" if v >= 1000 else f"USD {int(v)}k"))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28),
              ncol=3, frameon=False, fontsize=9)
    ax.set_axisbelow(True)
    ax.grid(axis="x", visible=False)
    return save(fig, "exhibit3.png")


# ---------- Exhibit 4: Donut composição da economia ----------
def chart_donut():
    labels = ["Benefício tributário SC", "Hedge cambial",
              "Câmbio sem taxas",       "Capital de giro liberado"]
    values = [42, 28, 12, 18]
    colors = [GREEN_600, GREEN_300, GREEN_800, GREEN_200]

    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    fig.patch.set_facecolor("white")
    wedges, _ = ax.pie(values, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.36, edgecolor="white", linewidth=3))
    ax.text(0, 0.05, "100%", ha="center", va="center",
            fontsize=22, fontweight="bold", color=GRAY_900)
    ax.text(0, -0.18, "economia\nrealizada", ha="center", va="center",
            fontsize=8, color=GRAY_700)

    legend_labels = [f"{l}  ·  {v}%" for l, v in zip(labels, values)]
    ax.legend(wedges, legend_labels, loc="lower center",
              bbox_to_anchor=(0.5, -0.18), ncol=1, frameon=False, fontsize=9)
    ax.set_aspect("equal")
    return save(fig, "exhibit4.png")


# ---------- Generate charts ----------
exhibit1 = chart_cost()
exhibit2 = chart_hedge()
exhibit3 = chart_cash()
exhibit4 = chart_donut()
print("Charts generated:", exhibit1, exhibit2, exhibit3, exhibit4)


# ---------- HTML for PDF ----------
HTML_DOC = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Ekoquim Financial Services · Relatório</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..900;1,9..144,400..900&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<!-- COVER -->
<section class="cover">
    <div class="cover-mark">EK</div>
    <div class="cover-meta">
        <span>Relatório · Ekoquim Insights</span>
        <span>Maio 2026 · Volume IV</span>
    </div>
    <h1>Estruturas <em>financeiras</em> sob medida<br>para a indústria química brasileira.</h1>
    <p class="cover-lede">
        Importação por encomenda, hedge cambial, financiamento de até 365 dias
        e fechamento de câmbio sem taxas — desenhados para reduzir custo total,
        proteger margens e liberar capital de giro.
    </p>
    <div class="cover-stats">
        <div><strong>−4%</strong><span>Redução tributária via Santa Catarina</span></div>
        <div><strong>365</strong><span>Dias de financiamento da operação</span></div>
        <div><strong>R$ 0</strong><span>Taxa de fechamento de câmbio</span></div>
        <div><strong>100%</strong><span>Proteção contra volatilidade do dólar</span></div>
    </div>
    <div class="cover-foot">
        <span>Ekoquim Financial Services</span>
        <span>Engenharia financeira para a indústria química</span>
    </div>
</section>

<!-- 01 SUMÁRIO -->
<section class="page">
    <div class="chapter">01 / Sumário Executivo</div>
    <h2>A complexidade da operação cambial está corroendo margem da sua indústria.</h2>

    <div class="two-col">
        <div>
            <p class="lead">
                Empresas químicas brasileiras importadoras enfrentam três pressões
                simultâneas: <strong>volatilidade do real</strong>,
                <strong>custo tributário elevado</strong> e
                <strong>capital de giro travado</strong> em ciclos de até 12 meses.
            </p>
            <p>
                A Ekoquim atua como parceira financeira de ponta a ponta na cadeia
                de importação de insumos químicos, combinando engenharia tributária
                via Santa Catarina, instrumentos derivativos para travar o câmbio e
                linhas de crédito estendidas para diluir o desembolso ao longo
                de até 365 dias.
            </p>
            <p>
                Este relatório consolida os <strong>quatro pilares</strong> da nossa
                oferta financeira e apresenta os ganhos mensuráveis observados
                na carteira atual.
            </p>
        </div>
        <aside class="callout">
            <span class="eyebrow">Pull quote</span>
            <blockquote>
                "Cada ponto percentual reduzido no custo de importação se traduz,
                em média, em <em>3,2 pontos</em> de margem operacional para o
                cliente final."
            </blockquote>
            <cite>— Análise interna Ekoquim, base 2025</cite>
        </aside>
    </div>
</section>

<!-- 02 PILARES -->
<section class="page">
    <div class="chapter">02 / Os quatro pilares</div>
    <h2>Quatro instrumentos. Uma única tese: previsibilidade financeira.</h2>

    <div class="pillars">
        <article>
            <span class="pillar-num">01</span>
            <h3>Importação por encomenda</h3>
            <p class="pillar-claim">Redução de até <strong>4% nos custos tributários</strong> ao importar via regime especial de Santa Catarina.</p>
            <ul>
                <li>Estrutura via TTD 409/410 com benefício de ICMS</li>
                <li>Cliente entra apenas como adquirente final</li>
                <li>Sem necessidade de RADAR ou habilitação aduaneira própria</li>
                <li>Logística porto-fábrica integrada</li>
            </ul>
            <div class="pillar-metric"><strong>−4%</strong><span>custo tributário médio</span></div>
        </article>
        <article>
            <span class="pillar-num">02</span>
            <h3>Hedge cambial</h3>
            <p class="pillar-claim">Fixe a taxa do dólar no momento do pedido e <strong>elimine surpresas</strong> entre embarque e nacionalização.</p>
            <ul>
                <li>NDF (Non-Deliverable Forward) sob medida</li>
                <li>Trava de PTAX ou taxa spot na data do contrato</li>
                <li>Casamento perfeito com vencimento da operação</li>
                <li>Sem chamada de margem para o cliente final</li>
            </ul>
            <div class="pillar-metric"><strong>±0,0%</strong><span>exposição cambial residual</span></div>
        </article>
        <article>
            <span class="pillar-num">03</span>
            <h3>Financiamento de operações</h3>
            <p class="pillar-claim">Prazo de pagamento de <strong>até 365 dias</strong> contados a partir do desembaraço da mercadoria.</p>
            <ul>
                <li>Linha em USD ou BRL conforme estratégia</li>
                <li>Carência alinhada ao ciclo produtivo do cliente</li>
                <li>Análise de crédito interna e ágil</li>
                <li>Liberação de capital de giro imediato</li>
            </ul>
            <div class="pillar-metric"><strong>365d</strong><span>prazo máximo de financiamento</span></div>
        </article>
        <article>
            <span class="pillar-num">04</span>
            <h3>Fechamento de câmbio</h3>
            <p class="pillar-claim">Operação de câmbio <strong>sem taxas</strong> para o cliente Ekoquim, com PTAX competitiva e liquidação D+0.</p>
            <ul>
                <li>Spread reduzido vs. mesa de banco tradicional</li>
                <li>Sem IOF adicional além do legal</li>
                <li>Documentação cambial centralizada pela Ekoquim</li>
                <li>SWIFT enviado no mesmo dia útil</li>
            </ul>
            <div class="pillar-metric"><strong>R$ 0</strong><span>taxa de fechamento</span></div>
        </article>
    </div>
</section>

<!-- QUOTE -->
<section class="page page-dark">
    <div class="quote">
        <span class="quote-mark">"</span>
        <p>Não vendemos produto financeiro. Estruturamos
            <em>arquitetura de capital</em> para a indústria química operar com
            a mesma sofisticação cambial de uma trading global.</p>
        <cite>Time de Estruturação Ekoquim</cite>
    </div>
</section>

<!-- 03 EVIDÊNCIA -->
<section class="page">
    <div class="chapter">03 / Evidência quantitativa</div>
    <h2>Os números por trás da tese Ekoquim.</h2>

    <div class="exhibit">
        <span class="eyebrow">Exhibit 1</span>
        <h4>Decomposição do custo de importação</h4>
        <p class="sub">Operação tradicional vs. Ekoquim · % do CIF</p>
        <img src="pdf-assets/{exhibit1}" alt="Exhibit 1">
        <p class="source">Fonte: simulação Ekoquim sobre carga química padrão · 2025</p>
    </div>

    <div class="exhibit">
        <span class="eyebrow">Exhibit 2</span>
        <h4>Volatilidade do USD/BRL — exposição protegida</h4>
        <p class="sub">Cenário sem hedge vs. operação travada via NDF Ekoquim</p>
        <img src="pdf-assets/{exhibit2}" alt="Exhibit 2">
        <p class="source">Fonte: BCB / PTAX, série diária · base 100 = jan/2025</p>
    </div>
</section>

<section class="page">
    <div class="exhibit">
        <span class="eyebrow">Exhibit 3</span>
        <h4>Capital de giro liberado por extensão de prazo</h4>
        <p class="sub">Comparativo de pagamento à vista, 180 dias e 365 dias Ekoquim</p>
        <img src="pdf-assets/{exhibit3}" alt="Exhibit 3">
        <p class="source">Fonte: modelagem Ekoquim · operação média de USD 1,0 mi</p>
    </div>

    <div class="exhibit">
        <span class="eyebrow">Exhibit 4</span>
        <h4>Composição da economia total</h4>
        <p class="sub">Onde nasce o ganho de margem do cliente</p>
        <img src="pdf-assets/{exhibit4}" alt="Exhibit 4">
        <p class="source">Fonte: análise consolidada Ekoquim · 24 operações</p>
    </div>

    <div class="kpi-banner">
        <div><strong>−4,0%</strong><span>Custo tributário</span></div>
        <div><strong>+18,7%</strong><span>Capital de giro liberado</span></div>
        <div><strong>365</strong><span>Dias de prazo médio</span></div>
        <div><strong>0,0</strong><span>Reais em taxa cambial</span></div>
    </div>
</section>

<!-- 04 METODOLOGIA -->
<section class="page">
    <div class="chapter">04 / Metodologia operacional</div>
    <h2>Como a Ekoquim entrega cada operação, da cotação ao crédito.</h2>

    <ol class="timeline">
        <li><span class="step">01</span><div><h4>Diagnóstico financeiro</h4><p>Mapeamos volume, sazonalidade, exposição cambial e estrutura tributária atual do cliente.</p></div></li>
        <li><span class="step">02</span><div><h4>Estruturação tributária</h4><p>Avaliamos viabilidade da importação por encomenda via Santa Catarina e calculamos o ganho de ICMS.</p></div></li>
        <li><span class="step">03</span><div><h4>Trava cambial</h4><p>Contratamos NDF na data do pedido e fixamos a taxa do dólar até o vencimento da operação.</p></div></li>
        <li><span class="step">04</span><div><h4>Financiamento e desembaraço</h4><p>Liberamos a linha de crédito, executamos o desembaraço e entregamos o material na fábrica.</p></div></li>
        <li><span class="step">05</span><div><h4>Liquidação e relatório</h4><p>Câmbio fechado sem taxa, relatório consolidado com ganho realizado vs. operação tradicional.</p></div></li>
    </ol>
</section>

<!-- 05 CTA -->
<section class="page page-dark">
    <div class="chapter chapter-light">05 / Próximo passo</div>
    <h2 class="h2-light">Quer ver o impacto na <em>sua</em> operação?</h2>
    <p class="cta-lede">
        Em 30 minutos modelamos o ganho potencial sobre a sua próxima importação,
        considerando volume, NCM e estrutura societária.
    </p>
    <div class="cta-box">
        <h5>Como avançar</h5>
        <ol>
            <li>Solicite um diagnóstico Ekoquim pelo site ou e-mail.</li>
            <li>Compartilhe NCMs e volume estimado da próxima importação.</li>
            <li>Receba em até 48h o estudo personalizado de economia.</li>
            <li>Estruturamos a operação completa: tributos, hedge, crédito e câmbio.</li>
        </ol>
        <p class="cta-contact">contato@ekoquim.com.br · ekoquim.com.br</p>
    </div>
    <div class="cta-foot">
        <span>© 2026 Ekoquim Financial Services</span>
        <span>Relatório · Volume IV · Maio 2026</span>
    </div>
</section>

</body>
</html>
"""

CSS_DOC = """
@page {
    size: A4;
    margin: 22mm 18mm 20mm 18mm;
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-family: 'Manrope', sans-serif;
        font-size: 9pt;
        color: #6B7280;
    }
    @bottom-left {
        content: "Ekoquim Financial Services · Volume IV";
        font-family: 'Manrope', sans-serif;
        font-size: 9pt;
        color: #6B7280;
        letter-spacing: 0.04em;
    }
}
@page :first {
    margin: 0;
    @bottom-right { content: ""; }
    @bottom-left  { content: ""; }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    font-family: 'Manrope', sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1A1D1F;
    font-weight: 500;
    -weasy-text-rendering: geometricPrecision;
}

h1, h2, h3, h4, h5 {
    font-family: 'Fraunces', Georgia, serif;
    color: #1A1D1F;
    letter-spacing: -0.01em;
}
em { font-style: italic; color: #2D6A4F; font-weight: 600; }
strong { font-weight: 700; color: #1A1D1F; }

.page { page-break-before: always; padding: 0; }

/* ===== COVER ===== */
.cover {
    position: relative;
    width: 210mm; height: 297mm;
    padding: 30mm 24mm;
    background: linear-gradient(160deg, #0D2818 0%, #1B4332 55%, #2D6A4F 100%);
    color: #fff;
    page-break-after: always;
    overflow: hidden;
}
.cover::before {
    content: "";
    position: absolute;
    top: -60mm; right: -40mm;
    width: 160mm; height: 160mm;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(149, 213, 178, 0.35), transparent 70%);
}
.cover::after {
    content: "";
    position: absolute;
    bottom: -50mm; left: -30mm;
    width: 140mm; height: 140mm;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(64, 145, 108, 0.45), transparent 70%);
}

.cover-mark {
    width: 16mm; height: 16mm;
    border-radius: 3mm;
    background: linear-gradient(135deg, #95D5B2, #B7E4C7);
    color: #0D2818;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 16pt;
    letter-spacing: -0.02em;
    margin-bottom: 18mm;
    position: relative;
    z-index: 2;
}
.cover-meta {
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #B7E4C7;
    margin-bottom: 10mm;
    position: relative; z-index: 2;
}
.cover h1 {
    font-family: 'Fraunces', serif;
    font-size: 36pt;
    font-weight: 600;
    line-height: 1.05;
    color: #fff;
    margin-bottom: 12mm;
    position: relative; z-index: 2;
}
.cover h1 em { color: #95D5B2; }
.cover-lede {
    font-size: 12pt;
    line-height: 1.55;
    color: rgba(255,255,255,0.92);
    margin-bottom: 18mm;
    max-width: 150mm;
    font-weight: 500;
    position: relative; z-index: 2;
}
.cover-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 5mm 8mm;
    margin-bottom: 14mm;
    position: relative; z-index: 2;
}
.cover-stats > div {
    padding: 4mm 5mm;
    border-left: 2pt solid #95D5B2;
    background: rgba(255,255,255,0.06);
    border-radius: 2mm;
}
.cover-stats strong {
    display: block;
    font-family: 'Fraunces', serif;
    font-size: 22pt;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}
.cover-stats span {
    display: block;
    font-size: 8.5pt;
    color: rgba(255,255,255,0.85);
    margin-top: 2mm;
    line-height: 1.35;
}
.cover-foot {
    position: absolute;
    bottom: 18mm;
    left: 24mm; right: 24mm;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: rgba(255,255,255,0.75);
    letter-spacing: 0.05em;
    z-index: 2;
}

/* ===== GENERAL ===== */
.chapter {
    display: inline-block;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #2D6A4F;
    padding-bottom: 3mm;
    border-bottom: 0.4pt solid #D4D7DB;
    padding-right: 30mm;
    margin-bottom: 6mm;
}
.chapter-light { color: #95D5B2; border-color: rgba(255,255,255,0.25); }

h2 {
    font-size: 24pt;
    font-weight: 600;
    line-height: 1.1;
    margin-bottom: 10mm;
    max-width: 165mm;
}
.h2-light { color: #fff; }
.h2-light em { color: #95D5B2; }

p { margin-bottom: 4mm; font-size: 10.5pt; line-height: 1.6; }
p.lead { font-size: 12pt; line-height: 1.55; color: #1A1D1F; margin-bottom: 5mm; font-weight: 500; }

/* ===== TWO COLUMN ===== */
.two-col {
    display: grid;
    grid-template-columns: 1.55fr 1fr;
    gap: 10mm;
    align-items: start;
}
.callout {
    background: #F1EFE9;
    border-left: 2pt solid #2D6A4F;
    padding: 7mm 6mm;
    border-radius: 2mm;
}
.eyebrow {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #2D6A4F;
    margin-bottom: 3mm;
    display: block;
}
.callout blockquote {
    font-family: 'Fraunces', serif;
    font-size: 13pt;
    line-height: 1.4;
    font-weight: 500;
    margin-bottom: 4mm;
}
.callout blockquote em { color: #2D6A4F; font-weight: 600; }
.callout cite {
    font-style: normal;
    font-size: 8.5pt;
    color: #4A525A;
    letter-spacing: 0.04em;
    font-weight: 500;
}

/* ===== PILLARS ===== */
.pillars {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6mm;
}
.pillars article {
    background: #F1EFE9;
    border: 0.4pt solid #E0DDD2;
    border-radius: 3mm;
    padding: 6mm 6mm;
    page-break-inside: avoid;
    border-top: 1.5pt solid #2D6A4F;
}
.pillar-num {
    font-family: 'Fraunces', serif;
    font-size: 9pt;
    font-weight: 700;
    color: #2D6A4F;
    letter-spacing: 0.15em;
    margin-bottom: 2mm;
    display: block;
}
.pillars h3 {
    font-family: 'Fraunces', serif;
    font-size: 14pt;
    font-weight: 600;
    line-height: 1.2;
    margin-bottom: 3mm;
}
.pillar-claim {
    font-size: 10pt;
    line-height: 1.5;
    color: #1A1D1F;
    margin-bottom: 4mm;
    font-weight: 500;
}
.pillars ul {
    list-style: none;
    border-top: 0.4pt solid #D4D7DB;
    padding-top: 3mm;
    margin-bottom: 4mm;
}
.pillars ul li {
    font-size: 9pt;
    color: #3A3F44;
    padding: 1.2mm 0 1.2mm 4mm;
    position: relative;
    line-height: 1.45;
    font-weight: 500;
}
.pillars ul li::before {
    content: "→";
    position: absolute;
    left: 0;
    color: #2D6A4F;
    font-weight: 700;
}
.pillar-metric {
    border-top: 0.4pt solid #D4D7DB;
    padding-top: 3mm;
    display: flex;
    align-items: baseline;
    gap: 3mm;
}
.pillar-metric strong {
    font-family: 'Fraunces', serif;
    font-size: 22pt;
    font-weight: 700;
    color: #2D6A4F;
    line-height: 1;
    letter-spacing: -0.02em;
}
.pillar-metric span {
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4A525A;
    font-weight: 600;
}

/* ===== QUOTE PAGE ===== */
.page-dark {
    background: #0D2818;
    color: #fff;
    width: 210mm; height: 297mm;
    margin: 0;
    padding: 30mm 24mm;
}
.quote {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    max-width: 160mm;
    margin: 0 auto;
}
.quote-mark {
    font-family: 'Fraunces', serif;
    font-size: 80pt;
    color: #95D5B2;
    line-height: 1;
    margin-bottom: -10mm;
    display: block;
}
.quote p {
    font-family: 'Fraunces', serif;
    font-size: 24pt;
    line-height: 1.3;
    font-weight: 500;
    color: #fff;
    margin-bottom: 10mm;
}
.quote em { color: #95D5B2; font-weight: 600; }
.quote cite {
    font-style: normal;
    font-size: 9pt;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.75);
    font-weight: 600;
}

/* ===== EXHIBITS ===== */
.exhibit {
    background: #fff;
    border: 0.4pt solid #E0DDD2;
    border-radius: 3mm;
    padding: 6mm 6mm 5mm;
    margin-bottom: 7mm;
    page-break-inside: avoid;
}
.exhibit h4 {
    font-family: 'Fraunces', serif;
    font-size: 14pt;
    font-weight: 600;
    line-height: 1.25;
    margin: 1mm 0 1mm;
}
.exhibit .sub {
    font-size: 9.5pt;
    color: #4A525A;
    margin-bottom: 4mm;
    font-weight: 500;
}
.exhibit img {
    width: 100%;
    display: block;
    margin: 2mm 0 4mm;
}
.exhibit .source {
    font-size: 8.5pt;
    color: #4A525A;
    font-style: italic;
    border-top: 0.4pt solid #D4D7DB;
    padding-top: 2mm;
    margin: 0;
    font-weight: 500;
}

/* ===== KPI BANNER ===== */
.kpi-banner {
    background: linear-gradient(135deg, #0D2818, #2D5A3F);
    color: #fff;
    border-radius: 3mm;
    padding: 7mm 6mm;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4mm;
    margin-top: 4mm;
    page-break-inside: avoid;
}
.kpi-banner > div {
    text-align: center;
    border-right: 0.4pt solid rgba(255,255,255,0.18);
    padding: 0 2mm;
}
.kpi-banner > div:last-child { border-right: none; }
.kpi-banner strong {
    display: block;
    font-family: 'Fraunces', serif;
    font-size: 22pt;
    font-weight: 700;
    color: #95D5B2;
    line-height: 1;
}
.kpi-banner span {
    display: block;
    font-size: 7.5pt;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.85);
    margin-top: 2mm;
    font-weight: 600;
}

/* ===== TIMELINE ===== */
.timeline {
    list-style: none;
    counter-reset: t;
}
.timeline li {
    display: flex;
    gap: 6mm;
    padding: 5mm 0;
    border-bottom: 0.4pt solid #E0DDD2;
    page-break-inside: avoid;
}
.timeline li:last-child { border-bottom: none; }
.timeline .step {
    flex: 0 0 16mm;
    height: 16mm;
    border-radius: 50%;
    background: #fff;
    border: 0.6pt solid #D4D7DB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Fraunces', serif;
    font-size: 14pt;
    font-weight: 700;
    color: #2D6A4F;
}
.timeline h4 {
    font-family: 'Fraunces', serif;
    font-size: 13pt;
    font-weight: 600;
    margin-bottom: 2mm;
}
.timeline p {
    font-size: 10pt;
    color: #3A3F44;
    margin: 0;
    line-height: 1.55;
    font-weight: 500;
}

/* ===== CTA PAGE ===== */
.cta-lede {
    font-size: 13pt;
    line-height: 1.55;
    color: rgba(255,255,255,0.92);
    margin-bottom: 14mm;
    max-width: 150mm;
    font-weight: 500;
}
.cta-box {
    background: rgba(255,255,255,0.08);
    border: 0.4pt solid rgba(255,255,255,0.18);
    border-radius: 3mm;
    padding: 8mm;
    color: #fff;
}
.cta-box h5 {
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #95D5B2;
    margin-bottom: 5mm;
}
.cta-box ol {
    counter-reset: c;
    list-style: none;
    margin-bottom: 6mm;
}
.cta-box ol li {
    counter-increment: c;
    padding: 3mm 0 3mm 12mm;
    border-bottom: 0.3pt solid rgba(255,255,255,0.14);
    position: relative;
    font-size: 10.5pt;
    line-height: 1.5;
    color: rgba(255,255,255,0.95);
    font-weight: 500;
}
.cta-box ol li::before {
    content: counter(c, decimal-leading-zero);
    position: absolute;
    left: 0;
    top: 3mm;
    font-family: 'Fraunces', serif;
    font-weight: 700;
    color: #95D5B2;
    font-size: 11pt;
}
.cta-box ol li:last-child { border-bottom: none; }
.cta-contact {
    font-family: 'Fraunces', serif;
    font-size: 13pt;
    font-weight: 600;
    color: #95D5B2;
    border-top: 0.4pt solid rgba(255,255,255,0.18);
    padding-top: 5mm;
    margin: 0;
}
.cta-foot {
    position: absolute;
    bottom: 18mm;
    left: 24mm; right: 24mm;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: rgba(255,255,255,0.65);
    letter-spacing: 0.05em;
}
.page-dark { position: relative; }
"""

# ---------- Build PDF ----------
out_path = os.path.join(OUT_DIR, "ekoquim-relatorio.pdf")
HTML(string=HTML_DOC, base_url=OUT_DIR).write_pdf(
    out_path,
    stylesheets=[CSS(string=CSS_DOC)],
)
print(f"PDF written: {out_path}")
print(f"Size: {os.path.getsize(out_path):,} bytes")
