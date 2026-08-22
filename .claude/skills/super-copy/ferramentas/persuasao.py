#!/usr/bin/env python3
"""Scanner de conversão. Lê a página como um visitante apressado lê e aponta onde ela perde.

    python3 persuasao.py index.html
    python3 persuasao.py index.html --vista vista-site
    python3 persuasao.py index.html --material     # só o material pra reescrita
    python3 persuasao.py index.html --briefing     # prompt pronto pra qualquer ferramenta

NÃO é o antigenerico.py. Aquele é SUBTRATIVO: tira tique de escrita de IA. Este é
AVALIATIVO: pergunta se o texto faz a pessoa ficar e clicar. Um texto pode tirar 5/5
de limpeza e não converter nada — são dois problemas diferentes e duas ferramentas.

Três passes:

  1. ESTRUTURA   promessa vaga, CTA genérico, CTAs brigando na mesma faixa
  2. LEITURA     a página lida em 8 segundos, só pelos títulos e botões
  3. MATERIAL    cada linha fraca com o motivo, pronta pra virar variante

O que este script NÃO faz: reescrever. Reescrita persuasiva é julgamento, e regex não
julga. O passe 3 EXTRAI o material — a linha, o seletor CSS que casa com ela, e por que
ela está fraca.

`--briefing` empacota isso num prompt autocontido pra QUALQUER ferramenta. O motor de
texto é plugável do mesmo jeito que o de imagem: a skill não exige fornecedor nenhum.

    python3 persuasao.py index.html --briefing > briefing.md
    codex exec < briefing.md          # ou claude, ou colar em qualquer chat

O script garante a parte errável — os seletores certos e as regras que não podem ser
esquecidas. As palavras são de quem reescreve.

Saída não-zero apenas nos achados CERTOS (CTA genérico, título genérico, CTAs brigando).
Os de julgamento saem como aviso. Persuasão não é binária, e portão instável ensina a
pessoa a ignorar a ferramenta.
"""
import html as htmllib
import re
import sys
from collections import namedtuple

Item = namedtuple("Item", "tipo texto pos seletor casam")

VISTAS = ('vista-site', 'vista-sistema', 'vista-graficos', 'vista-fontes', 'vista-texto')

# ── CTA que não diz o que acontece no próximo clique ─────────────────────────
# "Saiba mais" não é chamada, é adiamento: não promete nada e não custa nada
# clicar, então também não custa nada NÃO clicar.
CTA_GENERICO = {
    'saiba mais': 'diga o que a pessoa recebe: "Ver os 12 modelos"',
    'clique aqui': 'nomeie o destino: "Baixar o guia"',
    'veja mais': 'diga quanto mais: "Ver os outros 8"',
    'confira': 'diga o que tem lá',
    'leia mais': 'diga o que a pessoa vai aprender',
    'entre em contato': 'diga o que acontece depois: "Pedir um orçamento em 24h"',
    'fale conosco': 'diga com quem e pra quê',
    'saber mais': 'diga o que a pessoa recebe',
    'quero saber mais': 'diga o que a pessoa recebe',
    'acesse': 'nomeie o que tem do outro lado',
    'descubra': 'diga o que é, em vez de prometer mistério',
    'conheça': 'diga o que a pessoa vai ver',
    'comece agora': 'diga por onde começa: "Criar meu primeiro projeto"',
    'começar': 'diga o primeiro passo concreto',
    'saiba como': 'diga como, na própria chamada',
    'cadastre-se': 'diga o que o cadastro destrava',
    'inscreva-se': 'diga o que a inscrição destrava',
    'enviar': 'diga o que é enviado e o que volta',
}

