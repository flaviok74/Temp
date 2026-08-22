# O fluxo com a /design

O pipeline completo, do rascunho ao site dinâmico:

1. **`/design`** cria o rascunho do site a partir das suas referências, com molduras tracejadas nos lugares de mídia. Você ajusta no canvas e salva.
2. **O Claude Code transforma em site de verdade** — pede-se em português mesmo: "transforma esse canvas num site, mantendo os espaços de mídia". A ponte desta skill lê tudo que ele precisa.
3. **`/gerar-imagem`** (esta skill) gera as peças nas medidas certas e aplica.
4. **`/super-copy`** melhora o texto.

## O prompt pra /design — cole e adapte

A `/design` só desenha os espaços reservados do jeito certo se você pedir. Este bloco pede tudo que a travessia precisa:

```
Crie o rascunho de uma landing page para [PRODUTO], com base nestas referências:
[URL A] — quero o ritmo das seções e o comprimento da página
[URL B] — quero o par de fontes
[URL C] — quero a cor e o quanto ela aparece

Regras do rascunho:
1. Onde entrar imagem ou vídeo, NÃO desenhe a arte: deixe uma moldura
   tracejada vazia com o tamanho escrito dentro, por exemplo
   "VÍDEO 1200 × 675" ou "IMAGEM 640 × 400".
2. Todo dado que ainda não existe vai entre colchetes: [X]%, R$ [valor],
   [Nome do cliente]. Não invente números, depoimentos nem avaliações.
3. Escreva o texto de venda de verdade (nada de lorem ipsum), sabendo
   que ele será refinado depois.
4. Deixe três notas no canvas: uma com o sistema de design (fontes,
   cores por função, raios, espaçamentos), uma listando cada espaço de
   mídia com a medida e o que a imagem precisa mostrar, e uma listando
   tudo que é provisório.
5. Anote também de qual referência veio cada decisão.
```

## O prompt do passo 2 — cole e adapte

Depois de salvar o canvas, este é o pedido que transforma o artefato em site e já emenda a geração de imagens:

```
Transforme o canvas da /design em um site de verdade e gere as imagens dele.

O canvas salvo está em: [CAMINHO ou link da página do canvas]

PASSO 1 — Ler o desenho.
Use a ponte da skill gerar-imagem (ferramentas/ler_design.py) sobre o arquivo
acima. Ela devolve as faixas na ordem, os espaços de mídia com as medidas, a
paleta, as fontes e as notas do canvas. Siga as notas: elas carregam o sistema
de design e a lista de mídia. Me mostre o briefing antes de construir.

PASSO 2 — Construir a página (index.html).
- Uma página só, responsiva. O artboard mobile diz como as faixas se comportam
  em tela estreita — não é uma segunda página.
- Mesma estrutura do artboard: mesmas faixas, na mesma ordem, com as mesmas
  alturas. Mesma paleta e mesmas fontes, carregadas do Google Fonts.
- Os espaços de mídia ficam VAZIOS, nas medidas que as molduras declaram.
- Todo espaço de vídeo já nasce com a marcação certa (data-raspa, muted,
  playsinline, preload="auto", poster) e com o raspagem.js da skill incluído
  uma vez antes de </body>. Nunca autoplay, loop ou controls.
- Mantenha o texto do artboard como está (a /super-copy refina depois) e
  mantenha os colchetes [X]%, R$ [valor] — não invente números.

PASSO 3 — Gerar e aplicar as imagens, com a skill /gerar-imagem.
- Motor: [Higgsfield via MCP / outro / vou trazer os arquivos].
- Antes de gastar crédito, diga quantas gerações o trabalho pede e espere o
  meu sim.
- Se houver personagem, folha de elenco e de modelo primeiro, e toda cena
  gerada contra elas.
- Cada peça na medida exata da moldura, aplicada seguindo as regras da skill
  (referencias/aplicar.md e video.md).
- Entregue o site + o inventario.html com todas as peças.

No final, abra a página pra eu ver e liste o que ainda está provisório.
```

## A travessia — um comando

Depois de salvar no canvas:

```bash
python3 ferramentas/ler_design.py pagina-do-canvas.html
```

Ele extrai os artboards sozinho e devolve: as faixas na ordem, **cada espaço de mídia com a medida** (que vira a lista de geração desta skill), a paleta, as fontes e as notas.

## Imagem pode nascer antes; movimento só nasce depois

O canvas **aceita imagem parada**: dá pra gerar as imagens cedo e colocar lá dentro, pra julgar o design com arte de verdade em vez de moldura cinza. As mesmas imagens atravessam depois pro site, nada se perde. O canvas quer imagens leves — comprima antes.

O canvas **não aceita vídeo**, e o efeito de rolagem não existe num quadro parado. O dinamismo só nasce no site real, no passo 2 em diante. No canvas, o lugar do vídeo fica como moldura marcada.

## Ao construir o site (passo 2), não esqueça

- Os espaços de mídia da página real ficam **vazios e nas medidas das molduras** — é esta skill que preenche.
- Os espaços de vídeo já nascem com a marcação de `video.md` e o `raspagem.js` no fim da página, esperando o arquivo.
- Se você editou o canvas e não salvou, o arquivo local está velho. Salve antes de atravessar.
