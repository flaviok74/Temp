# O sistema anti-genérico

Texto genérico é o som de uma regra que ninguém escreveu. Um modelo instruído a "escrever um bom texto" escreve a média de tudo que já leu, e essa média tem um sotaque muito reconhecível.

Este nível tem três partes móveis: **um catálogo, um linter e uma limpeza.** O linter é a que importa, porque é a única capaz de devolver REPROVADO.

---

## O catálogo é de português, não é traduzido

Isto precisa ser dito antes de qualquer coisa, porque é o erro mais fácil de cometer: **os tiques de um idioma não são a tradução dos tiques do outro.**

"Delve" não tem equivalente em português. "Descomplicar" não tem em inglês. Um catálogo em inglês rodado contra texto em português devolve 5/5 sempre — o que é pior do que não ter linter nenhum, porque parece uma aprovação.

E português flexiona muito mais que inglês. Listar "potencializar, potencializa, potencializando, potencialize" à mão garante que a forma que faltar é justamente a que vai passar. Por isso o catálogo usa radicais: uma entrada `potencializ*` cobre todas as conjugações.

---

## 1. O catálogo — o que é um tique, de fato

Os tiques vêm em cinco grupos, e a correção muda por grupo. Chutar "isso soa meio IA" não é sistema; isto é.

### Vocabulário
Palavras que modelos alcançam e pessoas em geral não. Cada uma tem uma troca plana:

| Tique | Troca |
|---|---|
| alavancar, potencializar, impulsionar, turbinar | usar, melhorar, aumentar |
| destravar, desbloquear, desvendar, desmistificar | liberar, mostrar, explicar |
| descomplicar, empoderar, capacitar | simplificar, dar controle, ensinar |
| revolucionar, disruptivo, inovador, transformador | mudar, novo, diferente |
| robusto, escalável, holístico, imersivo | sólido, que cresce, completo, envolvente |
| jornada, trajetória, universo de, panorama, patamar | processo, caminho, área, quadro, nível |
| curadoria, meticulosamente, ponta a ponta | seleção, com cuidado, do começo ao fim |
| literalmente, simplesmente, basicamente | (corte) |
| expertise, insights, mindset, know-how | experiência, conclusões, mentalidade, prática |

A correção é uma palavra mais plana, não um sinônimo da mesma palavra.

### Construções
Mais altas que qualquer palavra isolada, porque são formas e não vocabulário:

| Construção | Exemplo |
|---|---|
| "não é apenas X, é Y" | *Não é apenas um curso, é uma jornada* |
| "mais do que apenas" | *Mais do que apenas outro app* |
| "seja você X ou Y" | *Seja você iniciante ou avançado…* |
| "é aí que entra X" | *E é aí que entra o nosso produto* |
| "imagine um…" | *Imagine um mundo onde…* |
| "diga adeus a" | *Diga adeus ao achismo* |
| "nos dias de hoje" | *Nos dias de hoje, com tanta informação…* |
| "de forma X e Y" | *De forma simples e prática* |
| "a verdade é que" | *A verdade é que ninguém te contou isso* |
| "e o melhor de tudo?" | gancho de vídeo colado no texto |
| benefício com pé atrás | *pode ajudar você a*, *pode te auxiliar* |
| ressalva empilhada | *pode vir a*, *talvez possa eventualmente* |
| ressalva de professor | *vale ressaltar que*, *é importante destacar* |

**"Não é apenas X, é Y" é o tique mais alto do português hoje.** Se você corrigir uma coisa só, corrija essa.

### Cadência de pontuação
- Dois ou mais travessões dentro de uma frase
- Ponto e vírgula em texto de site (registro quase sempre errado)
- Reticências usadas como suspense
- Exclamações demais
- Uma ressalva anexada a cada afirmação

### Ritmo
O reflexo da regra de três: *rápido, simples e eficiente.* Um tricolon é retórica. Três na mesma página é uma máquina.

O paralelismo "mais X, mais Y e mais Z" é a versão mais óbvia disso.

### Prova inventada
Números, usuários, depoimentos ou notas que o produto não conquistou. É o único com custo real anexado — ver o fim desta página.

---

## 2. O linter — a parte que pode reprovar

```bash
python3 ferramentas/antigenerico.py index.html
```

```bash
python3 ferramentas/antigenerico.py index.html --vista vista-site
```

```bash
python3 ferramentas/antigenerico.py --texto "cole um rascunho aqui"
```

Ele lê apenas o que o visitante **vê** — `<script>`, `<style>` e todas as tags saem antes, então ele pontua as palavras e não a marcação.

Nota de 0 a 5, um ponto a menos por grupo reprovado. **Sai com código diferente de zero abaixo de 5/5**, porque "quase limpo" é exatamente como uma página acaba soando igual a todas as outras.

Rode nos dois lados de uma reescrita. Um modelo de ponta é muito bom em tirar tiques e perfeitamente capaz de acrescentar outros enquanto faz isso — então uma "limpeza" não conferida é cara ou coroa.

### O que a saída te dá

Cada acerto de vocabulário mostra a forma que apareceu **de verdade** na página, a contagem, e a troca sugerida:

```
  vocabulário de IA:
    · descomplicaram  (1×)  →  simplificar
    · jornada         (1×)  →  processo
```

A forma real, não o radical, porque `descomplicaram` você acha com Ctrl+F no arquivo e `descomplic*` não.

Cada trecho do texto só é contado uma vez. Sem isso "curadoria" seria contada duas vezes — uma por `curadoria`, outra pelo radical `curad*` — e contagem inflada faz a pessoa parar de confiar no número, que é o único valor que ele tem.

---

## 3. A limpeza

Passe o texto final por uma **família de modelo diferente** com uma instrução: tire os tiques, mantenha o sentido, mantenha o tamanho.

Famílias diferentes têm sotaques diferentes, e um modelo é péssimo em ouvir o próprio. Um modelo rival ouve na hora.

```
Reescreva isto de modo que nenhuma frase contenha tique de escrita de IA.
Mantenha todos os fatos e todos os números. Mantenha o tamanho dentro de 10%.
Não acrescente ressalvas, não acrescente frase de resumo.
Devolva apenas o texto reescrito.
```

**Passe a saída pelo linter.** Sempre. É a razão inteira de o linter existir.

---

## A regra com custo real

> **Nunca invente prova.**

Nada de contagem de usuários, depoimentos, notas, "mais de 10.000 alunos", a menos que cada um seja verdade e você possa mostrar.

Um produto que não lançou não pode ter 10.000 de coisa nenhuma. Essa linha é cortada na hora por qualquer leitor atento, e leva junto a credibilidade de todo o resto da página.

`antigenerico.py` sinaliza padrões de número-mais-substantivo como **possível prova inventada**, e `verificar.py` reprova o build direto neles. Os dois entendem o formato numérico brasileiro — `10.000` com ponto de milhar e `4,9` com vírgula decimal. Um regex escrito pro formato inglês não pega nenhum dos dois, que é exatamente o erro que deixa passar a linha mais perigosa da página.

Ambos são barulhentos aqui de propósito — um falso positivo te custa dez segundos, e um falso negativo é uma alegação que você não consegue sustentar.

Especificidade ganha de credibilidade fabricada de qualquer jeito. *"Cinco minutos de problemas reais de prompt, corrigidos no segundo em que você responde"* ganha de qualquer número inventado, e tem a vantagem de ser verdade.
