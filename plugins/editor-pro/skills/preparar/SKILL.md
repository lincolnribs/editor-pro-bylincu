---
name: preparar
description: "Editor Pro, etapa 1: inventário dos brutos, conversão 1080x1920 30 fps, folha por take, cor medida e transcrição. Aberta pela /editar."
---

# preparar
Transforma brutos em algo que o Claude lê barato. Não escolhe take nem corta.

Antes: ler `../editar/regras.md` (uma vez por sessão) e o guia do modelo em `../editar/formatos/`. `ep.py` = `python "<pasta do plugin>/scripts/ep.py"` (plugin = dois níveis acima desta skill).

- **Lê:** `ep.py status <pasta>`, `perfil-edicao.md` do cliente (se existir).
- **Escreve:** `_CLAUDE/inventario.txt`, `_CLAUDE/midia/`, `_CLAUDE/folhas/`, `_CLAUDE/transcricao/*.txt`, notas no estado.
- **Próximo:** `/editar` → plano.

## Passo a passo
1. `ep.py etapa <pasta> preparar=em_andamento`.
2. **Inventário:** `ep.py inventario <pasta> <brutos ou pasta>`. Mostre só os alertas. Só os brutos do pedido (se o cliente tem plano de conteúdo com takes escolhidos, só esses).
3. **Converter:** `ep.py converter <pasta>` (1080x1920, 30 fps CFR, rotação respeitada; nunca mexe no bruto). Horizontal: avisar que vai recortar no centro.
4. **Folha por take:** `ep.py folha _CLAUDE/midia/<take>.mp4 --quadros 12` (vai para `_CLAUDE/folhas/`). Olhe UMA folha por take e anote uma linha: o que mostra, fala ou b-roll, melhor trecho (s), problemas (tremido, foco, mão na frente).
5. **Cor:** `ep.py cor _CLAUDE/midia/*.mp4`. Anote só os takes que precisam de correção e o filtro sugerido (a correção é feita na montagem, take a take).
6. **Com fala** (talking-head, narrado, comercial, legenda): `ep.py transcrever <pasta>` em segundo plano. Leia só os `.txt` (por frase). Trecho com som e sem palavra: retranscreva aquele take sozinho antes de concluir que não tem fala.
7. **Sem fala** (reels-produto, aftermovie): anote se o som original vale (ASMR) ou é descartável.
8. **Perfil do cliente:** se não existir `perfil-edicao.md`, avise que o plano vai fazer 3–4 perguntas de estilo (cores, fontes, ritmo, trilha) e criar um simples.
9. Grave as notas: `ep.py set <pasta> takes '[{"take":"C001","tipo":"fala","melhor":"2.0-9.5","cor":"amarelado","obs":"..."}]'`.

## Fechamento
Tabela curta: take × tipo × melhor trecho × observação. `ep.py etapa <pasta> preparar=concluido` (sem pedir aprovação, salvo alerta) e sugerir `/clear` + `/editar`.
