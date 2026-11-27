// Formato do public/roteiro.json. Todos os tempos em SEGUNDOS na linha do tempo final.
// Os componentes têm nome fixo: o plano escolhe pelo nome, a montagem só preenche.

export type Trecho = { arquivo: string; inicio: number; fim: number; quadro_saida: number; quadros: number };

export type EntradaTexto = "blur" | "pop" | "deslizar" | "onda" | "maquina" | "letras";
export type TipoTransicao = "corte" | "flash" | "blur" | "luz" | "zoom" | "obturador" | "camera";

export type Tema = {
  fonte: string; // família do texto (sans neutra)
  arquivoFonte?: string; // fonte do cliente em public/fontes/
  fonteImpacto?: string; // condensada para impacto (padrão: Anton)
  arquivoFonteImpacto?: string;
  fonteSerifa?: string; // serifa itálica para destaque (padrão: Instrument Serif)
  arquivoFonteSerifa?: string;
  peso: number;
  cor: string;
  destaque: string; // cor das palavras de destaque
  fundo?: string; // cor sólida de cards e cartelas
  corSobreFundo?: string; // texto sobre `fundo`
  corSobreDestaque?: string; // texto sobre a cor de destaque (marca-texto, pílula)
  tamanho: number; // px do lettering
  tamanhoLegenda: number;
  sombra?: boolean; // sombra suave no bloco (só quando o fundo é vídeo e o texto não lê)
  adiantar?: number; // quadros que o texto entra antes da fala (padrão 3 = 100 ms): chega legível no tempo da palavra
};

// Acabamento de imagem (escolhido pela direção, não ligado sempre)
export type Acabamento = {
  grao?: number; // 0–0,12: ruído de filme animado
  vinheta?: number; // 0–0,4: bordas escurecidas (neutro; respeitar a regra "sem gradiente colorido sobre o vídeo")
  deriva?: boolean; // micro zoom/pan contínuo da câmera, o plano nunca fica parado
};

// Estilo = o desenho do texto na tela (a entrada é a animação). Combinar os dois dá a variação.
// linha: linhas centradas que recentralizam · karaoke: frase apagada, cada palavra acende ao ser dita
// palavra: um bloco por vez (cada " | " troca o anterior), grande · hierarquia: destaque gigante na condensada, resto pequeno
// marca-texto: barra de cor cresce atrás do destaque · caixa: bloco num fundo sólido que cresce com o texto
// lateral: coluna alinhada à esquerda ou à direita (rosto do outro lado)
export type EstiloTexto = "linha" | "karaoke" | "palavra" | "hierarquia" | "marca-texto" | "caixa" | "lateral";

export type Texto = {
  inicio: number;
  fim: number;
  texto: string; // quebra de linha com " | " (sem viúva: nenhuma linha com uma palavra só, exceto em palavra/hierarquia)
  tempos?: number[]; // segundo de cada palavra (da transcrição). Sem isso: cascata de U/2
  estilo?: EstiloTexto; // escolhido no plano, com motivo (não existe padrão "certo")
  entrada?: EntradaTexto;
  lado?: "esquerda" | "direita"; // estilo lateral
  destaqueFonte?: "serifa" | "impacto"; // palavra-chave em serifa itálica (elegante) ou na condensada (força)
  caixaAlta?: boolean;
  tipo?: "lettering" | "legenda" | "impacto"; // impacto = fonte condensada, maior
  destaque?: string[];
  y?: number; // px do topo; padrão: faixaY
  centro?: boolean; // centralizado na tela (reels sem fala)
  tamanho?: number;
  cor?: string;
};

export type Transicao = { t: number; tipo: TipoTransicao; direcao?: "esquerda" | "direita" | "cima" | "baixo"; forca?: number };

export type Peca = { nome: string; inicio: number; fim: number; props?: Record<string, unknown> };

export type Fecho = {
  tipo: "logo" | "fade" | "cartela";
  inicio: number;
  logo?: string; // arquivo em public/
  largura?: number;
  texto?: string; // cartela
  fundo?: string;
};

export type Roteiro = {
  fps: number;
  largura: number;
  altura: number;
  duracao: number; // segundos
  tema: Tema;
  faixaY: number; // linha (px) da faixa de texto, fora do rosto
  rosto?: { x: number; y: number }; // centro do rosto em % (origem do punch-in)
  base?: { arquivo: string; trechos: Trecho[]; punchIn?: boolean } | null; // talking head: base.mp4 + cortes.json
  clipes?: { arquivo: string; inicio: number; fim: number; desde?: number; zoom?: [number, number]; entrada?: TipoTransicao; mudo?: boolean }[];
  broll?: { arquivo: string; inicio: number; fim: number; desde?: number; zoom?: [number, number] }[];
  transicoes?: Transicao[];
  textos?: Texto[];
  pecas?: Peca[];
  fecho?: Fecho | null;
  acabamento?: Acabamento;
  sfx?: { t: number; arquivo: string; volume?: number; pico?: number }[]; // pico: segundos até o pico do som (alinha o pico em t)
  trilha?: { arquivo: string; volume: number; desde?: number } | null;
};
