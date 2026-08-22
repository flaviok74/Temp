#!/usr/bin/env python3
"""Caça tiques de escrita de IA no texto visível de uma página. Regex, sem opinião, sai vermelho.

    python3 antigenerico.py index.html
    python3 antigenerico.py index.html --vista vista-site     # pontua uma aba só
    python3 antigenerico.py --texto "algum texto pra conferir"

Lê apenas o que o visitante VÊ: remove <script>, <style> e todas as tags, então pontua
as palavras da página em vez da marcação em volta delas.

A nota vai de 0 a 5. Abaixo de 5 sai com código diferente de zero. Isso é de propósito —
texto "quase limpo" é exatamente como uma página acaba soando igual a todas as outras.

Este catálogo é de PORTUGUÊS BRASILEIRO. Os tiques de um idioma não são a tradução dos
tiques do outro: "delve" não tem equivalente em PT-BR, e "descomplicar" não tem em inglês.
Rodar um catálogo em inglês contra texto em português devolve 5/5 sempre — o que é pior
que não ter linter, porque parece uma aprovação.
"""
import html as htmllib
import re
import sys

# ── o catálogo ───────────────────────────────────────────────────────────────
# Agrupado por que tipo de tique é, porque a correção muda por grupo.

# palavra -> substituição mais simples.
# A regra: troque pela palavra plana, não por um sinônimo da mesma palavra.
#
# Um `*` no fim marca um RADICAL e casa com qualquer terminação. Isso não é
# preguiça de digitação: português flexiona muito mais que inglês, e listar
# "potencializar, potencializa, potencializando, potencialize, potencializou"
# à mão garante que a forma que faltar é justamente a que vai passar. Foi o que
# aconteceu no primeiro teste desta ferramenta — "descomplicar" estava no
# catálogo e "descomplicaram" passou batido.
VOCAB = {
    'alavanc*': 'usar',
    'potencializ*': 'melhorar',
    'impulsion*': 'aumentar',
    'turbin*': 'melhorar',
    'otimiz*': 'melhorar',
    'maximiz*': 'aumentar',
    'destrav*': 'liberar',
    'desbloque*': 'liberar',
    'desvend*': 'mostrar',
    'desmistific*': 'explicar',
    'descomplic*': 'simplificar',
    'empoder*': 'dar controle a',
    'capacit*': 'ensinar',
    'revolucion*': 'mudar',
    'disruptiv*': 'diferente',
    'inovador*': 'novo',
    'transformador*': 'que muda',
    'game changer': 'diferença real',
    'divisor de águas': 'virada',
    'robust*': 'sólido',
    'holístic*': 'completo',
    'sinergia': 'trabalho junto',
    'imersiv*': 'envolvente',
    'assertiv*': 'certeiro',
    'escaláve*': 'que cresce',
    'ponta a ponta': 'do começo ao fim',
    'de ponta': 'atual',
    'curad*': 'seleção',
    'meticulosamente': 'com cuidado',
    'cuidadosamente elaborad*': 'feito com cuidado',
    'ecossistema': 'conjunto',
    'jornada': 'processo',
    'trajetória': 'caminho',
    'universo de': 'área de',
    'panorama': 'quadro',
    'cenário atual': 'hoje',
    'patamar': 'nível',
    'protagonismo': 'destaque',
    'entregar valor': 'ser útil',
    'agregar valor': 'ser útil',
    'mão na massa': 'prático',
    'sem esforço': 'fácil',
    'efetivamente': 'de fato',
    'literalmente': '(corte)',
    'simplesmente': '(corte)',
    'basicamente': '(corte)',
    'incríve*': 'bom',
    'poderos*': 'forte',
    'imperdíve*': '(corte)',
    'expertise': 'experiência',
    'insights': 'conclusões',
    'mindset': 'mentalidade',
    'know-how': 'prática',
}

