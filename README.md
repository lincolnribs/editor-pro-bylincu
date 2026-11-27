<p align="center">
  <img src="assets/readme/banner.png" alt="Editor Pro by Lincu" width="100%">
</p>

<p align="center">
  <img src="assets/readme/selos.png" alt="V3.0 · Plugin do Claude Code · Feito com Remotion · Em português · Ferramentas grátis" width="100%">
</p>

---

## ⚡ Instale em 1 passo

<p align="center">
  <img src="assets/readme/instalar.png" alt="1 Copie o link deste repositório. 2 Cole no Claude e escreva instala isso. 3 Reinicie e mande o vídeo: edita esse vídeo." width="100%">
</p>

```
https://github.com/lincolnribs/editor-pro-bylincu
```

Não precisa de conta, login nem chave.

## 🎬 Como funciona

<p align="center">
  <img src="assets/readme/etapas.png" alt="1 Organiza: prepara os vídeos brutos. 2 Planeja: monta o roteiro e você aprova. 3 Edita: corta, limpa a voz e anima os textos. 4 Sonoriza: trilha e efeitos no tempo certo. 5 Entrega: revisa e exporta o vídeo pronto." width="100%">
</p>

Uma etapa por conversa. Se parar no meio, é só chamar `/editar` que ele continua de onde parou.

## ✨ O que deixa o vídeo premium

<p align="center">
  <img src="assets/readme/premium.png" alt="Voz limpa, texto animado no ritmo da fala, transições profissionais, animações suaves, cor corrigida cena a cena, cards e contadores prontos, efeitos sonoros no tempo certo, feito para Reels, revisão automática, roda no seu computador com ferramentas grátis, gasta pouco do seu plano e começa sozinho quando você manda o vídeo." width="100%">
</p>

**Nada sai no molde:** antes das cenas, o plano propõe 3 caminhos de direção para o vídeo e você escolhe. O texto combina 7 estilos (linha, karaokê, palavra, hierarquia, marca-texto, caixa, lateral) com 6 entradas, escolhidos pelo sentido de cada frase, e o histórico de cada cliente evita repetir o último vídeo.

## 🧩 Complementos (opcional)

<p align="center">
  <img src="assets/readme/complementos.png" alt="motionmaxxing (Apache-2.0), pixel2motion (MIT) e claude-video-effects (MIT)" width="100%">
</p>

Extras do plugin **Editor Pro Motion**. Só entram quando o vídeo pede: [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing), [pixel2motion](https://github.com/nolangz/pixel2motion) e [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects).

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
