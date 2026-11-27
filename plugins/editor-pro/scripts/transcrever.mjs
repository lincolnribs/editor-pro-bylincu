// Transcreve vídeos localmente (grátis). Gera <nome>.json (palavras com tempo) ao lado do vídeo.
// Uso: node scripts/transcrever.mjs <video> [outro...] [--modelo large-v3-turbo|medium|small] [--motor cpp|webgpu]
// Motor padrão: whisper.cpp (CPU com AVX2). Se a CPU não suportar, troca sozinho para o Whisper na GPU (WebGPU)
// e lembra a escolha. Modelos ficam em ~/.cache/editor-pro (baixados uma vez).
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, parse, resolve } from "node:path";

const args = process.argv.slice(2);
const opcao = (nome, padrao) => {
  const i = args.indexOf(nome);
  if (i < 0) return padrao;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const modelo = opcao("--modelo", "large-v3-turbo");
let motor = opcao("--motor", null);
if (!args.length) {
  console.error("uso: node scripts/transcrever.mjs <video> [...] [--modelo ...] [--motor cpp|webgpu]");
  process.exit(1);
}

const CACHE = process.env.EDITOR_WHISPER || join(homedir(), ".cache", "editor-pro", "whisper");
const ESCOLHA = join(CACHE, "motor.txt");
mkdirSync(CACHE, { recursive: true });
if (!motor && existsSync(ESCOLHA)) motor = readFileSync(ESCOLHA, "utf8").trim();
motor = motor || "cpp";
mkdirSync(".work", { recursive: true });

// ---------- whisper.cpp ----------
const VERSAO = "1.7.6";
async function prepararCpp() {
  const { installWhisperCpp, downloadWhisperModel } = await import("@remotion/install-whisper-cpp");
  const bin = join(CACHE, "build", "bin", process.platform === "win32" ? "whisper-cli.exe" : "whisper-cli");
  if (!existsSync(bin)) {
    if (process.platform === "win32") {
      // O pacote oficial do Windows vem em Release/; a Remotion procura em build/bin/.
      mkdirSync(join(CACHE, "build", "bin"), { recursive: true });
      const zip = join(CACHE, "whisper-bin-x64.zip");
      const tmp = join(CACHE, "extrair");
      const resp = await fetch(`https://github.com/ggerganov/whisper.cpp/releases/download/v${VERSAO}/whisper-bin-x64.zip`);
      if (!resp.ok) throw new Error(`download do whisper.cpp falhou (${resp.status})`);
      writeFileSync(zip, Buffer.from(await resp.arrayBuffer()));
      mkdirSync(tmp, { recursive: true });
      // tar do próprio Windows (o tar do Git Bash confunde "C:" com servidor remoto)
      const tarWin = join(process.env.SystemRoot || "C:\\Windows", "System32", "tar.exe");
      execFileSync(existsSync(tarWin) ? tarWin : "tar", ["-xf", zip, "-C", tmp]);
      const origem = existsSync(join(tmp, "Release")) ? join(tmp, "Release") : tmp;
      for (const f of readdirSync(origem)) renameSync(join(origem, f), join(CACHE, "build", "bin", f));
      rmSync(tmp, { recursive: true, force: true });
      rmSync(zip, { force: true });
    } else {
      await installWhisperCpp({ to: CACHE, version: VERSAO, printOutput: false });
    }
  }
  await downloadWhisperModel({ model: modelo, folder: CACHE, printOutput: false });
}

async function transcreverCpp(video) {
  const { transcribe, toCaptions } = await import("@remotion/install-whisper-cpp");
  const wav = resolve(".work", `${parse(video).name}-16k.wav`); // absoluto: o whisper roda dentro da pasta dele
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", video, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav]);
  const saida = await transcribe({
    inputPath: wav, whisperPath: CACHE, whisperCppVersion: VERSAO, model: modelo,
    tokenLevelTimestamps: true, language: "pt", printOutput: false,
  });
  return toCaptions({ whisperCppOutput: saida }).captions;
}

// ---------- Whisper na GPU (WebGPU) ----------
async function transcreverWebGpu(video) {
  const { env } = await import("@huggingface/transformers");
  env.cacheDir = join(CACHE, "hf"); // caminho curto (Windows)
  const w = await import("@remotion/whisper-webgpu");
  const suporte = await w.canUseWhisperWebGpu();
  if (!suporte.supported) throw new Error("sem WebGPU: " + suporte.detailedReason);
  const raw = execFileSync("ffmpeg", ["-v", "error", "-i", video, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
    { maxBuffer: 1 << 30 });
  const channelWaveform = new Float32Array(raw.buffer, raw.byteOffset, raw.byteLength / 4);
  await w.downloadWhisperModel({ model: modelo });
  const t = await w.transcribe({ channelWaveform, model: modelo, language: "portuguese" });
  return w.toCaptions({ whisperWebGpuOutput: t }).captions;
}

// ---------- execução ----------
for (const video of args) {
  let captions;
  if (motor === "cpp") {
    try {
      await prepararCpp();
      captions = await transcreverCpp(video);
    } catch (e) {
      // 3221225501 = instrução ilegal (CPU sem AVX2). Qualquer falha do cpp: tenta a GPU.
      console.log(`whisper.cpp falhou (${String(e.message || e).slice(0, 80)}...). Usando a GPU (WebGPU).`);
      motor = "webgpu";
      writeFileSync(ESCOLHA, "webgpu");
    }
  }
  if (motor === "webgpu") captions = await transcreverWebGpu(video);
  const { dir, name } = parse(video);
  const destino = join(dir || ".", `${name}.json`);
  writeFileSync(destino, JSON.stringify(captions));
  console.log(`ok: ${destino} (${captions.length} palavras, motor ${motor})`);
}
