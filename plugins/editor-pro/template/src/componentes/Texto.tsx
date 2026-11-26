// Texto cinético: uma palavra por camada, no tempo da fala. Sem máscara (nada corta acento ou letra).
// A linha desliza para continuar centrada a cada palavra que entra (larguras medidas no navegador).
// Entradas: blur (padrão) · pop · deslizar · onda · maquina · letras.
import React, { useLayoutEffect, useRef, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, interpolate, useCurrentFrame } from "remotion";
import { FAMILIA, IMPACTO, MARGEM_X, faixaSegura, q, r } from "../dados";
import { POP_LEVE, SAIDA, SOFT, U, blurIn, blurOut, clamp, corrente, fadeIn, fadeOut, respira } from "../motion";
import type { EntradaTexto, Texto as TTexto } from "../tipos";

const normal = (p: string) => p.replace(/[.,!?;:"“”()…]/g, "").toLocaleLowerCase("pt-BR");

type Visual = { css: React.CSSProperties; letra?: (i: number) => React.CSSProperties };

// Cada estilo devolve o estilo da palavra (ou de cada letra) no quadro local lf.
function animar(entrada: EntradaTexto, lf: number, n: number, lado: number): Visual {
  switch (entrada) {
    case "pop":
      return {
        css: { opacity: fadeIn(lf, 0, 5), filter: `blur(${blurIn(lf, 0, 5, 8)}px)`, transform: `scale(${corrente(lf, POP_LEVE)})` },
      };
    case "deslizar": {
      const passos = [U * 3, U, U];
      const x = (f: number) => corrente(f, [260 * lado, -6 * lado, 2 * lado, 0], passos);
      const vel = Math.abs(x(lf) - x(lf - 1));
      return {
        css: { opacity: fadeIn(lf, 0, 5), filter: `blur(${Math.min(12, vel * 0.25)}px)`, transform: `translateX(${x(lf)}px)` },
      };
    }
    case "onda":
      return {
        css: {},
        letra: (i) => {
          const l = lf - i;
          return {
            opacity: fadeIn(l, 0, 5),
            filter: `blur(${blurIn(l, 0, 5, 6)}px)`,
            transform: `translateY(${corrente(l, [34, -6, 2, 0], [U, U / 2, U / 2])}px)`,
          };
        },
      };
    case "maquina": {
      const passo = 1.3; // ~23 letras por segundo
      return {
        css: {},
        letra: (i) => {
          const l = lf - i * passo;
          return { opacity: interpolate(l, [0, 2], [0, 1], clamp), filter: `blur(${interpolate(l, [0, 2], [4, 0], clamp)}px)` };
        },
      };
    }
    case "letras":
      return {
        css: {},
        letra: (i) => {
          const l = lf - i * 2;
          return {
            opacity: fadeIn(l, 0, U),
            filter: `blur(${blurIn(l, 0, U, 10)}px)`,
            transform: `translateY(${corrente(l, [-40, 4, -1, 0])}px)`,
          };
        },
      };
    case "blur":
    default:
      return {
        css: {
          opacity: fadeIn(lf, 0, U),
          filter: `blur(${blurIn(lf, 0, U, 12)}px)`,
          transform: `translateY(${corrente(lf, [22, -3, 1, 0])}px)`,
        },
      };
  }
}

export const Texto: React.FC<TTexto & { dur: number }> = (t) => {
  const frame = useCurrentFrame();
  const entrada = t.entrada ?? "blur";
  const tipo = t.tipo ?? "lettering";
  const impacto = tipo === "impacto";
  const legenda = tipo === "legenda";
  const tamanho = t.tamanho ?? (legenda ? r.tema.tamanhoLegenda : impacto ? Math.round(r.tema.tamanho * 1.35) : r.tema.tamanho);
  const fonte: React.CSSProperties = {
    fontFamily: impacto ? IMPACTO : FAMILIA,
    fontWeight: impacto ? 400 : legenda ? 700 : r.tema.peso,
    fontSize: tamanho,
    letterSpacing: impacto ? "0.01em" : "-0.02em",
    lineHeight: legenda ? 1.05 : 0.98, // entrelinha quase zero: linhas coladas
    whiteSpace: "pre",
  };
  const gap = tamanho * 0.25;

  const linhas = t.texto.split("|").map((l) => l.trim().split(/\s+/).filter(Boolean));
  const palavras = linhas.flatMap((ps, linha) => ps.map((p) => ({ p, linha })));
  let inicioDe = palavras.map((_, k) => (t.tempos?.[k] !== undefined ? q(t.tempos[k] - t.inicio) : k * (U / 2)));
  if (entrada === "maquina" && !t.tempos) {
    // máquina de escrever: uma palavra depois da outra (~23 letras por segundo)
    let acc = 0;
    inicioDe = palavras.map((w) => {
      const ini = Math.round(acc);
      acc += (w.p.length + 1) * 1.3;
      return ini;
    });
  }
  if (entrada === "deslizar") {
    // deslizar: a linha entra inteira (cada linha de um lado), no tempo da 1ª palavra dela
    inicioDe = palavras.map((w) => inicioDe[palavras.findIndex((o) => o.linha === w.linha)]);
  }
  const fimEntrada = Math.max(...inicioDe) + U * 2;
  const alvo = new Set((t.destaque ?? []).map(normal));

  // Medir a largura de cada palavra depois que as fontes carregam.
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

  const saida = fadeOut(frame, t.dur, U);
  const sobe = interpolate(frame, [t.dur - U, t.dur], [0, -12], { ...clamp, easing: SAIDA });
  const sombra = r.tema.sombra ? interpolate(frame, [fimEntrada, fimEntrada + U], [0, 0.45], clamp) : 0;
  const filtros = [
    blurOut(frame, t.dur, U, 10) > 0 ? `blur(${blurOut(frame, t.dur, U, 10)}px)` : "",
    sombra > 0 ? `drop-shadow(0 4px 14px rgba(0,0,0,${sombra.toFixed(3)}))` : "", // no bloco, nunca palavra a palavra
  ].join(" ").trim();

  const altura = linhas.length * tamanho * (legenda ? 1.05 : 0.98);
  const posicao: React.CSSProperties = t.centro
    ? { top: (r.altura - altura) / 2 }
    : { top: faixaSegura(t.y ?? r.faixaY, altura) };

  let k = -1;
  return (
    <AbsoluteFill>
      <div ref={medidor} style={{ ...fonte, position: "absolute", visibility: "hidden", top: 0, left: 0 }}>
        {palavras.map((w, i) => (
          <span key={i} style={{ display: "inline-block" }}>{w.p}</span>
        ))}
      </div>
      {larg ? (
        <div
          style={{
            ...fonte, position: "absolute", left: MARGEM_X, right: MARGEM_X, ...posicao,
            color: t.cor ?? r.tema.cor, opacity: saida, filter: filtros || undefined,
            transform: `translateY(${sobe}px) scale(${respira(frame, fimEntrada)})`,
          }}
        >
          {linhas.map((ps, li) => {
            // Cada palavra ocupa a largura inteira assim que entra (nunca sobrepõe a vizinha). A linha recentraliza
            // deslizando: compensa metade da largura nova e solta em U quadros (SOFT).
            const k0 = k + 1;
            let desloca = 0;
            ps.forEach((_, pi) => {
              const lf = frame - inicioDe[k0 + pi];
              if (lf >= 0 && entrada !== "deslizar") desloca += ((larg[k0 + pi] + (pi > 0 ? gap : 0)) / 2) * (1 - interpolate(lf, [0, U], [0, 1], { ...clamp, easing: SOFT }));
            });
            return (
            <div key={li} style={{ display: "flex", justifyContent: "center", transform: `translateX(${desloca}px)` }}>
              {ps.map((p, pi) => {
                k += 1;
                const lf = frame - inicioDe[k];
                const v = animar(entrada, lf, p.length, li % 2 === 0 ? 1 : -1);
                const w = larg[k] + (pi > 0 ? gap : 0);
                const cor = alvo.has(normal(p)) ? r.tema.destaque : undefined;
                return (
                  <div key={pi} style={{ width: lf >= 0 ? w : 0, flex: "none", boxSizing: "border-box", paddingLeft: pi > 0 ? gap : 0 }}>
                    <span style={{ display: "inline-block", color: cor, ...(lf < 0 ? { opacity: 0 } : v.css) }}>
                      {v.letra
                        ? p.split("").map((c, i) => (
                            <span key={i} style={{ display: "inline-block", ...(lf < 0 ? { opacity: 0 } : v.letra!(i)) }}>{c}</span>
                          ))
                        : p}
                    </span>
                  </div>
                );
              })}
            </div>
            );
          })}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
