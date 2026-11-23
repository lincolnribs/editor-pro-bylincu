---
name: editor-pro-bylincu
description: Editor de vídeo profissional em português (Reels, Stories, TikTok, Shorts, talking head, takes brutos, b-roll, motion) com Remotion, limpeza de voz (DeepFilterNet), corte de silêncios, lettering cinético, SFX e trilha. Use SEMPRE em pedidos de edição de vídeo, mesmo genéricos ("edita esse vídeo", "edite isso", "monta esse reels", "corta os silêncios", "coloca legenda") e sem citar Remotion ou HyperFrames.
---

# Editor Pro (by Lincu)

Você segue um **trilho**: cada etapa é um comando do `scripts/editor.py` (caminho absoluto da pasta desta skill), e a saída de cada comando termina com `PRÓXIMO:`, dizendo exatamente o que fazer. Não planeje além da etapa atual, não leia arquivos que a saída não indicou e **não escreva código Remotion**: o vídeo inteiro é montado a partir de `public/roteiro.json`.

## Antes de começar (uma mensagem só)
Pergunte de uma vez, só o que faltar: nome do cliente, título do vídeo, **trilha sonora** (gênero ou tema, ou sem música) e a identidade (cores e fonte), caso o cliente seja novo. Depois dessa resposta, execute o trilho sem novas perguntas, salvo dúvida real.
Já começou antes? Rode `python editor.py status` e continue de onde parou.

## O trilho
| # | Comando / ação | O que você faz |
|---|---|---|
| 1 | `python editor.py novo "<Cliente>" "<Título>" <brutos...>` | Nada: cria pastas e projeto, converte os takes e transcreve. Leia o LEIAME do cliente. |
| 2 | Decupagem | Leia os `.txt` dos takes e escreva `public/<vídeo>/takes.txt` com o melhor trecho de cada fala (sem tropeços nem repetições), na ordem: `"caminho" inicio fim`. |
| 3 | `python editor.py voz` | Nada: limpa a voz, corta silêncios (respiro 0.14), retranscreve e confere as palavras. Se aparecer `CONFIRA`, ajuste o `takes.txt` e rode de novo. |
| 4 | `python editor.py roteiro` | Nada: gera o `roteiro.json` com legenda automática e o mapa do rosto. |
| 5 | Criação | Abra o mapa do rosto **uma vez**. Edite o `roteiro.json` seguindo `references/roteiro.md`: `tema`, `faixaY`, `lettering`, `broll`. |
| 6 | `python editor.py trilha <arquivo>` | Só se a trilha foi aprovada (Mixkit, ver `references/banco-de-midia.md`). |
| 7 | `python editor.py montar` | Nada: põe SFX nos letterings e b-rolls e tira a legenda onde há lettering. |
| 8 | `python editor.py preview` | Abra a folha da prévia **uma vez**. Confira rosto, margens e ritmo. Ajuste o roteiro e repita 7-8 no máximo 2 vezes. |
| 9 | `python editor.py final` | Nada: renderiza em `entregas/`, mede o volume e atualiza o histórico. Mostre ao usuário onde está o arquivo. |

Cor estranha num take (amarelado, escuro) ou b-roll tremido: corrija antes da etapa 3 (`references/roteiro.md`, seção Cor).

## Regras que não mudam
- Nada sobre o rosto e nada fora das margens seguras (220 px em cima, 450 embaixo, 35 dos lados). O template já limita a faixa às margens; você escolhe a `faixaY` fora do rosto.
- Lettering repete a palavra dita, com 2 a 4 palavras por vez. Legenda e lettering ficam na mesma faixa.
- Gancho com movimento em 1 a 2 s (lettering ou b-roll logo no início) e algo novo a cada 2 a 4 s.
- Nunca repetir take, b-roll ou música já entregues ao cliente (`historico.md`). A identidade de um cliente nunca vai para outro.
- Corte pontual pedido = só o tropeço, nunca a frase inteira.

## Economia de tokens
- Use só os comandos do trilho: eles imprimem poucas linhas. Nunca rode `ebur128`, `npx remotion render` ou ffmpeg sem `-v error` direto.
- No máximo 3 imagens por vídeo: mapa do rosto, folha da prévia e, se precisar, a folha de um take duvidoso.
- Um vídeo por conversa. Ao entregar, sugira `/compact` ou uma conversa nova.

## Fora do trilho
- **Peça sob medida** (card, tela de motion, fechamento): escreva só em `src/extras.tsx`.
- **Complementos incluídos** (efeito sobre a pessoa, vinheta, logo animado, motion contínuo...): tabela em `references/complementos.md`. As regras desta skill valem por cima das deles.
- **Instalação e problemas:** `references/instalacao.md`.
