---
name: super-copy
description: Melhora o texto de um site pra converter mais — escaneia a página como um visitante apressado lê, aponta cada linha fraca com o motivo, reescreve aplicando princípios clássicos de copywriting (Ogilvy, Caples, Sugarman, Cialdini), remove os tiques de escrita de IA em português, e entrega um relatório em HTML mostrando cada troca antes → depois. A reescrita roda em qualquer motor que a pessoa escolher (Codex CLI, o próprio Claude Code, outro modelo, ou à mão). Dispare com "/super-copy", "melhora a copy", "melhora o texto do site", "deixa o texto mais persuasivo", "reescreve os títulos", "passa o scanner de copy", "por que ninguém clica". NÃO use para roteiro de vídeo (isso é criador-de-roteiros) nem para título de YouTube (isso é youtube-titulos-descricoes).
---

# Super Copy

Um texto pode estar limpo, correto e bonito — e não converter nada. Esta skill trata o texto como sistema: mede, aponta, reescreve com princípio, e **prova o trabalho** num relatório antes → depois.

---

## A regra que vem antes de tudo

**Nunca invente prova.** Nada de contagem de usuários, depoimento, nota ou resultado que o produto não tenha. Se o produto não lançou, o texto diz isso. O ganho vem de especificidade sobre o que a coisa faz — "cinco minutos de problemas reais, corrigidos na hora" ganha de qualquer número fabricado, e tem a vantagem de ser verdade.

Esta regra não se negocia com motor nenhum: ela vai escrita dentro do briefing que qualquer motor recebe.

---

## O fluxo

### 1. Escanear

```bash
python3 ferramentas/persuasao.py index.html
```

Imprime a página **como ela é lida de verdade** — só os títulos e os botões, em ordem, que é o que um visitante apressado vê. Se essa sequência sozinha não explica a oferta, a página depende de alguém ler os parágrafos, e quase ninguém lê.

Depois aponta: CTA genérico ("Saiba mais" não é chamada, é adiamento), título que rotula em vez de afirmar ("Nossos recursos" é etiqueta de pasta), pedidos brigando na mesma tela, promessa vaga sem nada verificável.

E o segundo medidor:

```bash
python3 ferramentas/antigenerico.py index.html
```

Nota de 0 a 5 contra os tiques de escrita de IA em português — catálogo próprio, não traduzido do inglês. Abaixo de 5, precisa de limpeza. O catálogo completo: `referencias/anti-generico.md`.

### 2. Reescrever — no motor que a pessoa escolher

```bash
python3 ferramentas/persuasao.py index.html --briefing > briefing.md
```

O briefing é texto puro e autocontido: as regras inegociáveis, **os seletores CSS já calculados** (seletor errado é o bug que falha em silêncio — o script cuida dele, quem reescreve cuida só das palavras), o texto atual, o problema de cada linha, e a página inteira como contexto.

Daí, qualquer motor:

```bash
codex exec < briefing.md
```

```bash
claude -p "$(cat briefing.md)"
```

Ou colar em qualquer chat, ou reescrever à mão. A skill não tem opinião sobre o motor — tem opinião sobre as regras.

**A reescrita segue os princípios de `referencias/principios.md`**: especificidade do Ogilvy, títulos do Caples, o escorregador do Sugarman, prova honesta do Cialdini, consciência do Schwartz. Cada um com antes/depois em português. Não é lista decorativa — é o critério de aceitação da reescrita.

### 3. Conferir a reescrita

Modelo tira tique e põe tique ao mesmo tempo. Lint sempre a saída:

```bash
python3 ferramentas/antigenerico.py --texto "cole a linha reescrita"
```

Só entra na página o que passa. E toda troca aplicada é registrada num JSON (`trocas.json`) carregando o texto antigo, o novo e o motivo — é a matéria-prima do relatório.

### 4. O relatório — obrigatório na entrega

```bash
python3 ferramentas/relatorio.py trocas.json -o relatorio.html
```

Sai um HTML autocontido: a nota nas duas medições, cada linha trocada lado a lado com o motivo, e o que o scanner percebeu. É a aba de texto da entrega — quem abrir vê exatamente o que a skill fez e por quê. Entregue sempre a página **e** o relatório.

Formato do `trocas.json`:

```json
{
  "pagina": "index.html",
  "nota_antes": "2/5", "nota_depois": "5/5",
  "percepcoes": ["4 CTAs diferentes brigando na primeira tela"],
  "trocas": [
    { "onde": ".hero-cta .btn", "antes": "Clique aqui",
      "depois": "Ver a agenda funcionando", "motivo": "CTA genérico: nomeie o destino" }
  ]
}
```

---

## Portões — confira antes de entregar

- [ ] `antigenerico.py` dá 5/5 na página final.
- [ ] Zero prova inventada — número, usuário, depoimento, nota.
- [ ] Nenhum seletor do texto mágico/variantes avisando no console.
- [ ] Toda troca aplicada está no `relatorio.html`, com motivo.
- [ ] Os títulos sozinhos, lidos em sequência, explicam a oferta.
