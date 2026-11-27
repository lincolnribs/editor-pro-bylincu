// Transições com nome fixo. Escolher pelo contexto; não repetir a mesma em sequência.
// corte · flash · blur · luz (light leak) · obturador · zoom (zoom-in) · camera (chicote, speed ramp)
// zoom e camera mexem na imagem (ver `cameraDasTransicoes`); as outras são camadas por cima.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "raea";
import { q, r } from "../dados";
import { CHEGADA, EASE, SAIDA, U, clamp } from "../motion";
import type { Transicao } from "../tipos";

const DIR: Record<string, [number, number]> = { esquerda: [-1, 0], direita: [1, 0], cima: [0, -1], baixo: [0, 1] };

/** Escala, deslocamento e desfoque que as transições zoom/camera aplicam na imagem no quadro f. */
export function cameraDasTransicoes(f: number) {
  let escala = 1, x = 0, y = 0, blur = 0;
  for (const tr of r.transicoes ?? []) {
    const t = q(tr.t);
    if (f < t - U || f > t + U * 2) continue;
    const forca = tr.forca ?? 1;
    if (tr.tipo === "zoom") {
      escala *= f < t
        ? interpolate(f, [t - U, t], [1, 1 + 0.25 * forca], { ...clamp, easing: SAIDA }) // acelera para dentro
        : interpolate(f, [t, t + U * 2], [1 + 0.12 * forca, 1], { ...clamp, easing: CHEGADA }); // chega e assenta
      blur = Math.max(blur, interpolate(f, [t - 4, t, t + 4], [0, 8 * forca, 0], clamp));
    }
    if (tr.tipo === "camera") {
      const [dx, dy] = DIR[tr.direcao ?? "esquerda"];
      const d = f < t
        ? interpolate(f, [t - U, t], [0, 320 * forca], { ...clamp, easing: SAIDA }) // sai acelerando
        : interpolate(f, [t, t + U * 2], [-260 * forca, 0], { ...clamp, easing: CHEGADA }); // chega do outro lado e freia
      x += d * dx;
      y += d * dy;
      escala *= 1 + (2 * Math.abs(d)) / r.largura + 0.02; // aproxima junto: a borda do quadro nunca aparece
      blur = Math.max(blur, interpolate(f, [t - U / 2, t, t + U / 2], [0, 14 * forca, 0], clamp));
    }
  }
  return { escala, x, y, blur };
}

const Camada: React.FC<{ tr: Transicao }> = ({ tr }) => {
  const f = useCurrentFrame();
  const t = q(tr.t);
  const forca = tr.forca ?? 1;
  if (f < t - U || f > t + U * 2) return null;
  switch (tr.tipo) {
    case "flash":
      return <AbsoluteFill style={{ backgroundColor: "white", opacity: interpolate(f, [t - 2, t, t + U], [0, 0.7 * forca, 0], clamp) }} />;
    case "blur": {
      const b = interpolate(f, [t - U, t, t + U], [0, 18 * forca, 0], { ...clamp, easing: EASE });
      return <AbsoluteFill style={{ backdropFilter: `blur(${b}px)` }} />;
    }
    case "luz": {
      // light leak: manchas quentes cruzando a tela, em "screen" (clareia, não pinta o vídeo)
      const o = interpolate(f, [t - U, t, t + U * 2], [0, 0.65 * forca, 0], { ...clamp, easing: EASE });
      const p = interpolate(f, [t - U, t + U * 2], [-30, 130], clamp);
      return (
        <AbsoluteFill style={{ mixBlendMode: "screen", opacity: o,
          background: `radial-gradient(60% 45% at ${p}% 40%, rgba(255,190,120,0.95), rgba(255,120,60,0.5) 45%, transparent 75%),
                       radial-gradient(40% 35% at ${p - 25}% 70%, rgba(255,235,200,0.8), transparent 70%)` }} />
      );
    }
    case "obturador": {
      const h = f < t
        ? interpolate(f, [t - U, t], [0, 50], { ...clamp, easing: SAIDA })
        : interpolate(f, [t, t + U], [50, 0], { ...clamp, easing: CHEGADA });
      return (
        <AbsoluteFill>
          <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: `${h}%`, background: "black" }} />
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${h}%`, background: "black" }} />
        </AbsoluteFill>
      );
    }
    default:
      return null; // corte, zoom e camera não têm camada
  }
};

export const CamadasDeTransicao: React.FC = () => (
  <>
    {(r.transicoes ?? []).map((tr, k) => (
      <Camada key={k} tr={tr} />
    ))}
  </>
);
