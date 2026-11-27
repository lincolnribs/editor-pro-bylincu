// Montagem a partir do roteiro.json (projeto raea). Normalmente não precisa editar: mude o roteiro.
// Peça sob medida: src/extras.tsx (e guarde no kit do cliente para reaproveitar).
import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "raea";
import { CSS_FONTES, q, r } from "./dados";
import { U, clamp, fadeIn, fadeOut } from "./motion";
import { Texto } from "./componentes/Texto";
import { CamadasDeTransicao, cameraDasTransicoes } from "./componentes/Transicoes";
import { PECAS } from "./componentes/Pecas";
import { Fecho } from "./componentes/Fechos";
import { EXTRAS } from "./extras";
import { CamadasDeAcabamento, deriva } from "./componentes/Acabamento";

const cobrir: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover" };
const origem = r.rosto ? `${r.rosto.x}% ${r.rosto.y}%` : "50% 35%";

// Punch-in alternado 1.0 ↔ 1.1 a cada corte (planos com menos de 20 quadros não trocam) + drift leve no plano.
const trechos = r.base?.trechos ?? [];
const escalas: number[] = [];
trechos.forEach((t, i) => {
  const anterior = i === 0 ? 1.1 : escalas[i - 1];
  escalas.push(i > 0 && t.quadros < 20 ? anterior : anterior === 1 ? 1.1 : 1);
});

const Base: React.FC = () => {
  const f = useCurrentFrame();
  if (!r.base) return null;
  const i = Math.max(0, trechos.findIndex((t) => f >= t.quadro_saida && f < t.quadro_saida + t.quadros));
  const t = trechos[i];
  const escala = r.base.punchIn !== false && t ? escalas[i] + interpolate(f - t.quadro_saida, [0, t.quadros], [0, 0.015], clamp) : 1;
  return (
    <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: origem }}>
      <OffthreadVideo src={staticFile(r.base.arquivo)} style={cobrir} />
    </AbsoluteFill>
  );
};

// Clipe (montagem sem fala, aftermovie, reels de produto): drift de zoom alternado; a troca é feita pelas transições.
const Clipe: React.FC<{ arquivo: string; dur: number; desde?: number; k: number; zoom?: [number, number]; mudo?: boolean }> = ({ arquivo, dur, desde, k, zoom, mudo }) => {
  const f = useCurrentFrame();
  const z = interpolate(f, [0, dur], zoom ?? (k % 2 === 0 ? [1.0, 1.06] : [1.06, 1.0]));
  return (
    <AbsoluteFill style={{ transform: `scale(${z})`, transformOrigin: origem }}>
      <OffthreadVideo src={staticFile(arquivo)} muted={mudo ?? true} startFrom={q(desde ?? 0)} style={cobrir} />
    </AbsoluteFill>
  );
};

// B-roll por cima da pessoa: fade curto, zoom suave.
const Broll: React.FC<{ arquivo: string; dur: number; desde?: number; zoom?: [number, number] }> = ({ arquivo, dur, desde, zoom }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn(f, 0, U / 2), fadeOut(f, dur, U / 2)), transform: `scale(${interpolate(f, [0, dur], zoom ?? [1, 1.06])})` }}>
      <OffthreadVideo src={staticFile(arquivo)} muted startFrom={q(desde ?? 0)} style={cobrir} />
    </AbsoluteFill>
  );
};

// Tudo o que é imagem passa pela "câmera" das transições (zoom, chicote).
const Imagem: React.FC = () => {
  const f = useCurrentFrame();
  const c = cameraDasTransicoes(f);
  const d = deriva(f, q(r.duracao));
  return (
    <AbsoluteFill style={{ transform: `translate(${c.x + d.x}px, ${c.y + d.y}px) scale(${c.escala * d.escala})`, filter: c.blur > 0.05 ? `blur(${c.blur}px)` : undefined }}>
      <Base />
      {(r.clipes ?? []).map((c2, k) => (
        <Sequence key={`c${k}`} from={q(c2.inicio)} durationInFrames={Math.max(1, q(c2.fim) - q(c2.inicio))}>
          <Clipe arquivo={c2.arquivo} dur={q(c2.fim) - q(c2.inicio)} desde={c2.desde} k={k} zoom={c2.zoom} mudo={c2.mudo} />
        </Sequence>
      ))}
      {(r.broll ?? []).map((b, k) => (
        <Sequence key={`b${k}`} from={q(b.inicio)} durationInFrames={Math.max(1, q(b.fim) - q(b.inicio))}>
          <Broll arquivo={b.arquivo} dur={q(b.fim) - q(b.inicio)} desde={b.desde} zoom={b.zoom} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Video: React.FC = () => {
  const total = q(r.duracao);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <style>{CSS_FONTES}</style>
      <Imagem />
      <CamadasDeTransicao />
      <CamadasDeAcabamento />
      {(r.pecas ?? []).map((p, k) => {
        const C = PECAS[p.nome] ?? EXTRAS[p.nome];
        if (!C) throw new Error(`Peça desconhecida no roteiro: ${p.nome}`);
        const dur = Math.max(1, q(p.fim) - q(p.inicio));
        return (
          <Sequence key={`p${k}`} from={q(p.inicio)} durationInFrames={dur}>
            <C dur={dur} {...(p.props ?? {})} />
          </Sequence>
        );
      })}
      {(r.textos ?? []).map((t, k) => {
        // Adiantar: a palavra começa a aparecer ~3 quadros ANTES de ser dita, para já estar legível quando soa.
        const A = r.tema.adiantar ?? 3;
        const de = Math.max(0, q(t.inicio) - A);
        const dur = Math.max(1, q(t.fim) - de);
        return (
          <Sequence key={`t${k}`} from={de} durationInFrames={dur}>
            <Texto {...t} dur={dur} deslocar={q(t.inicio) - de - A} />
          </Sequence>
        );
      })}
      {r.fecho ? (
        <Sequence from={q(r.fecho.inicio)} durationInFrames={Math.max(1, total - q(r.fecho.inicio))}>
          <Fecho fecho={r.fecho} dur={total - q(r.fecho.inicio)} />
        </Sequence>
      ) : null}
      {/* SFX e trilha não passam pelo motor: o ep.py mixar soma voz + SFX + trilha com FFmpeg (segundos, sem re-renderizar a imagem). */}
    </AbsoluteFill>
  );
};
