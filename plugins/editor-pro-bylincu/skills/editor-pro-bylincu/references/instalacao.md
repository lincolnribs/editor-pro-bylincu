# Instalação (primeira vez)

Confira cada item antes de editar. Se algo faltar, diga ao usuário o que é e peça para instalar (ou instale com a permissão dele).

## 1. Programas
| Item | Para quê | Como conferir |
|---|---|---|
| Node.js 18+ | Remotion | `node -v` |
| Python 3.10+ | scripts desta skill | `python --version` (no Windows use `python`, não `python3`) |
| ffmpeg + ffprobe no PATH | conversão, cor, volume, contact sheet | `ffmpeg -version` |

## 2. Plugins e skills do Claude Code
- **Remotion** (obrigatório): plugin `remotion` do marketplace oficial do Remotion. Traz `remotion-best-practices`, `remotion-create`, `remotion-captions`, `remotion-render` e outras.
- **HyperFrames**: não instale o plugin só por causa do recorte. Ele adiciona cerca de 20 skills à lista que entra em toda conversa. O recorte de pessoa roda direto com `npx hyperframes remove-background` (lento em CPU: recorte só os trechos necessários).
- **Economia:** desative plugins e conectores (MCP) que você não usa. A lista de skills e ferramentas de todos eles entra no contexto de toda conversa.
- **assetseeker** (recomendado): skill de busca de mídia grátis (Mixkit, Pexels, Pixabay, Freesound, Iconify, Google Fonts). Instale pela skill `find-skills` ou pelo marketplace de skills.

> Licença do Remotion: grátis para uso individual e empresas pequenas; empresas maiores precisam de licença de empresa (ver remotion.dev/license). Avise o usuário se ele estiver numa equipe grande.

## 3. DeepFilterNet (limpeza de voz)
1. Baixe o executável oficial da release **0.5.6** em `github.com/Rikorose/DeepFilterNet/releases` (arquivo `deep-filter-0.5.6-x86_64-pc-windows-msvc.exe` no Windows; há versões para macOS e Linux). Peça permissão antes de baixar.
2. Salve como `~/tools/deepfilter/deep-filter.exe` (Windows) ou `~/tools/deepfilter/deep-filter` (macOS/Linux, com `chmod +x`), **ou** coloque no PATH com o nome `deep-filter`, **ou** defina a variável `DEEP_FILTER` com o caminho completo.
3. Teste: `python scripts/limpar_voz.py -h`.

Não use `pip install deepfilternet`: costuma quebrar com Python novo (dependência antiga do PyTorch). O executável não precisa de Python.

## 4. Transcrição (automática)
O projeto modelo traz `scripts/transcrever.mjs`, que usa o whisper.cpp local (grátis). Na primeira transcrição, ele baixa o programa e o modelo `large-v3-turbo` (cerca de 1,6 GB) para `~/.cache/editor-pro/whisper`, uma vez só. Em máquina fraca, use `--modelo small`. No macOS e no Linux, o whisper.cpp é compilado na primeira vez, o que exige `make` e um compilador C.

## 5. Ajustes de Windows
- Caminho longo (mais de 260 caracteres) quebra comandos e o render: mantenha o estúdio num caminho curto (o padrão `~/Videos/Edicao` serve). Se o render falhar por isso, aponte o Chrome headless para uma pasta curta em `remotion.config.ts` (a linha já está comentada no modelo).
- Em listas de takes, use caminhos `C:/...` (não `/c/...`). O `editor.py` já converte os caminhos.
