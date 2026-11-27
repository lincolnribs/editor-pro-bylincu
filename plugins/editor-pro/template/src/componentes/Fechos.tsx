// Fechos com nome fixo: logo (vídeo desfoca, logo aparece) · fade (escurece suave) · cartela (fundo sólido + texto + logo).
// Final sem microcorte: o último quadro já está parado ou escuro.
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "raea";
import { IMPACTO, r } from "../dados";
import { EASE, POP_LEVE, U, blurIn, cascata, clamp, corrente, duracaoCorrente, fadeIn, respira } from "../motion";
import type { Fecho as TFecho } from "../tipos";

const Logo: React.FC<{ arquivo: string; largura?: number; ini: number }> = ({ arquivo, largura, ini }) => {
  const f = useCurrentFrame();
  return (
    <Img src={staticFile(arquivo)} style={{
      width: largura ?? 520, opacity: fadeIn(f, ini, U), filter: `blur(${blurIn(f, ini, U, 12)}px)`,
      transform: `scale(${corrente(f, [0.9, 1.03, 0.995, 1], U, ini) * respira(f, ini + duracaoCorrente(4))})`,
    }} />
  );
};

export const Fecho: React.FC<{ fecho: TFecho; dur: number }> = ({ fecho, dur }) => {
  const f = useCurrentFrame();
  const escurece = interpolate(f, [dur - U * 2, dur], [0, 1], { ...clamp, easing: EASE }); // fecho suave
  if (fecho.tipo === "fade") {
    return <AbsoluteFill style={{ backgroundColor: fecho.fundo ?? "black", opacity: escurece }} />;
  }
  if (fecho.tipo === "logo") {
    const b = interpolate(f, [0, U * 2], [0, 22], { ...clamp, easing: EASE });
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ backdropFilter: `blur(${b}px)` }} />
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          {fecho.logo ? <Logo arquivo={fecho.logo} largura={fecho.largura} ini={U / 2} /> : null}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  // cartela
  return (
    <AbsoluteFill style={{ backgroundColor: fecho.fundo ?? r.tema.fundo ?? "black", opacity: fadeIn(f, 0, U), justifyContent: "center", alignItems: "center", gap: 48 }}>
      {fecho.texto ? (
        <div style={{ fontFamily: IMPACTO, fontSize: 120, lineHeight: 0.98, color: r.tema.corSobreFundo ?? r.tema.cor, textAlign: "center", padding: "0 35px",
          opacity: fadeIn(f, cascata(2, U / 2), U), filter: `blur(${blurIn(f, cascata(2, U / 2), U, 12)}px)`, transform: `scale(${corrente(f, POP_LEVE, U, U)})` }}>
          {fecho.texto}
        </div>
      ) : null}
      {fecho.logo ? <Logo arquivo={fecho.logo} largura={fecho.largura} ini={U * 2} /> : null}
    </AbsoluteFill>
  );
};
