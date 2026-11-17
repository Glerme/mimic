#!/usr/bin/env python3
"""Compara o seu vídeo com a referência: números de ritmo lado a lado e uma folha com os dois na mesma altura do tempo.

Uso (na pasta do kit):
  python3 skills/mimic/scripts/comparar.py referencias/<slug> <seu-video.mp4>

Grava referencias/<slug>/comparacao.jpg (em cima a referência, embaixo o seu, 8 momentos) e imprime a tabela.
Sai com erro se o formato de tela for outro, a duração fugir mais de 15% ou o número de planos fugir mais de 30%.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar import fail, ffmpeg, folha, mede, say  # noqa: E402


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    ref, meu = Path(a[0]), Path(a[1])
    if not (ref / "ficha.json").exists():
        fail(f"não achei {ref / 'ficha.json'}: rode o analisar.py primeiro")
    if not meu.exists():
        fail(f"não achei {meu}")
    o = json.loads((ref / "ficha.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        s = mede(meu, Path(tmp), com_fala="fala" in o and bool(o["fala"].get("palavras")))
        larg = 216 if o["formato"] == "9:16" else 384
        for nome, video, dur in (("a", ref / "original.mp4", o["duracao"]), ("b", meu, s["duracao"])):
            folha(video, [dur * (i + 0.5) / 8 for i in range(8)], f"{tmp}/{nome}.jpg", larg, 8)
        ffmpeg("-i", f"{tmp}/a.jpg", "-i", f"{tmp}/b.jpg", "-filter_complex", "[1][0]scale2ref[b][a];[a][b]vstack", "-q:v", "4", ref / "comparacao.jpg")

    linhas = [("formato de tela", o["formato"], s["formato"]), ("duração (s)", o["duracao"], s["duracao"]),
              ("planos", o["ritmo"]["planos"], s["ritmo"]["planos"]), ("plano médio (s)", o["ritmo"]["plano_medio_seg"], s["ritmo"]["plano_medio_seg"]),
              ("cortes a cada 10 s", o["ritmo"]["cortes_por_10s"], s["ritmo"]["cortes_por_10s"])]
    if "mudancas_por_10s" in o["ritmo"] and "mudancas_por_10s" in s["ritmo"]:
        linhas.append(("mudanças de tela / 10 s", o["ritmo"]["mudancas_por_10s"], s["ritmo"]["mudancas_por_10s"]))
    if o.get("fala", {}).get("palavras") and s.get("fala", {}).get("palavras"):
        linhas += [("palavras por segundo", o["fala"]["palavras_por_seg"], s["fala"]["palavras_por_seg"]),
                   ("primeira palavra em (s)", o["fala"]["primeira_palavra_em"], s["fala"]["primeira_palavra_em"])]
    say(f"{'':26}{'referência':>12}{'seu':>12}")
    for nome, x, y in linhas:
        say(f"{nome:26}{str(x):>12}{str(y):>12}")
    say(f"folha: {ref / 'comparacao.jpg'} (em cima a referência, embaixo o seu)")

    erros = []
    if o["formato"] != s["formato"]:
        erros.append(f"formato de tela diferente ({s['formato']} em vez de {o['formato']})")
    if abs(s["duracao"] - o["duracao"]) > 0.15 * o["duracao"]:
        erros.append("duração foge mais de 15% da referência")
    if abs(s["ritmo"]["planos"] - o["ritmo"]["planos"]) > max(1, 0.3 * o["ritmo"]["planos"]):
        erros.append("número de planos foge mais de 30% da referência")
    mo, ms = o["ritmo"].get("mudancas_por_10s"), s["ritmo"].get("mudancas_por_10s")
    if mo and ms is not None and ms < 0.6 * mo:
        erros.append("seu vídeo muda de tela bem menos vezes que a referência (está parado demais)")
    if erros:
        fail("ainda não bate: " + "; ".join(erros))
    say("ritmo dentro da margem. Agora olhe a folha: layout, cor e legenda batem?")


if __name__ == "__main__":
    main()
