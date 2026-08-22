# Vídeo — a imagem que se move quando o visitante rola

## A regra, antes de tudo

**Vídeo nunca dá autoplay.** Nem uma vez, nem "só o do hero", nem "mas é mudo".

Um vídeo em autoplay é a única coisa da página que se mexe sem a pessoa pedir — por isso rouba a atenção de tudo que está do lado, e é o que faz um site parecer anúncio. O que fazemos no lugar: **raspar o `currentTime` pela rolagem**. O quadro que aparece depende de onde o vídeo está na tela. Rolou, avançou. Parou, congelou. Voltou, retrocedeu. Quem gira a manivela é o visitante.

`prefers-reduced-motion` desliga tudo e o vídeo fica no primeiro quadro.

## A marcação

```html
<video data-raspa
       src="img/v1-hero.mp4"
       poster="img/v1-hero.webp"
       muted playsinline preload="auto"
       disablepictureinpicture></video>
```

E uma vez por página, antes de `</body>`:

```html
<script src="raspagem.js"></script>
```

O motor está em `modelos/raspagem.js` — copie pro projeto. Ele acha todo `video[data-raspa]` sozinho.

Nunca coloque `autoplay`, `loop` ou `controls`. Os três brigam com o raspador: `autoplay` viola a regra, `loop` faz o tempo saltar quando a rolagem passa do fim, e `controls` dá ao visitante um segundo relógio.

| Atributo | Por quê |
|---|---|
| `data-raspa` | é como o motor encontra o vídeo |
| `muted` | sem isso o iOS recusa qualquer manipulação programática |
| `playsinline` | sem isso o iPhone abre o player em tela cheia ao primeiro toque |
| `preload="auto"` | raspar exige o arquivo em memória; com `metadata` o tempo engasga |
| `poster` | o primeiro quadro como imagem, pra faixa não nascer preta |
| `disablepictureinpicture` | tira o botão de PiP que o Chrome injeta |

## A receita de codificação — onde a raspagem trava ou desliza

`currentTime = t` obriga o navegador a decodificar a partir do **quadro-chave anterior**. Um MP4 normal tem quadro-chave a cada 2 a 10 segundos, então cada mexida no scroll pode custar centenas de quadros de decodificação — aquele arrasto de meio segundo que parece bug de rolagem.

A correção é todo quadro virar quadro-chave. Vale pra vídeo gerado **e pra vídeo que a pessoa gravou**:

```bash
ffmpeg -i entrada.mp4 -an \
  -c:v libx264 -pix_fmt yuv420p \
  -g 1 -keyint_min 1 -sc_threshold 0 \
  -crf 26 -movflags +faststart \
  -vf "scale=1280:-2,fps=24" \
  img/v1-hero.mp4
```

`-g 1` é o que importa. O arquivo fica de duas a quatro vezes maior que o normal — por isso os orçamentos abaixo são apertados. `-an` remove o áudio: vídeo raspado não tem som.

Conferir antes de entregar:

```bash
ffprobe -v error -select_streams v:0 -show_entries frame=key_frame \
  -of csv=p=0 img/v1-hero.mp4 | sort | uniq -c
```

Todo quadro tem que sair como `1`. Apareceu `0`, o `-g 1` não pegou e vai travar.

## Orçamentos

| | Alvo | Teto |
|---|---|---|
| Duração | 2 a 4 s | 6 s |
| Quadros por segundo | 24 | 30 |
| Largura | 1280 | 1600 |
| Peso por peça | < 900 KB | 1,5 MB |
| Peças na página | 1 a 2 | 3 |

Passou disso, a página pesa e a raspagem perde resposta. Duas peças bem colocadas ganham de seis. **Onde vídeo vale a pena:** o hero e a faixa de vitrine — os dois lugares onde o visitante para.

## Gerando

Sempre contra as mesmas folhas de elenco e modelo das imagens paradas, senão o personagem muda de cara entre uma faixa e outra. Regras de prompt específicas de vídeo em `prompts.md`. E pergunte o custo antes: vídeo custa bem mais crédito que imagem.
