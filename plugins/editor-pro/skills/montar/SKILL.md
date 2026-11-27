---
name: montar
description: "Editor Pro, etapa 3: monta o plano aprovado no motor raea (voz, cor, cortes, texto cinético, peças, transições) e entrega a prévia já conferida. Aberta pela /editar."
---

# montar
Executa o plano aprovado. Não muda escolha criativa sem perguntar (Opus).

Antes: ler `_EDITOR-PRO/decisoes.md`, `../editar/regras.md`, `../editar/motion.md`, `roteiro.md` (nesta pasta) e o guia do modelo. Complementos escolhidos: `../editar/complementos.md`. Se `plano` não estiver `concluido`, parar.

- **Lê:** `ep.py ver <pasta> plano`, `_EDITOR-PRO/plano.md`, `perfil-edicao.md`, kit do cliente.
- **Escreve:** `_EDITOR-PRO/edicao/` (projeto raea: `roteiro.json`, `media/`), `_EDITOR-PRO/previa.mp4` (sempre o mesmo arquivo).
- **Próximo:** `/editar` → som (reels-produto: o som entra aqui e o próximo é entregar).

## Regra que mais economiza
**Você não escreve tempos de palavra.** Escreva cada texto só com a frase (como foi dita), o estilo e a entrada. O `ep.py render` acha a frase na fala e preenche `inicio`, `tempos` e `fim` (já sem colisão). Se a frase aparece duas vezes, ponha `"perto": <segundo>`.

## Passo a passo
1. `ep.py etapa <pasta> montar=em_andamento` e `ep.py projeto <pasta>` (cria `_EDITOR-PRO/edicao/`, liga `_EDITOR-PRO/midia` em `media/midia/` e aplica o `design.json` do cliente: não escreva cores nem fontes à mão). Faltou o motor: pedir o "sim" e `ep.py instalar motor`.
2. **Voz (com fala):** `ep.py voz --lista _EDITOR-PRO/takes.txt -o _EDITOR-PRO/edicao/media/base.mp4 --cortar-silencios --respiro 0.14 --escala 1080x1920` (um caminho só: DeepFilterNet, ou FFmpeg se ele falhar; não tente reinstalar). Depois `ep.py transcrever <pasta> _EDITOR-PRO/edicao/media/base.mp4` e leia o `base.txt`: nenhuma palavra sumiu, nenhum corte no nome da marca, nenhuma sílaba solta.
3. **Cor:** só nos takes anotados no preparar, com o filtro do `ep.py cor`, take a take. Talking head: corrija antes da voz (o `takes.txt` aponta para os corrigidos).
4. **Roteiro:** `_EDITOR-PRO/edicao/roteiro.json` cena a cena, com a direção e os componentes do plano. `base.trechos` = o conteúdo de `media/base.cortes.json`. Peça sob medida só em `src/extras.tsx`, com as constantes de `src/motion.ts`; guarde-a também em `<cliente>/kit-codigo/`.
5. **Complementos:** a ponte de `../editar/complementos.md`.
6. **reels-produto:** trilha e som original aqui (regras da etapa som).
7. **Conferir o roteiro:** `ep.py conferir <pasta>`. Corrija todo `✗`.
8. **Prévia:** `ep.py render <pasta> --previa`: calcula os tempos, **bloqueia** se a conferência achar problema (viúva, margem, zona proibida do cliente, buraco), renderiza a imagem na GPU e mixa o som. Log em `.work/`, nunca no chat.
9. **Conferência automática:** `ep.py checar <pasta>` (volume, pico, congelado, flash, área segura, tempo de leitura, legenda fora da palavra). Corrija todo `error`.
10. **Olhar como diretor de arte** (`../editar/revisao.md`): `ep.py revisar <pasta>` (tiras de quadros seguidos em cada entrada e transição) e, se precisar do todo, `ep.py folha _EDITOR-PRO/previa.mp4 --quadros 12`. Se a ferramenta tiver subagente, delegue a leitura das imagens e peça só o resumo (3–5 pontos); senão, olhe uma vez. Corrija os graves e renderize de novo **antes** de mostrar.

## Resumo e revisão
Caminho da prévia + o que pede atenção (curto). Cada pedido do usuário que vale até o fim do vídeo vai para `_EDITOR-PRO/decisoes.md`. `ep.py etapa <pasta> montar=aguardando_aprovacao`. Ajustes por id de cena, sobrescrevendo a mesma prévia. Template novo do plugin num projeto antigo: `ep.py projeto <pasta> --atualizar`. Aprovado → `concluido`, `/clear` + `/editar`.
