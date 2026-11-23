"""
Trilho do Editor Pro: uma etapa por comando, estado salvo, e a saída sempre diz o próximo passo.

  python editor.py status                                   # onde parou e o que fazer agora
  python editor.py novo "<Cliente>" "<Título>" <brutos...>   # 1. pastas + projeto + triagem + transcrição
  (você escreve takes.txt = decupagem)                       # 2. decupagem
  python editor.py voz                                      # 3. limpa a voz, corta silêncios, retranscreve, confere
  python editor.py roteiro                                  # 4. gera roteiro.json (legenda automática) + mapa do rosto
  (você edita roteiro.json: tema, faixaY, lettering, b-roll) # 5. criação
  python editor.py trilha <arquivo.mp3> [--volume 0.08]     # 6. trilha (opcional, só se aprovada)
  python editor.py montar                                   # 7. SFX automáticos + tira legenda onde há lettering
  python editor.py preview                                  # 8. prévia em baixa + folha
  python editor.py final                                    # 9. render final + volume + histórico
  python editor.py abrir <id>                               # volta a um vídeo anterior do cliente
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

PROXIMO = {
    "triagem": "2. DECUPAGEM: leia os .txt listados (e a folha só de take duvidoso). Escreva {vid}/takes.txt com o "
               "melhor trecho de cada fala, na ordem do vídeo, uma linha por trecho: \"caminho\" inicio fim. "
               "Depois: python editor.py voz",
    "voz": "4. python editor.py roteiro",
    "roteiro": "5. CRIAÇÃO: abra o mapa do rosto uma vez, depois edite public/roteiro.json: tema (cores/fonte do "
               "LEIAME do cliente), faixaY (fora do rosto), lettering (palavras-chave da fala, 2 a 4 palavras), "
               "broll. Trilha aprovada? python editor.py trilha <arquivo>. Depois: python editor.py montar",
    "montar": "8. python editor.py preview",
    "preview": "9. Confira a folha da prévia (rosto livre, margens, ritmo). Ajuste o roteiro e repita montar/preview, "
               "ou: python editor.py final",
    "final": "Entregue. Para outro vídeo: python editor.py novo ... (de preferência numa conversa nova)",
}


# ---------- utilidades ----------
def rodar(cmd, cwd=None, silencioso=True):
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


def duracao(v):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def estudio():
    cfg = ler(os.path.join(os.path.expanduser("~"), ".edicao-video", "config.json"), {})
    raiz = cfg.get("raiz")
    if not raiz or not os.path.isdir(raiz):
        rodar([PY, os.path.join(AQUI, "estudio.py"), "criar"])
        raiz = ler(os.path.join(os.path.expanduser("~"), ".edicao-video", "config.json"), {})["raiz"]
    return raiz


def projeto_atual():
    """Procura o projeto a partir da pasta atual (ou de EDITOR_PROJETO)."""
    p = os.environ.get("EDITOR_PROJETO") or os.getcwd()
    while True:
        if os.path.isfile(os.path.join(p, ".work", "estado.json")):
            return p
        pai = os.path.dirname(p)
        if pai == p:
            break
        p = pai
    ultimo = ler(os.path.join(os.path.expanduser("~"), ".edicao-video", "config.json"), {}).get("ultimo_projeto")
    if ultimo and os.path.isfile(os.path.join(ultimo, ".work", "estado.json")):
        return ultimo
    sys.exit("Nenhum vídeo em andamento. Comece com: python editor.py novo \"Cliente\" \"Título\" <brutos...>")


def estado(proj):
    return ler(os.path.join(proj, ".work", "estado.json"), {})


def salvar_estado(proj, est):
    gravar(os.path.join(proj, ".work", "estado.json"), est)
    cfgp = os.path.join(os.path.expanduser("~"), ".edicao-video", "config.json")
    cfg = ler(cfgp, {})
    cfg["ultimo_projeto"] = proj
    os.makedirs(os.path.dirname(cfgp), exist_ok=True)
    gravar(cfgp, cfg)


def proximo(est):
    print("PRÓXIMO: " + PROXIMO[est["etapa"]].format(vid=f"public/{est['video']}"))


def palavras_json(p):
    dados = ler(p, [])
    return [(w["startMs"] / 1000, w["endMs"] / 1000, w["text"].strip()) for w in dados if w.get("text", "").strip()]


def transcrever(proj, videos, frases_curtas=False):
    rodar([exe("node"), "scripts/transcrever.mjs", *videos], cwd=proj)
    txts = []
    extra = ["--max", "5", "--pausa", "0.3"] if frases_curtas else []
    for v in videos:
        js = os.path.splitext(os.path.join(proj, v))[0] + ".json"
        rodar([PY, os.path.join(AQUI, "transcricao.py"), js, *extra])
        txts.append(os.path.splitext(v)[0] + ".txt")
    return txts


# ---------- etapas ----------
def cmd_novo(a):
    raiz = estudio()
    rodar([PY, os.path.join(AQUI, "estudio.py"), "cliente", a.cliente])
    cli = os.path.join(raiz, "clientes", slug(a.cliente))
    proj = os.path.join(cli, "projeto")
    if not os.path.isfile(os.path.join(proj, "package.json")):
        shutil.copytree(MODELO, proj, dirs_exist_ok=True)
    if not os.path.isdir(os.path.join(proj, "node_modules")):
        print("instalando o projeto Remotion (só na primeira vez, ~1 min)...")
        rodar([exe("npm"), "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=proj)
    vid = f"{date.today():%Y-%m-%d}-{slug(a.titulo)}"
    pub = os.path.join(proj, "public", vid)
    os.makedirs(os.path.join(pub, "takes"), exist_ok=True)
    os.makedirs(os.path.join(proj, ".work"), exist_ok=True)
    guardar = os.path.join(cli, "01-brutos", vid)
    os.makedirs(guardar, exist_ok=True)

    takes = []
    for n, bruto in enumerate(a.brutos, 1):
        bruto = os.path.abspath(bruto)
        if not os.path.isfile(bruto):
            sys.exit(f"ERRO: bruto não encontrado: {bruto}")
        destino_bruto = os.path.join(guardar, os.path.basename(bruto))
        if not os.path.exists(destino_bruto):
            shutil.copy2(bruto, destino_bruto)
        saida = os.path.join(pub, "takes", f"{n:02d}.mp4")
        trc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=color_transfer", "-of", "csv=p=0", bruto], capture_output=True, text=True).stdout
        hdr = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0," \
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," if trc.strip() in ("arib-std-b67", "smpte2084") else ""
        vf = hdr + "scale=1080:1920:force_original_aspect_ratio=increase:in_range=tv:out_range=tv,crop=1080:1920," \
                   f"fps={FPS},format=yuv420p"
        rodar(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-vf", vf, "-color_range", "tv", "-colorspace", "bt709",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", saida])
        takes.append(f"public/{vid}/takes/{n:02d}.mp4")
    print(f"triagem: {len(takes)} takes em 1080x1920 30 fps. Transcrevendo (whisper local)...")
    txts = transcrever(proj, takes)

    est = {"cliente": a.cliente, "titulo": a.titulo, "video": vid, "etapa": "triagem", "takes": takes,
           "brutos": [os.path.basename(b) for b in a.brutos]}
    salvar_estado(proj, est)
    print(f"projeto: {proj}")
    print(f"leia antes: {os.path.join(cli, 'LEIAME.md')} (identidade do cliente)")
    for tk, tx in zip(takes, txts):
        n = len(palavras_json(os.path.join(proj, os.path.splitext(tk)[0] + ".json")))
        tipo = "fala" if n >= 4 else "b-roll? (quase sem fala)"
        print(f"  {tk}  {duracao(os.path.join(proj, tk)):.1f}s  {n} palavras  {tipo}  -> {tx}")
    print(f"folhas (só se precisar): python {os.path.join(AQUI, 'folha.py')} <take>")
    proximo(est)


def cmd_voz(_):
    proj = projeto_atual()
    est = estado(proj)
    vid = est["video"]
    lista = os.path.join(proj, "public", vid, "takes.txt")
    if not os.path.isfile(lista):
        sys.exit(f"ERRO: falta a decupagem em {lista}")
    trechos = []
    with open(lista, encoding="utf-8-sig") as f:
        for linha in f:
            m = re.match(r'\s*"?([^"]+?)"?\s+([\d.]+)\s+([\d.]+)\s*$', linha)
            if linha.strip() and not linha.strip().startswith("#"):
                if not m:
                    sys.exit(f"ERRO na linha do takes.txt: {linha.strip()}")
                caminho = m.group(1)
                if not os.path.isabs(caminho):
                    caminho = os.path.join(proj, caminho)
                trechos.append((caminho.replace("\\", "/"), float(m.group(2)), float(m.group(3))))
    absoluta = os.path.join(proj, ".work", "takes-abs.txt")
    with open(absoluta, "w", encoding="utf-8") as f:
        for c, i, fim in trechos:
            f.write(f'"{c}" {i} {fim}\n')
    base = os.path.join(proj, "public", vid, "base.mp4")
    print(rodar([PY, os.path.join(AQUI, "limpar_voz.py"), "--lista", absoluta, "-o", base, "--cortar-silencios",
                 "--respiro", "0.14", "--escala", "1080x1920", "--fps", str(FPS)]).strip().splitlines()[0])
    transcrever(proj, [f"public/{vid}/base.mp4"], frases_curtas=True)
    esperadas = 0
    for c, i, fim in trechos:
        ws = palavras_json(os.path.splitext(c)[0] + ".json")
        esperadas += sum(1 for w in ws if w[0] >= i - 0.05 and w[1] <= fim + 0.05)
    obtidas = len(palavras_json(os.path.splitext(base)[0] + ".json"))
    aviso = "ok" if abs(obtidas - esperadas) <= max(2, esperadas * 0.05) else "CONFIRA: diferença de palavras"
    print(f"conferência: {esperadas} palavras nos trechos x {obtidas} na base ({aviso})")
    print(f"texto da base: public/{vid}/base.txt")
    est["etapa"] = "voz"
    salvar_estado(proj, est)
    proximo(est)


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


def cmd_roteiro(_):
    proj = projeto_atual()
    est = estado(proj)
    vid = est["video"]
    pub = os.path.join(proj, "public", vid)
    cortes = ler(os.path.join(pub, "base.cortes.json"))
    if not cortes:
        sys.exit("ERRO: rode antes: python editor.py voz")
    trechos = cortes["trechos"] if isinstance(cortes, dict) else cortes
    total = max(t["quadro_saida"] + t["quadros"] for t in trechos)
    rot_path = os.path.join(proj, "public", "roteiro.json")
    antigo = ler(rot_path, {})
    rot = {
        "fps": FPS, "largura": 1080, "altura": 1920, "duracaoQuadros": total,
        "base": f"{vid}/base.mp4", "trechos": trechos,
        "tema": (antigo.get("tema") if antigo.get("base") else None) or {"fonte": "Montserrat", "peso": 800, "cor": "#FFFFFF", "destaque": "#FFD400",
                                      "tamanho": 92, "tamanhoLegenda": 46},
        "faixaY": antigo.get("faixaY", 1240) if antigo.get("base") else 1240, "punchIn": True,
        "lettering": [], "legenda": frases(palavras_json(os.path.join(pub, "base.json"))),
        "broll": [], "sfx": [], "trilha": None,
    }
    gravar(rot_path, rot)
    # mapa do rosto: 3 quadros com grade de 100 px numa imagem só
    seg = total / FPS
    entradas, filtros = [], []
    for k, frac in enumerate((0.15, 0.5, 0.85)):
        entradas += ["-ss", f"{seg * frac:.2f}", "-i", os.path.join(pub, "base.mp4")]
        filtros.append(f"[{k}:v]drawgrid=w=iw:h=100:t=2:c=red@0.7,scale=300:-2,trim=end_frame=1[q{k}]")
    mapa = os.path.join(proj, ".work", "mapa-rosto.jpg")
    rodar(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex",
           ";".join(filtros) + ";[q0][q1][q2]hstack=3", "-frames:v", "1", "-q:v", "5", mapa])
    est["etapa"] = "roteiro"
    salvar_estado(proj, est)
    print(f"roteiro: {rot_path} ({total / FPS:.1f}s, {len(trechos)} planos, {len(rot['legenda'])} legendas automáticas)")
    print(f"mapa do rosto (3 quadros; cada linha vermelha = 100 px do vídeo; y real = y na imagem x 3,6): {mapa}")
    print("tema e faixaY herdados do vídeo anterior do cliente" if antigo.get("base") else "tema padrão: troque pelo do cliente")
    proximo(est)


def cmd_trilha(a):
    proj = projeto_atual()
    est = estado(proj)
    vid = est["video"]
    ext = os.path.splitext(a.arquivo)[1] or ".mp3"
    destino = os.path.join(proj, "public", vid, "trilha" + ext)
    shutil.copy2(a.arquivo, destino)
    rot_path = os.path.join(proj, "public", "roteiro.json")
    rot = ler(rot_path)
    rot["trilha"] = {"arquivo": f"{vid}/trilha{ext}", "volume": a.volume}
    gravar(rot_path, rot)
    print(f"trilha: {destino} (volume {a.volume}). Registre a origem no historico.md do cliente.")
    proximo(est)


def biblioteca_sfx():
    raiz = estudio()
    base = os.path.join(raiz, "_biblioteca", "sfx", "_normalizados")
    achados = {}
    for cat in ("whoosh", "transicao", "pop"):
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
    # 1) legenda só onde não há lettering
    let = rot.get("lettering", [])
    antes = len(rot.get("legenda", []))
    rot["legenda"] = [g for g in rot.get("legenda", [])
                      if not any(g["inicio"] < l["fim"] and l["inicio"] < g["fim"] for l in let)]
    # 2) SFX automáticos: whoosh no lettering, transição no b-roll (mesmo volume, sem repetir seguido)
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

    for k, l in enumerate(let):
        usar("whoosh", l["inicio"], k)
    for k, b in enumerate(rot.get("broll", [])):
        usar("transicao", b["inicio"], k)
    rot["sfx"] = manuais + auto
    gravar(rot_path, rot)
    est["etapa"] = "montar"
    salvar_estado(proj, est)
    aviso = "" if lib else " (biblioteca de SFX vazia: monte uma em _biblioteca/sfx e rode estudio.py normalizar-sfx)"
    print(f"montado: {len(let)} letterings, {antes - len(rot['legenda'])} legendas removidas sob lettering, "
          f"{len(auto)} SFX automáticos{aviso}")
    proximo(est)


def cmd_preview(_):
    proj = projeto_atual()
    est = estado(proj)
    saida = os.path.join(".work", "preview.mp4")
    print(rodar([PY, os.path.join(AQUI, "render.py"), "Video", saida, "--preview"], cwd=proj).strip())
    print("folha: " + rodar([PY, os.path.join(AQUI, "folha.py"), saida, "--quadros", "20"], cwd=proj).strip())
    est["etapa"] = "preview"
    salvar_estado(proj, est)
    proximo(est)


def cmd_final(_):
    proj = projeto_atual()
    est = estado(proj)
    cli = os.path.dirname(proj)
    nome = f"{est['cliente']} - {est['titulo']}.mp4"
    saida = os.path.join(cli, "entregas", nome)
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    print(rodar([PY, os.path.join(AQUI, "render.py"), "Video", saida], cwd=proj).strip())
    print(rodar([PY, os.path.join(AQUI, "medir.py"), saida]).strip())
    rot = ler(os.path.join(proj, "public", "roteiro.json"), {})
    shutil.copy2(os.path.join(proj, "public", "roteiro.json"), os.path.join(proj, "public", est["video"], "roteiro.json"))
    hist = os.path.join(cli, "historico.md")
    usados = ", ".join(sorted(set(est.get("brutos") or [os.path.basename(t) for t in est.get("takes", [])]) |
                              {os.path.basename(b["arquivo"]) for b in rot.get("broll", [])}))
    trilha = (rot.get("trilha") or {}).get("arquivo", "sem trilha")
    with open(hist, "a", encoding="utf-8") as f:
        f.write(f"| {date.today():%d/%m/%Y} | {est['titulo']} | {usados} | {trilha} | |\n")
    est["etapa"] = "final"
    salvar_estado(proj, est)
    print(f"entregue: {saida}")
    print("confira: voz ≈ -14 LUFS (linha acima). Histórico do cliente atualizado.")
    proximo(est)


def cmd_abrir(a):
    proj = projeto_atual()
    rot = os.path.join(proj, "public", a.id, "roteiro.json")
    if not os.path.isfile(rot):
        sys.exit(f"ERRO: não achei {rot}")
    shutil.copy2(rot, os.path.join(proj, "public", "roteiro.json"))
    est = estado(proj)
    est.update({"video": a.id, "etapa": "montar"})
    salvar_estado(proj, est)
    print(f"aberto: {a.id}")
    proximo(est)


def cmd_status(_):
    proj = projeto_atual()
    est = estado(proj)
    print(f"cliente: {est.get('cliente')} | vídeo: {est.get('video')} | etapa concluída: {est.get('etapa')}")
    print(f"projeto: {proj}")
    proximo(est)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Trilho do Editor Pro")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("novo"); p.add_argument("cliente"); p.add_argument("titulo"); p.add_argument("brutos", nargs="+")
    p.set_defaults(f=cmd_novo)
    sub.add_parser("voz").set_defaults(f=cmd_voz)
    sub.add_parser("roteiro").set_defaults(f=cmd_roteiro)
    p = sub.add_parser("trilha"); p.add_argument("arquivo"); p.add_argument("--volume", type=float, default=0.08)
    p.set_defaults(f=cmd_trilha)
    sub.add_parser("montar").set_defaults(f=cmd_montar)
    sub.add_parser("preview").set_defaults(f=cmd_preview)
    sub.add_parser("final").set_defaults(f=cmd_final)
    p = sub.add_parser("abrir"); p.add_argument("id"); p.set_defaults(f=cmd_abrir)
    sub.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
