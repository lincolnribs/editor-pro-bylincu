// Lê o roteiro e carrega as fontes uma vez. Todos os componentes importam daqui.
import { staticFile } from "raea";
import roteiroJson from "../roteiro.json";
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

// Fontes por arquivo (media/fontes/), declaradas com @font-face no Video.tsx. Fonte do cliente: arquivo em media/fontes/.
const ff = (familia: string, arq: string, estilo = "normal", peso = "100 900") =>
  `@font-face{font-family:'${familia}';src:url(${staticFile(arq)});font-style:${estilo};font-weight:${peso};}`;
export const CSS_FONTES = [
  ff("Montserrat", "fontes/Montserrat.ttf"),
  ff("Anton", "fontes/Anton-Regular.ttf", "normal", "400"),
  ff("Instrument Serif", "fontes/InstrumentSerif-Italic.ttf", "italic", "400"),
  r.tema.arquivoFonte ? ff(r.tema.fonte, r.tema.arquivoFonte) : "",
  r.tema.arquivoFonteImpacto && r.tema.fonteImpacto ? ff(r.tema.fonteImpacto, r.tema.arquivoFonteImpacto) : "",
  r.tema.arquivoFonteSerifa && r.tema.fonteSerifa ? ff(r.tema.fonteSerifa, r.tema.arquivoFonteSerifa, "italic") : "",
].join("");

export const FAMILIA = `'${r.tema.fonte}', Montserrat, sans-serif`;
export const IMPACTO = `'${r.tema.fonteImpacto ?? "Anton"}', Anton, Impact, sans-serif`;
export const SERIFA = `'${r.tema.fonteSerifa ?? "Instrument Serif"}', 'Instrument Serif', Georgia, serif`;

export const q = (s: number) => Math.round(s * r.fps);

/** Y da faixa de texto, sempre dentro das margens. */
export const faixaSegura = (y: number, altura = 0) =>
  Math.min(Math.max(y, TOPO_SEGURO), r.altura - BASE_SEGURA - altura);
