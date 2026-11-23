# Formato: motion (peça animada, sem filmagem)

**Quando:** não há filmagem de pessoa, ou ela é só um detalhe. O pedido é uma animação: vinheta, abertura, peça de produto, lançamento, logo animado, post animado, tipografia cinética ou explicativo.

**Caminho:** `novo --formato motion "<Cliente>" "<Título>" [arquivos da marca]` → produzir com o complemento → `entregar <arquivo.mp4> --complemento <nome>`

O `editor.py` só cria a pasta e registra a entrega. A produção é feita pelo complemento certo, que já vem no pacote.

## Qual complemento usar
| Pedido | Complemento | Por quê |
|---|---|---|
| Peça a partir de uma frase ou brief, sem referência fechada | `remotion-director` | Propõe 3 direções, faz as prévias, critica e renderiza. É o melhor "diretor" para motion em geral |
| Lançamento de produto, UI, app, com forma contínua e cortes na batida | `product-launch-motion` | Uma forma que nunca corta, molas, motion blur real e ritmo da música |
| Peça de marca que precisa de uma ideia própria (não genérica) | `motionmaxxing` | Acha a ideia da marca e usa timing medido de peças profissionais |
| Abertura, bumper, vinheta curta ou explicativo animado 9:16 | `bang-motion` | Estilos prontos de abertura e explicativo |
| Título ou frase animada, lyric video, tipografia cinética | `kinetic-typography` | Técnicas de revelação de texto no ritmo |
| Logo animado (a partir de PNG ou JPG) | `pixel2motion` | Vetoriza e anima seguindo os princípios da animação |
| Ícone, sticker ou microanimação (Lottie) | `text-to-lottie` | JSON Lottie leve para usar em cards |
| Comercial premium com crítica rigorosa | `business-motion-film` | Ciclo de crítica independente e régua de qualidade |

## Regras
- Leia o LEIAME do cliente antes: cores, fontes e logo de `03-marca/`. A peça segue a identidade, não o estilo padrão do complemento.
- Formato padrão: 1080x1920, 30 fps, MP4, salvo que o pedido diga outro.
- As regras do editor valem por cima das do complemento: margens seguras, nada de texto genérico, som abaixo de -14 LUFS e trilha só se aprovada.
- A peça fica na pasta que o `novo` criou. Depois, `entregar` copia para `entregas/`, mede o volume e registra no histórico.
- Motion com pessoa falando (texto e cards sobre um talking head)? Isso é talking-head ou comercial, não motion.
