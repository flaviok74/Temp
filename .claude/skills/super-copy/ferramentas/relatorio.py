#!/usr/bin/env python3
"""Gera o relatório em HTML do trabalho de copy — cada troca antes → depois, com motivo.

    python3 relatorio.py trocas.json -o relatorio.html

É a prova do serviço: quem abrir vê a nota antes e depois, o que o scanner
percebeu, e cada linha trocada lado a lado com a razão da troca. Sem relatório,
o trabalho de copy é invisível — a página nova parece que sempre foi assim.

Formato de entrada (trocas.json):

    {
      "pagina": "index.html",
      "nota_antes": "2/5",
      "nota_depois": "5/5",
      "percepcoes": ["4 CTAs diferentes brigando na primeira tela"],
      "trocas": [
        { "onde": ".hero-cta .btn",
          "antes": "Clique aqui",
          "depois": "Ver a agenda funcionando",
          "motivo": "CTA genérico: nomeie o destino" }
      ]
    }

Todos os campos além de "trocas" são opcionais. Dependências: nenhuma.
"""
import html
import json
import pathlib
import sys


def linha(t):
    onde = f'<code class="onde">{html.escape(t.get("onde", ""))}</code>' if t.get('onde') else ''
    return f'''<div class="troca">
  <div class="par">
    <div class="antes"><span class="rotulo">antes</span>{html.escape(t.get('antes', ''))}</div>
    <div class="depois"><span class="rotulo">depois</span>{html.escape(t.get('depois', ''))}</div>
  </div>
  <div class="motivo">{html.escape(t.get('motivo', ''))} {onde}</div>
</div>'''


def pagina(d):
    trocas = d.get('trocas', [])
    corpo = '\n'.join(linha(t) for t in trocas) or '<p class="vazio">Nenhuma troca registrada.</p>'
    notas = ''
    if d.get('nota_antes') or d.get('nota_depois'):
        notas = f'''<div class="notas">
  <div class="nota"><span>{html.escape(d.get('nota_antes', '—'))}</span>antes</div>
  <div class="seta">→</div>
  <div class="nota boa"><span>{html.escape(d.get('nota_depois', '—'))}</span>depois</div>
</div>'''
    percepcoes = ''
    if d.get('percepcoes'):
        itens = '\n'.join(f'<li>{html.escape(p)}</li>' for p in d['percepcoes'])
        percepcoes = f'''<section>
  <h2>O que o scanner percebeu</h2>
  <ul class="percepcoes">{itens}</ul>
</section>'''
    origem = f' — {html.escape(d["pagina"])}' if d.get('pagina') else ''

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório de copy</title>
<style>
  :root {{ --papel:#faf8f4; --tinta:#20242c; --sec:#5c6470; --borda:#e3ded4;
           --carta:#fff; --ruim:#b3403c; --bom:#0a7a52; --fundo-ruim:#faf0ef;
           --fundo-bom:#edf7f2 }}
  * {{ box-sizing:border-box; margin:0 }}
  body {{ background:var(--papel); color:var(--tinta);
          font:16px/1.55 system-ui,-apple-system,sans-serif; padding:48px 24px }}
  main {{ max-width:880px; margin:0 auto }}
  h1 {{ font-size:34px; letter-spacing:-.02em }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.08em;
        color:var(--sec); margin:40px 0 16px }}
  .sub {{ color:var(--sec); margin-top:6px }}
  .notas {{ display:flex; align-items:center; gap:18px; margin:28px 0 8px }}
  .nota {{ background:var(--carta); border:1px solid var(--borda); border-radius:14px;
           padding:14px 22px; text-align:center; color:var(--sec); font-size:12px }}
  .nota span {{ display:block; font-size:30px; font-weight:700; color:var(--ruim) }}
  .nota.boa span {{ color:var(--bom) }}
  .seta {{ font-size:22px; color:var(--sec) }}
  .percepcoes {{ padding-left:20px; display:flex; flex-direction:column; gap:6px }}
  .troca {{ background:var(--carta); border:1px solid var(--borda); border-radius:14px;
            padding:18px; margin-bottom:14px }}
  .par {{ display:grid; grid-template-columns:1fr 1fr; gap:12px }}
  @media (max-width:640px) {{ .par {{ grid-template-columns:1fr }} }}
  .antes, .depois {{ border-radius:10px; padding:12px 14px; font-size:15px }}
  .antes {{ background:var(--fundo-ruim); text-decoration:line-through;
            text-decoration-color:rgba(179,64,60,.4); text-decoration-thickness:1px }}
  .depois {{ background:var(--fundo-bom); font-weight:600 }}
  .rotulo {{ display:block; font-size:10.5px; text-transform:uppercase;
             letter-spacing:.08em; color:var(--sec); margin-bottom:5px;
             font-weight:400; text-decoration:none }}
  .motivo {{ margin-top:10px; font-size:13.5px; color:var(--sec) }}
  .onde {{ background:#f3f0e9; border-radius:6px; padding:1px 7px; font-size:12px }}
  .vazio {{ color:var(--sec) }}
  footer {{ margin-top:40px; color:var(--sec); font-size:13px }}
</style>
</head>
<body>
<main>
  <h1>Relatório de copy</h1>
  <p class="sub">{len(trocas)} linha(s) reescrita(s){origem}</p>
  {notas}
  {percepcoes}
  <section>
    <h2>Cada troca, antes → depois</h2>
{corpo}
  </section>
  <footer>Gerado pela skill super-copy. Nenhuma prova foi inventada nestas trocas.</footer>
</main>
</body>
</html>
'''


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    entrada = pathlib.Path(args[0])
    saida = pathlib.Path(args[args.index('-o') + 1]) if '-o' in args \
        else entrada.with_name('relatorio.html')
    d = json.loads(entrada.read_text(encoding='utf-8'))
    saida.write_text(pagina(d), encoding='utf-8')
    print(f'{len(d.get("trocas", []))} troca(s) → {saida}')