# ── Título que resume em vez de afirmar ───────────────────────────────────────
# "Nossos recursos" é uma etiqueta de pasta. Não diz nada que a pessoa não
# soubesse, e ocupa a linha mais lida da faixa.
TITULO_GENERICO = {
    'sobre nós', 'sobre a empresa', 'quem somos', 'nossa história',
    'nossos serviços', 'nossos produtos', 'nossos recursos', 'recursos',
    'funcionalidades', 'nossas soluções', 'soluções', 'o que fazemos',
    'como funciona', 'benefícios', 'vantagens', 'diferenciais',
    'por que nos escolher', 'por que escolher', 'depoimentos',
    'perguntas frequentes', 'nosso time', 'nossa equipe', 'planos',
    'produtos', 'serviços', 'contato', 'introdução', 'conclusão',
}

# ── Promessa vaga: adjetivo de folder, sem nada verificável atrás ────────────
VAGO = [
    'melhor', 'melhores', 'qualidade', 'eficiência', 'eficiente', 'excelência',
    'resultados', 'solução completa', 'praticidade', 'facilidade', 'ideal',
    'perfeito', 'perfeita', 'moderno', 'moderna', 'profissional',
    'tecnologia de ponta', 'alto nível', 'diferencial', 'inovação',
    'personalizado', 'sob medida', 'exclusivo', 'exclusiva', 'premium',
    'otimizado', 'otimizada', 'simplificado', 'descomplicado', 'prático',
]

# Sinal de especificidade: número, unidade de tempo, ou moeda. Uma promessa que
# carrega qualquer um destes deixa de ser folder.
ESPECIFICO = re.compile(
    r'\d|\bR\$|\bum[ao]?\b|\bdois\b|\btrês\b|\bcinco\b|\bdez\b|'
    r'\bminutos?\b|\bhoras?\b|\bdias?\b|\bsemanas?\b|\bmeses\b', re.I)


def _limpar(t):
    t = htmllib.unescape(re.sub(r'<[^>]+>', ' ', t))
    return re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()


def _fatiar_vista(html, vid):
    ini = html.find(f'id="{vid}"')
    if ini < 0:
        return ''
    seguintes = [html.find(f'id="{v}"') for v in VISTAS if html.find(f'id="{v}"') > ini]
    return html[ini:min(seguintes) if seguintes else len(html)]


VAZIAS = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'path'}


def _classe_do_pai(html, pos):
    """A classe do elemento que ainda está aberto em `pos`, olhando pra trás.

    Serve pra escopar um seletor que sozinho é ambíguo: `.btn` casa com todo botão da
    página, `.hero-cta .btn` casa com um. É o que uma pessoa faria à mão.
    """
    for m in reversed(list(re.finditer(r'<(\w+)\b[^>]*class="([^"]+)"[^>]*>', html[:pos]))):
        tag = m.group(1).lower()
        if tag in VAZIAS:
            continue
        # ainda aberto em pos? conta fechamentos contra aberturas no meio
        meio = html[m.end():pos]
        if len(re.findall(rf'</{tag}>', meio, re.I)) <= len(re.findall(rf'<{tag}\b', meio, re.I)):
            return m.group(2).split()[0], tag, m.end()
    return None, None, None


def _fim_do_elemento(html, tag, inicio):
    """Onde o elemento aberto em `inicio` fecha. Balanceia aninhamento do mesmo tag."""
    prof = 1
    for m in re.finditer(rf'<{tag}\b|</{tag}>', html[inicio:], re.I):
        prof += 1 if m.group().startswith(f'</') is False else -1
        if prof == 0:
            return inicio + m.end()
    return len(html)


def _quantos(html, seletor):
    """Quantos elementos um seletor de classe simples casaria. Aproximação de regex."""
    partes = [p for p in seletor.split() if p.startswith('.')]
    if not partes:
        return 2          # seletor posicional: trata como não-verificável
    ultimo = partes[-1].lstrip('.')
    return len(re.findall(rf'class="[^"]*\b{re.escape(ultimo)}\b', html))


