#!/usr/bin/env python3
"""Gera o HISTORIA.md: a história inteira do SealCraft para ler e revisar.

Sai na ordem do jogo: cada ato, cada missão (textos, tarefas e recompensas) e,
no fim, todas as falas do Mestre Vellan e do Gabriel. Tudo vem direto do
gerar_missoes.py, então o documento sempre bate com o que está no jogo.

Uso: python3 -B tools/gerar_historia.py [pasta com os .jar dos mods] [pasta assets do Minecraft]
Os dois argumentos são opcionais e só servem para mostrar o nome dos itens em
português. Sem eles, os itens aparecem pelo código (ex.: minecraft:bread).
"""
import glob
import json
import os
import re
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, AQUI)
sys.dont_write_bytecode = True
import gerar_missoes as g  # noqa: E402

NOMES = {}


def carregar_nomes(pasta_jars=None, pasta_assets=None):
    """Junta as traduções: inglês do mod < português do mod < traduções do pacote."""
    if pasta_assets:
        for indice in sorted(glob.glob(os.path.join(pasta_assets, "indexes", "*.json"))):
            objs = json.load(open(indice))["objects"]
            info = objs.get("minecraft/lang/pt_br.json")
            if info:
                h = info["hash"]
                caminho = os.path.join(pasta_assets, "objects", h[:2], h)
                if os.path.exists(caminho):
                    NOMES.update(json.load(open(caminho, encoding="utf-8")))
    if pasta_jars:
        for jar in sorted(glob.glob(os.path.join(pasta_jars, "*.jar"))):
            try:
                z = zipfile.ZipFile(jar)
            except zipfile.BadZipFile:
                continue
            for idioma in ("en_us", "pt_br"):
                for nome in z.namelist():
                    if re.fullmatch(rf"assets/[^/]+/lang/{idioma}\.json", nome):
                        try:
                            NOMES.update(json.loads(z.read(nome).decode("utf-8", "replace")))
                        except ValueError:
                            pass
    for arq in glob.glob(os.path.join(RAIZ, "pack", "config", "openloader", "resources", "*", "assets", "*",
                                      "lang", "pt_br.json")):
        try:
            NOMES.update(json.load(open(arq, encoding="utf-8")))
        except ValueError:
            pass


def limpar(texto):
    texto = texto.replace("{@pagebreak}", "")
    texto = re.sub(r"&[0-9a-fk-or]", "", texto)
    return texto.replace("\\n", "\n").replace("@initiator", "[seu nome]").strip()


def nome_de(codigo):
    if codigo.startswith("#"):
        return codigo
    ns, _, caminho = codigo.partition(":")
    for chave in (f"item.{ns}.{caminho}", f"block.{ns}.{caminho}", f"entity.{ns}.{caminho}"):
        if chave in NOMES:
            return NOMES[chave]
    return codigo


def nome_item(it):
    if isinstance(it, str):
        return nome_de(it)
    tag = it.get("tag", {}) or {}
    exibicao = tag.get("display", {}).get("Name")
    if exibicao:
        try:
            d = json.loads(exibicao)
            texto = d.get("text", "") + "".join(x.get("text", "") for x in d.get("extra", []))
            if texto:
                return limpar(texto)
        except (ValueError, AttributeError):
            pass
    if "Potion" in tag:
        efeito = tag["Potion"].split(":")[-1]
        return NOMES.get(f"item.minecraft.potion.effect.{efeito}", f"Poção ({efeito})")
    raca = tag.get("BlockEntityTag", {}).get("Breed")
    if raca:
        return f"Ovo de dragão ({raca.split(':')[-1]})"
    feiticos = tag.get("ISB_Spells", {}).get("data")
    if feiticos:
        lista = ", ".join(nome_de(f"{s['id']}") for s in feiticos)
        return f"{nome_de(it['id'])} ({lista})"
    if "ISB_Spell" in tag or "ISB_spell" in tag:
        s = tag.get("ISB_Spell") or tag.get("ISB_spell")
        return f"Pergaminho: {s}"
    return nome_de(it["id"])


def qtd(v):
    if isinstance(v, g.Raw):
        v = v.s
    return int(re.sub(r"[^0-9]", "", str(v)) or 1)


def tarefa(t):
    tipo = t["type"]
    if t.get("title") and tipo != "item":
        return limpar(t["title"])
    if tipo == "item":
        n = qtd(t.get("count", 1))
        base = f"Entregar/ter {nome_item(t['item'])}" + (f" x{n}" if n > 1 else "")
        if t.get("title"):
            base = f"{limpar(t['title'])} ({base})"
        return base + (" (o item é consumido)" if t.get("consume_items") else "")
    if tipo == "kill":
        return f"Derrotar {qtd(t.get('value', 1))}x {nome_de(t['entity'])}"
    if tipo == "structure":
        return f"Encontrar a estrutura {t['structure']}"
    if tipo == "dimension":
        return f"Entrar em {t['dimension']}"
    if tipo == "biome":
        return f"Entrar no bioma {t['biome']}"
    if tipo == "advancement":
        return f"Conquista {t['advancement']}"
    return "Marcar como feita"


