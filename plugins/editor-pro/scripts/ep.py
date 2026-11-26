"""
Editor Pro: um comando para tudo o que é conta (tempo, volume, cor, render). Imprime só resumos curtos.

  ep.py onde                                  caminhos do plugin e da config
  ep.py config [chave=valor ...]              config local (~/.editor-pro/config.json): clientes, deep_filter, sfx_extra
  ep.py novo <pasta> cliente=X modelo=Y tema="..."
  ep.py status <pasta>                        onde o vídeo está
  ep.py ver <pasta> <bloco>                   um bloco do estado (plano, takes...)
  ep.py set <pasta> <caminho.no.json> <valor>
  ep.py etapa <pasta> <etapa>=<status>        pendente | em_andamento | aguardando_aprovacao | concluido | nao_precisa
  ep.py pendencia <pasta> <etapa> "<texto>"   |  ep.py resolver <pasta> <id>
  ep.py inventario <pasta> <arquivos ou pastas...>
  ep.py converter <pasta> [arquivos...]       1080x1920, 30 fps CFR, rotação respeitada -> _CLAUDE/midia/
  ep.py folha <video> [--quadros 12] [--em 3.2 --grade] [-o saida.jpg]
  ep.py cor <videos...>                       mede brilho, temperatura e saturação; sugere a correção
  ep.py transcrever <pasta> [videos...]       Whisper local -> _CLAUDE/transcricao/<nome>.txt (por frase)
  ep.py frases <captions.json>                JSON de palavras -> .txt por frase
  ep.py voz <args do limpar_voz.py>           limpeza de voz + corte de silêncios (DeepFilterNet)
  ep.py instalar                              instala o Remotion uma vez (~/.editor-pro/base)
  ep.py remotion <pasta> [--atualizar]        cria _CLAUDE/remotion a partir do template (e liga a mídia)
  ep.py render <pasta> [--previa]             previa: _CLAUDE/previa.mp4 (escala 0.4) | final: _CLAUDE/final.mp4
  ep.py medir <arquivos> [--ini s --dur s] [--ganho 0.07]
  ep.py sfx [categoria] [--busca termo]       biblioteca de SFX (duração e tempo até o pico)
  ep.py sfx-indice <pasta>                    (manutenção) gera o indice.json de uma pasta de SFX
  ep.py conferir <pasta>                      checklist automático do roteiro (margens, viúva, buracos, sons...)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(PLUGIN, "template")
SFX = os.path.join(PLUGIN, "sfx")
HOME = os.path.join(os.path.expanduser("~"), ".editor-pro")
CONFIG = os.path.join(HOME, "config.json")
BASE = os.path.join(HOME, "base")  # node_modules do Remotion, instalado uma vez
ETAPAS = ["preparar", "plano", "montar", "som", "entregar"]
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".mts", ".3gp")
U = 8


# ---------------- util ----------------
def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def probe(arq):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", arq])
    return json.loads(r.stdout or "{}")


def duracao(arq):
    try:
        return float(probe(arq).get("format", {}).get("duration", 0))
    except Exception:
        return 0.0


def ler_json(p, padrao=None):
    try:
        with open(p, encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return padrao


def gravar_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def claude(pasta, *partes):
    return os.path.join(os.path.abspath(pasta), "_CLAUDE", *partes)


def config():
    return ler_json(CONFIG, {}) or {}


def valor(v):
    try:
        return json.loads(v)
    except Exception:
        return v


# ---------------- config ----------------
def cmd_onde(_):
    c = config()
    print(f"plugin: {PLUGIN}")
    print(f"template: {TEMPLATE}")
    print(f"config: {CONFIG} ({'ok' if c else 'ainda não existe'})")
    print(f"clientes: {c.get('clientes', '(não definido)')}")
    print(f"remotion base: {BASE} ({'instalado' if os.path.isdir(os.path.join(BASE, 'node_modules')) else 'falta: ep.py instalar'})")


def cmd_config(a):
    c = config()
    if not a:
        print(json.dumps(c, ensure_ascii=False, indent=1) if c else "sem config. Ex.: ep.py config clientes=\"C:/.../Clientes\"")
        return
    for kv in a:
        k, v = kv.split("=", 1)
        c[k] = valor(v)
    gravar_json(CONFIG, c)
    print("ok:", ", ".join(k.split("=")[0] for k in a))


# ---------------- estado ----------------
def estado(pasta):
    d = ler_json(claude(pasta, "projeto.json"))
    if d is None:
        raise SystemExit(f"sem projeto em {pasta}. Use: ep.py novo <pasta> cliente=... modelo=... tema=...")
    return d


def salvar(pasta, d):
    gravar_json(claude(pasta, "projeto.json"), d)


def mostrar_status(d):
    print(f"{d.get('cliente', '?')} · {d.get('modelo', '?')} · {d.get('tema', '')}")
    print("  " + " → ".join(f"{e}: {d['etapas'].get(e, 'pendente')}" for e in ETAPAS))
    comp = d.get("complementos")
    if comp:
        print(f"complementos: {', '.join(comp)}")
    pend = d.get("pendencias", [])
    for p in pend:
        print(f"  {p['id']} [{p['etapa']}] {p['texto']}")
    if not pend:
        print("pendências: nenhuma")


def cmd_novo(a):
    pasta, kvs = a[0], a[1:]
    if os.path.exists(claude(pasta, "projeto.json")):
        raise SystemExit("já existe projeto aqui. Use: ep.py status <pasta>")
    d = {"etapas": {e: "pendente" for e in ETAPAS}, "pendencias": [], "criado": time.strftime("%Y-%m-%d")}
    for kv in kvs:
        k, v = kv.split("=", 1)
        d[k] = valor(v)
    if d.get("modelo") == "reels-produto":
        d["etapas"]["som"] = "nao_precisa"  # som entra junto na montagem
    if d.get("modelo") == "motion":
        d["etapas"]["preparar"] = "nao_precisa"
    for sub in ("midia", "folhas", "transcricao", "_lixo"):
        os.makedirs(claude(pasta, sub), exist_ok=True)
    salvar(pasta, d)
    mostrar_status(d)


def cmd_status(a):
    mostrar_status(estado(a[0]))


def cmd_ver(a):
    print(json.dumps(estado(a[0]).get(a[1]), ensure_ascii=False, indent=1))


def cmd_set(a):
    d = estado(a[0])
    alvo, partes = d, a[1].split(".")
    for p in partes[:-1]:
        alvo = alvo.setdefault(p, {})
    alvo[partes[-1]] = valor(a[2])
    salvar(a[0], d)
    print("ok")


def cmd_etapa(a):
    d = estado(a[0])
    e, s = a[1].split("=")
    if e not in ETAPAS:
        raise SystemExit(f"etapa inválida: {e}")
    d["etapas"][e] = s
    salvar(a[0], d)
    print(f"ok: {e} = {s}")


def cmd_pendencia(a):
    d = estado(a[0])
    n = max([int(p["id"][1:]) for p in d["pendencias"]] + [0]) + 1
    d["pendencias"].append({"id": f"p{n:02d}", "etapa": a[1], "texto": a[2]})
    salvar(a[0], d)
    print(f"ok: p{n:02d}")


def cmd_resolver(a):
    d = estado(a[0])
    d["pendencias"] = [p for p in d["pendencias"] if p["id"] != a[1]]
    salvar(a[0], d)
    print("ok")


# ---------------- mídia ----------------
def listar_videos(itens):
    out = []
    for it in itens:
        if os.path.isdir(it):
            out += sorted(os.path.join(it, f) for f in os.listdir(it) if f.lower().endswith(VIDEO_EXT))
        elif os.path.isfile(it):
            out.append(it)
    return [os.path.abspath(v) for v in out]


def rotacao(st):
    for sd in st.get("side_data_list", []) or []:
        if "rotation" in sd:
            return int(float(sd["rotation"]))
    return int(float(st.get("tags", {}).get("rotate", 0)))


def cmd_inventario(a):
    pasta, vids = a[0], listar_videos(a[1:])
    if not vids:
        raise SystemExit("nenhum vídeo encontrado")
    linhas, alertas = [], []
    for v in vids:
        p = probe(v)
        vs = next((s for s in p.get("streams", []) if s.get("codec_type") == "video"), None)
        tem_audio = any(s.get("codec_type") == "audio" for s in p.get("streams", []))
        dur = float(p.get("format", {}).get("duration", 0))
        nome = os.path.basename(v)
        if not vs:
            linhas.append(f"{nome} | sem vídeo")
            continue
        w, h, rot = int(vs["width"]), int(vs["height"]), rotacao(vs)
        if abs(rot) in (90, 270):
            w, h = h, w
        num, den = (vs.get("r_frame_rate") or "0/1").split("/")
        anum, aden = (vs.get("avg_frame_rate") or "0/1").split("/")
        fps = float(num) / float(den or 1)
        afps = float(anum) / float(aden or 1) if float(aden or 1) else fps
        vfr = abs(fps - afps) > 0.5
        orient = "vertical" if h > w else "horizontal" if w > h else "quadrado"
        linhas.append(f"{nome} | {dur:.1f}s | {w}x{h} {orient}{f' rot{rot}' if rot else ''} | {afps:.2f} fps{' VFR' if vfr else ''} | {'áudio' if tem_audio else 'sem áudio'}")
        if orient != "vertical":
            alertas.append(f"{nome}: {orient} (vai ser recortado 9:16 no centro; confira o enquadramento)")
        if vfr:
            alertas.append(f"{nome}: fps variável (a conversão deixa em 30 CFR)")
        if min(w, h) < 720:
            alertas.append(f"{nome}: resolução baixa ({w}x{h})")
    os.makedirs(claude(pasta), exist_ok=True)
    with open(claude(pasta, "inventario.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    d = ler_json(claude(pasta, "projeto.json"))
    if d is not None:
        d["brutos"] = vids
        salvar(pasta, d)
    total = sum(duracao(v) for v in vids)
    print(f"ok: {len(vids)} arquivos, {total:.0f}s no total -> _CLAUDE/inventario.txt")
    for al in alertas[:10]:
        print("  alerta:", al)


def cmd_converter(a):
    pasta = a[0]
    vids = listar_videos(a[1:]) or estado(pasta).get("brutos", [])
    os.makedirs(claude(pasta, "midia"), exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
    feitos = 0
    for v in vids:
        saida = claude(pasta, "midia", os.path.splitext(os.path.basename(v))[0] + ".mp4")
        if os.path.exists(saida) and os.path.getmtime(saida) > os.path.getmtime(v):
            continue
        r = run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", saida])
        if r.returncode != 0:
            print(f"  erro em {os.path.basename(v)}: {r.stderr.strip()[-200:]}")
            continue
        feitos += 1
    print(f"ok: {feitos} convertidos ({len(vids) - feitos} já estavam prontos) -> _CLAUDE/midia/")


def cmd_folha(a):
    import argparse
    ap = argparse.ArgumentParser(prog="ep.py folha")
    ap.add_argument("video")
    ap.add_argument("--quadros", type=int, default=12)
    ap.add_argument("--em", type=float)
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("-o", "--saida")
    o = ap.parse_args(a)
    base = os.path.splitext(os.path.basename(o.video))[0]
    pasta = os.path.join(os.path.dirname(os.path.abspath(o.video)), "..", "folhas")
    pasta = os.path.normpath(pasta) if os.path.isdir(os.path.normpath(pasta)) else os.path.dirname(os.path.abspath(o.video))
    if o.em is not None:
        saida = o.saida or os.path.join(pasta, f"quadro-{base}-{o.em:g}.jpg")
        vf = ("drawgrid=w=iw:h=100:t=2:c=red@0.7," if o.grade else "") + "scale=360:-2"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(o.em), "-i", o.video, "-frames:v", "1", "-vf", vf, "-q:v", "4", saida]
    else:
        n = max(1, min(o.quadros, 30))
        cols = min(6, n)
        rows = -(-n // cols)
        intervalo = max(duracao(o.video) / n, 0.1)
        saida = o.saida or os.path.join(pasta, f"folha-{base}.jpg")
        vf = f"fps=1/{intervalo:.3f},scale=180:-2,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.5,tile={cols}x{rows}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", o.video, "-vf", vf, "-frames:v", "1", "-q:v", "5", saida]
    r = run(cmd)
    if r.returncode != 0 and "drawtext" in " ".join(cmd):  # ffmpeg sem fonte: tenta sem o tempo escrito
        cmd[cmd.index("-vf") + 1] = re.sub(r"drawtext=[^,]*,", "", cmd[cmd.index("-vf") + 1])
        r = run(cmd)
    if r.returncode != 0:
        raise SystemExit("ffmpeg falhou: " + r.stderr.strip()[-300:])
    print(saida)


def cmd_cor(a):
    for v in listar_videos(a):
        dur = duracao(v)
        r = run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={min(2, 8 / max(dur, 1)):.3f},scale=320:-2,signalstats,metadata=print:file=-",
                 "-an", "-f", "null", "-"])
        vals = {}
        for k in ("YAVG", "UAVG", "VAVG", "SATAVG", "YHIGH", "YLOW"):
            xs = [float(x) for x in re.findall(rf"lavfi\.signalstats\.{k}=([\d.]+)", r.stdout)]
            vals[k] = sum(xs) / len(xs) if xs else 0
        y, u, vv, sat = vals["YAVG"], vals["UAVG"], vals["VAVG"], vals["SATAVG"]
        quente = (vv - 128) - (u - 128)
        notas, filtros = [], []
        if quente > 8:
            notas.append(f"amarelado ({quente:+.0f})")
            filtros.append(f"colorchannelmixer=rr={max(0.94, 1 - quente / 400):.3f}:bb={min(1.08, 1 + quente / 300):.3f}")
        elif quente < -8:
            notas.append(f"azulado ({quente:+.0f})")
            filtros.append(f"colorchannelmixer=rr={min(1.06, 1 - quente / 400):.3f}:bb={max(0.94, 1 + quente / 300):.3f}")
        if y < 75:
            notas.append(f"escuro (Y {y:.0f})")
            filtros.append("curves=all='0/0 0.25/0.30 0.5/0.56 1/1'")
        elif y > 185:
            notas.append(f"claro demais (Y {y:.0f})")
            filtros.append("curves=all='0/0 0.5/0.46 1/0.97'")
        if sat < 18:
            notas.append(f"chapado (sat {sat:.0f})")
            filtros.append("eq=contrast=1.04:saturation=1.10")
        nome = os.path.basename(v)
        if notas:
            print(f"{nome}: {', '.join(notas)} -> -vf \"{','.join(filtros)}\"")
        else:
            print(f"{nome}: ok (Y {y:.0f}, temp {quente:+.0f}, sat {sat:.0f}) -> sem correção")


# ---------------- fala ----------------
def palavras(dados):
    if isinstance(dados, dict):
        for chave in ("captions", "words", "segments", "transcription", "chunks"):
            if isinstance(dados.get(chave), list):
                return palavras(dados[chave])
        return []
    saida = []
    for p in dados:
        texto = (p.get("text") or p.get("word") or "").strip()
        if not texto:
            continue
        if "startMs" in p:
            ini, fim = p["startMs"] / 1000, p.get("endMs", p["startMs"]) / 1000
        elif "offsets" in p:
            ini, fim = p["offsets"]["from"] / 1000, p["offsets"]["to"] / 1000
        else:
            ini, fim = float(p.get("start", 0)), float(p.get("end", p.get("start", 0)))
        saida.append((ini, fim, texto))
    return saida


def frases(arq_json, pausa=0.45, maximo=14):
    ws = palavras(ler_json(arq_json, []))
    linhas, atual = [], []
    for w in ws:
        if atual and (w[0] - atual[-1][1] > pausa or len(atual) >= maximo):
            linhas.append(atual)
            atual = []
        atual.append(w)
    if atual:
        linhas.append(atual)
    mmss = lambda t: f"{int(t // 60):02d}:{t % 60:05.2f}"
    texto = "\n".join(f"[{mmss(l[0][0])}-{mmss(l[-1][1])}] " + " ".join(w[2] for w in l) for l in linhas)
    saida = os.path.splitext(arq_json)[0] + ".txt"
    with open(saida, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    return saida, len(ws), len(linhas)


def cmd_frases(a):
    s, n, l = frases(a[0])
    print(f"ok: {s} ({n} palavras, {l} frases)")


def precisa_base():
    if not os.path.isdir(os.path.join(BASE, "node_modules", "remotion")):
        raise SystemExit("O Remotion ainda não está instalado. Rode: ep.py instalar (uma vez só, ~2 min)")


def cmd_transcrever(a):
    precisa_base()
    pasta = a[0]
    vids = listar_videos(a[1:]) or listar_videos([claude(pasta, "midia")])
    destino = claude(pasta, "transcricao")
    os.makedirs(destino, exist_ok=True)
    script = os.path.join(BASE, "scripts", "transcrever.mjs")
    for v in vids:
        r = run(["node", script, v], cwd=BASE)
        js = os.path.splitext(v)[0] + ".json"
        if r.returncode != 0 or not os.path.exists(js):
            print(f"  erro em {os.path.basename(v)}: {(r.stderr or r.stdout).strip()[-300:]}")
            continue
        final = os.path.join(destino, os.path.basename(js))
        shutil.move(js, final)
        s, n, l = frases(final)
        motor = re.search(r"motor (\w+)", r.stdout)
        print(f"ok: {os.path.basename(s)} ({n} palavras, {l} frases{', ' + motor.group(1) if motor else ''})")


def cmd_voz(a):
    r = subprocess.run([sys.executable, os.path.join(PLUGIN, "scripts", "limpar_voz.py")] + a)
    sys.exit(r.returncode)


# ---------------- remotion ----------------
def ligar(link, alvo):
    if os.path.exists(link):
        return
    if os.name == "nt":
        r = run(["cmd", "/c", "mklink", "/J", link, alvo])
        if r.returncode != 0:
            raise SystemExit("não consegui ligar o node_modules: " + r.stderr.strip())
    else:
        os.symlink(alvo, link, target_is_directory=True)


def cmd_instalar(_):
    os.makedirs(os.path.join(BASE, "scripts"), exist_ok=True)
    shutil.copy2(os.path.join(TEMPLATE, "package.json"), os.path.join(BASE, "package.json"))
    shutil.copy2(os.path.join(TEMPLATE, "scripts", "transcrever.mjs"), os.path.join(BASE, "scripts", "transcrever.mjs"))
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        raise SystemExit("npm não encontrado: instale o Node.js 18+ (Windows: winget install OpenJS.NodeJS.LTS)")
    t0 = time.time()
    log = os.path.join(BASE, "instalar.log")
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        r = subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=BASE, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        with open(log, encoding="utf-8", errors="replace") as f:
            print("ERRO no npm install. Últimas linhas:\n" + "".join(f.readlines()[-10:]))
        sys.exit(1)
    print(f"ok: Remotion instalado em {BASE} ({time.time() - t0:.0f}s)")


def cmd_remotion(a):
    precisa_base()
    pasta = a[0]
    dest = claude(pasta, "remotion")
    novo = not os.path.isdir(os.path.join(dest, "src"))
    if novo:
        shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns("node_modules", ".work"))
        ligar(os.path.join(dest, "node_modules"), os.path.join(BASE, "node_modules"))
    elif "--atualizar" in a:
        # traz os componentes da versão atual do plugin; extras.tsx e roteiro.json do vídeo ficam
        for raiz, _, fs in os.walk(os.path.join(TEMPLATE, "src")):
            for f in fs:
                if f == "extras.tsx":
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), TEMPLATE)
                os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
                shutil.copy2(os.path.join(TEMPLATE, rel), os.path.join(dest, rel))
        print("componentes atualizados (extras.tsx e roteiro.json mantidos)")
    # public/ não aceita atalho (o Remotion copia a pasta a cada render): hardlink de cada arquivo, sem gastar disco.
    midia, pub = claude(pasta, "midia"), os.path.join(dest, "public", "midia")
    n = 0
    if os.path.isdir(midia):
        os.makedirs(pub, exist_ok=True)
        for f in os.listdir(midia):
            src, dst = os.path.join(midia, f), os.path.join(pub, f)
            if os.path.isfile(src) and not os.path.exists(dst):
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copy2(src, dst)
                n += 1
    print(f"ok: {dest} ({'criado' if novo else 'já existia'}; {n} arquivo(s) novos em public/midia/)")


def cmd_render(a):
    pasta = a[0]
    previa = "--previa" in a
    proj = claude(pasta, "remotion")
    if not os.path.isdir(proj):
        raise SystemExit("sem projeto Remotion. Rode: ep.py remotion <pasta>")
    saida = claude(pasta, "previa.mp4" if previa else "final.mp4")  # uma só versão: sobrescreve
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    cmd = [npx, "remotion", "render", "src/index.ts", "Video", saida, "--log=warn"] + (["--scale=0.4"] if previa else [])
    os.makedirs(os.path.join(proj, ".work"), exist_ok=True)
    log = os.path.join(proj, ".work", "render.log")
    t0 = time.time()
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        r = subprocess.run(cmd, cwd=proj, stdout=f, stderr=subprocess.STDOUT)
    seg = time.time() - t0
    if r.returncode != 0:
        with open(log, encoding="utf-8", errors="replace") as f:
            linhas = [l.rstrip() for l in f if l.strip() and not l.lstrip().startswith("at ")]
        if any("chrome-headless-shell" in l and "ENOENT" in l for l in linhas):
            print("ERRO: caminho longo demais para o Chrome headless. Aponte o navegador em remotion.config.ts.")
        else:
            print(f"ERRO no render ({seg:.0f}s). Últimas linhas:\n" + "\n".join(linhas[-12:]))
        sys.exit(1)
    print(f"ok: {saida} ({os.path.getsize(saida) / 1e6:.1f} MB, {duracao(saida):.2f}s) em {seg:.0f}s")


# ---------------- som ----------------
def medir(arq, ini=None, dur=None, ganho=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if ini is not None:
        cmd += ["-ss", str(ini)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    af = (f"volume={ganho}," if ganho else "") + "ebur128=peak=true"
    cmd += ["-i", arq, "-map", "a:0", "-af", af, "-f", "null", "-"]
    r = run(cmd)
    resumo = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else ""
    if not resumo:
        return f"{os.path.basename(arq)}: sem áudio ou erro"
    pega = lambda rot: (re.search(rot + r":\s*(-?[\d.]+|-inf)", resumo) or [None, "?"])[1]
    return f"{os.path.basename(arq)}{f' (ganho {ganho})' if ganho else ''}: {pega('I')} LUFS | pico {pega('Peak')} dBTP | faixa {pega('LRA')} LU"


def cmd_medir(a):
    import argparse
    ap = argparse.ArgumentParser(prog="ep.py medir")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--ini", type=float)
    ap.add_argument("--dur", type=float)
    ap.add_argument("--ganho", type=float, help="mesmo volume do roteiro (ex.: 0.07) para medir a trilha isolada")
    o = ap.parse_args(a)
    for f in o.arquivos:
        print(medir(f, o.ini, o.dur, o.ganho))


def pico_sfx(arq):
    """duração útil e tempo até o pico (s), lendo o envelope de 10 em 10 ms."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True)
    import array
    amostras = array.array("h", r.stdout[: len(r.stdout) // 2 * 2])
    if not amostras:
        return 0, 0, -99
    bloco = 80
    env = [max(abs(x) for x in amostras[i:i + bloco]) for i in range(0, len(amostras), bloco)]
    topo = max(env) or 1
    ini = next((i for i, e in enumerate(env) if e > topo * 0.05), 0)
    fim = len(env) - next((i for i, e in enumerate(reversed(env)) if e > topo * 0.05), 0)
    pico = env.index(topo)
    import math
    return round((fim - ini) * 0.01, 2), round((pico - ini) * 0.01, 2), round(20 * math.log10(topo / 32768), 1)


def cmd_sfx_indice(a):
    pasta = os.path.abspath(a[0])
    itens = []
    for raiz, _, fs in os.walk(pasta):
        for f in sorted(fs):
            if f.lower().endswith((".mp3", ".wav", ".ogg", ".m4a")):
                p = os.path.join(raiz, f)
                dur, pico, db = pico_sfx(p)
                itens.append({"arquivo": os.path.relpath(p, pasta).replace("\\", "/"), "categoria": os.path.relpath(raiz, pasta).split(os.sep)[0],
                              "dur": dur, "pico": pico, "db": db})
    gravar_json(os.path.join(pasta, "indice.json"), {"sons": itens})
    print(f"ok: {len(itens)} sons -> {os.path.join(pasta, 'indice.json')}")


def cmd_sfx(a):
    pastas = [SFX] + ([config()["sfx_extra"]] if config().get("sfx_extra") else [])
    busca = a[a.index("--busca") + 1].lower() if "--busca" in a else None
    cat = a[0] if a and not a[0].startswith("--") else None
    total = 0
    for p in pastas:
        ind = ler_json(os.path.join(p, "indice.json"))
        if not ind:
            print(f"(sem índice em {p}: ep.py sfx-indice \"{p}\")")
            continue
        sons = ind["sons"]
        if not cat and not busca:
            cats = {}
            for s in sons:
                cats[s["categoria"]] = cats.get(s["categoria"], 0) + 1
            print(f"{p}: " + ", ".join(f"{c} ({n})" for c, n in sorted(cats.items())))
            continue
        for s in sons:
            if (cat and s["categoria"] != cat) or (busca and busca not in s["arquivo"].lower()):
                continue
            total += 1
            print(f"{os.path.join(p, s['arquivo'])} | {s['dur']}s | pico em {s['pico']}s | {s['db']} dB")
    if cat or busca:
        print(f"({total} sons) No roteiro: copie para public/sfx/ e use \"pico\" para alinhar o pico no tempo da ação.")


# ---------------- conferência ----------------
def cmd_conferir(a):
    pasta = a[0]
    proj = claude(pasta, "remotion")
    rot = ler_json(os.path.join(proj, "public", "roteiro.json"))
    if rot is None:
        raise SystemExit("sem roteiro.json")
    fps, W, H = rot["fps"], rot["largura"], rot["altura"]
    total = rot["duracao"]
    q = lambda s: round(s * fps)
    prob, info = [], []
    pub = os.path.join(proj, "public")

    def existe(arq, oque):
        if arq and not os.path.exists(os.path.join(pub, arq)):
            prob.append(f"{oque}: arquivo não existe em public/ ({arq})")

    # duração x base
    if rot.get("base"):
        existe(rot["base"]["arquivo"], "base")
        tr = rot["base"].get("trechos", [])
        if tr:
            fim_base = (tr[-1]["quadro_saida"] + tr[-1]["quadros"]) / fps
            if abs(fim_base - total) > 0.5 and not rot.get("fecho"):
                prob.append(f"duração {total:.2f}s ≠ base {fim_base:.2f}s (sobra tela parada ou corta fala)")
    # buracos entre clipes
    clipes = sorted(rot.get("clipes") or [], key=lambda c: c["inicio"])
    for c in clipes:
        existe(c["arquivo"], "clipe")
    if clipes and not rot.get("base"):
        if clipes[0]["inicio"] > 0.05:
            prob.append(f"quadro 0 vazio: o primeiro clipe começa em {clipes[0]['inicio']}s")
        for x, y in zip(clipes, clipes[1:]):
            if y["inicio"] - x["fim"] > 1 / fps:
                prob.append(f"buraco de {y['inicio'] - x['fim']:.2f}s entre clipes em {x['fim']}s")
        if clipes[-1]["fim"] < total - 0.05 and not rot.get("fecho"):
            prob.append(f"fim sem imagem: último clipe acaba em {clipes[-1]['fim']}s de {total}s")
    # textos
    textos = sorted(rot.get("textos") or [], key=lambda t: t["inicio"])
    for t in textos:
        linhas = [l.split() for l in t["texto"].split("|")]
        n = sum(len(l) for l in linhas)
        if n > 1 and any(len(l) == 1 for l in linhas):
            prob.append(f"viúva em {t['inicio']}s: \"{t['texto']}\" (uma palavra sozinha na linha)")
        if len(linhas) == 1 and n > 4 and t.get("tipo") != "legenda":
            info.append(f"texto longo numa linha só em {t['inicio']}s (quebre com \" | \")")
        if t.get("tempos") and len(t["tempos"]) != n:
            prob.append(f"texto em {t['inicio']}s: {n} palavras e {len(t['tempos'])} tempos")
        y = t.get("y", rot["faixaY"])
        if not t.get("centro") and (y < 220 or y > H - 450):
            info.append(f"texto em {t['inicio']}s fora da faixa segura (y {y}); o template corrige, mas confira o rosto")
        if t["fim"] - t["inicio"] < 0.8:
            prob.append(f"texto em {t['inicio']}s fica só {t['fim'] - t['inicio']:.2f}s (não dá tempo de ler)")
    for x, y in zip(textos, textos[1:]):
        mesma_faixa = not x.get("centro") and not y.get("centro") and x.get("y", rot["faixaY"]) == y.get("y", rot["faixaY"])
        if y["inicio"] < x["fim"] - 0.01 and mesma_faixa:
            prob.append(f"textos colidindo: {x['inicio']}s e {y['inicio']}s na mesma faixa")
    # texto entrando bem na transição
    for tr in rot.get("transicoes") or []:
        for t in textos:
            if t["inicio"] < tr["t"] < t["fim"] and tr["tipo"] in ("camera", "zoom") and abs(tr["t"] - t["fim"]) > U / fps:
                info.append(f"texto em {t['inicio']}s atravessa a transição {tr['tipo']} de {tr['t']}s (confira colisão)")
    # peças
    for p in rot.get("pecas") or []:
        pr = p.get("props", {})
        x, y = pr.get("x", W / 2), pr.get("y", rot["faixaY"])
        if y < 220 or y > H - 450 or x < 35 or x > W - 35:
            prob.append(f"peça {p['nome']} em {p['inicio']}s fora das margens (x {x}, y {y})")
        if p["nome"] == "Contador" and (q(p["fim"]) - q(p["inicio"])) < U * 2 + 24 + U:
            prob.append(f"contador em {p['inicio']}s curto demais (precisa contar e segurar 24 quadros)")
        for k in ("inicio", "fim"):
            if q(p[k]) % 4:
                info.append(f"peça {p['nome']} {k} {p[k]}s não cai em múltiplo de 4 quadros")
    # sons
    vistos = {}
    for s in sorted(rot.get("sfx") or [], key=lambda s: s["t"]):
        existe(s["arquivo"], "sfx")
        if s["arquivo"] in vistos and s["t"] - vistos[s["arquivo"]] < 20:
            info.append(f"mesmo SFX repetido em menos de 20s ({os.path.basename(s['arquivo'])} em {s['t']}s)")
        vistos[s["arquivo"]] = s["t"]
        if s.get("volume", 0.5) > 1:
            prob.append(f"sfx em {s['t']}s com volume {s['volume']} (> 1 estoura)")
    if rot.get("trilha"):
        existe(rot["trilha"]["arquivo"], "trilha")
        if rot["trilha"]["volume"] < 0.03:
            prob.append(f"trilha com volume {rot['trilha']['volume']}: provavelmente inaudível (meça com ep.py medir --ganho)")
    if not rot.get("fecho"):
        info.append("sem fecho: confira que o final não tem microcorte")
    trs = sorted(rot.get("transicoes") or [], key=lambda t: t["t"])
    for x, y in zip(trs, trs[1:]):
        if x["tipo"] == y["tipo"] and x["tipo"] != "corte":
            info.append(f"transição {x['tipo']} repetida em sequência ({x['t']}s e {y['t']}s)")
    print(f"conferência: {len(prob)} problema(s), {len(info)} aviso(s)")
    for p in prob[:12]:
        print("  ✗", p)
    for i in info[:8]:
        print("  ·", i)
    if not prob:
        print("  ok nos itens automáticos. Falta conferir na folha: rosto livre, texto fluido, sílaba solta.")


CMDS = {
    "onde": cmd_onde, "config": cmd_config, "novo": cmd_novo, "status": cmd_status, "ver": cmd_ver, "set": cmd_set,
    "etapa": cmd_etapa, "pendencia": cmd_pendencia, "resolver": cmd_resolver, "inventario": cmd_inventario,
    "converter": cmd_converter, "folha": cmd_folha, "cor": cmd_cor, "transcrever": cmd_transcrever, "frases": cmd_frases,
    "voz": cmd_voz, "instalar": cmd_instalar, "remotion": cmd_remotion, "render": cmd_render, "medir": cmd_medir,
    "sfx": cmd_sfx, "sfx-indice": cmd_sfx_indice, "conferir": cmd_conferir,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
