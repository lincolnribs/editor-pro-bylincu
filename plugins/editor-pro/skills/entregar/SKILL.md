---
name: entregar
description: "Editor Pro, etapa 5: conferência final (checklist do cliente, acabamento e motion), render 1080x1920, volume medido e entrega em Finalizados. Aberta pela /editar."
---

# entregar
Fecha o vídeo (Sonnet).

Antes: ler `../editar/regras.md` (§5 e §6) e o checklist de `../editar/motion.md`.

- **Lê:** `ep.py status <pasta>`, última prévia aprovada, `perfil-edicao.md` (checklist do cliente).
- **Escreve:** `<cliente>/Finalizados/AAAA-MM-DD_tema.mp4` (o mesmo nome a cada rodada: sobrescreve) e uma linha em `_EDITOR-PRO/entregas.txt`.

## Passo a passo
1. `ep.py conferir <pasta>`: nenhum `✗`. Ler `_EDITOR-PRO/decisoes.md` e conferir que tudo ali foi respeitado.
2. **Checklist** (sim/não, curto): margens do Reels; sem viúva; rosto livre; texto fluido sem fantasma; quadro 0 pronto; nada congelado; sem buraco entre cenas; texto sem colisão na transição; sem dado não confirmado; logo no padrão do cliente; sem sílaba solta; fecho suave; SFX audível sem estourar. Item com "não" volta para a etapa dele.
3. **Render final:** `ep.py render <pasta>` em segundo plano (vai para `_EDITOR-PRO/final.mp4`).
4. **Medir e olhar:** `ep.py checar <pasta> --final` (nenhum `error`), `ep.py folha _EDITOR-PRO/final.mp4 --quadros 12` e `ep.py revisar <pasta> --final`, com a régua de `../editar/revisao.md`.
5. **Entregar:** copie para `Finalizados/` do cliente (sem pasta de clientes: `Finalizados/` ao lado dos brutos) com o nome `AAAA-MM-DD_tema.mp4`, sobrescrevendo se já existir. Avise o caminho.

## Fechamento
`ep.py historico <pasta> --gravar` (registra a direção e o desenho deste vídeo, para o próximo variar). `ep.py etapa <pasta> entregar=concluido`, diga quantos aprendizados ficaram anotados e sugira `/editar aprendizados` se houver.
