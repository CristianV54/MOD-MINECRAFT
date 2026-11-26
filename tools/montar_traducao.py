#!/usr/bin/env python3
"""Monta o pacote de tradução PT-BR dos mods a partir dos lotes traduzidos.

Uso:  python3 tools/montar_traducao.py <pasta_dos_lotes>
      (a pasta tem saida/lote_*.json e existentes.json)

Saída: pack/config/openloader/resources/terras_partidas_ptbr/
O Open Loader carrega esse pacote de recursos sozinho, sempre ativo e no topo da lista,
então as traduções valem sem o jogador precisar ligar nada.

Cada arquivo assets/<mod>/lang/pt_br.json traz só os textos que faltavam no mod.
O Minecraft junta os arquivos de idioma de todos os pacotes, então o português que o mod
já tinha continua valendo. Exceção: quando o pt_br.json do próprio mod está quebrado
(caso do Mowzie's Mobs), o arquivo daqui leva também as traduções boas que existiam nele.
"""
import glob
import json
import os
import sys

DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pack", "config", "openloader",
                       "resources", "terras_partidas_ptbr")


def main(pasta):
    por_mod = {}
    existentes = json.load(open(os.path.join(pasta, "existentes.json"), encoding="utf-8"))
    for ns, textos in existentes.items():
        por_mod.setdefault(ns, {}).update(textos)
    lotes = sorted(glob.glob(os.path.join(pasta, "saida", "lote_[0-9][0-9].json")))
    for lote in lotes:
        for ns, textos in json.load(open(lote, encoding="utf-8")).items():
            por_mod.setdefault(ns, {}).update(textos)
    # correções por cima do português do próprio mod (ex.: nomes que precisam bater com as missões)
    ajustes = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "traducao_ajustes.json"),
                             encoding="utf-8"))
    for ns, textos in ajustes.items():
        if not ns.startswith("_"):
            por_mod.setdefault(ns, {}).update(textos)
    os.makedirs(DESTINO, exist_ok=True)
    with open(os.path.join(DESTINO, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": 15,
                            "description": "SealCraft: tradução PT-BR dos mods"}}, f, ensure_ascii=False, indent=2)
    total = 0
    for ns, textos in sorted(por_mod.items()):
        caminho = os.path.join(DESTINO, "assets", ns, "lang", "pt_br.json")
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(textos.items())), f, ensure_ascii=False, indent=2)
        total += len(textos)
    print(f"{len(lotes)} lotes, {len(por_mod)} mods, {total} textos em {os.path.relpath(DESTINO)}")


if __name__ == "__main__":
    main(sys.argv[1])
