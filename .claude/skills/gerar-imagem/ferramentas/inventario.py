#!/usr/bin/env python3
"""Gera o inventário em HTML de tudo que a skill criou — a prova visual do trabalho.

    python3 inventario.py img/ -o inventario.html
    python3 inventario.py img/ -o inventario.html --manifest manifesto.json

Sai uma página autocontida com cada peça como um cartão: a imagem (ou o vídeo),
o nome do arquivo, a medida, o peso e o tipo. É a aba de sistema de design das
imagens: quem abrir vê de uma vez tudo que foi produzido.

O manifesto é opcional e enriquece os cartões:

    { "s1-hero.webp": { "papel": "hero · cena principal",
                        "motor": "Higgsfield / Nano Banana Pro",
                        "prompt": "flat background, full body, ..." } }

Guardar o prompt junto da peça não é burocracia: quando ela precisar ser
regerada — e vai precisar — você parte do prompt que funcionou.

Dependências: nenhuma obrigatória. Com Pillow instalado, os cartões mostram a
medida em pixels; sem ele, mostram só o peso. Vídeo mostra medida se o ffprobe
existir na máquina.
"""
import html
import json
import pathlib
import re
import subprocess
import shutil
import sys

IMAGENS = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg'}
VIDEOS = {'.mp4', '.webm', '.mov'}


def medida_imagem(caminho):
    try:
        from PIL import Image
        with Image.open(caminho) as im:
            return f'{im.width} × {im.height}'
    except Exception:
        return None


def medida_video(caminho):
    if not shutil.which('ffprobe'):
        return None
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=width,height,duration',
             '-of', 'csv=p=0', str(caminho)],
            capture_output=True, text=True, timeout=20)
        partes = r.stdout.strip().split(',')
        if len(partes) >= 2:
            m = f'{partes[0]} × {partes[1]}'
            if len(partes) >= 3 and re.match(r'^[\d.]+$', partes[2]):
                m += f' · {float(partes[2]):.1f}s'
            return m
    except Exception:
        pass
    return None


def peso(caminho):
    kb = caminho.stat().st_size / 1024
    return f'{kb / 1024:.1f} MB' if kb >= 1024 else f'{kb:.0f} KB'


def coletar(pasta, manifesto):
    pecas = []
    for arq in sorted(pasta.rglob('*')):
        if not arq.is_file():
            continue
        ext = arq.suffix.lower()
        if ext not in IMAGENS and ext not in VIDEOS:
            continue
        tipo = 'vídeo' if ext in VIDEOS else 'imagem'
        info = manifesto.get(arq.name, {})
        pecas.append({
            'rel': str(arq.relative_to(pasta.parent)),
            'nome': arq.name,
            'tipo': tipo,
            'medida': (medida_video(arq) if tipo == 'vídeo' else medida_imagem(arq)) or '—',
            'peso': peso(arq),
            'papel': info.get('papel', ''),
            'motor': info.get('motor', ''),
            'prompt': info.get('prompt', ''),
        })
    return pecas


def cartao(p):
    # No inventário o vídeo pode ter controls: isto é o manual, não a página de
    # marketing — a lei do movimento governa o site, não a documentação dele.
    if p['tipo'] == 'vídeo':
        midia = (f'<video src="{html.escape(p["rel"])}" controls muted playsinline '
                 f'preload="metadata"></video>')
    else:
        midia = f'<img src="{html.escape(p["rel"])}" alt="" loading="lazy">'
    extras = ''
    if p['papel']:
        extras += f'<span class="papel">{html.escape(p["papel"])}</span>'
    if p['motor']:
        extras += f'<span class="motor">{html.escape(p["motor"])}</span>'
    if p['prompt']:
        extras += (f'<details><summary>prompt</summary>'
                   f'<code>{html.escape(p["prompt"])}</code></details>')
    return f'''<figure class="carta">
  <div class="quadro">{midia}</div>
  <figcaption>
    <b>{html.escape(p['nome'])}</b>
    <span class="spec">{p['tipo']} · {html.escape(p['medida'])} · {p['peso']}</span>
    {extras}
  </figcaption>
</figure>'''


def pagina(pecas, titulo):
    n_img = sum(1 for p in pecas if p['tipo'] == 'imagem')
    n_vid = len(pecas) - n_img
    cartoes = '\n'.join(cartao(p) for p in pecas) or \
        '<p class="vazio">Nenhuma peça encontrada na pasta.</p>'
    resumo = f'{n_img} imagem(ns) · {n_vid} vídeo(s)'
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>
  :root {{
    --papel:#faf8f4; --tinta:#20242c; --sec:#5c6470; --borda:#e3ded4;
    --carta:#ffffff; --marca:#20242c;
  }}
  * {{ box-sizing:border-box; margin:0 }}
  body {{ background:var(--papel); color:var(--tinta);
         font:16px/1.55 system-ui,-apple-system,sans-serif; padding:48px 24px }}
  main {{ max-width:1180px; margin:0 auto }}
  h1 {{ font-size:34px; letter-spacing:-.02em }}
  .resumo {{ color:var(--sec); margin:6px 0 36px }}
  .grade {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:22px }}
  .carta {{ background:var(--carta); border:1px solid var(--borda); border-radius:14px;
            overflow:hidden; display:flex; flex-direction:column }}
  .quadro {{ background:#eeeae2; aspect-ratio:4/3; display:flex;
             align-items:center; justify-content:center; overflow:hidden }}
  .quadro img, .quadro video {{ width:100%; height:100%; object-fit:contain; display:block }}
  figcaption {{ padding:14px 16px; display:flex; flex-direction:column; gap:4px }}
  figcaption b {{ font-size:14px; word-break:break-all }}
  .spec {{ color:var(--sec); font-size:12.5px }}
  .papel {{ font-size:13px }}
  .motor {{ color:var(--sec); font-size:12px }}
  details {{ font-size:12px; margin-top:4px }}
  summary {{ cursor:pointer; color:var(--sec) }}
  details code {{ display:block; margin-top:6px; padding:8px; background:#f3f0e9;
                  border-radius:8px; white-space:pre-wrap; word-break:break-word;
                  font-size:11.5px }}
  .vazio {{ color:var(--sec) }}
  footer {{ margin-top:40px; color:var(--sec); font-size:13px }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(titulo)}</h1>
  <p class="resumo">{resumo}</p>
  <div class="grade">
{cartoes}
  </div>
  <footer>Inventário gerado pela skill gerar-imagem. Cada peça acima está aplicada no site.</footer>
</main>
</body>
</html>
'''


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    pasta = pathlib.Path(args[0])
    if not pasta.is_dir():
        sys.exit(f'{pasta} não é uma pasta.')
    saida = pathlib.Path(args[args.index('-o') + 1]) if '-o' in args \
        else pasta.parent / 'inventario.html'
    manifesto = {}
    if '--manifest' in args:
        manifesto = json.loads(
            pathlib.Path(args[args.index('--manifest') + 1]).read_text(encoding='utf-8'))
    titulo = args[args.index('--titulo') + 1] if '--titulo' in args else 'Inventário de mídia'

    pecas = coletar(pasta, manifesto)
    saida.write_text(pagina(pecas, titulo), encoding='utf-8')
    print(f'{len(pecas)} peça(s) → {saida}')
