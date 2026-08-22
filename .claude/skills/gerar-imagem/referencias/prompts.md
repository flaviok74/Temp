# Regras de prompt que mudam o resultado de verdade

Escreva em inglês, mesmo com o site em português. Os modelos de imagem foram treinados majoritariamente com legendas em inglês, e termos de composição como *full body*, *flat background* e *three-quarter view* têm efeito muito mais previsível na língua original. O prompt é instrução técnica pra máquina; o site é que fala português.

## Imagens paradas

- **Exija fundo chapado de cor única, e diga de três jeitos:** "completely flat plain background #F7F4ED, zero texture, zero gradient, no shadows on the background." Pedir transparência devolve um *xadrez pintado* — pixels 100% opacos que só parecem transparentes.
- **Nomeie a pele explicitamente**, ou os rostos voltam pálidos e sem expressão: "warm light-peach skin with soft coral blush, big expressive dark eyes with white catchlights."
- **Exija figuras completas:** "FULL BODY, head to feet, legs and shoes fully drawn, nothing cropped, generous empty margin below the feet." Sem isso o modelo corta na cintura na borda do quadro, e esconder essa emenda custa uma hora.
- **Exija separação entre objetos:** "each element clearly separated with visible gaps of background between them" — ou os objetos se fundem.
- **Proporção no pedido, não no corte.** Gere já em 4:3, 1:1, 16:9 — cortar depois perde composição.

## A folha de elenco e a folha de modelo

- Elenco: "character lineup, all characters standing front-facing, neutral pose, same scale, flat background" — todos os personagens numa imagem só.
- Modelo: "character model sheet, multiple angles (front, three-quarter, side), expression variants" — o guia do mascote.
- Estas duas são geradas primeiro e entram como referência em **todas** as cenas seguintes.

## Vídeo

- **Câmera parada:** "static camera, locked off, no camera movement." A câmera já se move — é a rolagem do visitante. Duas fontes de movimento brigam e enjoam.
- **Ciclo, não cena:** "seamless loop, the last frame matches the first." Sem isso a raspagem dá um salto visível quando a pessoa rola de volta.
- **Movimento pequeno:** "subtle motion only, gentle, minimal displacement." Movimento grande raspado parece acelerado, porque o visitante controla a velocidade — e ele sempre rola mais rápido do que você imaginou.
- **Um assunto se mexe, o resto parado.** Fundo em movimento raspado vira ruído.
- Fundo chapado, pelas mesmas razões das imagens.

## O hábito que economiza retrabalho

Guarde cada prompt usado junto do arquivo gerado (o `--manifest` do inventário existe pra isso). Quando uma peça precisar ser regerada (e vai precisar), você parte do prompt que funcionou em vez de reconstruir de memória.