def _seletor(tag, classes, html, texto, pos):
    """O seletor CSS que casa com este elemento, e SÓ com ele.

    Isto existe pra tirar a parte errável da mão de quem reescreve. A documentação já
    avisa que seletor errado é o bug inteiro do texto mágico: o motor grita no console e
    a linha não troca. Então o script, que já sabe onde o elemento está, calcula o
    seletor; quem reescreve cuida só das palavras.

    Devolve (seletor, quantos_casam). Quando `quantos` é maior que 1 o seletor é
    ambíguo e o briefing diz isso em voz alta, em vez de entregar um seletor que
    reescreve o botão errado — que foi o que a primeira versão desta função fez com
    quatro CTAs distintos, colapsando os quatro em `.btn`.
    """
    for c in classes:
        if len(re.findall(rf'class="[^"]*\b{re.escape(c)}\b', html)) == 1:
            return f'.{c}', 1

    if classes:
        simples = '.' + classes[0]
        pai, pai_tag, pai_fim = _classe_do_pai(html, pos)
        if pai and pai not in classes:
            escopado = f'.{pai} {simples}'
            # Pai único NÃO implica seletor único: um .hero pode conter dois .btn.
            # Conta o filho DENTRO do intervalo do pai, e multiplica pelo número de
            # pais, que é quantos elementos o seletor casaria de verdade.
            n_pais = len(re.findall(rf'class="[^"]*\b{re.escape(pai)}\b', html))
            dentro = html[pai_fim:_fim_do_elemento(html, pai_tag, pai_fim)]
            n_filhos = len(re.findall(rf'class="[^"]*\b{re.escape(classes[0])}\b', dentro))
            return escopado, max(1, n_pais * n_filhos)
        return simples, _quantos(html, simples)

    irmaos = [m.start() for m in re.finditer(rf'<{tag}\b', html, re.I)]
    return f'{tag}:nth-of-type({max(1, sum(1 for i in irmaos if i < pos))})', 1


def ler_pagina(html):
    """Títulos e chamadas, em ordem de documento. É a página como ela é lida de verdade.

    Quase ninguém lê os parágrafos na primeira passada: a pessoa desce a tela batendo o
    olho nos títulos e nos botões, e decide ali se fica. Então é essa sequência, e não o
    texto completo, que precisa fazer sentido sozinha.
    """
    itens = []
    padrao = re.compile(
        r'<(h1|h2|h3)\b([^>]*)>(.*?)</\1>|'
        r'<(a|button)\b([^>]*class="[^"]*\bbtn\b[^"]*"[^>]*)>(.*?)</(?:a|button)>',
        re.S | re.I)
    for m in padrao.finditer(html):
        if m.group(1):
            tag, attrs, bruto = m.group(1).lower(), m.group(2), m.group(3)
        else:
            tag, attrs, bruto = 'cta', m.group(5), m.group(6)
        texto = _limpar(bruto)
        if not texto:
            continue
        cls = re.search(r'class="([^"]*)"', attrs or '')
        classes = cls.group(1).split() if cls else []
        alvo = 'a' if tag == 'cta' else tag
        sel, n = _seletor(alvo, classes, html, texto, m.start())
        itens.append(Item(tag, texto, m.start(), sel, n))
    return itens