def recompensa(r):
    tipo = r["type"]
    if tipo == "item":
        n = qtd(r.get("count", 1))
        return nome_item(r["item"]) + (f" x{n}" if n > 1 else "")
    if tipo == "xp_levels":
        return f"{r['xp_levels']} níveis de XP"
    if tipo == "command":
        return limpar(r.get("title") or r["command"]) + (" (automática)" if r.get("auto") else "")
    return tipo


def capitulos():
    caps = {"ato1": g.ato1(), "ato2": g.ato2(), "ato3": g.ato3(), "ato4": g.ato4(), "ato5": g.ato5(),
            "cacadas": g.cacadas()}
    return caps


def secao_missoes(saida, cap):
    titulos = {q["id"]: limpar(q["title"]) for q in cap["quests"]}
    saida.append(f"## {limpar(cap['title'])}")
    if cap.get("subtitle"):
        saida.append(f"*{limpar(' '.join(cap['subtitle']))}*")
    saida.append("")
    for n, q in enumerate(cap["quests"], 1):
        marcas = []
        if q.get("shape") == "octagon":
            marcas.append("chefe")
        if q.get("optional"):
            marcas.append("opcional")
        if q.get("can_repeat"):
            marcas.append("repetível")
        cab = f"### {n}. {limpar(q['title'])}"
        if marcas:
            cab += f"  ({', '.join(marcas)})"
        saida.append(cab)
        if q.get("subtitle"):
            saida.append(f"*{limpar(q['subtitle'])}*")
            saida.append("")
        deps = [titulos.get(d, "missão de outro capítulo") for d in q.get("dependencies", [])]
        if deps:
            regra = " ou " if q.get("dependency_requirement") == "one_completed" else " e "
            saida.append(f"**Depois de:** {regra.join(deps)}")
            saida.append("")
        texto = [limpar(l) for l in q.get("description", [])]
        while texto and not texto[-1]:
            texto.pop()
        if texto:
            for linha in texto:
                saida.append(f"> {linha}" if linha else ">")
            saida.append("")
        tarefas = [tarefa(t) for t in q["tasks"]]
        if tarefas:
            saida.append("**Tarefa:** " + "; ".join(tarefas))
        recs = [recompensa(r) for r in q.get("rewards", [])]
        if recs:
            saida.append("**Recompensas:** " + "; ".join(recs))
        saida.append("")


def secao_npc(saida, titulo, preset, intro):
    saida.append(f"## {titulo}")
    saida.append(intro)
    saida.append("")
    for d in preset["data"]["DialogData"]["DialogDataSet"]:
        cond = d.get("Conditions")
        quando = ""
        if cond:
            quando = f" (quando o jogador tem a marca `{cond[0]['Name']}`)"
        elif d.get("Priority", 0) < 0:
            quando = " (aberta por um botão)"
        saida.append(f"### {limpar(d['Name'])}{quando}")
        for t in d["Texts"]:
            for linha in limpar(t["Text"]).split("\n"):
                saida.append(f"> {linha}" if linha else ">")
        botoes = [limpar(b["Name"]) for b in d.get("Buttons", [])]
        if botoes:
            saida.append("")
            saida.append("**Botões:** " + " · ".join(botoes))
        saida.append("")


def main():
    carregar_nomes(*(sys.argv[1:3]))
    saida = [
        "# A história do SealCraft",
        "",
        "Todas as missões do livro, na ordem do jogo, com os textos, tarefas e recompensas, "
        "e no fim todas as falas do Mestre Vellan e do Gabriel.",
        "",
        "Este arquivo é gerado por `tools/gerar_historia.py` a partir de `tools/gerar_missoes.py`. "
        "Para mudar um texto, mude no `gerar_missoes.py` e gere de novo.",
        "",
        "Onde aparece **[seu nome]**, o jogo coloca o nome do jogador.",
        "",
    ]
    for cap in capitulos().values():
        secao_missoes(saida, cap)
    secao_npc(saida, "Falas do Mestre Vellan", g.mestre_vellan(),
              "Clique nele com o botão direito. Ele mostra a fala do ato mais avançado que o jogador já terminou.")
    secao_npc(saida, "Falas do Gabriel, o Guardião dos Dragões", g.gabriel(),
              "Aparece no fim do Ato 2. A fala muda depois de \"Estou pronto\" e depois do primeiro voo.")
    destino = os.path.join(RAIZ, "HISTORIA.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(saida).rstrip() + "\n")
    print("escrito:", os.path.relpath(destino))


if __name__ == "__main__":
    main()
