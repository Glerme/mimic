#!/usr/bin/env python3
"""Mede um vídeo de referência pra copiar o FORMATO dele (ritmo, estrutura, visual), nunca o conteúdo.

Uso (na pasta do kit):
  python3 skills/mimic/scripts/analisar.py <link-ou-arquivo> [--nome slug] [--idioma pt] [--sem-fala]

Aceita link do YouTube, TikTok, Instagram, X (precisa do yt-dlp: pip install yt-dlp) ou um arquivo de vídeo.
Se o link não baixar (Instagram costuma pedir login), baixe o vídeo você mesmo e passe o arquivo.

Cria referencias/<slug>/:
  original.mp4           o vídeo (fica só na sua máquina: é referência, não entra em vídeo nenhum)
  ficha.json             os números: tamanho, duração, planos, cortes, ritmo, fala com tempo, som
  quadros/visao.jpg      o vídeo inteiro numa folha (um quadro por segundo, até 48)
  quadros/plano-NN.jpg   cada plano em quadros (os tempos de cada quadro estão na ficha.json)
  quadros/corte-NN.jpg   6 quadros seguidos em volta de cada corte (mostra como é a transição)
"""
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def acha_kit():
    aqui = Path(__file__).resolve().parent
    kit_txt = aqui.parent / "kit.txt"  # skill instalada com instalar_skills.py --global
    cands = ([Path(kit_txt.read_text(encoding="utf-8").strip())] if kit_txt.exists() else []) + list(aqui.parents) + [Path.cwd()]
    for c in cands:
        if (c / "ferramentas" / "comum.py").exists():
            return c
    raise SystemExit("ERRO: não achei a pasta do kit (a que tem ferramentas/comum.py). Rode este script de dentro dela.")


KIT = acha_kit()
sys.path.insert(0, str(KIT / "ferramentas"))
from comum import HF, fail, ffmpeg, say, tem  # noqa: E402

MEDIR = ["npx", "-y", "hyperframes@0.9.55", "measure"]  # o "measure" só existe a partir da 0.9; o render segue na versão do kit


def roda(cmd, **k):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **k)


def baixa(link, pasta):
    ytdlp = ["yt-dlp"] if tem("yt-dlp") else [sys.executable, "-m", "yt_dlp"]
    r = roda(ytdlp + ["--no-playlist", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b", "--merge-output-format", "mp4",
                      "--write-info-json", "-o", str(pasta / "original.%(ext)s"), link])
    mp4 = pasta / "original.mp4"
    if r.returncode or not mp4.exists():
        fail("não consegui baixar esse link (" + (r.stderr.strip().splitlines() or ["yt-dlp não instalado: pip install yt-dlp"])[-1][:200]
             + ").\nBaixe o vídeo você mesmo e rode de novo passando o arquivo.")
    info = pasta / "original.info.json"
    meta = {}
    if info.exists():
        d = json.loads(info.read_text(encoding="utf-8"))
        meta = {k: d.get(k) for k in ("title", "uploader", "view_count", "like_count", "webpage_url") if d.get(k) is not None}
        info.unlink()
    return mp4, meta


def sonda(video):
    r = roda(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video])
    try:
        d = json.loads(r.stdout)
        v = next(s for s in d["streams"] if s["codec_type"] == "video")
    except (json.JSONDecodeError, StopIteration, KeyError):
        fail(f"não consegui ler {video} como vídeo")
    w, h = int(v["width"]), int(v["height"])
    if str((v.get("side_data_list") or [{}])[0].get("rotation", 0)).lstrip("-") in ("90", "270"):
        w, h = h, w
    n, dn = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(n) / float(dn or 1) if float(dn or 1) else 30.0
    prop = w / h
    formato = "9:16" if prop < 0.7 else "16:9" if prop > 1.5 else "1:1" if 0.9 < prop < 1.1 else f"{w}x{h}"
    return {"largura": w, "altura": h, "fps": round(fps, 3), "duracao": round(float(d["format"]["duration"]), 3),
            "formato": formato, "tem_som": any(s["codec_type"] == "audio" for s in d["streams"])}


