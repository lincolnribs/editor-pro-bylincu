# Como preencher o roteiro.json (etapa 5)

O `editor.py roteiro` já preenche `fps`, `duracaoQuadros`, `base`, `trechos` (planos para o punch-in) e `legenda` (frases automáticas da fala). Você mexe só nos campos abaixo. Os tempos são em segundos na base: use os tempos do `base.txt`.

## tema
Cores e fonte do LEIAME do cliente (vídeos seguintes herdam o tema do anterior).
```json
"tema": {"fonte": "Montserrat", "peso": 800, "cor": "#FFFFFF", "destaque": "#FFD400", "tamanho": 92, "tamanhoLegenda": 46}
```
- Fonte do cliente: copie o arquivo para `public/fontes/` e adicione `"arquivoFonte": "fontes/NomeDaFonte.ttf"`, com `fonte` igual ao nome que você quer dar à família.
- Use `tamanho` de 80 a 110 para lettering e `tamanhoLegenda` de 40 a 52.

## faixaY
A linha (em px, num quadro de 1080x1920) onde ficam o lettering e a legenda. O mapa do rosto mostra 3 quadros reduzidos com uma grade vermelha a cada 100 px.
- Conte as linhas da grade até o queixo e até o topo da cabeça.
- Escolha a faixa abaixo do queixo (no peito ou na roupa), ou acima da cabeça se houver espaço.
- O template já força a faixa para dentro das margens seguras (de 220 a 1470).
- O padrão é 1240.

## lettering
O que dá ritmo ao vídeo. Coloque 1 lettering a cada 2 a 4 s, com as palavras-chave **ditas** naquele momento.
```json
{"inicio": 0.4, "fim": 2.1, "texto": "CORTE OS SILÊNCIOS", "destaque": ["SILÊNCIOS"]}
```
- Use de 2 a 4 palavras, em caixa alta se combinar com o cliente. Em `destaque` vão de 1 a 2 palavras, que saem na cor `tema.destaque`.
- `inicio` fica 1 a 2 quadros antes da palavra no `base.txt`, e `fim` fica antes do próximo lettering.
- O primeiro lettering começa antes de 1 s: é o gancho.
- A legenda automática some sozinha onde houver lettering (feito na etapa `montar`).

## broll
Imagem de apoio por cima da pessoa, nos momentos de argumento.
```json
{"inicio": 5.2, "fim": 7.8, "arquivo": "2026-11-23-reels/broll/obra.mp4", "desde": 0}
```
- Copie o arquivo para `public/<vídeo>/broll/`. Pode ser um take de b-roll do próprio cliente (os marcados "b-roll?" na etapa 1) ou um vídeo do Mixkit (`references/banco-de-midia.md`).
- Use de 1,5 a 3 s por b-roll, sem cobrir o gancho nem o fechamento. `desde` diz de onde começar o arquivo.

## sfx e trilha
- A etapa `montar` põe um whoosh em cada lettering e uma transição em cada b-roll, todos no mesmo volume.
- SFX manual: adicione `{"t": 3.2, "arquivo": "sfx/pop.wav", "volume": 0.3}`. Copie o arquivo para `public/sfx/`. Os automáticos têm `"auto": true` e são refeitos a cada `montar`.
- Trilha: use só `python editor.py trilha <arquivo>`, com volume de 0.07 a 0.11. O fade de entrada e saída é automático.

## punchIn
`true` alterna o zoom 1.0 ↔ 1.1 a cada corte, para esconder o pulo, com um drift leve dentro do plano. Desligue só se o cliente pedir.

## Peça sob medida (src/extras.tsx)
Só quando o pedido exigir algo que o roteiro não faz, como um card com ícone, uma tela de motion ou um fechamento com a logo. Escreva um componente com `<Sequence from={Math.round(t * 30)}>`, seguindo as mesmas regras de rosto e de margens.

## Cor e estabilização (antes da etapa 3, só se a folha mostrar problema)
Corrija o take em `public/<vídeo>/takes/NN.mp4` e salve por cima. Meça antes, com um quadro e as áreas claras. Nada de filtro igual para todos os takes.
```bash
# amarelado
ffmpeg -v error -y -i NN.mp4 -vf "colorchannelmixer=rr=0.975:bb=1.05,huesaturation=saturation=-0.4:colors=y" -c:a copy NN-cor.mp4
# escuro ou chapado
ffmpeg -v error -y -i NN.mp4 -vf "curves=all='0/0 0.25/0.29 0.5/0.55 1/1',eq=contrast=1.03:saturation=1.06" -c:a copy NN-cor.mp4
# b-roll tremido
ffmpeg -v error -i NN.mp4 -vf vidstabdetect=shakiness=6:result=t.trf -f null -
ffmpeg -v error -y -i NN.mp4 -vf "vidstabtransform=input=t.trf:smoothing=25:zoom=3" -c:a copy NN-estab.mp4
```
