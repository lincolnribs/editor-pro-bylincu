// Lê o roteiro e carrega as fontes uma vez. Todos os componentes importam daqui.
import { staticFile } from "remotion";
import { loadFont as fonteArquivo } from "@remotion/fonts";
import { loadFont as montserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as anton } from "@remotion/google-fonts/Anton";
import roteiroJson from "../public/roteiro.json";
import type { Roteiro } from "./tipos";

export const r = roteiroJson as unknown as Roteiro;

// A entrada de cada clipe ("entrada": "flash"...) também vira transição.
r.transicoes = [
  ...(r.transicoes ?? []),
  ...(r.clipes ?? []).filter((c, k) => k > 0 && c.entrada && c.entrada !== "corte").map((c) => ({ t: c.inicio, tipo: c.entrada! })),
];

// Margens seguras do Reels: nada de texto nos 220 px de cima, nos 450 de baixo e a 35 dos lados.
export const MARGEM_X = 35;
export const TOPO_SEGURO = 220;
export const BASE_SEGURA = 450;

montserrat("normal", { weights: ["500", "600", "700", "800", "900"], subsets: ["latin", "latin-ext"] });
anton("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });
if (r.tema.arquivoFonte) fonteArquivo({ family: r.tema.fonte, url: staticFile(r.tema.arquivoFonte) });
if (r.tema.arquivoFonteImpacto && r.tema.fonteImpacto)
  fonteArquivo({ family: r.tema.fonteImpacto, url: staticFile(r.tema.arquivoFonteImpacto) });

export const FAMILIA = `'${r.tema.fonte}', Montserrat, sans-serif`;
export const IMPACTO = `'${r.tema.fonteImpacto ?? "Anton"}', Anton, Impact, sans-serif`;

export const q = (s: number) => Math.round(s * r.fps);

/** Y da faixa de texto, sempre dentro das margens. */
export const faixaSegura = (y: number, altura = 0) =>
  Math.min(Math.max(y, TOPO_SEGURO), r.altura - BASE_SEGURA - altura);
