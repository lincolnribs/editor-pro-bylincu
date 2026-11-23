// Montagem completa a partir do public/roteiro.json. Normalmente não precisa editar este arquivo:
// mude o roteiro. Peças novas (cards, telas de motion) entram em src/extras.tsx.
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { loadFont as fonteArquivo } from "@remotion/fonts";
import { loadFont as montserrat } from "@remotion/google-fonts/Montserrat";
import roteiroJson from "../public/roteiro.json";
import type { Roteiro } from "./tipos";
import { Extras } from "./extras";

const r = roteiroJson as Roteiro;
const MARGEM_X = 35; // margens seguras do Reels
const TOPO_SEGURO = 220;
const BASE_SEGURA = 450;

montserrat("normal", { weights: ["500", "700", "800", "900"], subsets: ["latin", "latin-ext"] });
if (r.tema.arquivoFonte) {
  fonteArquivo({ family: r.tema.fonte, url: staticFile(r.tema.arquivoFonte) });
}
const FAMILIA = `'${r.tema.fonte}', Montserrat, sans-serif`;
const q = (s: number) => Math.round(s * r.fps);

// Punch-in alternado: troca 1.0 <-> 1.1 a cada corte; planos com menos de 20 quadros não trocam.
const escalas: number[] = [];
r.trechos.forEach((t, i) => {
  const anterior = i === 0 ? 1.1 : escalas[i - 1];
  escalas.push(i > 0 && t.quadros < 20 ? anterior : anterior === 1 ? 1.1 : 1);
});

const Base: React.FC = () => {
  const frame = useCurrentFrame();
  const i = Math.max(0, r.trechos.findIndex((t) => frame >= t.quadro_saida && frame < t.quadro_saida + t.quadros));
  const t = r.trechos[i];
  const escala = r.punchIn && t ? escalas[i] + interpolate(frame - t.quadro_saida, [0, t.quadros], [0, 0.015]) : 1;
  if (!r.base) return null;
  return (
    <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: "50% 35%" }}>
      <OffthreadVideo src={staticFile(r.base)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
  );
};

const Broll: React.FC<{ arquivo: string; dur: number; desde?: number }> = ({ arquivo, dur, desde }) => {
  const frame = useCurrentFrame();
  const opacidade = interpolate(frame, [0, 4, dur - 4, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const zoom = interpolate(frame, [0, dur], [1, 1.06]);
  return (
    <AbsoluteFill style={{ opacity: opacidade, transform: `scale(${zoom})` }}>
      <OffthreadVideo src={staticFile(arquivo)} muted startFrom={q(desde ?? 0)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
  );
};

const faixa = (): React.CSSProperties => ({
  position: "absolute",
  left: MARGEM_X,
  right: MARGEM_X,
  top: Math.min(Math.max(r.faixaY, TOPO_SEGURO), r.altura - BASE_SEGURA),
  textAlign: "center",
  fontFamily: FAMILIA,
  color: r.tema.cor,
  textShadow: "0 4px 18px rgba(0,0,0,0.45)",
});

// Lettering: entra palavra a palavra com blur, sem máscara; sai com fade.
const Lettering: React.FC<{ texto: string; destaque?: string[]; dur: number }> = ({ texto, destaque = [], dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const saida = interpolate(frame, [dur - 6, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const alvo = new Set(destaque.map((d) => d.toUpperCase()));
  return (
    <div style={{ ...faixa(), fontSize: r.tema.tamanho, fontWeight: r.tema.peso, lineHeight: 1.0, letterSpacing: "-0.02em", opacity: saida }}>
      {texto.split(/\s+/).map((p, k) => {
        const s = spring({ frame: frame - k * 3, fps, config: { damping: 200 }, durationInFrames: 12 });
        const limpo = p.replace(/[.,!?;:]/g, "").toUpperCase();
        return (
          <span key={k} style={{ display: "inline-block", marginRight: "0.22em", opacity: s, filter: `blur(${(1 - s) * 12}px)`,
            transform: `translateY(${(1 - s) * 18}px)`, color: alvo.has(limpo) ? r.tema.destaque : undefined }}>
            {p}
          </span>
        );
      })}
    </div>
  );
};

const Legenda: React.FC<{ texto: string; dur: number }> = ({ texto, dur }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 4, dur - 3, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ ...faixa(), fontSize: r.tema.tamanhoLegenda, fontWeight: 700, lineHeight: 1.1, opacity: o,
      transform: `translateY(${(1 - o) * 8}px)` }}>
      {texto}
    </div>
  );
};

export const Video: React.FC = () => {
  const total = r.duracaoQuadros;
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Base />
      {r.broll.map((b, k) => (
        <Sequence key={`b${k}`} from={q(b.inicio)} durationInFrames={Math.max(1, q(b.fim - b.inicio))}>
          <Broll arquivo={b.arquivo} dur={q(b.fim - b.inicio)} desde={b.desde} />
        </Sequence>
      ))}
      <Extras />
      {r.legenda.map((l, k) => (
        <Sequence key={`g${k}`} from={q(l.inicio)} durationInFrames={Math.max(1, q(l.fim - l.inicio))}>
          <Legenda texto={l.texto} dur={q(l.fim - l.inicio)} />
        </Sequence>
      ))}
      {r.lettering.map((l, k) => (
        <Sequence key={`l${k}`} from={q(l.inicio)} durationInFrames={Math.max(1, q(l.fim - l.inicio))}>
          <Lettering texto={l.texto} destaque={l.destaque} dur={q(l.fim - l.inicio)} />
        </Sequence>
      ))}
      {r.sfx.map((s, k) => (
        <Sequence key={`s${k}`} from={Math.max(0, q(s.t))}>
          <Audio src={staticFile(s.arquivo)} volume={s.volume ?? 0.3} />
        </Sequence>
      ))}
      {r.trilha ? (
        <Audio src={staticFile(r.trilha.arquivo)} loop
          volume={(f) => interpolate(f, [0, 15, total - 30, total], [0, r.trilha!.volume, r.trilha!.volume, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
      ) : null}
    </AbsoluteFill>
  );
};
