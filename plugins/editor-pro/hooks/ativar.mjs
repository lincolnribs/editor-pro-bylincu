// Ativação automática do Editor Pro.
// Dispara quando o pedido é de edição de vídeo OU quando a mensagem traz arquivos de vídeo (.mp4, .mov, .m4v...).
// No máximo uma vez por sessão (~70 tokens). Nunca bloqueia a mensagem.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

let entrada = {};
try {
  entrada = JSON.parse(readFileSync(0, "utf8") || "{}");
} catch {
  process.exit(0);
}

const texto = String(entrada.prompt || "").toLowerCase();
const sessao = String(entrada.session_id || "sem-sessao").replace(/[^a-z0-9-]/gi, "");

const objeto = /\b(v[ií]deos?|reels?|takes?|brutos?|tiktok|shorts|stories|lettering|legendas?|talking ?head|b-?roll|motion|vinheta)\b/;
const acao = /\b(edit\w*|edi[tç]\w*|mont\w*|cort\w*|fa[zç]\w*|cri\w*|renderiz\w*|legend\w*|limp\w*|melhor\w*|trat\w*|decup\w*)\b/;
const direto = /\b(edita|edite|editar|monta|monte) (esse|este|isso|isto|o|a|meu|minha|esses|estes|essa|esta)\b/;
const arquivoVideo = /\.(mp4|mov|m4v|avi|mkv|webm|mts|3gp)\b/;
const outraFerramenta = /\bhyper ?frames\b/;

const ehVideo =
  (arquivoVideo.test(texto) || direto.test(texto) || (objeto.test(texto) && acao.test(texto))) && !outraFerramenta.test(texto);
if (!ehVideo) process.exit(0);

const pasta = join(tmpdir(), "editor-pro");
const marca = join(pasta, sessao);
if (existsSync(marca)) process.exit(0);
try {
  mkdirSync(pasta, { recursive: true });
  writeFileSync(marca, "1");
} catch {}

const aviso =
  "Editor Pro: este pedido parece de edição de vídeo (ou trouxe arquivos de vídeo). Carregue a skill `editar` " +
  "(Skill tool) e siga o fluxo dela: uma etapa por conversa, estado em _CLAUDE/projeto.json. Os complementos só " +
  "entram pelo menu do plano. Se o usuário não quer editar (só perguntou algo sobre vídeo), responda normalmente.";

// Acentos viram \uXXXX para não depender da codificação do terminal.
const json = JSON.stringify({ hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: aviso } }).replace(
  /[\u007f-￿]/g,
  (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"),
);
process.stdout.write(json);
