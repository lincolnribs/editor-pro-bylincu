---
name: plano
description: "Editor Pro, etapa 2: direção criativa (3 caminhos para escolher), decupagem, cenas, texto pelo sentido de cada frase, transições, trilha, SFX e menu de complementos. Aberta pela /editar."
---

# plano
Olha o vídeo inteiro, pensa e decide. Não renderiza nada. Erro aqui custa uma rodada inteira: pensar bem (Opus).

Antes: ler `../editar/regras.md`, `../editar/motion.md`, `direcao.md` (nesta pasta) e o guia do modelo em `../editar/formatos/`. Se `preparar` não estiver `concluido` (ou `nao_precisa`), parar.

- **Lê:** `ep.py status <pasta>`, `ep.py ver <pasta> takes`, `_CLAUDE/inventario.txt`, `transcricao/*.txt`, `perfil-edicao.md`, **`ep.py historico <pasta>`** (o que os últimos vídeos do cliente já usaram).
- **Escreve:** `_CLAUDE/plano.md` (o que o usuário aprova), bloco `plano` no estado (com `plano.direcao`), `_CLAUDE/takes.txt` quando há fala.
- **Próximo:** `/editar` → montar.

## Regra de ouro: nada é automático
Não existe estilo padrão. Todo texto, transição e peça tem um **porquê** ligado ao que está sendo dito. Se a escolha caberia em qualquer outro vídeo, ela está genérica: pense de novo. Um vídeo bom tem uma ideia; o resto serve a ela.

## Sem perfil do cliente
Pergunte em UMA mensagem: cores (ou logo), fontes, ritmo, trilha. Grave `perfil-edicao.md` na pasta do cliente. Peça 1–2 referências de vídeo, sem travar.

## 1. Entender (antes de qualquer escolha)
- Leia a transcrição inteira. Escreva para você: **o que o espectador tem que sentir ou entender no fim?** Qual é a frase-chave? Onde está a virada? Há número, lista, contraste, pergunta, emoção?
- **Decupagem (com fala):** ler e decidir por frase. Take: o último completo costuma ser o melhor; se tropeçou e um anterior está limpo, o anterior. Nunca cortar no meio da frase; nome da marca nunca cortado. Na dúvida, não corta e marca. `takes.txt`: `"<caminho em _CLAUDE/midia>" inicio fim`.

## 2. Direção criativa: 3 caminhos (o usuário escolhe)
Monte **3 caminhos realmente diferentes** entre si e diferentes dos 2 últimos vídeos do histórico, todos dentro da identidade do cliente. Cada caminho em 4–5 linhas:
- **Nome e ideia** (ex.: "Manchete": cada argumento entra como título de jornal).
- **Linguagem do texto:** quais estilos e entradas, quanto texto (muito / pontual / quase nenhum), onde fica na tela.
- **Movimento:** ritmo, transições, câmera.
- **Momento-assinatura:** a cena que ninguém esquece (e onde ela cai).
- **Som:** clima da trilha e densidade de SFX.

Use `direcao.md` para montar caminhos com personalidade. Dê a sua recomendação e o porquê, e espere a escolha (pode ser mistura). Grave: `ep.py set <pasta> plano.direcao "<nome: ideia em uma frase>"`.

## 3. Cenas (só depois da escolha)
Tabela por cena: `c01`… · take e trecho (s) · duração · texto na tela (estilo + entrada + lugar) · peça/motion · transição de entrada · som · **porquê** (uma frase curta ligando a escolha à fala).
- **Texto pelo sentido da frase** (dicionário em `direcao.md`): pergunta, número, lista, contraste, virada e emoção pedem desenhos diferentes. Nem toda frase precisa de texto: deixe respirar.
- **Variar dentro do vídeo:** nenhuma combinação estilo+entrada em mais de 60% dos textos; mude também tamanho e lugar. O gancho e o clímax têm desenho próprio.
- **Ritmo:** gancho com movimento em 1–2 s; algo novo a cada 2–4 s; b-roll nos argumentos; um protagonista por vez.
- **Transição em toda troca**, escolhida pela energia do momento, sem repetir em sequência.
- **Trilha** pela emoção: 2–3 opções (Pixabay Music, Mixkit). **SFX** só nas ações visíveis.
- **Acabamento** faz parte da direção: grão, vinheta neutra, deriva da câmera, `Fundo` vivo nas telas de motion, destaque em serifa itálica (elegante) ou na condensada (força). Escolha o que serve ao caminho; não ligue tudo sempre.
- Peça sob medida (`extras.tsx`) quando nenhum componente expressa a ideia: descreva o que ela faz.

## Componentes do template (pelo nome)
- **Estilos de texto:** `linha` · `karaoke` · `palavra` · `hierarquia` · `marca-texto` · `caixa` · `lateral`. **Entradas:** `blur` · `pop` · `deslizar` · `onda` · `maquina` · `letras`. Tipos: `lettering` · `legenda` · `impacto`. Mais `tamanho`, `y`, `centro`, `caixaAlta`, `cor`.
- **Destaque:** `destaqueFonte` `serifa` (itálico) ou `impacto` (condensada). **Acabamento:** `grao` · `vinheta` · `deriva`.
- **Peças:** `Pilula` · `Card` · `Contador` · `Lista` · `Fundo`. **Transições:** `corte` · `flash` · `blur` · `luz` · `zoom` · `obturador` · `camera`. **Fechos:** `logo` · `fade` · `cartela`.

## Menu de complementos
Com a direção escolhida, siga `../editar/complementos.md`: só os que servem ao caminho, numerados, e grave a escolha (ou "nenhum").

## Revisão e aprovação
Ajustes por id ("c03 mais curta"). Anote aprendizados na hora. Aprovado → grave `plano` no estado, `ep.py etapa <pasta> plano=concluido`; o plano trava. Sugerir `/clear` + `/editar`.
