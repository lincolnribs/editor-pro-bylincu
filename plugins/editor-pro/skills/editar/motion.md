# Motion: o que a gente não vê, mas sente

Medido em 2.390 movimentos de projetos profissionais (1080x1920, 30 fps). Já está nas constantes do template (`src/motion.ts`); use-as em toda peça sob medida.

## Relógio
- **U = 8 quadros (0,27 s)** é a unidade. Todo tempo é `U`, `U*2`, `U*3` ou `U/2`. Nada de duração solta.
- Entrada que atravessa a tela: 3U. Fade de opacidade: 5–10 f. Desfoque de entrada: 5–8 f. Revelação por máscara (só imagem/card): 20–30 f.
- Plano na timeline: mediana 38 f (≈1,3 s) nos trechos de motion.

## Passar do ponto e assentar (o "premium")
Nada chega e para seco. Correntes de passos de U (`corrente()` no template):
- Escala forte `POP` 0 → 1,25 → 0,90 → 1,05 → 1. Leve `POP_LEVE` 0,6 → 1,05 → 0,99 → 1.
- Posição: passa 3–5% do destino e volta em 2 passos. Entrada lateral: 1% depois do destino, volta 0,5%.
- Rotação `BALANCO` 3° → -2° → 1,5° → 0°. Formas (pílula, card) crescem de quase zero, passam ~3% e assentam (`FORMA`).
- **Respiração:** parado, o elemento oscila 0,99 ↔ 1,01 (`respira()`). Nunca 100% estático.

## Curvas
- Movimento principal (entrada, câmera, transição): **65/65 = `Easing.bezier(0.65, 0, 0.35, 1)`** (`EASE`).
- Passos curtos do assentamento: `bezier(0.4, 0, 0.6, 1)` (`SOFT`).
- Saídas aceleram até o fim (`SAIDA`), mais rápidas que a entrada (~U). Nunca saem freando.
- Linear só em: piscar, desfoque e máscara girando.
- Bounce, wiggle e afins conforme o estilo do cliente (perfil).

## Opacidade, desfoque, cascata
- Toda entrada e saída tem fade junto com o movimento: é o que esconde o "pulo".
- Grupo: itens com 1–2 f de diferença (`cascata()`); grupos grandes 5 ou 10 f. Nunca tudo no mesmo quadro.
- Contraste de velocidades dá fluidez: entrada rápida sobre câmera lenta.

## Texto
- Uma palavra por camada, no tempo da fala (`tempos` da transcrição). A linha desliza para continuar centrada.
- Sem máscara: entrada por blur + opacidade. Revelação por máscara só em imagem, card ou forma.
- Duas fontes: uma sans neutra + uma condensada de impacto (do kit do cliente). Pesos médio/semibold. Entrelinha quase zero.
- Letreiro não sai colado na última palavra: segura ~1 s depois dela, se nada vier logo depois.
- Contador: troca o valor a cada quadro (65/65) e segura o final por 3U.

## Câmera
- Punch-in alternado 1,0 ↔ 1,1 a cada corte (talking head) + drift lento por baixo.
- Câmera fluida: um movimento emenda no outro sem a velocidade chegar a zero. Nada de vários movimentos que começam e terminam parados.
- Motion pedido como "plano contínuo" (held shot, sem corte, câmera estilo After Effects): complemento `motionmaxxing` (`complementos.md`).

## Visual
- Um protagonista por vez. Fundo sólido e limpo quando é tela de motion; interface simulada (cursor, toggle, chip) quando explica produto.
- Efeitos (glow, raios de luz, 3D, lag) com moderação: 1 ou 2 por peça, nos destaques.

## Checklist de motion (entra na conferência)
- [ ] Tempos em múltiplos de U (ou U/2).
- [ ] Toda entrada passa do ponto e assenta; nenhuma para seco.
- [ ] Toda entrada e saída com fade.
- [ ] Parado respira.
- [ ] Grupos em cascata de 1–2 f.
- [ ] Texto palavra a palavra, no tempo da fala, sem máscara cortando acento.
- [ ] Sombra só onde precisa, no bloco, sem fantasma no blur.
- [ ] Quadro 0 já pronto (nada vazio no primeiro quadro); nenhum trecho congelado.
- [ ] Texto sem colisão na transição; SFX audível sem estourar.
