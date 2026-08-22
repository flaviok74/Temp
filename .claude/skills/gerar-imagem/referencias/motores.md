# Motores — a pessoa escolhe, a skill se adapta

Esta skill não tem fornecedor. O que ela tem é **uma exigência técnica** e um jeito de conversar com cada tipo de motor.

## A exigência única

O motor precisa aceitar **referência de imagem** — receber a folha de elenco junto do prompt. É isso que mantém o personagem igual entre uma cena e outra. Um motor só-texto gera nove imagens bonitas de nove personagens diferentes.

Se o motor da pessoa não aceita referência, dá pra trabalhar assim mesmo, com honestidade: avise que a consistência entre cenas vai depender de sorte e de descrição muito detalhada, e prefira composições sem personagem recorrente (objetos, cenários, abstratos).

## Higgsfield (via MCP)

Se o MCP estiver conectado na sessão, as ferramentas aparecem como `mcp__higgsfield__*`:

- `generate_image` com `image_references` pra imagens paradas.
- `generate_video` com as folhas como referência pra vídeo.
- Em lote: `generate_image_batch` + `jobs_wait`.

Se não estiver conectado, a pessoa conecta em sessão interativa (`claude mcp` ou `/mcp`) ou pelos conectores do claude.ai. Não peça tokens no chat.

### Qual modelo escolher lá dentro

Não grave nome de modelo: o catálogo muda, e o próprio MCP tem a ferramenta de recomendação. Consulte na hora, descrevendo o trabalho:

- `models_explore` com `action: "recommend"`, `input: "image"` e a descrição ("website illustrations with character consistency, cast sheet passed into every scene").
- O critério de corte pra imagem parada: o modelo precisa aceitar **múltiplas** referências de imagem (papel `image_references`), porque cada cena recebe a folha de elenco E a folha de modelo juntas. Modelo que só aceita uma referência não serve pro fluxo principal.
- Pra vídeo, mesmo critério — e **desligue o áudio** (`generate_audio: false`) quando o modelo gerar áudio por padrão: vídeo raspado por rolagem não tem som, e áudio ligado é crédito jogado fora.
- Se houver variante econômica do modelo de vídeo, use-a pra testar o movimento antes de gastar no definitivo.
- Se o plano da pessoa inclui **gerações ilimitadas**, prefira os modelos e as configurações cobertos por elas — o `recommend` marca quais são (`supports_unlim`), e a cobertura vale por configuração (resolução, modo), não pelo modelo inteiro. Confira antes de gastar crédito à toa.
- Confira também **em qual conta o MCP está logado** (`balance`): plano e créditos são da conta conectada, que pode não ser a que a pessoa assina.

Uma foto do catálogo em agosto/2026, pra referência (confira sempre com o recommend, porque isto envelhece): Nano Banana Pro era o principal com múltiplas referências pra imagem parada, e Seedance 2.0 o equivalente pra vídeo, com o Seedance Mini como variante de teste.

## Outro serviço via MCP

Mesmo padrão: procure as ferramentas do serviço (busca por "image" ou "generate"), confira se alguma aceita referência de imagem, e siga a mesma ordem — elenco, modelo, cenas.

## Uma CLI qualquer

O formato muda, o padrão não:

```bash
<cli> gerar --prompt "…" \
  --referencia arte/folha-elenco.png \
  --proporcao 4:3
```

Descubra os parâmetros da CLI da pessoa (`--help`) e traduza: prompt, referência(s), proporção, resolução.

## Manual — a pessoa gera ou grava fora

Totalmente válido, e é o caminho de quem grava os próprios vídeos:

1. A skill entrega a **lista de encomenda**: cada peça com nome de arquivo, medida e o que precisa mostrar (a lista sai do `ler_design.py` ou das molduras da página).
2. A pessoa gera/grava onde quiser e salva em `img/` com os nomes combinados.
3. A skill segue do passo de aplicação em diante — codificação de vídeo incluída.

## Sempre, com qualquer motor

- **Pergunte o custo antes.** Diga quantas gerações e espere o sim.
- **Guarde os masters** em resolução cheia fora de `img/` — regenerar acontece mais do que se espera.
- Prompts em inglês. Regras em `prompts.md`.