def auditar(html):
    certos, avisos, material = [], [], []
    itens = ler_pagina(html)
    texto_todo = _limpar(re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I))

    # ── 1. CTA genérico ──────────────────────────────────────────────────────
    for it in itens:
        if it.tipo != 'cta':
            continue
        chave = it.texto.lower().strip(' .!→»›')
        if chave in CTA_GENERICO:
            certos.append((f'CTA genérico: "{it.texto}"', CTA_GENERICO[chave]))
            material.append((it, CTA_GENERICO[chave]))

    # ── 2. Título que resume em vez de afirmar ──────────────────────────────
    for it in itens:
        if it.tipo not in ('h1', 'h2', 'h3'):
            continue
        if it.texto.lower().strip(' .:!?') in TITULO_GENERICO:
            certos.append((f'título de etiqueta: "{it.texto}"',
                           'a linha mais lida da faixa está sendo gasta com o nome '
                           'da pasta. Afirme algo: o que essa faixa prova?'))
            material.append((it, 'título genérico: afirme, não rotule'))

    # ── 3. CTAs brigando na mesma tela ──────────────────────────────────────
    # Dois pedidos diferentes na mesma faixa é zero pedido: a pessoa não escolhe,
    # ela sai. Chamadas repetidas (o mesmo texto) não contam — isso é reforço.
    ctas = [(i.texto, i.pos) for i in itens if i.tipo == 'cta']
    for i in range(len(ctas)):
        janela = [c for c in ctas if 0 <= c[1] - ctas[i][1] < 2600]
        distintos = {c[0].lower() for c in janela}
        if len(distintos) > 2:
            certos.append((f'{len(distintos)} pedidos diferentes na mesma faixa: '
                           f'{sorted(distintos)[:3]}',
                           'um pedido por tela. Dois CTAs é zero CTA — '
                           'escolha o principal e rebaixe o resto a link'))
            break

    # ── 4. Promessa vaga sem nada verificável ───────────────────────────────
    for it in itens:
        if it.tipo == 'cta':
            continue
        achados = [v for v in VAGO if re.search(rf'(?<!\w){re.escape(v)}', it.texto, re.I)]
        if achados and not ESPECIFICO.search(it.texto):
            avisos.append((f'promessa vaga em <{it.tipo}>: "{it.texto[:64]}"',
                           f'{achados[0]} não é verificável. Troque por um número, '
                           'um prazo ou a coisa concreta que acontece'))
            material.append((it, f'vago ("{achados[0]}"): traga um número ou o fato'))

    # ── 5. A dobra pede alguma coisa? ───────────────────────────────────────
    if ctas and ctas[0][1] > 4200:
        avisos.append(('nenhum pedido na primeira tela',
                       'a pessoa decide em segundos. Se não há o que clicar antes '
                       'de rolar, ela rola pra fora'))
    elif not ctas:
        certos.append(('a página não pede nada',
                       'nenhum elemento .btn encontrado — não existe próximo passo'))

    # ── 6. Manchete longa demais pra ser manchete ───────────────────────────
    for it in [i for i in itens if i.tipo == 'h1']:
        n = len(it.texto.split())
        if n > 12:
            avisos.append((f'manchete de {n} palavras: "{it.texto[:64]}"',
                           'manchete acima de ~12 palavras vira parágrafo e '
                           'ninguém lê parágrafo em corpo 50px'))
            material.append((it, f'{n} palavras: corte pela metade'))

    return itens, certos, avisos, material


BRIEFING = """\
Você vai reescrever linhas de uma landing page em português do Brasil.

REGRAS, todas obrigatórias:

1. NUNCA invente prova. Nada de contagem de usuários, depoimento, nota ou
   resultado que o produto não tenha. Se o produto não lançou, o texto diz isso.
   O ganho vem de especificidade sobre o que a coisa faz, não de credibilidade
   emprestada.
2. Mantenha o comprimento parecido. Manchete que dobra de tamanho quebra o
   layout: ela foi desenhada pra caber em duas linhas a 50px.
3. Sem tique de escrita de IA. Nada de "não é apenas X, é Y", "descomplicar",
   "jornada", "potencializar", "nos dias de hoje", "de forma simples e prática",
   nem lista de três adjetivos.
4. Toda chamada diz o que acontece no próximo clique. "Saiba mais" não é
   chamada, é adiamento.
5. Todo título afirma alguma coisa. "Nossos recursos" é etiqueta de pasta e
   está ocupando a linha mais lida da faixa.

DEVOLVA APENAS um bloco JavaScript neste formato, sem comentário em volta:

variants: {
  '<seletor>': 'texto novo',
  '<seletor>': { html: 'texto novo com <b>marcação</b>' },
}

Use os seletores EXATAMENTE como estão abaixo. Eles foram calculados a partir da
página e já casam com o elemento certo — seletor trocado é o bug inteiro, porque
a linha simplesmente não troca e nada explode.

LINHAS A REESCREVER:
"""


