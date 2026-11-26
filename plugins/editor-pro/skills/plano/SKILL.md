---
name: plano
description: "Editor Pro, etapa 2: decupagem, ordem das cenas, texto, componentes, transições, câmera, trilha, SFX e menu de complementos. Plano curto para aprovar. Aberta pela /editar."
---

# plano
Olha o vídeo inteiro e decide. Não renderiza nada. Erro aqui custa uma rodada inteira: pensar bem (Opus).

Antes: ler `../editar/regras.md`, `../editar/motion.md` e o guia do modelo em `../editar/formatos/`. Se `preparar` não estiver `concluido` (ou `nao_precisa`), parar.

- **Lê:** `ep.py status <pasta>`, `ep.py ver <pasta> takes`, `_CLAUDE/inventario.txt`, `transcricao/*.txt`, `perfil-edicao.md`, o que já está em `Finalizados/` do cliente (para não repetir).
- **Escreve:** `_CLAUDE/plano.md` (o que o usuário aprova), bloco `plano` no estado, `_CLAUDE/takes.txt` quando há fala.
- **Próximo:** `/editar` → montar.

## Sem perfil do cliente
Pergunte em UMA mensagem: cores (ou logo para tirar as cores), fontes, ritmo (calmo / médio / acelerado), trilha (sim/não, clima). Grave `perfil-edicao.md` na pasta do cliente. Referências de vídeo ajudam muito: peça 1–2 links ou arquivos, sem travar.

## Ofício (o editor sênior)
- **Decupagem (com fala):** ler por frase, decidir por frase. Take: o último completo costuma ser o melhor; se ele tropeçou e um anterior está limpo, o anterior. Nunca cortar no meio da frase; nome da marca nunca cortado. Hesitação colada na fala fica. Na dúvida, não corta e marca. Ordem = a gravada (reordenar só como sugestão forte, ex.: a frase de impacto no gancho).
- `takes.txt`: uma linha por trecho, `"<caminho em _CLAUDE/midia>" inicio fim`.
- **A ideia nasce do que está sendo dito**, nunca de um template: qual imagem, peça ou movimento explica melhor aquela frase? Um protagonista por vez.
- **Ritmo:** gancho com movimento em 1–2 s; algo novo a cada 2–4 s; b-roll nos argumentos.
- **Texto:** palavras-chave ditas, curto, sem viúva (quebre com ` | `), na faixa fora do rosto; só dado confirmado.
- **Transição em toda troca**, escolhida pelo contexto e variando: `blur` (suave), `flash` (impacto), `luz` (light leak, emoção), `zoom` (aproximar a ideia), `camera` (chicote, energia), `obturador` (foto, antes/depois), flash só no personagem (complemento `effects`).
- **Trilha** pela emoção da mensagem: 2–3 opções (Pixabay Music, Mixkit) com nome e link. **SFX** só nas ações visíveis e nos respiros.

## Componentes do template (escolher pelo nome)
- **Entradas de texto:** `blur` (padrão) · `pop` · `deslizar` · `onda` · `maquina` · `letras`. Tipos: `lettering` · `legenda` · `impacto` (condensada).
- **Peças:** `Pilula` (chip curto) · `Card` (título + apoio) · `Contador` (número subindo) · `Lista` (itens um a um).
- **Transições:** `corte` · `flash` · `blur` · `luz` · `zoom` · `obturador` · `camera`.
- **Fechos:** `logo` (vídeo desfoca + logo) · `fade` · `cartela` (fundo sólido + texto + logo).
- Câmera: punch-in alternado + drift (talking head, automático).
- Peça sob medida (`extras.tsx`) só quando nenhuma acima resolve: diga qual e por quê.

## Menu de complementos
Depois de ter o plano na cabeça, siga `../editar/complementos.md`: mostre só os que combinam, numerados, e grave a escolha (ou "nenhum").

## Plano (o que mostrar)
Tabela por cena: `c01`… · take e trecho (s) · duração · texto na tela (com a entrada) · peça/motion · transição de entrada · som. Depois: duração total, trilha (opções), complementos escolhidos, dúvidas. Curto.

## Revisão e aprovação
Ajustes por id ("c03 mais curta"). Anote aprendizados na hora. Aprovado → grave `plano` no estado, `ep.py etapa <pasta> plano=concluido`; o plano trava (se mudar depois, avisar que a montagem refaz). Sugerir `/clear` + `/editar`.