PHRASES = [
    # construções, não palavras — estes são os tiques mais altos
    (r"\bnão (é|se trata de)\s+(apenas|só|somente)\b[^.!?]{0,70}\b(mas|é|e sim)\b",
     "a construção 'não é apenas X, é Y'"),
    (r"\bmais (do )?que (apenas|só|simplesmente)\b",
     "'mais do que apenas'"),
    (r"\bseja você\b[^.!?]{0,50}\bou\b",
     "a abertura 'seja você X ou Y'"),
    (r"\bé a[íi] que\b[^.!?]{0,40}\bentra",
     "'é aí que entra X'"),
    (r"\bdiga adeus\b|\besqueça (de vez|tudo)\b",
     "'diga adeus a'"),
    (r"\bimagine (um|uma|o|a|só|poder)\b",
     "a abertura 'imagine um…'"),
    (r"\bprepare-se para\b|\bchegou a hora de\b",
     "abertura de aquecimento"),
    (r"\ba verdade é que\b|\bo segredo é\b|\ba chave é\b|\bo ponto é que\b",
     "abertura de pigarro"),
    (r"\bquando se trata de\b|\bno que diz respeito a\b",
     "enchimento 'quando se trata de'"),
    (r"\bno final das contas\b|\bno fim do dia\b",
     "'no final das contas'"),
    (r"\bem resumo\b|\bem suma\b|\bconcluindo\b|\bpor fim, mas não menos importante\b",
     "fechamento de redação escolar"),
    (r"\bvale (a pena )?(ressaltar|destacar|lembrar|mencionar)\b|\bé importante (ressaltar|destacar|lembrar)\b",
     "ressalva de professor"),
    (r"\bnão é à toa que\b",
     "'não é à toa que'"),
    (r"\b(pode|podem) (ajudar|te ajudar|ajudar você|auxiliar)\b|\bajuda você a\b",
     "benefício com pé atrás ('pode ajudar você a…')"),
    (r"\b(pode|poderá|poderia) (vir a|eventualmente|possivelmente)\b|\btalvez possa\b",
     "ressalva empilhada"),
    (r"\bvamos (lá|nessa|juntos|mergulhar)\b|\bbora (lá|nessa)\b|\bsem mais delongas\b",
     "chamada de apresentador"),
    (r"\be (o melhor|sabe o que é melhor)\b|\bspoiler\s*:",
     "gancho de vídeo colado no texto"),
    (r"\bnos dias de hoje\b|\bno mundo (de hoje|atual)\b|\bna era da\b|\bhoje em dia\b",
     "abertura 'nos dias de hoje'"),
    (r"\bcada vez mais\b",
     "'cada vez mais'"),
    (r"\bde forma \w+ e \w+\b|\bde maneira \w+ e \w+\b",
     "'de forma simples e prática'"),
    (r"\bseja bem-?vindo\b",
     "'seja bem-vindo ao'"),
    (r"\btudo (isso )?(em um só lugar|num só lugar)\b",
     "'tudo em um só lugar'"),
]

# prova inventada — a única que coloca um site real em apuros.
# Formato numérico brasileiro: 10.000 e 4,9 — o separador de milhar é ponto
# e o decimal é vírgula. Um regex escrito pro formato inglês não pega nenhum
# dos dois, que é exatamente o erro que deixa passar a linha mais perigosa da página.
PROOF = re.compile(
    r"(\+\s*de\s*|mais\s+de\s+|acima\s+de\s+)?"
    r"(\d[\d.,]{2,}|\d+\s*(mil|milhões|milhão))\s*\+?\s*"
    r"(alunos?|usuários?|clientes?|estudantes?|assinantes?|membros?|seguidores?|"
    r"pessoas|profissionais|empresas|times?|equipes?|negócios|downloads?|"
    r"seguidores?|seguindo|inscritos?)",
    re.I)

# Terminações que marcam qualidade (adjetivo, advérbio, gerúndio) em vez de coisa.
# É o que separa "rápida, intuitiva e poderosa" de "Fontes, ícones e licenças".
QUALIDADE = re.compile(
    r"(mente|ado|ada|ados|adas|ido|ida|idos|idas|ivo|iva|ivos|ivas|"
    r"oso|osa|osos|osas|ável|áveis|ível|íveis|ante|antes|ente|entes|"
    r"ando|endo|indo)$")

RATING = re.compile(
    r"\b([0-5][,.]\d)\s*(de\s*5|/\s*5|estrelas?|★)|"
    r"\bnota\s+([0-5][,.]\d)\b",
    re.I)


