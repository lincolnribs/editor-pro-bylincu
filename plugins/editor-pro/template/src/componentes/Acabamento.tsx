// Acabamento de imagem: o que tira a "cara de HTML animado". Escolhido pela direção, nunca ligado por padrão.
// grão (ruído de filme animado) · vinheta (bordas neutras) · deriva (a câmera nunca fica parada, em Video.tsx)
// + peça Fundo: fundo sólido vivo para telas de motion (brilho lento + grão).
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "raea";
import { r } from "../dados";
import { U, clamp, fadeIn, fadeOut } from "../motion";

/** Ruído de filme: semente nova a cada 2 quadros, por cima em "overlay" (clareia e escurece, não pinta). */
export const Grao: React.FC<{ forca: number }> = ({ forca }) => {
  const f = useCurrentFrame();
  const semente = Math.floor(f / 2) % 97;
  return (
    <AbsoluteFill style={{ mixBlendMode: "overlay", opacity: forca, pointerEvents: "none" }}>
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <filter id={`grao${semente}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={semente} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grao${semente})`} />
      </svg>
    </AbsoluteFill>
  );
};

export const Vinheta: React.FC<{ forca: number }> = ({ forca }) => (
  <AbsoluteFill style={{ pointerEvents: "none", background: `radial-gradient(120% 85% at 50% 45%, transparent 55%, rgba(0,0,0,${forca}) 100%)` }} />
);

/** Deriva da câmera: micro zoom e pan contínuos (sem parar, sem voltar). */
export function deriva(f: number, total: number) {
  if (!r.acabamento?.deriva) return { escala: 1, x: 0, y: 0 };
  const p = f / Math.max(1, total);
  return { escala: 1.02 + 0.03 * p, x: Math.sin(f / 90) * 6, y: Math.cos(f / 120) * 4 };
}

export const CamadasDeAcabamento: React.FC = () => {
  const a = r.acabamento;
  if (!a) return null;
  return (
    <>
      {a.vinheta ? <Vinheta forca={Math.min(0.4, a.vinheta)} /> : null}
      {a.grao ? <Grao forca={Math.min(0.12, a.grao)} /> : null}
    </>
  );
};

/** Peça Fundo: cor sólida com um brilho que anda devagar e grão. Use antes das outras peças numa tela de motion. */
export const Fundo: React.FC<{ dur: number; cor?: string; brilho?: string; grao?: number }> = ({ dur, cor, brilho, grao }) => {
  const f = useCurrentFrame();
  const o = Math.min(fadeIn(f, 0, U), fadeOut(f, dur, U));
  const x = interpolate(f, [0, dur], [70, 30], clamp);
  const y = 30 + Math.sin(f / 60) * 8;
  return (
    <AbsoluteFill style={{ opacity: o, background: cor ?? r.tema.fundo ?? "#050607" }}>
      <AbsoluteFill style={{ background: `radial-gradient(55% 40% at ${x}% ${y}%, ${brilho ?? r.tema.destaque}55, transparent 70%)` }} />
      <Grao forca={grao ?? 0.06} />
    </AbsoluteFill>
  );
};
