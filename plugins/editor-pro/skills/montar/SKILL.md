---
name: montar
description: "Editor Pro, etapa 3: monta no Remotion o plano aprovado (voz, cor, cortes, texto cinético, peças, transições, câmera) e gera a prévia. Aberta pela /editar."
---

# montar
Executa o plano aprovado. Não muda escolha criativa sem perguntar (Opus).

Antes: ler `../editar/regras.md`, `../editar/motion.md`, `roteiro.md` (nesta pasta) e o guia do modelo. Complementos escolhidos: `../editar/complementos.md`. Se `plano` não estiver `concluido`, parar.

- **Lê:** `ep.py ver <pasta> plano`, `_CLAUDE/plano.md`, `perfil-edicao.md`, kit do cliente.
- **Escreve:** `_CLAUDE/remotion/` (projeto), `public/roteiro.json`, `_CLAUDE/previa.mp4` (sempre o mesmo arquivo).
- **Próximo:** `/editar` → som (reels-produto: o som entra aqui e o próximo é entregar).

## Passo a passo
1. `ep.py etapa <pasta> montar=em_andamento` e `ep.py remotion <pasta>` (cria o projeto e liga `_CLAUDE/midia` em `public/midia/`). Se o Remotion não estiver instalado: pedir o "sim" e `ep.py instalar`.
2. **Voz (com fala):** `ep.py voz --lista _CLAUDE/takes.txt -o _CLAUDE/remotion/public/base.mp4 --cortar-silencios --respiro 0.14 --escala 1080x1920`. Retranscreva a base (`ep.py transcrever <pasta> _CLAUDE/remotion/public/base.mp4`) e confira que nenhuma palavra sumiu, nenhum corte caiu no nome da marca e não sobrou sílaba solta. Os `tempos` dos textos saem desse `.txt`.
3. **Cor:** só nos takes anotados no preparar, com o filtro do `ep.py cor`, take a take (nunca um filtro igual para tudo). Talking head: corrija os takes antes da voz (o `takes.txt` aponta para os corrigidos).
4. **Roteiro:** preencha `public/roteiro.json` cena a cena, exatamente com a direção e os componentes do plano (estilo, entrada, lugar e tamanho de cada texto). Faltou detalhe no plano? Decida pelo sentido da frase (`../plano/direcao.md`), nunca pelo padrão. Tempos em múltiplos de U (8 quadros) onde for movimento. Peça sob medida só em `src/extras.tsx`, com as constantes de `src/motion.ts`; guarde-a também em `<cliente>/kit-codigo/`.
5. **Complementos:** a ponte de `complementos.md` (motion contínuo vira clipe; logo animado vira peça; efeito vira base).
6. **reels-produto:** trilha e som original aqui (regras da etapa som).
7. **Conferir antes de renderizar:** `ep.py conferir <pasta>`. Corrija todo `✗`.
8. **Prévia:** `ep.py render <pasta> --previa` em segundo plano; depois `ep.py folha _CLAUDE/previa.mp4 --quadros 18`. Olhe a folha uma vez: rosto livre, margens, algo novo a cada 2–4 s, sem buraco. Dúvida em entrada/saída de número ou card: `ep.py folha _CLAUDE/previa.mp4 --em <s>` em 2–3 quadros seguidos (sem fantasma, sem travar).

## Resumo e revisão
Caminho da prévia + o que pede atenção (curto). `ep.py etapa <pasta> montar=aguardando_aprovacao`. Ajustes por id de cena, sobrescrevendo a mesma prévia. Template novo do plugin num projeto antigo: `ep.py remotion <pasta> --atualizar`. Aprovado → `concluido`, `/clear` + `/editar`.
