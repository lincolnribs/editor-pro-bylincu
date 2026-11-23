"""
Trilho do Editor Pro: o formato do vídeo define o caminho. Uma etapa por comando, estado salvo,
e a saída sempre termina com PRÓXIMO: (o que fazer agora).

  python editor.py analisar <arquivos...>                      # sugere o formato (sem gastar imagem)
  python editor.py novo --formato <F> "<Cliente>" "<Título>" <arquivos...>
  python editor.py status                                      # onde parou e o próximo passo

Formatos (guia em references/formatos/<F>.md):
  talking-head  pessoa falando, brutos com takes: Reels premium (decupagem, voz, lettering, b-roll, SFX)
  comercial     anúncio/oferta: talking-head + cards de oferta, prova, CTA e fechamento com marca
  decupagem     só montar os takes: decupagem, voz e silêncios, legenda simples
  legenda       vídeo já editado: só voz limpa (sem cortar) e legenda
  aftermovie    evento/bastidores sem fala: clipes na batida da música, título e fechamento
  motion        sem filmagem: peça de motion com os complementos (remotion-director e outros)

Etapas: voz, roteiro, trilha <arquivo>, montar, preview, final, entregar <mp4>, abrir <id>.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(AQUI)
MODELO = os.path.join(SKILL, "template")
PY = sys.executable
FPS = 30
CFG = os.path.join(os.path.expanduser("~"), ".edicao-video", "config.json")

FORMATOS = ["talking-head", "comercial", "decupagem", "legenda", "aftermovie", "motion"]

# Sequência de etapas por formato. Etapas entre [] são do Claude (não são comandos).
FLUXOS = {
    "talking-head": ["novo", "[decupagem]", "voz", "roteiro", "[criacao]", "montar", "preview", "final"],
    "comercial":    ["novo", "[decupagem]", "voz", "roteiro", "[criacao-comercial]", "montar", "preview", "final"],
    "decupagem":    ["novo", "[decupagem]", "voz", "roteiro", "[revisar-legenda]", "montar", "final"],
    "legenda":      ["novo", "voz", "roteiro", "[revisar-legenda]", "montar", "final"],
    "aftermovie":   ["novo", "trilha", "[selecao]", "roteiro", "[criacao-aftermovie]", "montar", "preview", "final"],
    "motion":       ["novo", "[motion]", "entregar"],
}

INSTR = {
    "[decupagem]": "DECUPAGEM: leia os .txt dos takes (folha só de take duvidoso) e escreva {vid}/takes.txt com o melhor "
                   "trecho de cada fala, na ordem: \"caminho\" inicio fim. Depois: python editor.py voz",
    "voz": "python editor.py voz",
    "roteiro": "python editor.py roteiro",
    "[criacao]": "CRIAÇÃO: abra o mapa do rosto uma vez e edite public/roteiro.json (references/roteiro.md): tema, faixaY, "
                 "lettering a cada 2-4 s, broll nos argumentos. Trilha aprovada? python editor.py trilha <arquivo>. "
                 "Depois: python editor.py montar",
    "[criacao-comercial]": "CRIAÇÃO COMERCIAL (references/formatos/comercial.md): como talking-head, mais oferta/prova/CTA em "
                           "src/extras.tsx e fechamento com a marca. Trilha: python editor.py trilha <arquivo>. "
                           "Depois: python editor.py montar",
    "[revisar-legenda]": "REVISÃO: leia {vid}/base.txt, corrija nomes e marcas em public/roteiro.json (campo legenda) e ajuste "
                         "faixaY pelo mapa do rosto. Depois: python editor.py montar",
    "trilha": "TRILHA (obrigatória): python editor.py trilha <musica.mp3>. Ela define o ritmo dos cortes.",
    "[selecao]": "SELEÇÃO: abra o catálogo de clipes uma vez e escreva {vid}/selecao.txt na ordem do filme, uma linha por "
                 "clipe: NN [segundo de início] (ex.: 07 2.5). Abertura forte, meio variado, final emocional. "
                 "Depois: python editor.py roteiro",
    "[criacao-aftermovie]": "CRIAÇÃO: em public/roteiro.json ajuste o título (lettering do início), o fechamento e, se quiser, "
                            "a ordem/duração dos clipes. Depois: python editor.py montar",
    "montar": "python editor.py montar",
    "preview": "python editor.py preview",
    "final": "Confira a folha (rosto, margens, ritmo). Ajuste e repita montar/preview (no máximo 2 vezes) ou: python editor.py final",
    "[motion]": "MOTION: siga references/formatos/motion.md, escolha o complemento pelo pedido e produza a peça na pasta "
                "{pasta}. Ao terminar: python editor.py entregar <arquivo.mp4> --complemento <nome>",
    "entregar": "python editor.py entregar <arquivo.mp4>",
}


# ---------- utilidades ----------
def rodar(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(f"ERRO em {os.path.basename(str(cmd[0]))}: " + (r.stderr or r.stdout).strip()[-600:])
        sys.exit(1)
    return r.stdout


def exe(nome):
    caminho = shutil.which(nome) or shutil.which(nome + ".cmd")
    if not caminho:
        sys.exit(f"ERRO: '{nome}' não encontrado. Veja references/instalacao.md.")
    return caminho


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower() or "video"


def ler(p, padrao=None):
    try:
        with open(p, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return padrao


def gravar(p, dados):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def probe(v, campos="format=duration"):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", campos, "-of", "csv=p=0", v],
                          capture_output=True, text=True).stdout.strip()


def duracao(v):
    try:
        return float(probe(v).split("\n")[0] or 0)
    except ValueError:
        return 0.0


def estudio():
    raiz = ler(CFG, {}).get("raiz")
    if not raiz or not os.path.isdir(raiz):
        rodar([PY, os.path.join(AQUI, "estudio.py"), "criar"])
        raiz = ler(CFG, {})["raiz"]
    return raiz


def projeto_atual():
    p = os.environ.get("EDITOR_PROJETO") or os.getcwd()
    while True:
        if os.path.isfile(os.path.join(p, ".work", "estado.json")):
            return p
        pai = os.path.dirname(p)
        if pai == p:
            break
        p = pai
    ultimo = ler(CFG, {}).get("ultimo_projeto")
    if ultimo and os.path.isfile(os.path.join(ultimo, ".work", "estado.json")):
        return ultimo
    sys.exit("Nenhum vídeo em andamento. Comece com: python editor.py analisar <arquivos> e depois novo --formato ...")


def estado(proj):
    return ler(os.path.join(proj, ".work", "estado.json"), {})


def salvar_estado(proj, est):
    gravar(os.path.join(proj, ".work", "estado.json"), est)
    cfg = ler(CFG, {})
    cfg["ultimo_projeto"] = proj
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    gravar(CFG, cfg)


def concluir(proj, est, etapa):
    est["etapa"] = etapa
    salvar_estado(proj, est)
    fluxo = FLUXOS[est["formato"]]
    i = fluxo.index(etapa) if etapa in fluxo else -1
    if i + 1 >= len(fluxo):
        print("PRÓXIMO: entregue. Para outro vídeo, de preferência numa conversa nova: python editor.py analisar ...")
        return
    nxt = fluxo[i + 1]
    if nxt == "final" and "preview" not in fluxo:
        texto = "python editor.py final"
    else:
        texto = INSTR[nxt].format(vid=f"public/{est['video']}", pasta=est.get("pasta_motion", proj))
    print(f"PRÓXIMO ({est['formato']}): {texto}")


def palavras_json(p):
    dados = ler(p, [])
    return [(w["startMs"] / 1000, w["endMs"] / 1000, w["text"].strip()) for w in dados if w.get("text", "").strip()]


def transcrever(proj, videos, frases_curtas=False):
    rodar([exe("node"), "scripts/transcrever.mjs", *videos], cwd=proj)
    extra = ["--max", "5", "--pausa", "0.3"] if frases_curtas else []
    txts = []
    for v in videos:
        rodar([PY, os.path.join(AQUI, "transcricao.py"), os.path.splitext(os.path.join(proj, v))[0] + ".json", *extra])
        txts.append(os.path.splitext(v)[0] + ".txt")
    return txts


def converter(bruto, saida, com_audio=True):
    trc = probe(bruto, "stream=color_transfer").split("\n")[0]
    hdr = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,") if trc in ("arib-std-b67", "smpte2084") else ""
    vf = hdr + f"scale=1080:1920:force_original_aspect_ratio=increase:in_range=tv:out_range=tv,crop=1080:1920,fps={FPS},format=yuv420p"
    audio = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if com_audio else ["-an"]
    rodar(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-vf", vf, "-color_range", "tv", "-colorspace", "bt709",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
           *audio, saida])


# ---------- análise ----------
def analisar_arquivo(v):
    dur = duracao(v)
    tem_audio = "audio" in probe(v, "stream=codec_type")
    som = 0.0
    if tem_audio and dur > 0:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-af", "silencedetect=n=-32dB:d=0.4", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        silencio = sum(float(x) for x in re.findall(r"silence_duration: ([\d.]+)", r))
        som = max(0.0, 1 - silencio / dur)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-vf", "scale=160:-2,scdet=t=12", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    cortes = len(re.findall(r"lavfi\.scd\.time", r))
    wh = [x for x in probe(v, "stream=width,height").split("\n")[0].split(",") if x]
    return {"dur": dur, "som": som, "cortes": cortes, "wh": wh}


def cmd_analisar(a):
    infos = []
    for v in a.arquivos:
        if not os.path.isfile(v):
            sys.exit(f"ERRO: não achei {v}")
        i = analisar_arquivo(v)
        infos.append(i)
        cpm = i["cortes"] / max(i["dur"] / 60, 0.01)
        print(f"{os.path.basename(v)}: {i['dur']:.1f}s | {'x'.join(i['wh'])} | som em {i['som']:.0%} do tempo | "
              f"{i['cortes']} cortes de cena ({cpm:.0f}/min)")
    som = sum(i["som"] for i in infos) / len(infos)
    editado = len(infos) == 1 and infos[0]["dur"] > 20 and infos[0]["cortes"] / (infos[0]["dur"] / 60) > 12
    if editado:
        sug = "legenda (um arquivo já editado: muitos cortes de cena)"
    elif som < 0.35:
        sug = "aftermovie (pouca fala: clipes para montar na música)"
    else:
        sug = "talking-head (fala em takes brutos). Anúncio/oferta = comercial; pediram só os cortes = decupagem"
    print(f"SUGESTÃO: {sug}")
    print("Sem arquivos e pedido de animação, logo ou vinheta = motion. Decida junto com o pedido do usuário e siga "
          "references/formatos/<formato>.md")


# ---------- etapas ----------
def cmd_novo(a):
    raiz = estudio()
    rodar([PY, os.path.join(AQUI, "estudio.py"), "cliente", a.cliente])
    cli = os.path.join(raiz, "clientes", slug(a.cliente))
    vid = f"{date.today():%Y-%m-%d}-{slug(a.titulo)}"

    if a.formato == "motion":
        pasta = os.path.join(cli, "motion", vid)
        os.makedirs(os.path.join(pasta, ".work"), exist_ok=True)
        for arq in a.arquivos:
            shutil.copy2(arq, pasta)
        est = {"cliente": a.cliente, "titulo": a.titulo, "video": vid, "formato": "motion", "pasta_motion": pasta,
               "cliente_dir": cli}
        print(f"pasta do motion: {pasta}")
        print(f"leia antes: {os.path.join(cli, 'LEIAME.md')} (identidade do cliente)")
        concluir(pasta, est, "novo")
        return

    proj = os.path.join(cli, "projeto")
    if not os.path.isfile(os.path.join(proj, "package.json")):
        shutil.copytree(MODELO, proj, dirs_exist_ok=True)
    if not os.path.isdir(os.path.join(proj, "node_modules")):
        print("instalando o projeto Remotion (só na primeira vez do cliente, ~1 min)...")
        rodar([exe("npm"), "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=proj)
    pasta_takes = "clipes" if a.formato == "aftermovie" else "takes"
    pub = os.path.join(proj, "public", vid)
    os.makedirs(os.path.join(pub, pasta_takes), exist_ok=True)
    os.makedirs(os.path.join(proj, ".work"), exist_ok=True)
    guardar = os.path.join(cli, "01-brutos", vid)
    os.makedirs(guardar, exist_ok=True)

    takes = []
    for n, bruto in enumerate(a.arquivos, 1):
        bruto = os.path.abspath(bruto)
        if not os.path.isfile(bruto):
            sys.exit(f"ERRO: arquivo não encontrado: {bruto}")
        if not os.path.exists(os.path.join(guardar, os.path.basename(bruto))):
            shutil.copy2(bruto, guardar)
        converter(bruto, os.path.join(pub, pasta_takes, f"{n:02d}.mp4"), com_audio=a.formato != "aftermovie")
        takes.append(f"public/{vid}/{pasta_takes}/{n:02d}.mp4")
    est = {"cliente": a.cliente, "titulo": a.titulo, "video": vid, "formato": a.formato, "takes": takes,
           "brutos": [os.path.basename(b) for b in a.arquivos]}
    print(f"triagem: {len(takes)} arquivos em 1080x1920 30 fps")
    print(f"projeto: {proj}")
    print(f"leia antes: {os.path.join(cli, 'LEIAME.md')} (identidade do cliente)")

    if a.formato == "aftermovie":
        catalogo(proj, takes)
    elif a.formato == "legenda":
        print("vídeo já editado: sem decupagem; a transcrição vem depois da voz")
    else:
        print("transcrevendo (whisper local)...")
        txts = transcrever(proj, takes)
        for tk, tx in zip(takes, txts):
            n = len(palavras_json(os.path.join(proj, os.path.splitext(tk)[0] + ".json")))
            tipo = "fala" if n >= 4 else "b-roll? (quase sem fala)"
            print(f"  {tk}  {duracao(os.path.join(proj, tk)):.1f}s  {n} palavras  {tipo}  -> {tx}")
    concluir(proj, est, "novo")


def catalogo(proj, clipes):
    """Uma imagem com 1 quadro do meio de cada clipe, em ordem (linha a linha), para a seleção."""
    for k, c in enumerate(clipes):
        rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{duracao(os.path.join(proj, c)) / 2:.2f}", "-i",
               os.path.join(proj, c), "-frames:v", "1", "-vf", "scale=160:-2", os.path.join(proj, ".work", f"cat-{k:03d}.jpg")])
    cols = 6
    saida = os.path.join(proj, ".work", "catalogo.jpg")
    rodar(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(proj, ".work", "cat-%03d.jpg"),
           "-vf", f"tile={cols}x{-(-len(clipes) // cols)}:padding=4", "-frames:v", "1", "-q:v", "5", saida])
    for k in range(len(clipes)):
        os.remove(os.path.join(proj, ".work", f"cat-{k:03d}.jpg"))
    print(f"catálogo: {saida} ({len(clipes)} clipes, numerados 01.. da esquerda para a direita, linha a linha)")
    print("  " + " | ".join(f"{os.path.basename(c)[:2]} {duracao(os.path.join(proj, c)):.1f}s" for c in clipes))


def cmd_voz(_):
    proj = projeto_atual()
    est = estado(proj)
    vid, formato = est["video"], est["formato"]
    lista = os.path.join(proj, "public", vid, "takes.txt")
    if formato == "legenda" and not os.path.isfile(lista):
        with open(lista, "w", encoding="utf-8") as f:
            for tk in est["takes"]:
                f.write(f'"{tk}" 0 {duracao(os.path.join(proj, tk)):.3f}\n')
    if not os.path.isfile(lista):
        sys.exit(f"ERRO: falta a decupagem em {lista}")
    trechos = []
    with open(lista, encoding="utf-8-sig") as f:
        for linha in f:
            if not linha.strip() or linha.strip().startswith("#"):
                continue
            m = re.match(r'\s*"?([^"]+?)"?\s+([\d.]+)\s+([\d.]+)\s*$', linha)
            if not m:
                sys.exit(f"ERRO na linha do takes.txt: {linha.strip()}")
            c = m.group(1) if os.path.isabs(m.group(1)) else os.path.join(proj, m.group(1))
            trechos.append((c.replace("\\", "/"), float(m.group(2)), float(m.group(3))))
    absoluta = os.path.join(proj, ".work", "takes-abs.txt")
    with open(absoluta, "w", encoding="utf-8") as f:
        for c, i, fim in trechos:
            f.write(f'"{c}" {i} {fim}\n')
    base = os.path.join(proj, "public", vid, "base.mp4")
    cortar = [] if formato == "legenda" else ["--cortar-silencios", "--respiro", "0.14"]
    print(rodar([PY, os.path.join(AQUI, "limpar_voz.py"), "--lista", absoluta, "-o", base, *cortar,
                 "--escala", "1080x1920", "--fps", str(FPS)]).strip().splitlines()[0])
    transcrever(proj, [f"public/{vid}/base.mp4"], frases_curtas=True)
    if formato == "legenda":
        ws = palavras_json(os.path.splitext(base)[0] + ".json")
        seg = duracao(base)
        if seg and len(ws) / seg < 0.8:
            print(f"ATENÇÃO: só {len(ws)} palavras em {seg:.0f}s. Pode ter música mixada (a limpeza estraga a trilha) ou "
                  "pouca fala. Confira com o usuário; com música, peça a versão sem trilha.")
    else:
        esperadas = sum(sum(1 for w in palavras_json(os.path.splitext(c)[0] + ".json") if w[0] >= i - 0.05 and w[1] <= fim + 0.05)
                        for c, i, fim in trechos)
        obtidas = len(palavras_json(os.path.splitext(base)[0] + ".json"))
        aviso = "ok" if abs(obtidas - esperadas) <= max(2, esperadas * 0.05) else "CONFIRA: diferença de palavras"
        print(f"conferência: {esperadas} palavras nos trechos x {obtidas} na base ({aviso})")
    print(f"texto da base: public/{vid}/base.txt")
    concluir(proj, est, "voz")


def frases(ws, pausa=0.35, maximo=5, dur_max=2.2):
    grupos, atual = [], []
    for w in ws:
        if atual and (w[0] - atual[-1][1] > pausa or len(atual) >= maximo or w[1] - atual[0][0] > dur_max):
            grupos.append(atual)
            atual = []
        atual.append(w)
    if atual:
        grupos.append(atual)
    return [{"inicio": round(g[0][0], 2), "fim": round(g[-1][1] + 0.12, 2),
             "texto": re.sub(r"[.,!?;:]+", "", " ".join(x[2] for x in g)).strip()} for g in grupos]


def tema_padrao(antigo):
    if antigo.get("base") or antigo.get("clipes"):
        return antigo.get("tema"), antigo.get("faixaY", 1240), True
    return ({"fonte": "Montserrat", "peso": 800, "cor": "#FFFFFF", "destaque": "#FFD400", "tamanho": 92,
             "tamanhoLegenda": 46}, 1240, False)


def mapa_rosto(proj, video, seg):
    entradas, filtros = [], []
    for k, frac in enumerate((0.15, 0.5, 0.85)):
        entradas += ["-ss", f"{seg * frac:.2f}", "-i", video]
        filtros.append(f"[{k}:v]drawgrid=w=iw:h=100:t=2:c=red@0.7,scale=300:-2,trim=end_frame=1[q{k}]")
    mapa = os.path.join(proj, ".work", "mapa-rosto.jpg")
    rodar(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros) + ";[q0][q1][q2]hstack=3",
           "-frames:v", "1", "-q:v", "5", mapa])
    return mapa


def cmd_roteiro(_):
    proj = projeto_atual()
    est = estado(proj)
    if est["formato"] == "aftermovie":
        return roteiro_montagem(proj, est)
    vid = est["video"]
    pub = os.path.join(proj, "public", vid)
    cortes = ler(os.path.join(pub, "base.cortes.json"))
    if not cortes:
        sys.exit("ERRO: rode antes: python editor.py voz")
    trechos = cortes["trechos"]
    total = max(t["quadro_saida"] + t["quadros"] for t in trechos)
    rot_path = os.path.join(proj, "public", "roteiro.json")
    antigo = ler(rot_path, {})
    tema, faixa, herdado = tema_padrao(antigo)
    trilha = {"arquivo": est["trilha"], "volume": 0.08} if est.get("trilha") else None
    rot = {"fps": FPS, "largura": 1080, "altura": 1920, "duracaoQuadros": total, "base": f"{vid}/base.mp4",
           "trechos": trechos, "clipes": [], "tema": tema, "faixaY": faixa, "punchIn": est["formato"] != "legenda",
           "lettering": [], "legenda": frases(palavras_json(os.path.join(pub, "base.json"))),
           "broll": [], "sfx": [], "trilha": trilha}
    gravar(rot_path, rot)
    mapa = mapa_rosto(proj, os.path.join(pub, "base.mp4"), total / FPS)
    print(f"roteiro: {rot_path} ({total / FPS:.1f}s, {len(trechos)} planos, {len(rot['legenda'])} legendas automáticas)")
    print(f"mapa do rosto (cada linha vermelha = 100 px; y real = y na imagem x 3,6): {mapa}")
    print("tema e faixaY herdados do vídeo anterior do cliente" if herdado else "tema padrão: troque pelo do cliente")
    concluir(proj, est, "roteiro")


# ---------- aftermovie ----------
def batidas(musica):
    """Grade de batidas (s) por fluxo espectral + autocorrelação. Sem numpy: 120 BPM."""
    dur = duracao(musica)
    try:
        import numpy as np
    except ImportError:
        return [round(k * 0.5, 3) for k in range(int(dur / 0.5))], 120.0
    sr, hop, win = 11025, 256, 1024
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", musica, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = max(1, (len(x) - win) // hop)
    quadros = np.lib.stride_tricks.as_strided(x, shape=(n, win), strides=(x.strides[0] * hop, x.strides[0]))
    spec = np.abs(np.fft.rfft(quadros * np.hanning(win), axis=1))
    fluxo = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(axis=1)
    fluxo = (fluxo - fluxo.mean()) / (fluxo.std() + 1e-9)
    fps_env = sr / hop
    ac = np.correlate(fluxo, fluxo, mode="full")[len(fluxo) - 1:]
    lo, hi = int(fps_env * 60 / 180), int(fps_env * 60 / 70)
    periodo = lo + int(np.argmax(ac[lo:hi]))
    fase = int(np.argmax([fluxo[f::periodo].sum() for f in range(periodo)]))
    tempos = [round((fase + k * periodo) / fps_env, 3) for k in range(int((len(fluxo) - fase) / periodo))]
    return tempos, round(60 * fps_env / periodo, 1)


def roteiro_montagem(proj, est):
    vid = est["video"]
    sel = os.path.join(proj, "public", vid, "selecao.txt")
    if not os.path.isfile(sel):
        sys.exit(f"ERRO: falta a seleção em {sel}")
    if not est.get("trilha"):
        sys.exit("ERRO: aftermovie precisa da trilha antes: python editor.py trilha <musica>")
    passo = 2 if est.get("bpm", 120) < 100 else 4  # corte a cada 2 ou 4 batidas (~1,5 a 2 s)
    marcas = est.get("batidas", [])[::passo] or [k * 2.0 for k in range(300)]
    t = marcas[0]
    clipes = []
    linhas = [l.split() for l in open(sel, encoding="utf-8-sig") if l.strip() and not l.strip().startswith("#")]
    for k, partes in enumerate(linhas):
        n = int(partes[0])
        desde = float(partes[1]) if len(partes) > 1 else 0.0
        caminho = est["takes"][n - 1]
        fim = marcas[k + 1] if k + 1 < len(marcas) else t + 2.0
        dur = min(fim - t, max(0.5, duracao(os.path.join(proj, caminho)) - desde))
        clipes.append({"arquivo": caminho.replace("public/", "", 1), "inicio": round(t - marcas[0], 3),
                       "fim": round(t - marcas[0] + dur, 3), "desde": round(desde, 2)})
        t += dur
    total_s = t - marcas[0]
    rot_path = os.path.join(proj, "public", "roteiro.json")
    tema, faixa, _ = tema_padrao(ler(rot_path, {}))
    rot = {"fps": FPS, "largura": 1080, "altura": 1920, "duracaoQuadros": int(round(total_s * FPS)), "base": "",
           "trechos": [], "clipes": clipes, "tema": tema, "faixaY": 900, "punchIn": False,
           "lettering": [{"inicio": 0.2, "fim": min(2.6, total_s), "texto": est["titulo"].upper()},
                         {"inicio": max(0, total_s - 2.2), "fim": total_s, "texto": est["cliente"].upper()}],
           "legenda": [], "broll": [], "sfx": [],
           "trilha": {"arquivo": est["trilha"], "volume": 0.9, "desde": marcas[0]}}
    gravar(rot_path, rot)
    print(f"roteiro: {len(clipes)} clipes na batida ({est.get('bpm', '?')} BPM, corte a cada {passo} batidas), {total_s:.1f}s")
    print("título no início e cliente no fim: ajuste os textos em lettering")
    concluir(proj, est, "roteiro")


def cmd_trilha(a):
    proj = projeto_atual()
    est = estado(proj)
    vid = est["video"]
    ext = os.path.splitext(a.arquivo)[1] or ".mp3"
    destino = os.path.join(proj, "public", vid, "trilha" + ext)
    shutil.copy2(a.arquivo, destino)
    est["trilha"] = f"{vid}/trilha{ext}"
    if est["formato"] == "aftermovie":
        est["batidas"], est["bpm"] = batidas(destino)
        print(f"trilha: {destino} | {est['bpm']} BPM, {len(est['batidas'])} batidas")
        concluir(proj, est, "trilha")
        return
    rot_path = os.path.join(proj, "public", "roteiro.json")
    rot = ler(rot_path)
    if rot and rot.get("base"):
        rot["trilha"] = {"arquivo": est["trilha"], "volume": a.volume}
        gravar(rot_path, rot)
    print(f"trilha: {destino} (volume {a.volume}). Registre a origem no historico.md do cliente.")
    concluir(proj, est, est["etapa"])


def biblioteca_sfx():
    base = os.path.join(estudio(), "_biblioteca", "sfx", "_normalizados")
    achados = {}
    for cat in ("whoosh", "transicao", "pop", "impacto"):
        pasta = os.path.join(base, cat)
        if os.path.isdir(pasta):
            arqs = sorted(f for f in os.listdir(pasta) if f.lower().endswith((".wav", ".mp3")))
            if arqs:
                achados[cat] = [os.path.join(pasta, f) for f in arqs]
    return achados


def cmd_montar(_):
    proj = projeto_atual()
    est = estado(proj)
    rot_path = os.path.join(proj, "public", "roteiro.json")
    rot = ler(rot_path)
    let = rot.get("lettering", [])
    antes = len(rot.get("legenda", []))
    rot["legenda"] = [g for g in rot.get("legenda", []) if not any(g["inicio"] < l["fim"] and l["inicio"] < g["fim"] for l in let)]
    lib = biblioteca_sfx()
    pasta_sfx = os.path.join(proj, "public", "sfx")
    os.makedirs(pasta_sfx, exist_ok=True)
    manuais = [s for s in rot.get("sfx", []) if not s.get("auto")]
    auto = []

    def usar(cat, t, k):
        lista = lib.get(cat) or lib.get("whoosh") or lib.get("pop")
        if not lista:
            return
        src = lista[k % len(lista)]
        shutil.copy2(src, os.path.join(pasta_sfx, os.path.basename(src)))
        auto.append({"t": round(max(0, t - 0.03), 2), "arquivo": f"sfx/{os.path.basename(src)}", "volume": 0.3, "auto": True})

    simples = est["formato"] in ("legenda", "decupagem")
    if not simples:
        for k, l in enumerate(let):
            usar("whoosh", l["inicio"], k)
        for k, b in enumerate(rot.get("broll", [])):
            usar("transicao", b["inicio"], k)
    rot["sfx"] = manuais + auto
    gravar(rot_path, rot)
    aviso = "" if lib or simples else " (biblioteca de SFX vazia: _biblioteca/sfx + estudio.py normalizar-sfx)"
    print(f"montado: {len(let)} letterings, {antes - len(rot['legenda'])} legendas removidas sob lettering, {len(auto)} SFX{aviso}")
    concluir(proj, est, "montar")


def cmd_preview(_):
    proj = projeto_atual()
    est = estado(proj)
    saida = os.path.join(".work", "preview.mp4")
    print(rodar([PY, os.path.join(AQUI, "render.py"), "Video", saida, "--preview"], cwd=proj).strip())
    print("folha: " + rodar([PY, os.path.join(AQUI, "folha.py"), saida, "--quadros", "20"], cwd=proj).strip())
    concluir(proj, est, "preview")


def registrar(cli, est, saida, usados, trilha):
    print(rodar([PY, os.path.join(AQUI, "medir.py"), saida]).strip())
    with open(os.path.join(cli, "historico.md"), "a", encoding="utf-8") as f:
        f.write(f"| {date.today():%d/%m/%Y} | {est['titulo']} ({est['formato']}) | {usados} | {trilha} | |\n")
    print(f"entregue: {saida}")


def cmd_final(_):
    proj = projeto_atual()
    est = estado(proj)
    cli = os.path.dirname(proj)
    saida = os.path.join(cli, "entregas", f"{est['cliente']} - {est['titulo']}.mp4")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    print(rodar([PY, os.path.join(AQUI, "render.py"), "Video", saida], cwd=proj).strip())
    rot = ler(os.path.join(proj, "public", "roteiro.json"), {})
    shutil.copy2(os.path.join(proj, "public", "roteiro.json"), os.path.join(proj, "public", est["video"], "roteiro.json"))
    usados = ", ".join(sorted(set(est.get("brutos", [])) | {os.path.basename(b["arquivo"]) for b in rot.get("broll", [])}))
    registrar(cli, est, saida, usados, (rot.get("trilha") or {}).get("arquivo", "sem trilha"))
    concluir(proj, est, "final")


def cmd_entregar(a):
    proj = projeto_atual()
    est = estado(proj)
    cli = est.get("cliente_dir") or os.path.dirname(proj)
    saida = os.path.join(cli, "entregas", f"{est['cliente']} - {est['titulo']}{os.path.splitext(a.arquivo)[1] or '.mp4'}")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    shutil.copy2(a.arquivo, saida)
    registrar(cli, est, saida, a.complemento or "motion", "ver peça")
    concluir(proj, est, "entregar")


def cmd_abrir(a):
    proj = projeto_atual()
    rot = os.path.join(proj, "public", a.id, "roteiro.json")
    if not os.path.isfile(rot):
        sys.exit(f"ERRO: não achei {rot}")
    shutil.copy2(rot, os.path.join(proj, "public", "roteiro.json"))
    est = estado(proj)
    est["video"] = a.id
    print(f"aberto: {a.id}")
    concluir(proj, est, "montar")


def cmd_status(_):
    proj = projeto_atual()
    est = estado(proj)
    print(f"cliente: {est.get('cliente')} | vídeo: {est.get('video')} | formato: {est.get('formato')} | "
          f"etapa concluída: {est.get('etapa')}")
    print(f"projeto: {proj}")
    concluir(proj, est, est.get("etapa", "novo"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Trilho do Editor Pro")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("analisar"); p.add_argument("arquivos", nargs="+"); p.set_defaults(f=cmd_analisar)
    p = sub.add_parser("novo"); p.add_argument("--formato", required=True, choices=FORMATOS)
    p.add_argument("cliente"); p.add_argument("titulo"); p.add_argument("arquivos", nargs="*"); p.set_defaults(f=cmd_novo)
    sub.add_parser("voz").set_defaults(f=cmd_voz)
    sub.add_parser("roteiro").set_defaults(f=cmd_roteiro)
    p = sub.add_parser("trilha"); p.add_argument("arquivo"); p.add_argument("--volume", type=float, default=0.08)
    p.set_defaults(f=cmd_trilha)
    sub.add_parser("montar").set_defaults(f=cmd_montar)
    sub.add_parser("preview").set_defaults(f=cmd_preview)
    sub.add_parser("final").set_defaults(f=cmd_final)
    p = sub.add_parser("entregar"); p.add_argument("arquivo"); p.add_argument("--complemento")
    p.set_defaults(f=cmd_entregar)
    p = sub.add_parser("abrir"); p.add_argument("id"); p.set_defaults(f=cmd_abrir)
    sub.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args()
    if a.cmd == "novo" and a.formato != "motion" and not a.arquivos:
        sys.exit("ERRO: informe os arquivos de vídeo")
    a.f(a)


if __name__ == "__main__":
    main()
