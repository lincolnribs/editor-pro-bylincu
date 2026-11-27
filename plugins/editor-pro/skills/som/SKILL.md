---
name: som
description: "Editor Pro, etapa 4: SFX nas ações e respiros, trilha pela emoção e volumes medidos (voz -14 LUFS, trilha ~10 dB abaixo). Aberta pela /editar."
---

# som
O som entra por último, sobre a imagem aprovada. Menos é mais (Sonnet).

Antes: ler `../editar/regras.md` (§6). Se `montar` não estiver `concluido`, parar.

- **Lê:** som por cena no plano, `_CLAUDE/edicao/roteiro.json`, `perfil-edicao.md`.
- **Escreve:** `sfx` e `trilha` no roteiro, `_CLAUDE/som.txt` (o que entrou, onde, volumes medidos), prévia nova.
- **Próximo:** `/editar` → entregar.

## Ofício
1. **O som segue o que se vê.** Ação visível pede som (transição, peça entrando, número batendo, câmera rápida); o que não aparece, não. Corte invisível (punch-in) não leva som.
2. **Um protagonista por momento**, no máximo 3 camadas (principal, grave só nos momentos fortes, apoio).
3. **Sincronia:** impacto no quadro do evento; whoosh com o **pico** no quadro da troca (use `pico` no roteiro); pop, clique e plim começam no evento.
4. **Respiro:** nada nos ~0,5 s antes do maior impacto. O maior impacto do vídeo vai no gancho.
5. **Combina com o movimento:** grande e lento → whoosh grave e longo; pequeno e rápido → curto e agudo; número → contador/plim; dinheiro → caixa; foto → obturador.
6. **Variar:** não repetir o mesmo arquivo em ~20 s.
7. **Nível:** todos os SFX no mesmo nível entre si, bem abaixo da voz.

## Biblioteca
`ep.py sfx` lista as categorias; `ep.py sfx <categoria>` mostra duração e tempo até o pico. Copie os escolhidos para `_CLAUDE/edicao/media/sfx/`. Os sons da biblioteca têm níveis diferentes (coluna dB do `ep.py sfx`): compense no `volume` para ficarem no mesmo nível. Pasta própria do usuário: `ep.py config sfx_extra="<pasta>"` (e `ep.py sfx-indice "<pasta>"` uma vez).

## Trilha
Só se o plano aprovou. Pela emoção da mensagem, opções do Pixabay Music ou Mixkit (perguntar antes de baixar). Ensino e saúde: calma (piano, ambient).

## Medição (sempre medir, nunca chutar)
1. Trilha isolada com o mesmo ganho: `ep.py medir _CLAUDE/edicao/media/trilha.mp3 --ganho <volume>` → ≈ -24 LUFS (≈10 dB abaixo da voz), nunca abaixo de -30.
2. `ep.py render <pasta> --previa` (o limitador já entra no fim) e `ep.py checar <pasta>`: volume, pico, trilha sob a voz e som que corta seco. Um SFX que estoura ou some: `--ini <s> --dur 1`.
3. Registre tudo no `som.txt`.

## Fechamento
Prévia + números (voz, trilha, master). `aguardando_aprovacao`; ajustes por tempo ("o whoosh do 5 s mais baixo"). Aprovado → `concluido`, `/clear` + `/editar`.
