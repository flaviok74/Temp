# Aplicar — a peça no lugar certo, do jeito certo

Gerar é metade do trabalho. A outra metade é a peça entrar na página sem denunciar que foi colada depois. Esta página cobre as duas famílias: a imagem parada e o vídeo raspado.

---

## Imagem parada

### A moldura manda

A moldura declarou uma medida (`IMAGEM 640 × 400`). A peça entra **nessa medida e nessa proporção**. Se a peça saiu noutra proporção, regere — não estique nem corte no olho. Imagem esticada denuncia o site inteiro; corte automático decapita personagem.

### A marcação

```html
<img src="img/s2-modulo.webp" alt="descrição real do que a imagem mostra"
     width="640" height="400" loading="lazy">
```

- **`width` e `height` sempre**, com os números reais. É o que impede a página de pular enquanto carrega. Sem eles, o texto dança quando a imagem chega, e isso lê como site quebrado.
- **`loading="lazy"` em tudo que está abaixo da dobra.** Na primeira imagem do hero, não. Ela precisa chegar junto com a página.
- **`alt` de verdade**, dizendo o que a imagem mostra. Vazio só quando a imagem é decorativa pura.

### Encaixe dentro do espaço

Quando o contêiner tem tamanho próprio e a imagem precisa se adaptar:

```css
.espaco img { width: 100%; height: 100%; object-fit: cover; }
```

- `cover` preenche o espaço cortando as bordas — bom pra foto e cena cheia. **Cuidado com personagem**: `cover` corta cabeça e pés. Nesse caso use `contain`, ou regere na proporção do espaço.
- `contain` mostra a peça inteira, sobrando respiro — é o certo pra logo, ícone e qualquer coisa que não pode ser cortada.

### Posição na faixa

- **A imagem senta do lado que a moldura sentava.** O rascunho decidiu arte à esquerda ou à direita por um motivo de leitura — não inverta na aplicação.
- **Alinhamento vertical pelo centro da coluna de texto** (`align-items: center` no contêiner da faixa), não pelo topo. Imagem colada no topo com texto centrado lê como erro.
- **Respiro**: a imagem não encosta na borda do contêiner nem no texto. Se a moldura tinha margem em volta, a peça também tem.

### Formato e peso

- **WebP** pra tudo que não precisa de transparência perfeita em SVG. Qualidade 80–85 é invisível a olho e pesa um terço do PNG.
- Teto de bom senso: **200 KB por imagem de conteúdo**, 400 KB pra uma cena de hero. Acima disso, redimensione. A imagem não precisa ser maior que o dobro do espaço em que vai (tela retina = 2×).
- Logos e ícones: SVG quando existir, senão PNG pequeno.

### O toque que separa aplicado de colado

Se a página tem sistema de revelação (elementos que chegam ao rolar), a imagem nova entra nele **igual às vizinhas** — mesma classe, mesmo atraso. Uma imagem que aparece seca no meio de uma página onde tudo desliza denuncia o enxerto. Se a página não tem sistema nenhum, não invente um só pra imagem: consistência ganha de efeito.

---

## Vídeo raspado

O passo a passo completo está em `video.md`. O resumo de aplicação:

1. Codifique com todo quadro como quadro-chave (`ffmpeg -g 1` — a receita está lá). Vale pra vídeo gerado e pra vídeo que a pessoa gravou.
2. Gere o poster: `ffmpeg -i v1.mp4 -frames:v 1 img/v1-hero.webp`.
3. Marcação: `<video data-raspa src="…" poster="…" muted playsinline preload="auto" disablepictureinpicture>`.
4. `raspagem.js` (de `modelos/`) copiado pro projeto e incluído uma vez antes de `</body>`.
5. Nunca `autoplay`, `loop` ou `controls`.

Teste rolando devagar e rolando rápido. Devagar mostra se a codificação ficou boa. Rápido mostra se o arquivo está pesado demais.

---

## Checklist de aplicação

- [ ] Toda imagem na proporção da moldura — nada esticado, nenhum personagem cortado.
- [ ] `width`/`height` explícitos em toda `<img>`; a página não pula ao carregar.
- [ ] `loading="lazy"` abaixo da dobra, e a imagem do hero sem lazy.
- [ ] `alt` descrevendo o que a imagem mostra.
- [ ] Imagens em WebP, dentro do teto de peso.
- [ ] Imagem nova entra no sistema de revelação da página, se houver.
- [ ] Vídeos: marcação completa, `raspagem.js` incluído, raspagem suave nos dois ritmos de rolagem.
