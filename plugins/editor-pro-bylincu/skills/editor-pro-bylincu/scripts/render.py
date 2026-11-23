"""
Renderiza no Remotion guardando o log em arquivo. Imprime só o resultado (ou as últimas linhas do erro).
O log de progresso do Remotion tem milhares de linhas: nunca leia ele inteiro.

Uso (dentro da pasta do projeto Remotion):
  python render.py <Composicao> <saida.mp4> [--preview] [--entrada src/index.ts] [-- args extras do remotion]
  --preview  = --scale=0.4 (conferência rápida)
"""
import argparse
import os
import shutil
import subprocess
import sys
import time


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    extras = []
    if "--" in argv:
        i = argv.index("--")
        argv, extras = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("composicao")
    ap.add_argument("saida")
    ap.add_argument("--entrada", default="src/index.ts")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args(argv)

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise SystemExit("npx não encontrado (instale o Node.js).")
    cmd = [npx, "remotion", "render", a.entrada, a.composicao, a.saida, "--log=warn"]
    if a.preview:
        cmd.append("--scale=0.4")
    cmd += extras

    os.makedirs(".work", exist_ok=True)
    log = os.path.join(".work", "render.log")
    t0 = time.time()
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    seg = time.time() - t0
    if r.returncode != 0:
        with open(log, encoding="utf-8", errors="replace") as f:
            linhas = [l.rstrip() for l in f if l.strip()]
        texto = "\n".join(linhas)
        if "chrome-headless-shell" in texto and "ENOENT" in texto:
            print(f"ERRO no render: caminho longo demais para o Chrome headless ({len(os.getcwd())} caracteres na pasta). "
                  "Use um estúdio num caminho curto (padrão ~/Videos/Edicao) ou aponte o navegador em remotion.config.ts.")
            sys.exit(1)
        linhas = [l for l in linhas if not l.lstrip().startswith("at ")]
        print(f"ERRO no render ({seg:.0f}s). Últimas linhas de {log}:")
        print("\n".join(linhas[-12:]))
        sys.exit(1)
    dur = ""
    if shutil.which("ffprobe"):
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.saida],
                           capture_output=True, text=True)
        if p.stdout.strip():
            dur = f", {float(p.stdout):.2f}s de vídeo"
    tam = os.path.getsize(a.saida) / 1e6 if os.path.exists(a.saida) else 0
    print(f"ok: {a.saida} ({tam:.1f} MB{dur}) em {seg:.0f}s. Log: {log}")


if __name__ == "__main__":
    main()
