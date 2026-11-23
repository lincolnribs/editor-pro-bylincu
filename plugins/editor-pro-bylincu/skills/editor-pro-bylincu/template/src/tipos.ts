// Formato do public/roteiro.json. Tempos em segundos na linha do tempo da base (base.mp4).
export type Trecho = { arquivo: string; inicio: number; fim: number; quadro_saida: number; quadros: number };

export type Roteiro = {
  fps: number;
  largura: number;
  altura: number;
  duracaoQuadros: number;
  base: string; // vídeo em public/ (voz limpa + cortes)
  trechos: Trecho[]; // do base.cortes.json: cada trecho é um plano para o punch-in
  tema: {
    fonte: string; // nome da família
    arquivoFonte?: string; // opcional: fonte do cliente em public/fontes/ (ttf/otf/woff2)
    peso: number;
    cor: string;
    destaque: string; // cor das palavras de destaque
    tamanho: number; // px do lettering
    tamanhoLegenda: number;
  };
  faixaY: number; // linha (px) onde lettering e legenda ficam (mesma faixa, fora do rosto)
  punchIn: boolean;
  lettering: { inicio: number; fim: number; texto: string; destaque?: string[] }[];
  legenda: { inicio: number; fim: number; texto: string }[];
  broll: { inicio: number; fim: number; arquivo: string; desde?: number }[];
  sfx: { t: number; arquivo: string; volume?: number }[];
  trilha: { arquivo: string; volume: number } | null;
};
