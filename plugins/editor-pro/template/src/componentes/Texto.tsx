// Texto cinético: uma palavra por camada, no tempo da fala. Sem máscara (nada corta acento ou letra).
// Dois eixos que se combinam: ESTILO (o desenho na tela) × ENTRADA (a animação de cada palavra).
// Estilos: linha · karaoke · palavra · hierarquia · marca-texto · caixa · lateral
// Entradas: blur · pop · deslizar · onda · maquina · letras
import React, { useLayoutEffect, useRef, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, interpolate, useCurrentFrame } from "remotion";
import { FAMILIA, IMPACTO, MARGEM_X, faixaSegura, q, r } from "../dados";
import { FORMA, POP_LEVE, SAIDA, SOFT, U, blurIn, blurOut, clamp, corrente, fadeIn, fadeOut, respira } from "../motion";
import type { EntradaTexto, Texto as TTexto } from "../tipos";

const normal = (p: string) => p.replace(/[.,!?;:"“”()…]/g, "").toLocaleLowerCase("pt-BR");

type Visual = { css: React.CSSProperties; letra?: (i: number) => React.CSSProperties };

// Cada entrada devolve o estilo da palavra (ou de cada letra) no quadro local lf.
function animar(entrada: EntradaTexto, lf: number, n: number, lado: number): Visual {
  switch (entrada) {
    case "pop":
      return { css: { opacity: fadeIn(lf, 0, 5), filter: `blur(${blurIn(lf, 0, 5, 8)}px)`, transform: `scale(${corrente(lf, POP_LEVE)})` } };
    case "deslizar": {
      const passos = [U * 3, U, U];
      const x = (f: number) => corrente(f, [260 * lado, -6 * lado, 2 * lado, 0], passos);
      const vel = Math.abs(x(lf) - x(lf - 1));
      return { css: { opacity: fadeIn(lf, 0, 5), filter: `blur(${Math.min(12, vel * 0.25)}px)`, transform: `translateX(${x(lf)}px)` } };
    }
    case "onda":
      return {
        css: {},
        letra: (i) => {
          const l = lf - i;
          return { opacity: fadeIn(l, 0, 5), filter: `blur(${blurIn(l, 0, 5, 6)}px)`, transform: `translateY(${corrente(l, [34, -6, 2, 0], [U, U / 2, U / 2])}px)` };
        },
      };
    case "maquina":
      return {
        css: {},
        letra: (i) => {
          const l = lf - i * 1.3; // ~23 letras por segundo
          return { opacity: interpolate(l, [0, 2], [0, 1], clamp), filter: `blur(${interpolate(l, [0, 2], [4, 0], clamp)}px)` };
        },
      };
    case "letras":
      return {
        css: {},
        letra: (i) => {
          const l = lf - i * 2;
          return { opacity: fadeIn(l, 0, U), filter: `blur(${blurIn(l, 0, U, 10)}px)`, transform: `translateY(${corrente(l, [-40, 4, -1, 0])}px)` };
        },
      };
    case "blur":
    default:
      return { css: { opacity: fadeIn(lf, 0, U), filter: `blur(${blurIn(lf, 0, U, 12)}px)`, transform: `translateY(${corrente(lf, [22, -3, 1, 0])}px)` } };
  }
}

type Pal = { p: string; linha: number; destaque: boolean };

export const Texto: React.FC<TTexto & { dur: number }> = (t) => {
  const frame = useCurrentFrame();
  const entrada = t.entrada ?? "blur";
  const estilo = t.estilo ?? "linha";
  const tipo = t.tipo ?? "lettering";
  const legenda = tipo === "legenda";
  const impacto = tipo === "impacto";
  const base = t.tamanho ?? (legenda ? r.tema.tamanhoLegenda : impacto ? Math.round(r.tema.tamanho * 1.35) : r.tema.tamanho);
  const corBase = t.cor ?? r.tema.cor;
  const corSobre = r.tema.corSobreDestaque ?? "#050607";
  const alvo = new Set((t.destaque ?? []).map(normal));

  // Linhas e palavras. No estilo "palavra" sem " | ", cada palavra é um bloco.
  let linhas = t.texto.split("|").map((l) => l.trim().split(/\s+/).filter(Boolean));
  if (estilo === "palavra" && linhas.length === 1) linhas = linhas[0].map((p) => [p]);
  const palavras: Pal[] = linhas.flatMap((ps, linha) => ps.map((p) => ({ p, linha, destaque: alvo.has(normal(p)) })));

  // Fonte de cada palavra (a hierarquia mistura tamanhos e famílias).
  const fonteDe = (w: Pal): React.CSSProperties => {
    const caixaAlta = t.caixaAlta ? "uppercase" : "none";
    if (estilo === "hierarquia") {
      return w.destaque
        ? { fontFamily: IMPACTO, fontWeight: 400, fontSize: Math.round(base * 1.9), letterSpacing: "0.005em", textTransform: "uppercase" }
        : { fontFamily: FAMILIA, fontWeight: 600, fontSize: Math.round(base * 0.62), letterSpacing: "-0.01em", textTransform: caixaAlta };
    }
    const tam = estilo === "palavra" ? Math.round(base * 1.45) : base;
    return {
      fontFamily: impacto ? IMPACTO : FAMILIA,
      fontWeight: impacto ? 400 : legenda ? 700 : r.tema.peso,
      fontSize: tam,
      letterSpacing: impacto ? "0.01em" : "-0.02em",
      textTransform: caixaAlta,
    };
  };
  const tamDe = (w: Pal) => fonteDe(w).fontSize as number;
  const lh = legenda ? 1.05 : 0.98; // entrelinha quase zero

  // Tempo de entrada de cada palavra (quadro local).
  let inicioDe = palavras.map((_, k) => (t.tempos?.[k] !== undefined ? q(t.tempos[k] - t.inicio) : k * (U / 2)));
  if (entrada === "maquina" && !t.tempos) {
    let acc = 0;
    inicioDe = palavras.map((w) => {
      const ini = Math.round(acc);
      acc += (w.p.length + 1) * 1.3;
      return ini;
    });
  }
  if (entrada === "deslizar") inicioDe = palavras.map((w) => inicioDe[palavras.findIndex((o) => o.linha === w.linha)]);
  const fimEntrada = Math.max(...inicioDe) + U * 2;

  // Medir a largura de cada palavra (com a fonte dela) depois que as fontes carregam.
  const medidor = useRef<HTMLDivElement>(null);
  const [larg, setLarg] = useState<number[] | null>(null);
  const [handle] = useState(() => delayRender("medindo o texto"));
  useLayoutEffect(() => {
    let feito = false;
    const fim = () => {
      if (!feito) {
        feito = true;
        continueRender(handle);
      }
    };
    document.fonts.ready.then(() => {
      if (medidor.current) setLarg(Array.from(medidor.current.children).map((c) => (c as HTMLElement).offsetWidth));
      fim();
    });
    return fim;
  }, [handle]);

  // Saída do bloco: rápida, acelerando.
  const saida = fadeOut(frame, t.dur, U);
  const sobe = interpolate(frame, [t.dur - U, t.dur], [0, -12], { ...clamp, easing: SAIDA });
  const sombra = r.tema.sombra && estilo !== "caixa" ? interpolate(frame, [fimEntrada, fimEntrada + U], [0, 0.45], clamp) : 0;
  const filtros = [
    blurOut(frame, t.dur, U, 10) > 0 ? `blur(${blurOut(frame, t.dur, U, 10)}px)` : "",
    sombra > 0 ? `drop-shadow(0 4px 14px rgba(0,0,0,${sombra.toFixed(3)}))` : "", // no bloco, nunca palavra a palavra
  ].join(" ").trim();

  // Alinhamento: 0 = esquerda, 0,5 = centro, 1 = direita.
  const lateral = estilo === "lateral";
  const alinha = lateral ? (t.lado === "direita" ? 1 : 0) : 0.5;
  const justify = alinha === 0 ? "flex-start" : alinha === 1 ? "flex-end" : "center";
  const larguraFixa = estilo === "karaoke" || estilo === "caixa"; // a frase ocupa o lugar desde o início

  const alturaLinha = (ps: number[]) => Math.max(...ps.map((k) => tamDe(palavras[k]))) * lh;
  const indicesPorLinha = linhas.map((_, li) => palavras.map((w, k) => (w.linha === li ? k : -1)).filter((k) => k >= 0));
  const altura =
    estilo === "palavra" ? Math.max(...indicesPorLinha.map(alturaLinha)) : indicesPorLinha.reduce((s, ps) => s + alturaLinha(ps), 0);
  const top = t.centro ? (r.altura - altura) / 2 : faixaSegura(t.y ?? r.faixaY, altura);

  const palavra = (k: number, pi: number, li: number, w: number) => {
    const pal = palavras[k];
    const lf = frame - inicioDe[k];
    const gap = tamDe(pal) * 0.24;
    const largura = larguraFixa || lf >= 0 ? w + (pi > 0 ? gap : 0) : 0;
    let css: React.CSSProperties;
    let letra: Visual["letra"];
    let cor = pal.destaque ? r.tema.destaque : undefined;
    let barra: React.ReactNode = null;
    if (estilo === "karaoke") {
      // apagada desde o início; acende quando é dita
      const aceso = interpolate(lf, [0, U / 2], [0, 1], { ...clamp, easing: SOFT });
      css = { opacity: 0.32 + 0.68 * aceso, transform: `scale(${lf >= 0 ? corrente(lf, [1, 1.05, 0.99, 1], U / 2) : 1})` };
      cor = aceso > 0.5 && pal.destaque ? r.tema.destaque : undefined;
    } else {
      const v = animar(entrada, lf, pal.p.length, li % 2 === 0 ? 1 : -1);
      css = lf < 0 ? { opacity: 0 } : v.css;
      letra = v.letra;
    }
    if (estilo === "marca-texto" && pal.destaque && lf >= 0) {
      const s = corrente(lf - U / 2, FORMA);
      barra = (
        <span style={{ position: "absolute", left: "-0.12em", right: "-0.12em", top: "14%", bottom: "4%", background: r.tema.destaque,
          borderRadius: "0.12em", transform: `scaleX(${lf < U / 2 ? 0 : s})`, transformOrigin: "left center", zIndex: 0 }} />
      );
      cor = lf >= U ? corSobre : r.tema.destaque;
    }
    return (
      <div key={k} style={{ width: largura, flex: "none", boxSizing: "border-box", paddingLeft: pi > 0 ? gap : 0 }}>
        <span style={{ position: "relative", display: "inline-block", whiteSpace: "pre", ...fonteDe(pal), lineHeight: lh, color: cor, ...css }}>
          {barra}
          <span style={{ position: "relative", zIndex: 1 }}>
            {letra && !(lf < 0)
              ? pal.p.split("").map((c, i) => <span key={i} style={{ display: "inline-block", ...letra!(i) }}>{c}</span>)
              : pal.p}
          </span>
        </span>
      </div>
    );
  };

  const linha = (li: number) => {
    const ps = indicesPorLinha[li];
    // A linha compensa o pulo de cada palavra nova e solta em U quadros (centro: metade; direita: inteira).
    let desloca = 0;
    if (!larguraFixa && entrada !== "deslizar") {
      ps.forEach((k, pi) => {
        const lf = frame - inicioDe[k];
        const w = larg![k] + (pi > 0 ? tamDe(palavras[k]) * 0.24 : 0);
        if (lf >= 0) desloca += w * alinha * (1 - interpolate(lf, [0, U], [0, 1], { ...clamp, easing: SOFT }));
      });
    }
    return (
      <div key={li} style={{ display: "flex", justifyContent: justify, alignItems: "baseline", height: alturaLinha(ps), transform: `translateX(${desloca}px)` }}>
        {ps.map((k, pi) => palavra(k, pi, li, larg![k]))}
      </div>
    );
  };

  // Estilo "palavra": um bloco por vez, cada um sai (rápido) quando o próximo entra.
  const blocos = () =>
    linhas.map((_, li) => {
      const ini = inicioDe[indicesPorLinha[li][0]];
      const prox = li + 1 < linhas.length ? inicioDe[indicesPorLinha[li + 1][0]] : t.dur + U;
      if (frame < ini || frame >= prox) return null;
      const sai = li + 1 < linhas.length ? interpolate(frame, [prox - U / 2, prox], [0, 1], { ...clamp, easing: SAIDA }) : 0;
      return (
        <div key={li} style={{ position: "absolute", left: 0, right: 0, top: 0, opacity: 1 - sai, filter: sai > 0 ? `blur(${sai * 8}px)` : undefined,
          transform: `scale(${1 - sai * 0.08})` }}>
          {linha(li)}
        </div>
      );
    });

  const caixa = estilo === "caixa";
  const fundoCaixa = (
    <div style={{ position: "absolute", inset: 0, background: r.tema.fundo ?? "#111", borderRadius: base * 0.3,
      opacity: fadeIn(frame, 0, U / 2), transform: `scaleX(${corrente(frame, FORMA)})` }} />
  );

  return (
    <AbsoluteFill>
      <div ref={medidor} style={{ position: "absolute", visibility: "hidden", top: 0, left: 0, whiteSpace: "pre" }}>
        {palavras.map((w, i) => <span key={i} style={{ display: "inline-block", ...fonteDe(w) }}>{w.p}</span>)}
      </div>
      {larg ? (
        <div
          style={{
            position: "absolute", top,
            left: lateral && alinha === 1 ? r.largura * 0.3 : MARGEM_X,
            right: lateral && alinha === 0 ? r.largura * 0.3 : MARGEM_X,
            display: "flex", justifyContent: justify,
            color: corBase, opacity: saida, filter: filtros || undefined,
            transform: `translateY(${sobe}px) scale(${respira(frame, fimEntrada)})`,
            transformOrigin: alinha === 0 ? "left center" : alinha === 1 ? "right center" : "center",
          }}
        >
          <div style={{ position: "relative", padding: caixa ? `${base * 0.28}px ${base * 0.4}px` : 0, color: caixa ? r.tema.corSobreFundo ?? corBase : undefined,
            width: estilo === "palavra" ? "100%" : undefined, height: estilo === "palavra" ? altura : undefined }}>
            {caixa ? fundoCaixa : null}
            <div style={{ position: "relative" }}>
              {estilo === "palavra" ? blocos() : linhas.map((_, li) => linha(li))}
            </div>
          </div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