def briefing(material, itens):
    """Um prompt autocontido, pra qualquer ferramenta.

    O motor de texto é plugável do mesmo jeito que o de imagem: a skill não exige
    fornecedor nenhum. Este bloco sai em texto puro pra ser redirecionado pro CLI que
    a pessoa usar, ou colado em qualquer chat. O que o script garante é a parte
    errável — os seletores certos e as regras que não podem ser esquecidas. As
    palavras são de quem reescreve.
    """
    linhas = [BRIEFING]
    for it, motivo in material:
        linhas.append(f"\nseletor: {it.seletor}")
        if it.casam != 1:
            linhas.append(f"AVISO:   este seletor casa com {it.casam} elementos. "
                          "Dê uma classe própria ao elemento no HTML antes de reescrever, "
                          "ou o texto novo vai parar no primeiro que casar.")
        linhas.append(f"atual:   {it.texto}")
        linhas.append(f"problema: {motivo}")
    linhas.append("\n\nA PÁGINA INTEIRA, como ela é lida (para você manter a coerência "
                  "entre as linhas em vez de reescrever cada uma isolada):\n")
    for it in itens:
        linhas.append(f"  [{it.tipo}] {it.texto}")
    return "\n".join(linhas)


def imprimir(itens, certos, avisos, material, so_material=False):
    if not so_material:
        print('── a página em 8 segundos '
              '(só títulos e chamadas, que é como ela é lida)\n')
        if not itens:
            print('   nada encontrado — a vista tem <h1>/<h2>/<h3> e elementos .btn?\n')
        for it in itens:
            marca = '▸' if it.tipo == 'cta' else ' '
            print(f'   {marca} {it.tipo:4} {it.texto[:78]}')
        print(f'\n   {sum(len(i.texto.split()) for i in itens)} palavras no total. '
              'Se isso sozinho não explica a oferta, a página depende de alguém '
              'ler os parágrafos — e quase ninguém lê.\n')

        if certos:
            print('── problemas certos\n')
            for o_que, porque in certos:
                print(f'   ✗ {o_que}\n     → {porque}\n')
        if avisos:
            print('── julgamento seu\n')
            for o_que, porque in avisos:
                print(f'   ? {o_que}\n     → {porque}\n')
        if not certos and not avisos:
            print('── nada a apontar. A estrutura está de pé.\n')

    if material:
        print('── material pra reescrita\n')
        print('   Cada linha abaixo está fraca pelo motivo indicado. Reescreva e jogue')
        print('   na tabela de variantes do texto mágico. Nunca invente prova.\n')
        for it, motivo in material:
            marca = '' if it.casam == 1 else f'   ⚠ AMBÍGUO: casa com {it.casam} elementos'
            print(f"   {it.seletor}{marca}")
            print(f'      atual:  {it.texto[:72]}')
            print(f'      motivo: {motivo}\n')

    return len(certos)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    html = open(args[0], encoding='utf-8').read()
    html = re.sub(r'<!--.*?-->', ' ', html, flags=re.S)
    if '--vista' in args:
        html = _fatiar_vista(html, args[args.index('--vista') + 1])
    elif 'id="vista-site"' in html:
        # por padrão só o site: as outras três abas são manual, não peça de venda
        html = _fatiar_vista(html, 'vista-site')

    itens, certos, avisos, material = auditar(html)

    if '--briefing' in args:
        if not material:
            print('# Nada a reescrever: o scanner não achou linha fraca.')
            sys.exit(0)
        print(briefing(material, itens))
        sys.exit(0)

    n = imprimir(itens, certos, avisos, material, so_material='--material' in args)
    sys.exit(1 if n else 0)
