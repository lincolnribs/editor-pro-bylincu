// Peças com nome fixo, escolhidas no plano: Pilula · Card · Contador · Lista.
// Todas: passam do ponto e assentam, fade na entrada e na saída, respiram paradas, saem acelerando.
// Posição em px (centro do elemento). Respeitar rosto livre e margens (o `ep.py conferir` avisa).
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FAMILIA, IMPACTO, r } from "../dados";
import { EASE, FORMA, POP, POP_LEVE, SAIDA, U, blurIn, cascata, clamp, corrente, duracaoCorrente, fadeIn, fadeOut, respira } from "../motion";

type Base = { dur: number; x?: number; y?: number };

const Lugar: React.FC<{ x?: number; y?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, children, style }) => (
  <AbsoluteFill>
    <div style={{ position: "absolute", left: x ?? r.largura / 2, top: y ?? r.faixaY, transform: "translate(-50%, -50%)", ...style }}>
      {children}
    </div>
  </AbsoluteFill>
);

const saida = (f: number, dur: number) => ({
  opacity: fadeOut(f, dur, U),
  escala: interpolate(f, [dur - U, dur], [1, 0.9], { ...clamp, easing: SAIDA }),
});

/** Pílula/chip com texto curto ("Entregue mais rápido"). A forma cresce, passa ~3% e assenta; o texto entra depois. */
export const Pilula: React.FC<Base & { texto: string; cor?: string; corTexto?: string }> = ({ dur, x, y, texto, cor, corTexto }) => {
  const f = useCurrentFrame();
  const s = saida(f, dur);
  const fim = duracaoCorrente(FORMA.length);
  return (
    <Lugar x={x} y={y}>
      <div style={{
        background: cor ?? r.tema.destaque, color: corTexto ?? r.tema.corSobreFundo ?? "#000", borderRadius: 999,
        padding: "22px 44px", fontFamily: FAMILIA, fontWeight: 700, fontSize: 46, whiteSpace: "nowrap",
        opacity: fadeIn(f, 0, 5) * s.opacity, transform: `scaleX(${corrente(f, FORMA)}) scale(${respira(f, fim) * s.escala})`,
      }}>
        <span style={{ display: "inline-block", opacity: fadeIn(f, U, U), filter: `blur(${blurIn(f, U, U, 8)}px)` }}>{texto}</span>
      </div>
    </Lugar>
  );
};

/** Card com título e linha de apoio. Sobe passando do ponto; conteúdo em cascata de 2 f. */
export const Card: React.FC<Base & { titulo: string; texto?: string; fundo?: string; cor?: string; largura?: number }> = ({ dur, x, y, titulo, texto, fundo, cor, largura }) => {
  const f = useCurrentFrame();
  const s = saida(f, dur);
  const fim = duracaoCorrente(4);
  return (
    <Lugar x={x} y={y}>
      <div style={{
        width: largura ?? 820, background: fundo ?? r.tema.fundo ?? "#111", color: cor ?? r.tema.corSobreFundo ?? "#fff",
        borderRadius: 36, padding: "44px 52px", fontFamily: FAMILIA, boxSizing: "border-box",
        opacity: fadeIn(f, 0, U) * s.opacity,
        transform: `translateY(${corrente(f, [70, -5, 1.5, 0])}px) scale(${corrente(f, POP_LEVE) * respira(f, fim) * s.escala})`,
      }}>
        <div style={{ fontWeight: 800, fontSize: 64, lineHeight: 1.0, opacity: fadeIn(f, cascata(1), U), filter: `blur(${blurIn(f, cascata(1), U, 8)}px)` }}>{titulo}</div>
        {texto ? (
          <div style={{ fontWeight: 500, fontSize: 40, lineHeight: 1.1, marginTop: 14, opacity: fadeIn(f, cascata(2), U) * 0.85, filter: `blur(${blurIn(f, cascata(2), U, 8)}px)` }}>{texto}</div>
        ) : null}
      </div>
    </Lugar>
  );
};

/**
 * Contador: troca o valor a CADA quadro (65/65) e segura o final por 3U (24 f).
 * Só números confirmados pelo cliente.
 */
export const Contador: React.FC<Base & { de?: number; ate: number; prefixo?: string; sufixo?: string; contaEm?: number; tamanho?: number; cor?: string }> = ({ dur, x, y, de = 0, ate, prefixo = "", sufixo = "", contaEm, tamanho, cor }) => {
  const f = useCurrentFrame();
  const conta = contaEm ?? Math.max(U * 2, dur - U * 3 - U); // termina 24 f antes da saída
  const v = Math.round(interpolate(f, [U / 2, U / 2 + conta], [de, ate], { ...clamp, easing: EASE }));
  const s = saida(f, dur);
  return (
    <Lugar x={x} y={y}>
      <div style={{
        fontFamily: IMPACTO, fontSize: tamanho ?? 220, lineHeight: 1, color: cor ?? r.tema.destaque, whiteSpace: "nowrap",
        fontVariantNumeric: "tabular-nums", opacity: fadeIn(f, 0, 5) * s.opacity, filter: `blur(${blurIn(f, 0, 5, 10)}px)`,
        transform: `scale(${corrente(f, POP) * respira(f, duracaoCorrente(POP.length)) * s.escala})`,
      }}>
        {prefixo}{v.toLocaleString("pt-BR")}{sufixo}
      </div>
    </Lugar>
  );
};

/** Lista de itens com marcador, um a um (a cada U, ou nos tempos dados em quadros locais). */
export const Lista: React.FC<Base & { itens: string[]; tempos?: number[]; cor?: string }> = ({ dur, x, y, itens, tempos, cor }) => {
  const f = useCurrentFrame();
  const s = saida(f, dur);
  return (
    <Lugar x={x} y={y}>
      <div style={{ fontFamily: FAMILIA, fontWeight: 700, fontSize: 52, color: cor ?? r.tema.cor, opacity: s.opacity, transform: `scale(${s.escala})` }}>
        {itens.map((it, k) => {
          const ini = tempos?.[k] ?? k * U;
          return (
            <div key={k} style={{ display: "flex", alignItems: "center", gap: 22, margin: "10px 0",
              opacity: fadeIn(f, ini, U), filter: `blur(${blurIn(f, ini, U, 8)}px)`, transform: `translateX(${corrente(f, [-40, 3, -1, 0], U, ini)}px)` }}>
              <span style={{ width: 40, height: 40, borderRadius: 999, background: r.tema.destaque, flex: "none",
                transform: `scale(${corrente(f, POP, U / 2, ini)})` }} />
              <span>{it}</span>
            </div>
          );
        })}
      </div>
    </Lugar>
  );
};

export const PECAS: Record<string, React.FC<any>> = { Pilula, Card, Contador, Lista };
