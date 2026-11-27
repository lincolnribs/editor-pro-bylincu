# roteiro.json (campos)

Arquivo `_CLAUDE/edicao/roteiro.json`. Tempos em **segundos** na linha do tempo final. Arquivos com caminho relativo a `media/`. Tipos completos em `src/tipos.ts`.

**Textos não levam tempo:** escreva `texto`, `estilo`, `entrada`, `destaque`. O `ep.py render` (ou `ep.py tempos`) acha a frase na fala da base e preenche `inicio`, `tempos` e `fim`. Frase repetida: `"perto": <segundo>`.

```json
{
  "fps": 30, "largura": 1080, "altura": 1920, "duracao": 24.5,
  "tema": {"fonte": "Montserrat", "peso": 800, "cor": "#FFFFFF", "destaque": "#C6FF34",
           "fundo": "#111111", "corSobreFundo": "#FFFFFF", "tamanho": 96, "tamanhoLegenda": 48, "sombra": false,
           "arquivoFonte": "fontes/Cliente.ttf", "fonteImpacto": "Cliente Condensed", "arquivoFonteImpacto": "fontes/Cond.ttf"},
  "faixaY": 1240,
  "rosto": {"x": 50, "y": 33},
  "base": {"arquivo": "base.mp4", "trechos": [/* base.cortes.json */], "punchIn": true},
  "clipes": [{"arquivo": "reel/c01.mp4", "inicio": 0, "fim": 2.2, "entrada": "flash", "zoom": [1, 1.06], "mudo": true}],
  "broll": [{"arquivo": "midia/obra.mp4", "inicio": 5.2, "fim": 7.8, "desde": 1.0}],
  "transicoes": [{"t": 5.2, "tipo": "luz"}, {"t": 9.0, "tipo": "camera", "direcao": "esquerda"}],
  "textos": [{"texto": "Isso muda | tudo no seu negócio", "estilo": "hierarquia", "entrada": "blur", "destaque": ["tudo"]}],
  "pecas": [{"nome": "Contador", "inicio": 10.4, "fim": 13.6, "props": {"ate": 1200, "prefixo": "+", "y": 1100}}],
  "fecho": {"tipo": "logo", "inicio": 22.0, "logo": "marca/logo.png", "largura": 520},
  "acabamento": {"grao": 0.05, "vinheta": 0.2, "deriva": true},
  "sfx": [{"t": 5.2, "arquivo": "sfx/whoosh-01.mp3", "volume": 0.5, "pico": 0.18}],
  "trilha": {"arquivo": "trilha.mp3", "volume": 0.12}
}
```

- **tema:** do perfil do cliente. Fonte do cliente: copie para `media/fontes/` (Montserrat, Anton e Instrument Serif já vêm). Lettering 80–110 px, legenda 40–52.
- **faixaY:** linha da faixa de texto, abaixo do queixo ou acima da cabeça (mapa: `ep.py folha <take> --em <s> --grade`). O template mantém dentro das margens. **rosto:** centro do rosto em %, origem do punch-in.
- **base:** talking head/narrado: `base.mp4` + `trechos` = o conteúdo do `base.cortes.json`. `punchIn: false` para legenda ou narrado.
- **clipes:** montagem sem fala; `entrada` vira transição no início do clipe. Sem buraco entre clipes.
- **textos:** `estilo` (`linha` · `karaoke` · `palavra` · `hierarquia` · `marca-texto` · `caixa` · `lateral` + `lado`) e `entrada` vêm do plano, cena a cena: não preencha com padrão. `caixaAlta: true` quando o caminho pedir. `texto` com ` | ` para quebrar linha (sem viúva; em `palavra` cada ` | ` é um bloco que troca o anterior; em `hierarquia` o destaque fica gigante). `tempos` só se quiser forçar (o script preenche). `tipo`: `lettering` | `legenda` | `impacto`. `centro: true` centraliza na tela. `y` muda a faixa só daquele texto.
- **acabamento:** só se a direção pediu. `grao` 0–0,12, `vinheta` 0–0,4 (neutra), `deriva` true. `tema.adiantar`: quadros que o texto entra antes da fala (padrão 3). `destaqueFonte` por texto: `serifa` | `impacto`.
- **pecas:** `Fundo` {cor, brilho, grao} (tela de motion viva; primeiro da lista) · `Pilula` {texto, x, y, cor} · `Card` {titulo, texto, x, y, largura} · `Contador` {de, ate, prefixo, sufixo, y} · `Lista` {itens, tempos, x, y} · ou o nome de uma peça de `src/extras.tsx`. Início e fim em múltiplos de 4 quadros quando der (0,133 s).
- **sfx:** `pico` = segundos até o pico do som (`ep.py sfx`): o pico cai em `t`. Volume 0–1.
- **trilha:** volume medido (`ep.py medir trilha.mp3 --ganho <volume>` ≈ -24 LUFS sob voz a -14). Fade automático.
