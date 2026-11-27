---
name: editar
description: "Editor Pro: ponto de entrada para editar vídeo (Reels, talking head, narrado, motion) no motor raea. Mostra onde o vídeo está e abre a etapa certa. Use em /editar, em pedido de edição de vídeo ou quando mandarem arquivos de vídeo."
---

# editar

Fluxo: **preparar → plano → montar → som → entregar**, uma etapa por conversa. Esta skill não edita: lê o estado e abre a etapa.

`EP` = a pasta do plugin (dois níveis acima desta skill). Comandos: `python "<EP>/scripts/ep.py" <comando>`.
Antes de tudo, leia `regras.md` (nesta pasta), uma vez por sessão.

## /editar
1. **Primeira vez no computador** (`ep.py onde` diz que não há config): pergunte em UMA mensagem onde ficam as pastas dos clientes (ou se não usa) e grave com `ep.py config clientes="<pasta>"`. Rode `ep.py doctor`. Se faltar o motor ou a transcrição, peça o "sim" e rode `ep.py instalar` em segundo plano (motor raea ~335 MB, transcrição ~2 min).
2. **Sem projeto** (não há `_EDITOR-PRO/projeto.json` na pasta do vídeo): pergunte em UMA mensagem o cliente, os brutos (pasta ou arquivos; se ele só mandou arquivos, já são esses), o modelo de vídeo (sugira um, com o porquê) e o pedido (tema, frase, peça do plano de conteúdo). Crie a pasta do vídeo (`regras.md` §0) e rode `ep.py novo <pasta> cliente=... modelo=... tema="..."`. Depois abra a skill `preparar`.
   - Modelos: `talking-head`, `reels-produto` (6–12 s sem fala), `narrado`, `motion`, `comercial`, `aftermovie`, `legenda` (vídeo já editado). Guia de cada um em `formatos/<modelo>.md`: a etapa lê só o do vídeo.
3. **Com projeto:** `ep.py status <pasta>`. Mostre curto: modelo, etapas, pendências, aprendizados anotados (`_EDITOR-PRO/aprendizados.md`).
4. **Próximo passo:** diga qual é e pergunte se segue. Etapa aguardando aprovação → continuar nela. Algo mudou depois de aprovado → avisar antes.
5. Modelo sugerido por etapa: Sonnet em preparar, som e entregar; Opus em plano e montar. Trocar logo após o `/clear`.

## /editar aprendizados
Ler as linhas `- [ ]` do `_EDITOR-PRO/aprendizados.md` do vídeo, propor onde cada uma entra (`regras.md` §7), o usuário filtra, gravar e marcar.

## Regras
- Não editar vídeo aqui. Nunca mover, renomear ou apagar brutos.
- Nunca dar `/clear` (é do usuário).
