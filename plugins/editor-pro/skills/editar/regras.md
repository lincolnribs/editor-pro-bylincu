# Regras comuns do Editor Pro

Lidas uma vez por sessão por todas as etapas. Depois delas, leia `~/.editor-pro/regras-locais.md` se existir (regras do usuário; valem por cima destas).

## 0. Onde fica cada coisa
- **Plugin** (`EP` = pasta dois níveis acima desta skill): `scripts/ep.py` (todos os comandos), `template/` (Remotion), `sfx/` (biblioteca), `skills/editar/` (estas regras, `motion.md`, `complementos.md`, `formatos/`).
- **Config local** `~/.editor-pro/config.json` (`ep.py config`): `clientes` = pasta com uma subpasta por cliente. Nada de cliente vai para o plugin.
- **Cliente:** `<clientes>/<Cliente>/` com `perfil-edicao.md` (gosto: cores, fontes, ritmo, trilha, logo), kit (`kit-codigo/`, logo, fontes) e `Finalizados/`. Identidade de um cliente nunca vai para outro.
- **Vídeo:** `<clientes>/<Cliente>/videos/AAAA-MM-DD_tema/` com `_CLAUDE/` dentro (tudo o que o Claude gera). Brutos ficam onde estão: só se aponta para eles. Sem pasta de clientes: `_CLAUDE/` ao lado dos brutos.
- Comando: `python "<EP>/scripts/ep.py" <comando>`. Sem argumentos mostra a ajuda.

## 1. Conversa e segurança
- Português, frases curtas. O usuário não é desenvolvedor.
- Nunca mover, renomear ou apagar brutos nem arquivos do cliente. Apagar = mover para `_CLAUDE/_lixo/`.
- **Uma só versão:** alterações sobrescrevem a prévia (`_CLAUDE/previa.mp4`) e a entrega (`Finalizados/AAAA-MM-DD_tema.mp4`). Nada de `_v02`.
- Instalar programa ou baixar arquivo: dizer o quê e esperar o "sim".

## 2. Fluxo e estado
- Etapas: preparar → plano → montar → som → entregar. Uma por conversa; nunca encadear sozinho.
- Estado em `_CLAUDE/projeto.json`, lido e mudado só pelo `ep.py` (`status`, `ver`, `set`, `etapa`, `pendencia`, `resolver`).
- Cada etapa parte da anterior aprovada. Se algo aprovado mudar depois, avisar o que precisa refazer.
- **Ponto salvo:** revisões aplicadas + arquivo gerado. Aí `ep.py etapa <pasta> <etapa>=concluido`, dizer quantos aprendizados ficaram anotados e sugerir `/clear` + `/editar`. Nunca sugerir `/clear` com pedido não aplicado nem anotado (`ep.py pendencia`).

## 3. Economia de tokens (meta: cada etapa ≤ 30–40 mil)
- O Claude decide sobre texto; o `ep.py` calcula (tempos, cor, LUFS, render, conferência) e devolve poucas linhas.
- Transcrição: ler o `.txt` por frase, nunca o JSON. Volume: `ep.py medir`, nunca ebur128 cru. Render: `ep.py render`, nunca o log.
- Imagens: no máximo uma folha por take e uma da prévia. Quadro isolado só com dúvida real.
- Render e tarefas longas em segundo plano.
- Modelo sugerido: Sonnet em preparar, som e entregar; Opus em plano e montar (trocar logo depois do `/clear`).
- Documentação do Remotion só para peça sob medida, e só se o `ctx7` existir: `ctx7 docs /remotion-dev/remotion "<pergunta>"`.

## 4. Gosto separado do ofício
- Ofício (vale para qualquer vídeo) está nas etapas e em `motion.md`. Gosto do cliente está no `perfil-edicao.md`: quando ele diz outra coisa, vale o perfil.
- **Nada automático:** toda escolha criativa tem um porquê ligado à fala. O plano propõe 3 caminhos de direção e o usuário escolhe (`../plano/direcao.md`).
- **Variar entre vídeos:** `ep.py historico <pasta>` mostra o que os últimos vídeos do cliente usaram (direção, texto, transições, trilha); o próximo muda pelo menos a linguagem do texto e o momento-assinatura. Regras técnicas (margens, volume, sincronia) são firmes.

## 5. Acabamento (vale para todo vídeo)
- **Margens do Reels:** sem texto nos 220 px de cima, 450 de baixo e 35 dos lados.
- **Rosto livre:** nenhum texto ou card sobre o rosto (mapear com `ep.py folha --em <s> --grade`).
- **Texto:** sem máscara, nunca cortar acento nem letra; palavra a palavra no tempo da fala, com blur; lettering e legenda na MESMA faixa; entrelinha curta; **sem viúva** (nenhuma linha com uma palavra só: linha de cima mais curta).
- **Sombra:** só quando ajuda (fundo de vídeo que não deixa ler); no bloco, nunca palavra a palavra; entra depois do blur, com fade. Sem gradiente nem sombra colorida sobre o vídeo.
- **Animação fluida:** curva 65/65, nada para seco, nada congela, nada "dobrado" (fantasma do mesmo texto). Conferir quadro a quadro entradas e saídas de números e cards. Detalhes em `motion.md`.
- **Transições sempre**, escolhidas pelo contexto (blur, flash, flash só no personagem, light leak, zoom-in, câmera), rápidas e com a cara do cliente; não repetir a mesma em sequência.
- **Sem buraco entre cenas:** a fala da cena seguinte entra junto com a transição.
- **Ritmo:** gancho com movimento em 1–2 s; algo novo a cada 2–4 s (≈1,3 s nos trechos de motion); b-roll ilustrando a fala.
- **Não afirmar dado não confirmado** pelo cliente (preço, prazo, duração, números). Na dúvida, só o que a pessoa fala.
- Nada de card ou tag enfeitando o óbvio: só o que soma.
- Logo de marca d'água: se um vídeo do cliente tem, todos têm.
- **Final** sem microcorte, fecho suave. **Restos de fala:** depois de cortar pausas, conferir que não sobrou sílaba solta.

## 6. Som
- Voz final ≈ -14 LUFS. SFX no mesmo nível entre si, nos respiros e nas ações da tela.
- Trilha escolhida pela emoção da mensagem; mostrar 2–3 opções antes (Pixabay Music e Mixkit, sem direitos autorais). Medida isolada com o mesmo ganho: ≈10 dB abaixo da voz (≈ -24 LUFS), nunca abaixo de -30. Instituição de ensino ou saúde: calma (piano, ambient).
- Sem voz: master ≈ -14 LUFS.

## 7. Caderno de aprendizados (`_CLAUDE/aprendizados.md`)
- Na revisão, toda correção ou elogio que vale para outros vídeos vira `- [ ] <etapa> · <pedido> · <dd/mm>`. Só deste vídeo não entra; na dúvida, "(talvez só deste vídeo)".
- Aplicar só quando o usuário pedir (`/editar aprendizados`): gosto do cliente → `perfil-edicao.md`; geral → `~/.editor-pro/regras-locais.md`. Mostrar antes, marcar `[x] → onde entrou`.
