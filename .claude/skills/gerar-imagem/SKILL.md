---
name: gerar-imagem
description: Gera as imagens e os vídeos de um site — inclusive as peças animadas que se movem com a rolagem — e aplica cada uma no lugar certo da página, entregando junto um inventário em HTML com tudo que foi criado. Funciona com qualquer motor de imagem (Higgsfield, outro MCP, uma CLI, ou arquivos que a pessoa gravou). Lê direto um canvas da /design e descobre sozinha o que gerar e em que tamanho. Dispare com "/gerar-imagem", "gera as imagens do site", "cria as imagens e os vídeos", "deixa o site dinâmico", "aplica as imagens na página", "preenche os espaços de imagem", ou quando a pessoa tiver uma página com molduras vazias esperando mídia. NÃO use para editar vídeo de YouTube (isso é edicao-video) nem para construir o site em si.
---

# Gerar Imagem

Uma página com moldura vazia não está pronta. Esta skill preenche: gera as imagens paradas, gera ou prepara os vídeos que se movem com a rolagem, encaixa cada peça no lugar, e entrega um **inventário em HTML** — a prova visual de tudo que foi criado.

---

## Antes de gerar qualquer coisa

Três perguntas, nesta ordem. Não pule nenhuma.

1. **Qual motor?** A pessoa escolhe — Higgsfield, outro serviço, uma CLI, ou ela mesma grava/gera fora e traz os arquivos. Ver `referencias/motores.md` pra exigência técnica e como conectar cada um.
2. **O que gerar, em que tamanho?** Se a página veio da `/design`, a resposta já existe:

```bash
python3 ferramentas/ler_design.py pagina-do-canvas.html
```

Um comando. Ele extrai os artboards e devolve a lista de mídia com as medidas, as faixas, a paleta e as notas do canvas. Se a página não veio da `/design`, monte a lista olhando as molduras da própria página.

3. **Quanto custa?** Diga quantas gerações o trabalho pede e **espere um sim antes de gastar crédito**. Um trabalho típico: uma folha de elenco, uma folha de modelo, e de quatro a nove peças.

---

## A ordem que mantém tudo consistente

**1. Folha de elenco primeiro.** Todo personagem, de frente, neutro, em fundo chapado.
**2. Folha de modelo em segundo.** O mascote em vários ângulos e expressões.
**3. Cada cena depois, sempre com as duas folhas como referência de imagem.**

É só isso que faz um personagem parecer o mesmo personagem em nove imagens diferentes. Um motor que não aceita referência de imagem não consegue este trabalho direito.

Regras de prompt que mudam o resultado: `referencias/prompts.md`. Escreva os prompts em inglês, mesmo com o site em português — os modelos de imagem entendem os termos de composição muito melhor na língua em que foram treinados.

---

## Vídeo: o que deixa o site dinâmico

O vídeo aqui **nunca dá autoplay**. Ele é raspado pela rolagem: a pessoa rola, o vídeo avança. Para, congela. Volta, retrocede. Quem gira a manivela é o visitante.

Tudo sobre isso em `referencias/video.md`: a marcação, a receita de codificação (todo quadro precisa virar quadro-chave, senão a raspagem trava e parece bug), os orçamentos de peso, e o motor de rolagem pronto em `modelos/raspagem.js` — ~50 linhas que você injeta na página.

**Vídeo gravado pela pessoa entra pelo mesmo caminho** que vídeo gerado: passa pela receita de codificação e encaixa no espaço. Gravado ou gerado, a aplicação é igual.

---

## Aplicar — metade do trabalho

Esta skill não termina quando a peça existe: termina quando ela está **na página, do jeito certo**. As regras completas estão em `referencias/aplicar.md` — proporção que a moldura mandou, `width`/`height` pra página não pular, `object-fit` certo pra não decapitar personagem, lazy abaixo da dobra, peso máximo, e a peça entrando no sistema de revelação da página igual às vizinhas.

Pra vídeo: a marcação de `video.md` mais o `raspagem.js` (em `modelos/`) incluído uma vez no fim da página. Nunca `autoplay`, `loop` ou `controls`.

**Nada de esticar**: se a peça saiu 4:3 e o espaço é 16:9, regere na proporção certa. Imagem esticada denuncia o site inteiro.

---

## O inventário — obrigatório na entrega

Depois de aplicar, gere a página de inventário:

```bash
python3 ferramentas/inventario.py img/ -o inventario.html
```

Sai um HTML autocontido com **cada peça criada como um cartão**: a imagem, o nome do arquivo, a medida, o peso, o tipo. Com `--manifest manifesto.json` os cartões também mostram o papel de cada peça, o motor e o prompt usados.

É a aba de sistema de design das imagens: quem abrir vê, de uma vez, tudo que a skill produziu. Entregue sempre o site **e** o inventário.

---

## Portões — confira antes de entregar

- [ ] Nenhum `<video>` com `autoplay`, `loop` ou `controls`.
- [ ] Todo vídeo com `muted`, `playsinline`, `preload="auto"` e `poster`.
- [ ] Todo quadro dos vídeos é quadro-chave (`referencias/video.md` mostra como conferir).
- [ ] Nenhuma peça esticada fora da proporção.
- [ ] Toda peça aplicada aparece no `inventario.html`.
- [ ] Nenhum crédito gasto sem um sim explícito antes.
