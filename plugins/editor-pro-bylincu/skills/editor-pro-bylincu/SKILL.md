---
name: editor-pro-bylincu
description: Editor de vídeo profissional em português (Reels, Stories, TikTok, Shorts, talking head, takes brutos, comercial, aftermovie, legenda, motion) com Remotion, limpeza de voz (DeepFilterNet), corte de silêncios, lettering cinético, SFX e trilha. Use SEMPRE em pedidos de edição ou criação de vídeo, mesmo genéricos ("edita esse vídeo", "edite isso", "monta esse reels", "faz um aftermovie", "só legenda", "cria um motion") e sem citar Remotion ou HyperFrames.
---

# Editor Pro (by Lincu)

Cada vídeo segue um **formato**, e cada formato tem o seu caminho. Os comandos ficam em `scripts/editor.py` (caminho absoluto da pasta desta skill). Cada comando termina com `PRÓXIMO:`, que diz exatamente o que fazer. Não planeje além da etapa atual, não leia arquivos que a saída não indicou e não escreva código Remotion: o vídeo é montado a partir de `public/roteiro.json`.

## 1. Descubra o formato
Rode `python editor.py analisar <arquivos>` (sem imagem: duração, quanto do tempo tem som, cortes de cena) e cruze com o pedido:

| Pedido / material | Formato | Guia |
|---|---|---|
| Pessoa falando em takes brutos, Reels com ritmo | `talking-head` | `references/formatos/talking-head.md` |
| Vender: oferta, preço, produto, CTA | `comercial` | `references/formatos/comercial.md` |
| "Só monta os takes / corta erros e silêncios", depoimento, aula | `decupagem` | `references/formatos/decupagem.md` |
| Vídeo já editado, "só legenda / melhora o áudio" | `legenda` | `references/formatos/legenda.md` |
| Vários clipes sem fala: evento, bastidores, obra, viagem | `aftermovie` | `references/formatos/aftermovie.md` |
| Sem filmagem: vinheta, logo, lançamento, post animado | `motion` | `references/formatos/motion.md` |

Leia **só o guia do formato escolhido**. Em dúvida entre dois formatos, pergunte na mensagem de abertura.

## 2. Mensagem de abertura (uma só)
Diga o formato escolhido e o porquê, em uma linha, e pergunte de uma vez só o que faltar: cliente, título, trilha (gênero, tema ou sem música; obrigatória no aftermovie) e a identidade, se o cliente for novo. Depois da resposta, execute o caminho sem novas perguntas, salvo dúvida real.
Já começou antes? `python editor.py status`.

## 3. Execute o caminho
`python editor.py novo --formato <formato> "<Cliente>" "<Título>" <arquivos>` e siga cada `PRÓXIMO:`. O que é seu em cada formato (decupagem, criação, seleção, revisão) está no guia. O resto é automático.

## Regras que valem para todos
- Nada sobre o rosto e nada fora das margens seguras (220 px em cima, 450 embaixo, 35 dos lados).
- Lettering repete a palavra dita, com 2 a 4 palavras. Legenda e lettering ficam na mesma faixa.
- Nunca repetir take, b-roll ou música já entregues ao cliente (`historico.md`). A identidade de um cliente nunca vai para outro.
- Corte pontual pedido = só o tropeço, nunca a frase inteira.
- Nunca invente preço, dado ou promessa: use só o que veio no pedido ou no material.

## Economia de tokens
- Use só os comandos do caminho. Nunca rode `ebur128`, `npx remotion render` ou ffmpeg sem `-v error` direto.
- No máximo 3 imagens por vídeo: mapa do rosto ou catálogo, folha da prévia e, se precisar, uma folha de take.
- Um vídeo por conversa. Ao entregar, sugira `/compact` ou uma conversa nova.

## Referências
- `references/roteiro.md`: campos do roteiro.json, cor e estabilização.
- `references/complementos.md`: as 9 skills de motion incluídas.
- `references/banco-de-midia.md`: Mixkit, SFX e trilha.
- `references/instalacao.md`: instalação e problemas.
- Peça sob medida (card, oferta, fechamento): só em `src/extras.tsx`.