def medidor(oque, video):
    """JSON do "hyperframes measure <oque>", ou None. Roda numa pasta temporária pra não deixar lixo no kit."""
    if not tem("npx"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        r = roda(MEDIR + [oque, Path(video).resolve()], cwd=tmp)
    try:
        return json.loads(r.stdout[r.stdout.index("{"):]) if r.returncode == 0 else None
    except ValueError:
        return None


def cortes(video, dur):
    """Tempos dos cortes. O medidor do HyperFrames acha corte que a nota de cena do ffmpeg perde; sem ele, cai no ffmpeg."""
    d = medidor("cuts", video)
    if d and "cuts" in d:
        return [c["t"] for c in d["cuts"]], "hyperframes measure"
    r = roda(["ffmpeg", "-hide_banner", "-i", video, "-vf", "select='gt(scene,0.2)',showinfo", "-an", "-f", "null", "-"])
    ts = [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    return [t for t in ts if 0.2 < t < dur - 0.2], "ffmpeg (aproximado: confira nas folhas)"


def folha(video, tempos, saida, larg, colunas):
    """Uma folha com um quadro por tempo, em grade."""
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(tempos):
            ffmpeg("-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-update", "1", "-vf", f"scale={larg}:-2", "-q:v", "4", f"{tmp}/q{i:03d}.jpg")
        cols = min(colunas, len(tempos))
        ffmpeg("-i", f"{tmp}/q%03d.jpg", "-vf", f"tile={cols}x{math.ceil(len(tempos) / cols)}:padding=4:color=white",
               "-frames:v", "1", "-update", "1", "-q:v", "4", saida)


def transcreve(video, idioma, tmp):
    """[(palavra, início, fim)] ou None se não houver Whisper."""
    wav = Path(tmp) / "fala.wav"
    ffmpeg("-i", video, "-vn", "-ac", "1", "-ar", "16000", wav)
    if tem("whisper"):
        r = roda(["whisper", wav, "--model", "small", "--word_timestamps", "True", "--output_format", "json",
                  "--output_dir", tmp, "--fp16", "False", "--verbose", "False"] + (["--language", idioma] if idioma else []))
        f = Path(tmp) / "fala.json"
        if r.returncode == 0 and f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            return [(w["word"].strip(), round(w["start"], 2), round(w["end"], 2)) for s in d["segments"] for w in s.get("words", [])], d.get("language")
    r = roda(HF + ["transcribe", wav, "-m", "small", "--json", "-d", tmp] + (["-l", idioma] if idioma else []))
    if r.returncode == 0:
        try:
            d = json.loads(r.stdout)
            ws = d.get("words") or d.get("transcript", {}).get("words") or []
            return [((w.get("text") or w.get("word")).strip(), round(w["start"], 2), round(w["end"], 2)) for w in ws], idioma
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
    return None, None


def silencios(video):
    r = roda(["ffmpeg", "-hide_banner", "-i", video, "-vn", "-af", "silencedetect=noise=-38dB:d=0.35", "-f", "null", "-"])
    a = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    b = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [[round(max(0, x), 2), round(y, 2)] for x, y in zip(a, b)]


def mede(video, pasta, idioma=None, com_fala=True):
    """Mede o vídeo e grava as folhas em pasta/quadros. Devolve a ficha (dict)."""
    p = sonda(video)
    dur, fps = p["duracao"], p["fps"]
    larg = 216 if p["formato"] == "9:16" else 384 if p["formato"] == "16:9" else 288
    q = pasta / "quadros"
    q.mkdir(parents=True, exist_ok=True)
    for velho in q.glob("*.jpg"):
        velho.unlink()

    ts, como = cortes(video, dur)
    ts = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] >= 0.15]  # clarão de 1 ou 2 quadros não é plano
    bordas = [0.0] + ts + [dur]
    n = min(48, max(8, math.ceil(dur)))
    folha(video, [dur * (i + 0.5) / n for i in range(n)], q / "visao.jpg", min(larg, 256), 8)

    planos = []
    for i, (a, b) in enumerate(zip(bordas, bordas[1:]), 1):
        seg = b - a
        k = min(12, max(2, math.ceil(seg / 0.75)))
        tempos = [round(a + seg * (j + 0.5) / k, 2) for j in range(k)]
        plano = {"n": i, "de": round(a, 2), "ate": round(b, 2), "seg": round(seg, 2)}
        if i <= 60:  # ponytail: acima de 60 planos só os 60 primeiros ganham folha; o ritmo sai dos números
            folha(video, tempos, q / f"plano-{i:02d}.jpg", larg, 6)
            plano.update(folha=f"quadros/plano-{i:02d}.jpg", tempos=tempos)
        planos.append(plano)
    tiras = []
    for i, t in enumerate(ts[:24], 1):
        ffmpeg("-ss", f"{max(0, t - 3 / fps):.3f}", "-i", video, "-vf", f"scale={larg}:-2,tile=6x1:padding=4:color=white",
               "-frames:v", "1", "-update", "1", "-q:v", "4", q / f"corte-{i:02d}.jpg")
        tiras.append({"t": round(t, 2), "folha": f"quadros/corte-{i:02d}.jpg"})

    segs = [x["seg"] for x in planos]
    ficha = {**p, "planos": planos, "cortes": tiras, "cortes_medidos_com": como,
             "ritmo": {"planos": len(planos), "plano_medio_seg": round(sum(segs) / len(segs), 2), "plano_mais_curto_seg": min(segs),
                       "plano_mais_longo_seg": max(segs), "cortes_por_10s": round(len(ts) / dur * 10, 2)}}

    # vídeo de motion quase não tem corte seco: o ritmo dele está nas mudanças de tela (algo entra, sai ou troca)
    ev = medidor("events", video)
    if ev and "events" in ev:
        mud = [{"t": round(e["t"], 2), "tipo": {"appear": "entra", "disappear": "sai", "cut": "corte", "flash": "clarão"}.get(e["type"], "muda"),
                "forca": round(e["magnitude"], 1)} for e in ev["events"] if e["type"] != "hold" and e.get("magnitude", 0) >= 5]
        mud = [m for i, m in enumerate(mud) if i == 0 or m["t"] - mud[i - 1]["t"] >= 0.25]
        paradas = [e["seconds"] for e in ev["events"] if e["type"] == "hold"]
        ficha["mudancas"] = mud
        ficha["ritmo"].update(mudancas_por_10s=round(len(mud) / dur * 10, 2), parada_mais_longa_seg=max(paradas, default=0))

    if p["tem_som"]:
        sil = silencios(video)
        ficha["som"] = {"silencios": sil, "seg_em_silencio": round(sum(b - a for a, b in sil), 2)}
        if com_fala:
            with tempfile.TemporaryDirectory() as tmp:
                ws, lingua = transcreve(video, idioma, tmp)
            if ws is None:
                say("sem Whisper: a ficha sai sem a fala (instale com: pip install openai-whisper)")
            elif ws:
                falado = sum(e - s for _, s, e in ws)
                pausas = [[ws[i][2], ws[i + 1][1]] for i in range(len(ws) - 1) if ws[i + 1][1] - ws[i][2] >= 0.6]
                # pausa da fala que não é silêncio no áudio = tem trilha ou efeito por baixo
                com_som = [x for x in pausas if not any(a <= x[0] + 0.1 and b >= x[1] - 0.1 for a, b in sil)]
                ficha["fala"] = {"idioma": lingua, "palavras": len(ws), "palavras_por_seg": round(len(ws) / dur, 2),
                                 "seg_falando": round(falado, 2), "primeira_palavra_em": ws[0][1], "ultima_palavra_em": ws[-1][2],
                                 "gancho_3s": " ".join(w for w, s, _ in ws if s < 3.0), "pausas": pausas,
                                 "texto": " ".join(w for w, _, _ in ws), "palavras_com_tempo": ws}
                ficha["som"]["trilha_ou_efeito_nas_pausas"] = bool(com_som) if pausas else None
                for x in planos:
                    x["fala"] = " ".join(w for w, s, _ in ws if x["de"] <= s < x["ate"])
            else:
                ficha["fala"] = {"palavras": 0, "obs": "o Whisper não ouviu fala: vídeo só com música ou texto na tela"}
    return ficha


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("-"):
        print(__doc__)
        sys.exit(1)
    alvo = a[0]
    idioma = a[a.index("--idioma") + 1] if "--idioma" in a else None
    link = re.match(r"https?://", alvo)
    if not link and not Path(alvo).exists():
        fail(f"não achei o arquivo {alvo}")
    slug = a[a.index("--nome") + 1] if "--nome" in a else re.sub(r"[^a-z0-9]+", "-", (alvo.rstrip("/").split("/")[-1] if link else Path(alvo).stem).lower()).strip("-")[:40] or "referencia"
    pasta = KIT / "referencias" / slug
    pasta.mkdir(parents=True, exist_ok=True)
    video, fonte = pasta / "original.mp4", {"arquivo": alvo}
    if link:
        say("baixando o vídeo...")
        video, meta = baixa(alvo, pasta)
        fonte = {"link": alvo, **meta}
    elif Path(alvo).resolve() != video.resolve():
        ffmpeg("-i", alvo, "-c", "copy", "-movflags", "+faststart", video)
    say("medindo cortes, planos e fala (a primeira vez demora mais)...")
    ficha = {"fonte": fonte, **mede(video, pasta, idioma, "--sem-fala" not in a)}
    (pasta / "ficha.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=1), encoding="utf-8")
    r, f = ficha["ritmo"], ficha.get("fala", {})
    say(f"ok: {pasta}\n  {ficha['formato']} {ficha['largura']}x{ficha['altura']}, {ficha['duracao']:.1f}s, {r['planos']} planos "
        f"(médio {r['plano_medio_seg']}s, {r['cortes_por_10s']} cortes a cada 10s"
        + (f", {r['mudancas_por_10s']} mudanças de tela a cada 10s" if "mudancas_por_10s" in r else "") + ")"
        + (f", {f['palavras_por_seg']} palavras/s" if f.get("palavras") else "")
        + f"\n  leia: {pasta / 'ficha.json'} e as folhas em {pasta / 'quadros'}")


if __name__ == "__main__":
    main()
