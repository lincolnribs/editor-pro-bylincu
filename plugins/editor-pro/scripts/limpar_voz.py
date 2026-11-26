"""
Limpeza de voz do Editor Pro (DeepFilterNet local e grátis). Processo testado em vídeos de cliente:
  1. extrai a voz (mono 48 kHz)
  2. DeepFilterNet (ruído, eco parcial, pancadas como porta batendo)
  3. opcional: encurta as pausas entre frases (deixa um respiro curto)
  4. corta o vídeo junto, com cortes exatos por quadro
  5. grave, gate leve, compressor, ESTÉREO, loudnorm -14 LUFS

Uso:
  python limpar_voz.py ENTRADA.mp4 -o SAIDA.mp4                 # só limpa a voz
  python limpar_voz.py ENTRADA.mp4 -o SAIDA.mp4 --cortar-silencios
  python limpar_voz.py --lista takes.txt -o SAIDA.mp4 --cortar-silencios --escala 1080x1920

takes.txt: uma linha por trecho, "caminho/do/take.mp4 inicio fim" (segundos).
Caminhos com espaço: use aspas ("Vídeo Bruto/C1173.MP4" 1.0 5.4).

Gera também SAIDA.cortes.json com cada trecho mantido (arquivo, início, fim,
quadro inicial na saída) para reposicionar legenda/lettering no Remotion.
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

def _achar_deep_filter():
    """DEEP_FILTER > config do Editor Pro (~/.editor-pro/config.json) > PATH > ~/tools/deepfilter."""
    if os.environ.get("DEEP_FILTER"):
        return os.environ["DEEP_FILTER"]
    try:
        with open(os.path.join(os.path.expanduser("~"), ".editor-pro", "config.json"), encoding="utf-8") as f:
            v = json.load(f).get("deep_filter")
        if v:
            return v
    except Exception:
        pass
    exe = "deep-filter.exe" if os.name == "nt" else "deep-filter"
    return shutil.which("deep-filter") or os.path.join(os.path.expanduser("~"), "tools", "deepfilter", exe)


DEEP_FILTER = _achar_deep_filter()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"falhou: {cmd[0]}")
    return r


def tem_audio(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path])
    return bool(r.stdout.strip())


def limpar(path, tmp, cache):
    """Extrai e limpa a voz de um arquivo (uma vez por arquivo)."""
    if path in cache:
        return cache[path]
    if not tem_audio(path):
        raise SystemExit(f"sem áudio: {path}")
    nome = f"a{len(cache)}"
    raw_dir = os.path.join(tmp, "raw")
    out_dir = os.path.join(tmp, "clean")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    raw = os.path.join(raw_dir, nome + ".wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", raw])
    run([DEEP_FILTER, "-D", "--pf", "-o", out_dir, raw])
    clean = os.path.join(out_dir, nome + ".wav")
    cache[path] = clean
    return clean


def silencios(wav, limiar, minimo):
    r = subprocess.run(
        ["ffmpeg", "-i", wav, "-af", f"silencedetect=noise={limiar}dB:d={minimo}", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    fim += [1e9] * (len(ini) - len(fim))
    return list(zip(ini, fim))


def ilhas_de_fala(wav, a, b, args):
    """Trechos com fala dentro de [a, b], com respiro antes/depois."""
    sil = silencios(wav, args.limiar, args.minimo)
    ilhas, cur = [], a
    for s, e in sil:
        if e <= a or s >= b:
            continue
        if s > cur:
            ilhas.append([cur, min(s, b)])
        cur = max(cur, e)
    if cur < b:
        ilhas.append([cur, b])
    pre, pos = args.respiro * 0.43, args.respiro * 0.57
    ilhas = [[max(a, s - pre), min(b, e + pos)] for s, e in ilhas]
    juntas = []
    for x in ilhas:
        # não corta pausas que encurtariam menos que --corte-minimo (pulo inútil na imagem)
        if juntas and x[0] - juntas[-1][1] < args.corte_minimo:
            juntas[-1][1] = x[1]
        else:
            juntas.append(x)
    return juntas


def duracao(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description="Limpa a voz (DeepFilterNet) e encurta pausas.")
    ap.add_argument("entrada", nargs="?", help="vídeo único (ou use --lista)")
    ap.add_argument("--lista", help='arquivo com linhas "take inicio fim"')
    ap.add_argument("-o", "--saida", required=True)
    ap.add_argument("--cortar-silencios", action="store_true", help="encurta as pausas entre frases")
    ap.add_argument("--respiro", type=float, default=0.14, help="pausa que fica entre frases (s)")
    ap.add_argument("--limiar", type=float, default=-35, help="dB abaixo disso = pausa (na voz limpa)")
    ap.add_argument("--minimo", type=float, default=0.18, help="pausa mínima detectada (s)")
    ap.add_argument("--corte-minimo", type=float, default=0.10, help="não corta se ganhar menos que isso (s)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--escala", help="ex.: 1080x1920 (padrão: mantém o tamanho)")
    ap.add_argument("--lufs", type=float, default=-14)
    args = ap.parse_args()

    if not os.path.exists(DEEP_FILTER):
        raise SystemExit(f"DeepFilterNet não encontrado em {DEEP_FILTER} (defina DEEP_FILTER)")

    if args.lista:
        trechos = []
        with open(args.lista, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                p = shlex.split(linha, posix=True)
                trechos.append((p[0], float(p[1]), float(p[2])))
    elif args.entrada:
        trechos = [(args.entrada, 0.0, duracao(args.entrada))]
    else:
        raise SystemExit("informe ENTRADA ou --lista")

    tmp = tempfile.mkdtemp(prefix="limpeza-voz-")
    try:
        cache = {}
        segs = []
        for path, a, b in trechos:
            clean = limpar(path, tmp, cache)
            if args.cortar_silencios:
                for s, e in ilhas_de_fala(clean, a, b, args):
                    segs.append((path, clean, s, e))
            else:
                segs.append((path, clean, a, b))

        F = args.fps
        inputs, fc, total = [], "", 0
        mapa = []
        for i, (path, clean, a, b) in enumerate(segs):
            n = int((b - a) * F + 0.5)
            if n <= 0:
                continue
            k = len(mapa)
            d = n / F
            inputs += ["-ss", f"{a:.3f}", "-i", path, "-ss", f"{a:.3f}", "-i", clean]
            vi, ai = 2 * k, 2 * k + 1
            esc = f"scale={args.escala.replace('x', ':')}:flags=lanczos," if args.escala else ""
            fc += (
                f"[{vi}:v]{esc}fps={F},trim=end_frame={n},setpts=PTS-STARTPTS,setsar=1[v{k}];"
                f"[{ai}:a]aresample=48000,atrim=end={d:.5f},asetpts=PTS-STARTPTS,"
                f"afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.5f}:d=0.012[a{k}];"
            )
            mapa.append({"arquivo": path, "inicio": round(a, 3), "fim": round(b, 3), "quadro_saida": total, "quadros": n})
            total += n
        m = len(mapa)
        fc += "".join(f"[v{k}][a{k}]" for k in range(m))
        fc += (
            f"concat=n={m}:v=1:a=1[v][a0];"
            "[a0]highpass=f=80,agate=threshold=0.02:ratio=2:attack=5:release=120,"
            "acompressor=threshold=-20dB:ratio=2.5:attack=5:release=120,"
            f"pan=stereo|c0=c0|c1=c0,loudnorm=I={args.lufs}:TP=-1.5:LRA=9[a]"
        )
        run(
            ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "256k", "-ar", "48000", args.saida]
        )
        base = os.path.splitext(args.saida)[0]
        with open(base + ".cortes.json", "w", encoding="utf-8") as f:
            json.dump({"fps": F, "quadros": total, "trechos": mapa}, f, ensure_ascii=False, indent=2)
        antes = sum(b - a for _, a, b in trechos)
        print(f"ok: {args.saida}  {total} quadros ({total / F:.2f} s; antes {antes:.2f} s)  trechos: {m}")
        print(f"mapa de cortes: {base}.cortes.json")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
