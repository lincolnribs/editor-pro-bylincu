# Formato: aftermovie (evento, bastidores, institucional sem fala)

**Quando:** vários clipes curtos sem fala importante (evento, festa, obra, bastidores, loja, viagem), montados no ritmo da música.

**Caminho:** `novo --formato aftermovie` → `trilha` (obrigatória) → seleção → `roteiro` → criação → `montar` → `preview` → `final`

## O que acontece
- `novo` converte os clipes (sem áudio) e gera **um catálogo**: uma imagem com um quadro de cada clipe, numerados da esquerda para a direita.
- `trilha` detecta o BPM e as batidas da música.
- `roteiro` corta um clipe a cada 2 ou 4 batidas (cerca de 1,5 a 2 s), com zoom leve alternado e um flash curto no corte. Coloca o título no início e o nome do cliente no fim.

## Onde você trabalha
1. **Trilha:** pergunte o clima (festa, emoção, corporativo) e escolha no Mixkit. Ela dita o filme.
2. **Seleção (`selecao.txt`):** abra o catálogo uma vez. Escreva uma linha por clipe, `NN [segundo de início]`, com o arco:
   - **abertura (1 a 3 clipes):** os mais fortes e abertos (local, multidão, logo do evento);
   - **meio:** varie plano aberto e detalhe, pessoas e ambiente, sem repetir o mesmo assunto em sequência;
   - **final (2 a 3 clipes):** emoção, aplauso, brinde, pôr do sol, e o nome da marca.
   - Use cada clipe uma vez. Tire os tremidos, escuros e sem ação.
3. **Criação:** textos do título e do fechamento no `lettering`. Ajuste a duração de um clipe só se precisar (`inicio` e `fim` em `clipes`).

## Para ficar excelente
- Corte sempre na batida. Nos momentos fortes da música, use clipes de mais ação.
- No máximo 2 letterings no filme: título e fechamento. Data e local entram no título, se o cliente quiser.
- Termine com fade e com a logo. Para uma logo animada, use `pixel2motion`.
