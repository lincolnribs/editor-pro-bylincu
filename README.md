<p align="center">
  <img src="assets/banner.svg" alt="Editor Pro by Lincu" width="100%">
</p>

<p align="center">
  <img alt="versão" src="https://img.shields.io/badge/versão-3.0-b8e351?labelColor=050607">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-b8e351?labelColor=050607">
  <img alt="Remotion" src="https://img.shields.io/badge/Remotion-4.0-b8e351?labelColor=050607">
  <img alt="idioma" src="https://img.shields.io/badge/idioma-português-b8e351?labelColor=050607">
  <img alt="custo" src="https://img.shields.io/badge/ferramentas-grátis%20e%20locais-b8e351?labelColor=050607">
</p>

<p align="center"><b>Você manda os brutos e pede “edita esse vídeo”. Ele entrega o Reels pronto, etapa por etapa.</b></p>

---

## ⚡ Instale em 1 passo

Cole o link no chat do Claude Code e escreva **instala isso**:

```
https://github.com/lincolnribs/editor-pro-bylincu
```

Depois, reinicie o Claude Code. Não precisa de conta, login nem chave.

## 🎬 Como funciona

Cinco etapas, uma por conversa. Cada uma termina num ponto salvo, e o `/editar` sabe sempre onde o vídeo parou.

| Etapa | O que acontece |
|---|---|
| **1 · preparar** | Converte os brutos para 1080x1920, faz uma folha de miniaturas por take, mede a cor e transcreve a fala. |
| **2 · plano** | Escolhe os melhores trechos e monta o plano cena a cena: texto, peças, transições, trilha e som. Você aprova pelo chat. |
| **3 · montar** | Limpa a voz, corta os silêncios, corrige a cor take a take e monta tudo no Remotion. Sai uma prévia. |
| **4 · som** | SFX nas ações da tela, trilha pela emoção da mensagem e volume medido (voz a -14 LUFS). |
| **5 · entregar** | Conferência completa, render final e o vídeo salvo na pasta do cliente. |

## ✨ O que deixa o vídeo premium

| | |
|---|---|
| 🎙️ **Voz limpa** | Tira eco, ruído e pancadas (DeepFilterNet, no seu computador) e corta os silêncios. |
| 🔤 **Texto cinético** | Palavra a palavra, no tempo da fala, com blur e sem cortar acento. Seis entradas: blur, pop, deslizar, onda, máquina de escrever e letras. |
| 🌀 **Motion medido** | Tempos em múltiplos de 8 quadros, curva 65/65 e tudo passando do ponto e assentando, como nos projetos profissionais. |
| 🎞️ **Transições sempre** | Blur, flash, light leak, zoom, chicote de câmera e obturador, escolhidos pelo contexto. |
| 🧩 **Peças prontas** | Pílula, card, contador e lista, além de fechos com logo, fade ou cartela. |
| 🔊 **Som no ponto** | Biblioteca de SFX própria, com o pico de cada som alinhado à ação. |
| ✅ **Conferência automática** | Margens do Reels, sem viúva, sem buraco entre cenas, sem texto colidindo, volume certo. |
| 📉 **Gasta pouco** | Um script faz as contas e devolve 5 a 10 linhas. Cada etapa cabe numa conversa curta. |
| ⚡ **Ativa sozinho** | Entra em ação num pedido de edição ou quando você só manda os arquivos de vídeo. |

## 🧩 Complementos (opcional)

O plugin **Editor Pro Motion** traz três ferramentas extras. Elas só entram quando o vídeo pede: no plano, o Editor Pro mostra as que combinam, e você escolhe por número ou responde “nenhum”.

| Para | Complemento | Licença |
|---|---|---|
| Motion em plano contínuo, sem corte, com câmera estilo After Effects | [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing) | Apache-2.0 |
| Logo do fechamento e ícones animados | [pixel2motion](https://github.com/nolangz/pixel2motion) | MIT |
| Flash só na pessoa, texto atrás da cabeça | [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects) | MIT |

<sub>Créditos em <a href="THIRD_PARTY_NOTICES.md">THIRD_PARTY_NOTICES.md</a>.</sub>

## ❓ Perguntas rápidas

<details>
<summary><b>Do que eu preciso no computador?</b></summary>

Node.js 18+, Python 3.10+, ffmpeg e o DeepFilterNet 0.5.6. Na primeira vez, o Claude confere o que falta e instala com a sua permissão. O Remotion é instalado uma vez só (cerca de 2 minutos).
</details>

<details>
<summary><b>Onde ficam os meus clientes e os vídeos?</b></summary>

No seu computador, fora do plugin. Na primeira vez o Editor Pro pergunta a pasta dos clientes. Cada cliente tem um `perfil-edicao.md` com o estilo dele (cores, fontes, ritmo, trilha), e cada vídeo tem uma pasta `_CLAUDE/` com tudo o que o Claude gerou.
</details>

<details>
<summary><b>Funciona no Windows?</b></summary>

Sim. Foi feito e testado no Windows, e também roda em macOS e Linux.
</details>

<details>
<summary><b>Posso usar em vídeos de clientes?</b></summary>

Sim. Tudo no pacote é grátis para uso comercial, complementos e efeitos sonoros incluídos. Só o Remotion tem uma regra: é grátis para uso individual e para empresas pequenas, e empresas maiores precisam de [licença](https://www.remotion.dev/license).
</details>

<details>
<summary><b>Como atualizo?</b></summary>

`/plugin marketplace update bylincu`
</details>

<details>
<summary><b>Instalação manual</b></summary>

```
/plugin marketplace add lincolnribs/editor-pro-bylincu
/plugin install editor-pro@bylincu
/plugin install editor-pro-motion@bylincu
```
No terminal, troque `/plugin` por `claude plugin`. O segundo é opcional. Para chamar direto: `/editar`.
</details>

<details>
<summary><b>Instruções para o Claude (instalação automática)</b></summary>

Se o usuário te mandou este link pedindo para instalar, explique cada passo em uma linha e peça permissão antes de baixar ou instalar programas.

1. Rode no terminal: `claude plugin marketplace add lincolnribs/editor-pro-bylincu` e `claude plugin install editor-pro@bylincu`. Pergunte se ele quer também os complementos (`claude plugin install editor-pro-motion@bylincu`).
2. Sem o comando `claude`: peça ao usuário para digitar no chat os mesmos comandos com `/plugin` no lugar de `claude plugin`.
3. Confira Node.js, Python, ffmpeg e DeepFilterNet. Instale só o que faltar, com permissão (no Windows, prefira `winget`).
4. Peça para reiniciar o Claude Code e depois mandar o vídeo com **edita esse vídeo**.
</details>

---

<sub>DeepFilterNet: MIT/Apache-2.0. Remotion: licença própria. Fluxo de etapas inspirado no <a href="https://github.com/LeiteZ/fluxo-de-edicao">fluxo-de-edicao</a> (MIT).</sub>