def texto_visivel(html):
    """O que o visitante realmente lê. Script/style fora, tags removidas."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    # unescape do stdlib resolve toda entidade nomeada e numérica de uma vez,
    # inclusive as acentuadas (&ccedil;, &atilde;, &#231;) que uma lista manual
    # de replace sempre acaba esquecendo em português.
    t = htmllib.unescape(t).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def texto_markdown(md):
    """O que um leitor lê num .md — sem frontmatter, sem código, sem marcadores.

    Existe porque o rascunho vem antes da página: você quer linter no texto enquanto
    ele ainda é Markdown, não só depois de virar HTML. Sem estes três cortes a
    ferramenta acusa o que não devia — travessões dentro do `description:` do
    frontmatter, `font-style: italic;` contado como ponto e vírgula de texto, e
    cada item de lista fundido no vizinho porque item de lista não tem ponto final.
    """
    md = re.sub(r'\A---\n.*?\n---\n', '', md, flags=re.S)   # frontmatter YAML
    md = re.sub(r'```.*?```', ' ', md, flags=re.S)          # blocos de código
    md = re.sub(r'`[^`\n]+`', ' ', md)                      # código em linha
    # Item de lista e célula de tabela viram frases próprias: sem isso a janela de
    # 220 caracteres junta cinco itens e acusa cadência que ninguém escreveu.
    md = re.sub(r'^\s*([-*+]|\d+\.)\s+', '', md, flags=re.M)
    md = re.sub(r'^\s*\|.*$', '', md, flags=re.M)           # tabelas
    md = re.sub(r'^\s*#{1,6}\s+', '', md, flags=re.M)       # títulos
    md = re.sub(r'\n', '.\n', md)
    return re.sub(r'\s+', ' ', md).strip()


def auditar(texto):
    hits = {'vocab': [], 'frases': [], 'pontuacao': [], 'ritmo': [], 'prova': []}
    baixo = texto.lower()

    # Entradas mais específicas primeiro, e cada trecho do texto só pode ser
    # reclamado uma vez. Sem isso "curadoria" é contada duas vezes — uma por
    # `curadoria`, outra por `curad*` — e o mesmo vale pra "de ponta a ponta",
    # que casa com `de ponta` e com `ponta a ponta`. Contagem inflada faz a
    # pessoa parar de confiar no número, que é o único valor que ele tem.
    reclamados = set()
    for palavra, troca in sorted(VOCAB.items(), key=lambda kv: -len(kv[0])):
        if palavra.endswith('*'):
            padrao = rf"(?<!\w){re.escape(palavra[:-1])}\w*(?!\w)"
        else:
            padrao = rf"(?<!\w){re.escape(palavra)}(?!\w)"
        achados = []
        for m in re.finditer(padrao, baixo):
            faixa = range(m.start(), m.end())
            if any(i in reclamados for i in faixa):
                continue
            reclamados.update(faixa)
            achados.append(m.group(0))
        if achados:
            # mostra a forma que apareceu de verdade na página, não o radical —
            # "descomplicaram" é procurável no arquivo, "descomplic*" não é.
            formas = ', '.join(sorted(set(achados))[:3])
            hits['vocab'].append((formas, len(achados), troca))

    for pat, rotulo in PHRASES:
        achados = re.findall(pat, baixo)
        if achados:
            hits['frases'].append((rotulo, len(achados)))

    # Densidade de travessão: dois ou mais na mesma frase lê como cadência de máquina.
    # Limitado a uma janela de 220 caracteres de propósito — textos de interface (itens
    # de menu, opções de quiz, rótulos) não têm pontuação final, então uma divisão
    # ingênua por frase funde a página inteira numa "frase" só e a regra dispara em
    # toda página. Um linter que grita à toa é um linter que a pessoa desliga.
    for s in re.split(r'(?<=[.!?])\s+', texto):
        for i in range(0, max(1, len(s)), 220):
            janela = s[i:i + 220]
            if janela.count('—') >= 2:
                hits['pontuacao'].append(('dois ou mais travessões na mesma frase',
                                          janela[:70].strip()))
                break
    if texto.count(';') > max(1, len(texto) // 2500):
        hits['pontuacao'].append(('ponto e vírgula demais pra texto de site',
                                  f"{texto.count(';')} encontrados"))
    reticencias = len(re.findall(r'\.\.\.|…', texto))
    if reticencias > max(1, len(texto) // 3000):
        hits['pontuacao'].append(('reticências como suspense', f'{reticencias} encontradas'))
    if texto.count('!') > max(2, len(texto) // 1200):
        hits['pontuacao'].append(('exclamações demais', f"{texto.count('!')} encontradas"))

    # tricolon: "rápido, simples e eficiente" — o reflexo da regra de três.
    # Em português não existe vírgula de Oxford, então o padrão é "A, B e C".
    #
    # Mas "A, B e C" também é como se enumera qualquer coisa: "Fontes, ícones e
    # licenças" é um título, não retórica. Sinalizar toda enumeração é o caminho
    # mais rápido pra pessoa desligar a ferramenta — e o tricolon retórico tem uma
    # marca que a enumeração não tem: ele empilha QUALIDADES, não coisas. Então
    # exigimos que pelo menos dois dos três carreguem terminação de adjetivo,
    # advérbio ou gerúndio, ou que a lista venha logo depois de verbo de ligação.
    for m in re.finditer(r'\b(\w{4,}),\s+(\w{4,})\s+e\s+(\w{4,})\b', texto):
        partes = [p.lower() for p in m.groups()]
        qualidades = sum(bool(re.search(QUALIDADE, p)) for p in partes)
        antes = texto[max(0, m.start() - 24):m.start()].lower()
        ligacao = re.search(r'\b(é|são|fica|ficam|era|eram|mais|muito)\s*$', antes)
        if qualidades >= 2 or ligacao:
            hits['ritmo'].append(('regra de três retórica', m.group(0)[:60]))
    for m in re.finditer(r'\bmais\s+\w+,\s+mais\s+\w+\s+e\s+mais\s+\w+', texto, re.I):
        hits['ritmo'].append(('paralelismo "mais X, mais Y e mais Z"', m.group(0)[:60]))

    for m in PROOF.finditer(texto):
        hits['prova'].append(m.group(0).strip())
    for m in RATING.finditer(texto):
        hits['prova'].append(f'nota/avaliação: {m.group(0).strip()}')

    return hits


def relatorio(hits, rotulo=''):
    reprovados = [k for k, v in hits.items() if v]
    nota = max(0, 5 - len(reprovados))

    titulos = {
        'vocab': 'vocabulário de IA',
        'frases': 'construções de IA',
        'pontuacao': 'cadência de pontuação',
        'ritmo': 'ritmo de regra de três',
        'prova': 'possível prova inventada',
    }

    if rotulo:
        print(f'── {rotulo}')
    for k in ('prova', 'frases', 'vocab', 'pontuacao', 'ritmo'):
        if not hits[k]:
            continue
        print(f'  {titulos[k]}:')
        for item in hits[k][:8]:
            if k == 'vocab':
                palavra, n, troca = item
                print(f'    · {palavra}  ({n}×)  →  {troca}')
            elif isinstance(item, tuple):
                print(f'    · {item[0]}  ({item[1]})')
            else:
                print(f'    · {item}')
        if len(hits[k]) > 8:
            print(f'    · …e mais {len(hits[k]) - 8}')

    print(f'\n  nota {nota}/5', end='  ')
    print('LIMPO' if nota == 5 else 'precisa de uma limpeza')
    return nota


VISTAS = ('vista-site', 'vista-sistema', 'vista-graficos', 'vista-fontes', 'vista-texto')

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    if args[0] == '--texto':
        texto = ' '.join(args[1:])
    else:
        html = open(args[0], encoding='utf-8').read()
        if args[0].lower().endswith(('.md', '.markdown')):
            texto = texto_markdown(html)
            print(f'{len(texto.split())} palavras de texto visível\n')
            sys.exit(0 if relatorio(auditar(texto)) == 5 else 1)
        if '--vista' in args:
            vid = args[args.index('--vista') + 1]
            inicio = html.find(f'id="{vid}"')
            if inicio < 0:
                sys.exit(f'não existe a vista {vid}')
            seguintes = [html.find(f'id="{v}"') for v in VISTAS]
            seguintes = [n for n in seguintes if n > inicio]
            html = html[inicio:min(seguintes) if seguintes else len(html)]
        texto = texto_visivel(html)

    print(f'{len(texto.split())} palavras de texto visível\n')
    sys.exit(0 if relatorio(auditar(texto)) == 5 else 1)
