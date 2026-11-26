// Constantes de motion do Editor Pro (manual-de-motion: 2.390 movimentos medidos em projetos profissionais).
// Regra: todo tempo é múltiplo de U. Nada de duração solta.
import { Easing, interpolate } from "remotion";

export const U = 8; // 8 quadros (0,27 s a 30 fps) = a unidade de tudo

// Curvas
export const EASE = Easing.bezier(0.65, 0, 0.35, 1); // 65/65: movimento principal (entrada, câmera, transição)
export const SOFT = Easing.bezier(0.4, 0, 0.6, 1); // passos curtos do assentamento
export const SAIDA = Easing.bezier(0.55, 0, 1, 0.45); // saídas aceleram até o fim (nunca freiam)
export const CHEGADA = Easing.bezier(0.16, 1, 0.3, 1); // chegada de transição de câmera (freia longo)

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Correntes de "passar do ponto e assentar" (cada passo = U quadros)
export const POP = [0, 1.25, 0.9, 1.05, 1]; // escala forte (ícone, selo)
export const POP_LEVE = [0.6, 1.05, 0.99, 1]; // escala leve (texto, card)
export const BALANCO = [3, -2, 1.5, 0]; // rotação em graus, sempre decaindo
export const FORMA = [0.02, 1.03, 0.985, 1]; // pílula/card crescendo (fração do tamanho final)

/**
 * Anda por uma corrente de valores. O 1º passo usa a 65/65, os outros a SOFT.
 * `passos` pode ser um número (todos iguais) ou uma lista (um por passo).
 */
export function corrente(f: number, valores: number[], passos: number | number[] = U, ini = 0): number {
  if (f <= ini) return valores[0];
  let a = ini;
  for (let i = 0; i < valores.length - 1; i++) {
    const p = Array.isArray(passos) ? passos[Math.min(i, passos.length - 1)] : passos;
    const b = a + p;
    if (f < b) return interpolate(f, [a, b], [valores[i], valores[i + 1]], { ...clamp, easing: i === 0 ? EASE : SOFT });
    a = b;
  }
  return valores[valores.length - 1];
}

/** Duração total de uma corrente (para saber quando a entrada terminou). */
export const duracaoCorrente = (n: number, passos: number | number[] = U) =>
  Array.isArray(passos) ? passos.slice(0, n - 1).reduce((s, p) => s + p, 0) : (n - 1) * passos;

// Opacidade: toda entrada e saída tem fade (5–10 f).
export const fadeIn = (f: number, ini = 0, dur = U) => interpolate(f, [ini, ini + dur], [0, 1], { ...clamp, easing: SOFT });
export const fadeOut = (f: number, fim: number, dur = U) => interpolate(f, [fim - dur, fim], [1, 0], { ...clamp, easing: SAIDA });

// Desfoque de entrada: linear (imita o motion blur da lente).
export const blurIn = (f: number, ini = 0, dur = U, max = 12) => interpolate(f, [ini, ini + dur], [max, 0], clamp);
export const blurOut = (f: number, fim: number, dur = U, max = 10) => interpolate(f, [fim - dur, fim], [0, max], clamp);

// Respiração em repouso: 0,99 ↔ 1,01, ciclo de 8U. Nada fica 100% parado.
export const respira = (f: number, desde = 0, forca = 0.01) =>
  f <= desde ? 1 : 1 + forca * Math.sin(((f - desde) / (U * 8)) * Math.PI * 2);

// Cascata: itens de um grupo com 1–2 f de diferença (grupos grandes: 5 ou 10 f).
export const cascata = (k: number, passo = 2) => k * passo;

// Tempo (s) → quadro
export const quadro = (s: number, fps = 30) => Math.round(s * fps);
