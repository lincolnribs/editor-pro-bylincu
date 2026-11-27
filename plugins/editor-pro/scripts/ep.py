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
  ep.py converter <pasta> [arquivos...]       1080x1920, 30 fps CFR, rotação respeitada -> _EDITOR-PRO/midia/
  ep.py folha <video> [--quadros 12] [--em 3.2 --grade] [-o saida.jpg]
  ep.py cor <videos...>                       mede brilho, temperatura e saturação; sugere a correção
  ep.py transcrever <pasta> [videos...]       Whisper local -> _EDITOR-PRO/transcricao/<nome>.txt (por frase)
  ep.py frases <captions.json>                JSON de palavras -> .txt por frase
  ep.py voz <args do limpar_voz.py>           limpeza de voz + corte de silêncios (DeepFilterNet)
  ep.py doctor                                confere em segundos o que falta no computador
  ep.py instalar [motor|transcricao]          instala o motor raea (fixo, checksum) e a transcrição local
  ep.py projeto <pasta> [--atualizar]         cria _EDITOR-PRO/edicao (projeto raea) a partir do template e liga a mídia
  ep.py tempos <pasta>                        acha cada texto do roteiro na fala e preenche inicio, tempos e fim
  ep.py mixar <pasta> [--final]               voz + SFX + trilha só com FFmpeg (segundos), sem re-renderizar a imagem
  ep.py marca <pasta>                         design.json do cliente (cores, fontes, zonas proibidas); cria o modelo se faltar
  ep.py render <pasta> [--previa] [--forcar]  confere, renderiza a imagem no raea (GPU) e mixa o som: previa.mp4 | final.mp4
  ep.py checar <pasta> [--final]              raea check: volume, congelado, área segura, leitura, legenda fora da palavra
  ep.py medir <arquivos> [--ini s --dur s] [--ganho 0.07]
  ep.py sfx [categoria] [--busca termo]       biblioteca de SFX (duração e tempo até o pico)
  ep.py sfx-indice <pasta>                    (manutenção) gera o indice.json de uma pasta de SFX
  ep.py conferir <pasta>                      checklist automático do roteiro (margens, viúva, buracos, variação, sons...)
  ep.py historico <pasta> [--gravar]          o que os últimos vídeos do cliente já usaram (para não repetir)
  ep.py revisar <pasta> [--final]             tiras de quadros seguidos em cada entrada/transição (revisão de diretor de arte)
  ep.py alinhar <captions.json> <video>       ajusta o início das palavras pelo ataque da voz (o transcrever já faz)
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
BASE = os.path.join(HOME, "base")  # transcrição local (Whisper), instalada uma vez
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
    if os.path.dirname(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


PASTA_TRABALHO = "_EDITOR-PRO"  # visível de propósito (a prévia mora aqui); projetos antigos em _CLAUDE continuam funcionando


def trabalho(pasta, *partes):
    raiz = os.path.abspath(pasta)
    antiga = os.path.join(raiz, "_CLAUDE")
    nome = "_CLAUDE" if os.path.isdir(antiga) and not os.path.isdir(os.path.join(raiz, PASTA_TRABALHO)) else PASTA_TRABALHO
    return os.path.join(raiz, nome, *partes)


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
    print(f"motor raea: {raea_exe() or 'falta: ep.py instalar motor'}")
    print(f"transcrição: {BASE} ({'instalada' if os.path.isdir(os.path.join(BASE, 'node_modules')) else 'falta: ep.py instalar transcricao'})")


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
    d = ler_json(trabalho(pasta, "projeto.json"))
    if d is None:
        raise SystemExit(f"sem projeto em {pasta}. Use: ep.py novo <pasta> cliente=... modelo=... tema=...")
    return d


def salvar(pasta, d):
    gravar_json(trabalho(pasta, "projeto.json"), d)


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
    if os.path.exists(trabalho(pasta, "projeto.json")):
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
        os.makedirs(trabalho(pasta, sub), exist_ok=True)
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
    os.makedirs(trabalho(pasta), exist_ok=True)
    with open(trabalho(pasta, "inventario.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    d = ler_json(trabalho(pasta, "projeto.json"))
    if d is not None:
        d["brutos"] = vids
        salvar(pasta, d)
    total = sum(duracao(v) for v in vids)
    print(f"ok: {len(vids)} arquivos, {total:.0f}s no total -> _EDITOR-PRO/inventario.txt")
    for al in alertas[:10]:
        print("  alerta:", al)


def cmd_converter(a):
    pasta = a[0]
    vids = listar_videos(a[1:]) or estado(pasta).get("brutos", [])
    os.makedirs(trabalho(pasta, "midia"), exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1"
    feitos = 0
    for v in vids:
        saida = trabalho(pasta, "midia", os.path.splitext(os.path.basename(v))[0] + ".mp4")
        if os.path.exists(saida) and os.path.getmtime(saida) > os.path.getmtime(v):
            continue
        r = run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", saida])
        if r.returncode != 0:
            print(f"  erro em {os.path.basename(v)}: {r.stderr.strip()[-200:]}")
            continue
        feitos += 1
    print(f"ok: {feitos} convertidos ({len(vids) - feitos} já estavam prontos) -> _EDITOR-PRO/midia/")


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


def envelope_db(video, passo=0.01):
    """Energia do áudio (dB) a cada 10 ms, mono 16 kHz."""
    import array, math
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True)
    am = array.array("h", r.stdout[: len(r.stdout) // 2 * 2])
    n = int(16000 * passo)
    env = []
    for i in range(0, len(am), n):
        bloco = am[i:i + n]
        rms = math.sqrt(sum(x * x for x in bloco) / max(1, len(bloco))) or 1
        env.append(20 * math.log10(rms / 32768))
    return env


def ataques(env):
    """Momentos (em blocos de 10 ms) em que a voz começa depois de um vale: sobe 8 dB ou mais em até 60 ms."""
    piso = sorted(env)[len(env) // 10] if env else -90
    out, i = [], 3
    while i < len(env) - 6:
        if env[i] < piso + 18 and env[i] <= min(env[i - 3:i + 1]):
            sobe = next((j for j in range(i + 1, min(len(env), i + 7)) if env[j] >= env[i] + 8), None)
            if sobe is not None:
                out.append(sobe)
                i = sobe + 5
                continue
        i += 1
    return out


def alinhar(arq_json, video):
    """Corrige o início de cada palavra pelo ataque da voz. Medido: o Whisper marca as palavras 130–560 ms DEPOIS
    da hora (média ~300 ms), e é isso que deixa a legenda atrasada. Duas fases:
    1) atraso sistemático = mediana da distância até o ataque anterior mais próximo; todas as palavras voltam esse tanto;
    2) cada palavra encaixa no ataque mais próximo (±150 ms), sem passar da palavra anterior."""
    import bisect
    dados = ler_json(arq_json, [])
    lista = dados if isinstance(dados, list) else dados.get("captions", [])
    if not lista or "startMs" not in lista[0]:
        return 0, 0
    env = envelope_db(video)
    at = [a / 100 for a in ataques(env)]
    if not at:
        return 0, 0
    inicios = [p["startMs"] / 1000 for p in lista]
    difs = []
    for s in inicios:
        k = bisect.bisect_right(at, s + 0.03) - 1
        if k >= 0 and s - at[k] <= 0.75:
            difs.append(s - at[k])
    atraso = sorted(difs)[len(difs) // 2] if len(difs) >= 3 else 0.0

    # Casamento em ordem (programação dinâmica): cada palavra pega um ataque diferente, sempre para a frente,
    # entre 50 ms depois e 800 ms antes do tempo do Whisper, com custo = distância do atraso típico.
    # Palavra sem ataque possível (fala colada) fica com o tempo do Whisper menos o atraso típico.
    SEM = 0.25
    W, A = len(inicios), len(at)
    INF = float("inf")
    custo = [[INF] * (A + 1) for _ in range(W)]  # coluna A = "sem ataque"; guarda o último ataque usado
    volta = [[None] * (A + 1) for _ in range(W)]
    for i, s in enumerate(inicios):
        anteriores = [(0.0, -1)] if i == 0 else [(custo[i - 1][j], j) for j in range(A + 1) if custo[i - 1][j] < INF]
        for c_ant, j_ant in anteriores:
            ultimo = -1 if j_ant in (-1,) else j_ant
            if j_ant == A:  # anterior sem ataque: herda o último ataque usado antes dele
                ultimo = volta[i - 1][A][1] if volta[i - 1][A] else -1
            # opção sem ataque
            if c_ant + SEM < custo[i][A]:
                custo[i][A] = c_ant + SEM
                volta[i][A] = (j_ant, ultimo)
            for j in range(max(0, ultimo + 1), A):
                d = s - at[j]
                if d > 0.8:
                    continue
                if d < -0.05:
                    break
                c = c_ant + abs(d - atraso)
                if c < custo[i][j]:
                    custo[i][j] = c
                    volta[i][j] = (j_ant, j)
    j = min(range(A + 1), key=lambda k: custo[W - 1][k])
    escolha = [None] * W
    for i in range(W - 1, -1, -1):
        escolha[i] = j
        j = volta[i][j][0] if volta[i][j] else -1
    mudou, soma, anterior = 0, 0.0, -1.0
    for p, s, j in zip(lista, inicios, escolha):
        novo = at[j] if j is not None and 0 <= j < A else max(s - atraso, anterior + 0.06)
        novo = max(0.0, novo - 0.01)
        if abs(novo - s) >= 0.02:
            mudou += 1
            soma += abs(novo - s)
        dur = max(0.04, (p.get("endMs", p["startMs"]) - p["startMs"]) / 1000)
        p["startMs"] = round(novo * 1000)
        p["endMs"] = round((novo + dur) * 1000)
        anterior = novo
    gravar_json(arq_json, dados)
    return mudou, (soma / mudou * 1000 if mudou else 0)


def cmd_alinhar(a):
    m, media = alinhar(a[0], a[1])
    print(f"ok: {m} inícios de palavra ajustados (média {media:.0f} ms)")


def cmd_frases(a):
    s, n, l = frases(a[0])
    print(f"ok: {s} ({n} palavras, {l} frases)")


# ---------------- motor (raea) e transcrição ----------------
RAEA_VERSAO = "0.1.11"  # fixa: só subir depois de testar o template na versão nova
RAEA_SHA256 = {"windows-x86_64": "1ae7a26d092f0a49252a50875d841e547064bd5935092e01ed848039b01eea5c"}
PACOTE_TRANSCRICAO = {
    "name": "editor-pro-transcricao", "private": True, "type": "module",
    "dependencies": {"@remotion/install-whisper-cpp": "4.0.536", "@remotion/whisper-webgpu": "4.0.536", "@huggingface/transformers": "4.2.0"},
}


def raea_exe():
    """Onde está o raea: config > ~/.raea > PATH."""
    c = config().get("raea")
    if c and os.path.exists(c):
        return c
    exe = os.path.join(os.path.expanduser("~"), ".raea", "bin", "raea.exe" if os.name == "nt" else "raea")
    if os.path.exists(exe):
        return exe
    return shutil.which("raea")


def precisa_raea():
    exe = raea_exe()
    if not exe:
        raise SystemExit("O motor raea não está instalado. Rode: ep.py instalar motor (uma vez, ~335 MB)")
    return exe


def raea(args, cwd, log, timeout=None):
    """Roda o raea com o log em arquivo (nunca no chat). Devolve (código, linhas úteis do log)."""
    env = dict(os.environ, RAEA_OFFLINE="1", NO_COLOR="1")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        r = subprocess.run([precisa_raea()] + args, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env, timeout=timeout)
    with open(log, encoding="utf-8", errors="replace") as f:
        ruido = ("OpenH264", "Vello bump", "symphonia", "the rule ", "[WARN")
        linhas = [l.rstrip() for l in f if l.strip() and not any(x in l for x in ruido)]
    return r.returncode, linhas


def precisa_transcricao():
    if not os.path.isdir(os.path.join(BASE, "node_modules", "@remotion", "install-whisper-cpp")):
        raise SystemExit("A transcrição ainda não está instalada. Rode: ep.py instalar transcricao (uma vez, ~2 min)")


def cmd_transcrever(a):
    precisa_transcricao()
    pasta = a[0]
    vids = listar_videos(a[1:]) or listar_videos([trabalho(pasta, "midia")])
    destino = trabalho(pasta, "transcricao")
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
        m, media = alinhar(final, v)  # início de cada palavra pelo ataque da voz
        s, n, l = frases(final)
        motor = re.search(r"motor (\w+)", r.stdout)
        print(f"ok: {os.path.basename(s)} ({n} palavras, {l} frases{', ' + motor.group(1) if motor else ''}; {m} inícios ajustados, média {media:.0f} ms)")


def cmd_voz(a):
    r = subprocess.run([sys.executable, os.path.join(PLUGIN, "scripts", "limpar_voz.py")] + a)
    sys.exit(r.returncode)


def instalar_transcricao():
    os.makedirs(os.path.join(BASE, "scripts"), exist_ok=True)
    gravar_json(os.path.join(BASE, "package.json"), PACOTE_TRANSCRICAO)
    shutil.copy2(os.path.join(PLUGIN, "scripts", "transcrever.mjs"), os.path.join(BASE, "scripts", "transcrever.mjs"))
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
    print(f"ok: transcrição instalada em {BASE} ({time.time() - t0:.0f}s)")


def instalar_motor():
    """Baixa o raea fixo (RAEA_VERSAO) do GitHub, confere o SHA-256 e extrai em ~/.raea (sem script e sem skill automática)."""
    import hashlib, urllib.request, zipfile, tempfile
    if os.name != "nt":
        raise SystemExit("Fora do Windows, instale pelo site oficial: curl -fsSL https://raea.io/install | RAEA_NO_SKILLS=1 sh")
    alvo = os.path.join(os.path.expanduser("~"), ".raea")
    if os.path.exists(os.path.join(alvo, "bin", "raea.exe")):
        r = run([os.path.join(alvo, "bin", "raea.exe"), "--version"])
        print(f"já instalado: raea {r.stdout.strip()} em {alvo}")
        return
    nome = f"raea-{RAEA_VERSAO}-windows-x86_64.zip"
    url = f"https://github.com/shinyobjectz/raea/releases/download/v{RAEA_VERSAO}/{nome}"
    tmp = tempfile.mkdtemp(prefix="raea-")
    zipp = os.path.join(tmp, nome)
    print(f"baixando {nome} (~335 MB)...", flush=True)
    for tentativa in range(4):
        try:
            urllib.request.urlretrieve(url, zipp)
            break
        except Exception as e:
            if tentativa == 3:
                raise SystemExit(f"download falhou: {e}")
    h = hashlib.sha256()
    with open(zipp, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    if h.hexdigest() != RAEA_SHA256["windows-x86_64"]:
        raise SystemExit("o arquivo baixado não confere (SHA-256 diferente): nada foi instalado")
    with zipfile.ZipFile(zipp) as z:
        z.extractall(tmp)
    shutil.move(os.path.join(tmp, "raea"), alvo)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"ok: raea {RAEA_VERSAO} em {alvo} (checksum conferido)")


def cmd_instalar(a):
    oque = a[0] if a else "tudo"
    if oque in ("motor", "tudo"):
        instalar_motor()
    if oque in ("transcricao", "tudo"):
        instalar_transcricao()


def cmd_doctor(_):
    """Confere em segundos o que o Editor Pro precisa. Uma linha por item."""
    import platform
    exe = raea_exe()
    rv = run([exe, "--version"]).stdout.strip() if exe else ""
    node = run(["node", "--version"]).stdout.strip() if shutil.which("node") else ""
    sys.path.insert(0, os.path.join(PLUGIN, "scripts"))
    try:
        import limpar_voz
        df = os.path.exists(limpar_voz.DEEP_FILTER)
    except Exception:
        df = False
    transc = os.path.isdir(os.path.join(BASE, "node_modules", "@remotion", "install-whisper-cpp"))
    livre = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    itens = [
        (True, f"sistema: {platform.system()} {platform.release()}"),
        (sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}"),
        (bool(node), f"Node.js {node or '(falta: winget install OpenJS.NodeJS.LTS)'}"),
        (bool(shutil.which('ffmpeg')), "ffmpeg" + ("" if shutil.which("ffmpeg") else " (falta: winget install Gyan.FFmpeg)")),
        (bool(rv), f"motor raea {rv or '(falta: ep.py instalar motor)'}"),
        (transc, "transcrição Whisper local" + ("" if transc else " (falta: ep.py instalar transcricao)")),
        (True, "limpeza de voz: " + ("DeepFilterNet" if df else "FFmpeg (DeepFilterNet não achado: funciona, qualidade um pouco menor)")),
        (livre > 5, f"disco livre: {livre:.0f} GB"),
        (bool(config().get("clientes")), "pasta de clientes: " + (config().get("clientes") or "não definida (ep.py config clientes=...)")),
    ]
    for b, txt in itens:
        print(("ok    " if b else "FALTA ") + txt)


def projeto(pasta):
    return trabalho(pasta, "edicao")


def cmd_projeto(a):
    """Cria _EDITOR-PRO/edicao/ (projeto raea) a partir do template e liga a mídia em media/midia/ (hardlink, sem gastar disco)."""
    pasta = a[0]
    dest = projeto(pasta)
    novo = not os.path.isdir(os.path.join(dest, "src"))
    if novo:
        shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns(".work"))
    elif "--atualizar" in a:
        for raiz, _, fs in os.walk(os.path.join(TEMPLATE, "src")):
            for f in fs:
                if f == "extras.tsx":
                    continue
                rel = os.path.relpath(os.path.join(raiz, f), TEMPLATE)
                os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
                shutil.copy2(os.path.join(TEMPLATE, rel), os.path.join(dest, rel))
        print("componentes atualizados (extras.tsx e roteiro.json mantidos)")
    midia, pub = trabalho(pasta, "midia"), os.path.join(dest, "media", "midia")
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
    marca = aplicar_design(pasta)
    print(f"ok: {dest} ({'criado' if novo else 'já existia'}; {n} arquivo(s) novos em media/midia/{'; identidade do cliente aplicada' if marca else ''}). Arquivos do vídeo vão em media/.")


def cmd_render(a):
    """Imagem no motor (voz junto, sem SFX nem trilha) + mixagem por FFmpeg. Antes, a conferência bloqueia o que daria retrabalho."""
    pasta = a[0]
    previa = "--previa" in a
    proj = projeto(pasta)
    if not os.path.isdir(proj):
        raise SystemExit("sem projeto. Rode: ep.py projeto <pasta>")
    n = preencher_tempos(pasta)
    if n:
        print(f"tempos calculados para {n} texto(s)")
    prob, _ = conferir(pasta)
    if prob and "--forcar" not in a:
        print(f"render bloqueado: {len(prob)} problema(s) no roteiro (corrija ou use --forcar):")
        for p in prob[:8]:
            print("  ✗", p)
        sys.exit(1)
    imagem = trabalho(pasta, "imagem-previa.mp4" if previa else "imagem.mp4")  # cache da imagem: o som muda sem re-renderizar
    args = ["render", "edit.tsx", "-o", imagem, "--manifest", os.path.join(proj, ".work", "render.json")]
    args += ["--scale", "0.5", "--quality", "draft"] if previa else ["--quality", "high"]
    t0 = time.time()
    cod, linhas = raea(args, proj, os.path.join(proj, ".work", "render.log"))
    seg = time.time() - t0
    if cod != 0 or not os.path.exists(imagem):
        print(f"ERRO no render ({seg:.0f}s). Últimas linhas (log em .work/render.log):")
        print("\n".join(linhas[-10:]))
        sys.exit(1)
    avisos = [l for l in linhas if l.lstrip().startswith(("warn", "error", "NOTE", "REFUSED"))]
    print(f"imagem: {os.path.basename(imagem)} em {seg:.0f}s")
    for l in avisos[:6]:
        print("  " + l.strip()[:200])
    mixar(pasta, final=not previa)


def _alvo_sfx_lufs():
    return float(config().get("sfx_lufs", -24.0))  # loudness de cada SFX com volume 0.5 (≈10 dB sob a voz a -14)


def lufs_sfx(arq):
    """Loudness de um som curto: integrado do ebur128; sons curtos demais caem no curto prazo máximo (S)."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", arq, "-af", "apad=pad_dur=0.5,ebur128", "-f", "null", "-"])
    resumo = r.stderr[r.stderr.rfind("Summary:"):]
    m = re.search(r"I:\s*(-?[\d.]+) LUFS", resumo)
    if m and float(m.group(1)) > -70:
        return float(m.group(1))
    curtos = [float(x) for x in re.findall(r"S:\s*(-?[\d.]+)", r.stderr) if float(x) > -70]
    return max(curtos) if curtos else -30.0


def mixar(pasta, final=False):
    """Voz (do vídeo da imagem) + SFX + trilha, só com FFmpeg, em segundos. Corrige sozinho:
    pico de cada SFX medido no próprio arquivo (o pico cai em `t`), nível igualado entre os SFX, trilha com fade,
    limitador no fim (-1 dBTP). Gera previa.mp4/final.mp4 e sfx-stem.wav (só os SFX, para quem for refinar)."""
    proj = projeto(pasta)
    rot = ler_json(os.path.join(proj, "roteiro.json"), {}) or {}
    imagem = trabalho(pasta, "imagem.mp4" if final else "imagem-previa.mp4")
    saida = trabalho(pasta, "final.mp4" if final else "previa.mp4")
    if not os.path.exists(imagem):
        raise SystemExit(f"sem imagem renderizada ({os.path.basename(imagem)}). Rode: ep.py render <pasta>{'' if final else ' --previa'}")
    dur = duracao(imagem)
    tem_voz = any(s.get("codec_type") == "audio" for s in probe(imagem).get("streams", []))
    media = os.path.join(proj, "media")
    entradas, filtros, rotulos, sfx_rotulos, corrigidos = ["-i", imagem], [], [], [], 0
    if tem_voz:
        filtros.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[voz]")
        rotulos.append("[voz]")
    for k, s in enumerate(rot.get("sfx") or []):
        arq = os.path.join(media, s["arquivo"])
        if not os.path.exists(arq):
            print(f"  aviso: SFX não existe: {s['arquivo']}")
            continue
        _, pico_med, _ = pico_sfx(arq)
        pico = s.get("pico")
        if pico is None and pico_med > 0.03:
            pico, corrigidos = pico_med, corrigidos + 1
        # nivelado pela loudness (não pelo pico): todos os SFX no mesmo nível percebido; `volume` 0.5 = alvo, 1 = +6 dB
        ganho_db = (_alvo_sfx_lufs() - lufs_sfx(arq)) + 20 * __import__("math").log10(max(0.01, s.get("volume", 0.5)) / 0.5)
        ganho_db = max(-24.0, min(18.0, ganho_db))
        ini = max(0.0, s["t"] - (pico or 0))
        i = len(entradas) // 2
        entradas += ["-i", arq]
        filtros.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={ganho_db:.2f}dB,adelay={int(ini * 1000)}:all=1[s{k}]")
        sfx_rotulos.append(f"[s{k}]")
    if sfx_rotulos:
        if len(sfx_rotulos) > 1:
            filtros.append(f"{''.join(sfx_rotulos)}amix=inputs={len(sfx_rotulos)}:normalize=0:dropout_transition=0,asplit=2[sfx][sfxstem]")
        else:
            filtros.append(f"{sfx_rotulos[0]}asplit=2[sfx][sfxstem]")
        rotulos.append("[sfx]")
    tr = rot.get("trilha")
    if tr and os.path.exists(os.path.join(media, tr["arquivo"])):
        i = len(entradas) // 2
        entradas += ["-stream_loop", "-1", "-ss", str(tr.get("desde", 0)), "-i", os.path.join(media, tr["arquivo"])]
        fo = max(0.0, dur - 1.0)
        filtros.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{dur:.3f},volume={tr['volume']},"
                       f"afade=t=in:d=0.5,afade=t=out:st={fo:.3f}:d=1[trilha]")
        rotulos.append("[trilha]")
    if not rotulos:
        shutil.copy2(imagem, saida)
        print(f"ok: {saida} (sem som)")
        return
    filtros.append(f"{''.join(rotulos)}amix=inputs={len(rotulos)}:normalize=0:dropout_transition=0,"
                   f"atrim=0:{dur:.3f},alimiter=limit=0.84:level=disabled:attack=2:release=60[mix]")
    cmd = ["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[mix]",
                                                         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", saida]
    if sfx_rotulos:
        cmd += ["-map", "[sfxstem]", "-ac", "2", trabalho(pasta, "sfx-stem.wav")]
    t0 = time.time()
    r = run(cmd)
    if r.returncode != 0:
        raise SystemExit("mixagem falhou: " + r.stderr.strip()[-400:])
    print(f"ok: {saida} ({duracao(saida):.2f}s) mixado em {time.time() - t0:.1f}s: voz {'sim' if tem_voz else 'não'}, "
          f"{len(sfx_rotulos)} SFX{f' ({corrigidos} com pico preenchido)' if corrigidos else ''}, trilha {'sim' if tr else 'não'}")
    print("  " + medir(saida))


def cmd_mixar(a):
    mixar(a[0], final="--final" in a)


# ---------------- identidade do cliente (design.json) ----------------
DESIGN_MODELO = {
    "cores": {"texto": "#FFFFFF", "destaque": "#B8E351", "fundo": "#050607", "sobreFundo": "#FFFFFF", "sobreDestaque": "#050607"},
    "fontes": {
        "texto": {"familia": "Montserrat", "arquivo": None, "peso": 800},
        "impacto": {"familia": "Anton", "arquivo": None},
        "serifa": {"familia": "Instrument Serif", "arquivo": None},
    },
    "tamanhos": {"lettering": 92, "legenda": 48},
    "zonas": {"faixaY": 1240, "proibidas": []},
    "sombra": False,
    "logo": None,
}


def arquivo_design(pasta):
    d = ler_json(trabalho(pasta, "projeto.json"), {}) or {}
    clientes = config().get("clientes")
    if clientes and d.get("cliente") and os.path.isdir(os.path.join(clientes, d["cliente"])):
        return os.path.join(clientes, d["cliente"], "design.json")
    return None


def aplicar_design(pasta):
    """Copia a identidade do cliente para o tema do roteiro e as fontes dele para media/fontes. Zero token."""
    arq = arquivo_design(pasta)
    des = ler_json(arq, None) if arq else None
    if not des:
        return False
    proj = projeto(pasta)
    rot = ler_json(os.path.join(proj, "roteiro.json"), {}) or {}
    tema = rot.setdefault("tema", {})
    c, f, tam = des.get("cores", {}), des.get("fontes", {}), des.get("tamanhos", {})
    tema.update({k2: c[k1] for k1, k2 in [("texto", "cor"), ("destaque", "destaque"), ("fundo", "fundo"),
                                          ("sobreFundo", "corSobreFundo"), ("sobreDestaque", "corSobreDestaque")] if c.get(k1)})
    for chave, (fam, arqk) in {"texto": ("fonte", "arquivoFonte"), "impacto": ("fonteImpacto", "arquivoFonteImpacto"),
                               "serifa": ("fonteSerifa", "arquivoFonteSerifa")}.items():
        fonte = f.get(chave) or {}
        if fonte.get("familia"):
            tema[fam] = fonte["familia"]
        if fonte.get("arquivo"):
            origem = fonte["arquivo"] if os.path.isabs(fonte["arquivo"]) else os.path.join(os.path.dirname(arq), fonte["arquivo"])
            if os.path.exists(origem):
                os.makedirs(os.path.join(proj, "media", "fontes"), exist_ok=True)
                shutil.copy2(origem, os.path.join(proj, "media", "fontes", os.path.basename(origem)))
                tema[arqk] = "fontes/" + os.path.basename(origem)
        if chave == "texto" and fonte.get("peso"):
            tema["peso"] = fonte["peso"]
    if tam.get("lettering"):
        tema["tamanho"] = tam["lettering"]
    if tam.get("legenda"):
        tema["tamanhoLegenda"] = tam["legenda"]
    if "sombra" in des:
        tema["sombra"] = bool(des["sombra"])
    if des.get("zonas", {}).get("faixaY"):
        rot.setdefault("faixaY", des["zonas"]["faixaY"])
    gravar_json(os.path.join(proj, "roteiro.json"), rot)
    return True


def cmd_marca(a):
    """Mostra o design.json do cliente, ou cria o modelo para preencher (cores, fontes, tamanhos, zonas proibidas, logo)."""
    arq = arquivo_design(a[0])
    if not arq:
        raise SystemExit("defina a pasta de clientes (ep.py config clientes=...) e o cliente no projeto")
    if not os.path.exists(arq):
        gravar_json(arq, DESIGN_MODELO)
        print(f"criado: {arq} (preencha com as cores, fontes e zonas do cliente)")
        return
    des = ler_json(arq, {})
    c = des.get("cores", {})
    print(f"{arq}: cores {c.get('texto')} / destaque {c.get('destaque')} / fundo {c.get('fundo')} · "
          f"fontes {', '.join((v or {}).get('familia', '?') for v in des.get('fontes', {}).values())} · "
          f"{len(des.get('zonas', {}).get('proibidas', []))} zona(s) proibida(s)")


def cmd_checar(a):
    """raea check no vídeo pronto: volume, pico, trilha sob a voz, congelado, flash, área segura, leitura, legenda fora da palavra."""
    pasta = a[0]
    proj = projeto(pasta)
    video = trabalho(pasta, "final.mp4" if "--final" in a else "previa.mp4")
    if not os.path.exists(video):
        raise SystemExit(f"sem vídeo: {video}")
    args = ["check", video, "--platform", config().get("plataforma", "instagram"), "-o", os.path.join(proj, ".work", "check.json")]
    man = os.path.join(proj, ".work", "render.json")
    if os.path.exists(man):
        args += ["--manifest", man]
    pal = os.path.join(proj, "words.json")
    if os.path.exists(pal):
        args += ["--words", pal]
    cod, linhas = raea(args, proj, os.path.join(proj, ".work", "check.log"))
    ruins = [l for l in linhas if l.lstrip().startswith(("error", "warn"))]
    # Karaokê mostra a frase apagada antes de cada palavra acender: "cue" adiantado nessas palavras é o estilo, não erro.
    rot = ler_json(os.path.join(proj, "roteiro.json"), {}) or {}
    karaoke = {_norm(p) for t in rot.get("textos") or [] if t.get("estilo") == "karaoke" for p in t["texto"].replace("|", " ").split()}
    esperados = [l for l in ruins if " cue " in f" {l} " and any(f"“{w}”" in l or _norm(re.sub(r'.*?“([^”]+)”.*', r'\1', l)) == w for w in karaoke)]
    ruins = [l for l in ruins if l not in esperados]
    if esperados:
        print(f"  ({len(esperados)} aviso(s) de legenda adiantada no karaokê: esperado, a frase aparece apagada antes)")
    fim = next((l for l in reversed(linhas) if l.startswith("raea check:")), "")
    if esperados and not ruins:
        fim = "raea check: ok (o único aviso era o karaokê)"
    print(fim or f"raea check terminou com código {cod}")
    for l in ruins[:10]:
        print("  " + l.strip()[:220])
    if not ruins:
        print("  tudo ok nos itens medidos")


# ---------------- tempos das legendas (o Claude não escreve tempos) ----------------
def _norm(p):
    import unicodedata
    p = unicodedata.normalize("NFD", p.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in p if unicodedata.category(c) != "Mn"))


def palavras_da_base(pasta):
    """Palavras da base (tempo final do vídeo): _EDITOR-PRO/transcricao/base.json, no formato do Whisper/Remotion."""
    arq = trabalho(pasta, "transcricao", "base.json")
    if not os.path.exists(arq):
        return []
    return [(ini, fim, txt) for ini, fim, txt in palavras(ler_json(arq, []))]


def preencher_tempos(pasta):
    """Para cada texto sem `tempos`: acha a frase na transcrição da base (a partir de `perto`, se dado, ou da frase anterior)
    e preenche inicio, tempos de cada palavra e fim (segura ~1 s depois da última palavra, sem passar do próximo texto).
    Também grava words.json no projeto para o raea check medir legenda fora da palavra."""
    proj = projeto(pasta)
    arq = os.path.join(proj, "roteiro.json")
    rot = ler_json(arq)
    ws = palavras_da_base(pasta)
    if not rot or not ws:
        return 0
    gravar_json(os.path.join(proj, "words.json"), [{"text": t, "start_ms": round(i * 1000), "end_ms": round(f * 1000)} for i, f, t in ws])
    norm = [_norm(t) for _, _, t in ws]
    textos = rot.get("textos") or []
    feitos, cursor = 0, 0
    for t in textos:
        alvo = [_norm(p) for p in t["texto"].replace("|", " ").split() if _norm(p)]
        if t.get("tempos") and len(t["tempos"]) == len(alvo):
            cursor = max(cursor, next((k for k, (i, _, _) in enumerate(ws) if i >= t["tempos"][-1]), cursor))
            continue
        ini_busca = cursor
        if t.get("perto") is not None:
            ini_busca = next((k for k, (i, _, _) in enumerate(ws) if i >= t["perto"] - 1.0), 0)
        achou = None
        for k in range(ini_busca, len(ws) - len(alvo) + 1):
            if norm[k:k + len(alvo)] == alvo:
                achou = k
                break
        if achou is None and len(alvo) >= 3:  # tolera palavras trocadas pela transcrição ("num" × "no")
            minimo = max(2, -(-len(alvo) * 6 // 10))
            for k in range(ini_busca, len(ws) - len(alvo) + 1):
                if norm[k] == alvo[0] and sum(a == b for a, b in zip(norm[k:k + len(alvo)], alvo)) >= minimo:
                    achou = k
                    break
        if achou is None:  # frase resumida (não literal): ancora na 1ª palavra que bate
            k0 = next((k for k in range(ini_busca, len(ws)) if norm[k] == alvo[0]), None)
            if k0 is None:
                print(f"  aviso: \"{t['texto']}\" não foi achada na fala; ponha \"perto\": <segundo> ou ajuste o texto")
                continue
            passo = max(0.12, (ws[min(len(ws) - 1, k0 + len(alvo))][0] - ws[k0][0]) / max(1, len(alvo)))
            tempos = [round(ws[k0][0] + i * passo, 2) for i in range(len(alvo))]
            ultimo = min(len(ws) - 1, k0 + len(alvo) - 1)
        else:
            tempos = [round(ws[k][0], 2) for k in range(achou, achou + len(alvo))]
            ultimo = achou + len(alvo) - 1
            k0 = achou
        t["tempos"] = tempos
        t["inicio"] = round(tempos[0], 2)
        t["fim"] = round(max(ws[ultimo][1] + 1.0, tempos[0] + 0.8), 2)
        cursor = ultimo + 1
        feitos += 1
    # sem colisão: cada texto termina antes do próximo começar
    ordem = sorted(textos, key=lambda x: x["inicio"])
    for x, y in zip(ordem, ordem[1:]):
        if x["fim"] > y["inicio"] - 0.05:
            x["fim"] = round(max(x["inicio"] + 0.5, y["inicio"] - 0.05), 2)
    if feitos:
        gravar_json(arq, rot)
    return feitos


def cmd_tempos(a):
    n = preencher_tempos(a[0])
    print(f"ok: tempos calculados para {n} texto(s)")


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
        print(f"({total} sons) No roteiro: copie para media/sfx/ do projeto e use \"pico\" para alinhar o pico no tempo da ação.")


# ---------------- revisão de diretor de arte ----------------
def cmd_revisar(a):
    """Tiras de 6 quadros seguidos (-4, -2, 0, +2, +4, +8) em cada momento de movimento: mostra o tempo, não só o quadro."""
    pasta = a[0]
    video = trabalho(pasta, "final.mp4" if "--final" in a else "previa.mp4")
    rot = ler_json(os.path.join(projeto(pasta), "roteiro.json"), {})
    if not os.path.exists(video):
        raise SystemExit(f"sem vídeo: {video}")
    fps = rot.get("fps", 30)
    momentos = []
    for t in rot.get("textos") or []:
        momentos.append((t["inicio"], f"texto entra: {t['texto'][:28]}"))
    for tr in rot.get("transicoes") or []:
        momentos.append((tr["t"], f"transição {tr['tipo']}"))
    for p in rot.get("pecas") or []:
        momentos.append((p["inicio"], f"peça {p['nome']}"))
    if rot.get("fecho"):
        momentos.append((rot["fecho"]["inicio"], f"fecho {rot['fecho']['tipo']}"))
    momentos = sorted(momentos)
    vistos, sel = [], []
    for t, nome in momentos:  # um por janela de 0,5 s, até 12
        if all(abs(t - v) > 0.5 for v in vistos):
            vistos.append(t)
            sel.append((t, nome))
    sel = sel[:12]
    pasta_out = trabalho(pasta, "folhas")
    os.makedirs(pasta_out, exist_ok=True)
    tiras = []
    for i, (t, _) in enumerate(sel):
        f0 = max(4, round(t * fps))  # no começo do vídeo, desloca para ter 4 quadros antes
        quadros = [max(0, f0 + d) for d in (-4, -2, 0, 2, 4, 8)]
        expr = "+".join(f"eq(n\\,{q})" for q in quadros)
        out = os.path.join(pasta_out, f".tira{i:02d}.jpg")
        r = run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"select='{expr}',scale=150:-2,tile=6x1:padding=4:color=black",
                 "-frames:v", "1", "-fps_mode", "passthrough", out])
        if r.returncode == 0 and os.path.exists(out):
            tiras.append(out)
    if not tiras:
        raise SystemExit("não consegui montar as tiras")
    saida = os.path.join(pasta_out, "revisao.jpg")
    entradas = sum([["-i", x] for x in tiras], [])
    filtro = f"{''.join(f'[{i}]' for i in range(len(tiras)))}vstack=inputs={len(tiras)}" if len(tiras) > 1 else "null"
    run(["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex", filtro, "-q:v", "4", saida])
    for x in tiras:
        os.remove(x)
    print(saida)
    for i, (t, nome) in enumerate(sel[:len(tiras)]):
        print(f"  linha {i + 1}: {t:.2f}s {nome}")
    print("Cada linha: 4 e 2 quadros antes, o quadro do momento, 2, 4 e 8 depois. Avalie com ../editar/revisao.md.")


# ---------------- histórico do cliente (para variar entre vídeos) ----------------
def arquivo_historico(pasta):
    d = ler_json(trabalho(pasta, "projeto.json"), {}) or {}
    clientes = config().get("clientes")
    if clientes and d.get("cliente") and os.path.isdir(os.path.join(clientes, d["cliente"])):
        return os.path.join(clientes, d["cliente"], "historico-edicao.json")
    return os.path.join(os.path.dirname(trabalho(pasta)), "historico-edicao.json")


def historico_cliente(pasta):
    return (ler_json(arquivo_historico(pasta), {}) or {}).get("videos", [])


def assinatura(rot):
    """O 'desenho' de um vídeo: combinações de texto, transições, peças, fecho e trilha."""
    contar = lambda xs: [f"{k}×{v}" for k, v in sorted({x: xs.count(x) for x in xs}.items(), key=lambda kv: -kv[1])]
    return {
        "texto": contar([f"{t.get('estilo', 'linha')}+{t.get('entrada', 'blur')}" for t in rot.get("textos") or []]),
        "transicoes": contar([t["tipo"] for t in rot.get("transicoes") or []]),
        "pecas": contar([p["nome"] for p in rot.get("pecas") or []]),
        "fecho": (rot.get("fecho") or {}).get("tipo"),
        "trilha": os.path.basename((rot.get("trilha") or {}).get("arquivo", "")) or None,
    }


def cmd_historico(a):
    pasta = a[0]
    vids = historico_cliente(pasta)
    if "--gravar" in a:
        d = estado(pasta)
        rot = ler_json(os.path.join(projeto(pasta), "roteiro.json"), {})
        reg = {"data": time.strftime("%Y-%m-%d"), "tema": d.get("tema"), "modelo": d.get("modelo"),
               "direcao": (d.get("plano") or {}).get("direcao"), "assinatura": assinatura(rot)}
        vids = [v for v in vids if v.get("tema") != reg["tema"]] + [reg]
        gravar_json(arquivo_historico(pasta), {"videos": vids})
        print(f"ok: registrado em {arquivo_historico(pasta)} ({len(vids)} vídeos)")
        return
    if not vids:
        print("sem histórico deste cliente ainda (primeiro vídeo: liberdade total)")
        return
    for v in vids[-5:]:
        s = v.get("assinatura", {})
        print(f"{v.get('data')} · {v.get('tema')} · direção: {v.get('direcao') or '?'}")
        print(f"   texto {', '.join(s.get('texto', [])) or '-'} | transições {', '.join(s.get('transicoes', [])) or '-'} | "
              f"peças {', '.join(s.get('pecas', [])) or '-'} | fecho {s.get('fecho') or '-'} | trilha {s.get('trilha') or '-'}")


# ---------------- conferência ----------------
def cmd_conferir(a):
    prob, info = conferir(a[0])
    print(f"conferência: {len(prob)} problema(s), {len(info)} aviso(s)")
    for p in prob[:12]:
        print("  ✗", p)
    for i in info[:8]:
        print("  ·", i)
    if not prob:
        print("  ok nos itens automáticos. Falta conferir na prévia: rosto livre, texto fluido, sílaba solta.")


def conferir(pasta):
    proj = projeto(pasta)
    rot = ler_json(os.path.join(proj, "roteiro.json"))
    if rot is None:
        raise SystemExit("sem roteiro.json")
    fps, W, H = rot["fps"], rot["largura"], rot["altura"]
    total = rot["duracao"]
    q = lambda s: round(s * fps)
    prob, info = [], []
    pub = os.path.join(proj, "media")

    def existe(arq, oque):
        if arq and not os.path.exists(os.path.join(pub, arq)):
            prob.append(f"{oque}: arquivo não existe em media/ ({arq})")

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
        if n > 1 and any(len(l) == 1 for l in linhas) and t.get("estilo") not in ("palavra", "hierarquia"):
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
    # variação: nada de molde repetido
    if len(textos) >= 3:
        combos = [(t.get("estilo", "linha"), t.get("entrada", "blur")) for t in textos]
        mais, n = max(((c, combos.count(c)) for c in set(combos)), key=lambda x: x[1])
        if n / len(combos) > 0.6:
            prob.append(f"texto sempre igual: {n} de {len(combos)} em {mais[0]}+{mais[1]} (varie estilo, entrada, tamanho ou lugar pelo sentido da frase)")
        for x, y in zip(textos, textos[1:]):
            if (x.get("estilo", "linha"), x.get("entrada", "blur"), x.get("y"), x.get("centro")) == (y.get("estilo", "linha"), y.get("entrada", "blur"), y.get("y"), y.get("centro")):
                info.append(f"textos seguidos idênticos no desenho ({x['inicio']}s e {y['inicio']}s)")
                break
    if len(trs) >= 3 and len({t["tipo"] for t in trs}) == 1:
        prob.append(f"todas as transições são {trs[0]['tipo']}")
    anteriores = historico_cliente(pasta)[-2:]
    atual = assinatura(rot)
    for h in anteriores:
        if h.get("assinatura", {}).get("texto") == atual["texto"] and atual["texto"]:
            info.append(f"mesma linguagem de texto do vídeo \"{h.get('tema', '?')}\" ({', '.join(atual['texto'])})")
        if atual["trilha"] and h.get("assinatura", {}).get("trilha") == atual["trilha"]:
            prob.append(f"mesma trilha do vídeo \"{h.get('tema', '?')}\"")

    # zonas proibidas do cliente (design.json: logo, bordado, produto) — texto e peça não podem cair nelas
    des = ler_json(arquivo_design(pasta), {}) if arquivo_design(pasta) else {}
    for z in (des or {}).get("zonas", {}).get("proibidas", []):
        x0, y0, x1, y1 = z
        for t in textos:
            y = t.get("y", rot["faixaY"]) if not t.get("centro") else H / 2
            if y0 <= y <= y1:
                prob.append(f"texto em {t.get('inicio', '?')}s na zona proibida do cliente ({x0},{y0})-({x1},{y1})")
        for p in rot.get("pecas") or []:
            pr = p.get("props", {})
            if x0 <= pr.get("x", W / 2) <= x1 and y0 <= pr.get("y", rot["faixaY"]) <= y1:
                prob.append(f"peça {p['nome']} em {p['inicio']}s na zona proibida do cliente")
    return prob, info


CMDS = {
    "onde": cmd_onde, "config": cmd_config, "novo": cmd_novo, "status": cmd_status, "ver": cmd_ver, "set": cmd_set,
    "etapa": cmd_etapa, "pendencia": cmd_pendencia, "resolver": cmd_resolver, "inventario": cmd_inventario,
    "converter": cmd_converter, "folha": cmd_folha, "cor": cmd_cor, "transcrever": cmd_transcrever, "frases": cmd_frases,
    "voz": cmd_voz, "instalar": cmd_instalar, "projeto": cmd_projeto, "doctor": cmd_doctor, "checar": cmd_checar, "tempos": cmd_tempos, "mixar": cmd_mixar, "marca": cmd_marca, "render": cmd_render, "medir": cmd_medir,
    "sfx": cmd_sfx, "sfx-indice": cmd_sfx_indice, "conferir": cmd_conferir, "historico": cmd_historico,
    "revisar": cmd_revisar, "alinhar": cmd_alinhar,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    CMDS[sys.argv[1]](sys.argv[2:])
