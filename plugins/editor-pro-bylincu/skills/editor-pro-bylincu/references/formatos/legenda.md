# Formato: legenda (vídeo já editado)

**Quando:** o vídeo chegou pronto (com cortes, b-roll, card final, às vezes rodapé), e o pedido é só legendar ou melhorar o áudio.

**Caminho:** `novo --formato legenda` → `voz` → `roteiro` → revisar legenda → `montar` → `final`

## O que acontece
- `voz` limpa a voz **sem cortar nada**, então a duração e a edição ficam iguais. Em seguida, transcreve.
- `roteiro` cria a legenda automática, desliga o punch-in e gera o mapa do rosto.

## Onde você trabalha
- **Revisar legenda:** corrija nomes, marcas e termos técnicos. Frases curtas, de 3 a 5 palavras, sem pontuação no fim.
- Com o mapa do rosto, ajuste a `faixaY` para fora do rosto e acima de rodapés ou cards já existentes.

## Cuidados
- **Música já mixada no vídeo:** a limpeza de voz estraga a trilha. Nesse caso, pule a limpeza: escreva o `takes.txt` com o vídeo inteiro e avise o usuário, ou peça a versão sem música.
- Não aplique zoom nem corte em vídeo que já vem com rodapé ou card final.
