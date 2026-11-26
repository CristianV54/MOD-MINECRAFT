#!/usr/bin/env python3
"""Equilíbrio dos monstros do SealCraft.

Problema: o Born in Chaos e o The Undead Revamped somam ~860 de peso de nascimento
em TODOS os biomas (incluindo Nether e End), contra ~515 dos monstros normais do
mundo normal. Ou seja, só ~37% dos monstros eram os normais, e muitos dos novos são
fortes demais para o começo do jogo.

O que este script faz:
  1. Sobrescreve os "biome modifiers" dos dois mods no datapack do pacote (mesmo
     caminho do arquivo original, então o nosso vale no lugar do deles):
     peso x FATOR (mínimo 1) e só no mundo normal quando o original era "todo bioma".
  2. Ajusta configs: explosão do Bomber (dano 1000 = morte instantânea), mutantes
     mais raros e chefes aleatórios do Apotheosis menos frequentes.

Uso: python3 tools/gerar_equilibrio.py <pasta com os .jar dos mods> <pasta config gerada pelo servidor>
"""
import json
import os
import re
import sys
import zipfile

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATAPACK = os.path.join(RAIZ, "pack", "config", "openloader", "data", "terras_partidas", "data")
CONFIG = os.path.join(RAIZ, "pack", "config")

FATOR = 0.35
MODS = {"born_in_chaos": "born_in_chaos_v1", "THEUNDEAD": "undead_revamp2"}

# Ajustes de config: arquivo -> lista de (regex, substituição)
AJUSTES = {
    "Undead_mobs.toml": [
        (r'("Explosion impact damage" = )1000\.0', r"\g<1>24.0"),   # Bomber: de morte instantânea para 12 corações
        (r'("Ordure death explosion damage" = )30\.0', r"\g<1>16.0"),
    ],
    "mutantmonsters-common.toml": [
        (r"(mutant_(creeper|enderman|skeleton|zombie)_spawn_weight = )0\.05", r"\g<1>0.015"),
    ],
    "apotheosis/adventure.cfg": [
        (r'(S:"Random Affix Chance"=)0\.075', r"\g<1>0.04"),
        (r'(I:"Boss Spawn Cooldown"=)3600', r"\g<1>12000"),
        (r"minecraft:overworld\|0\.018\|NEEDS_SKY", "minecraft:overworld|0.008|NEEDS_SKY"),
    ],
}


def biome_modifiers(pasta_jars):
    total_antes = total_depois = 0
    for jar in sorted(os.listdir(pasta_jars)):
        ns = next((n for chave, n in MODS.items() if jar.startswith(chave)), None)
        if not ns:
            continue
        with zipfile.ZipFile(os.path.join(pasta_jars, jar)) as z:
            for nome in z.namelist():
                if not (nome.startswith(f"data/{ns}/forge/biome_modifier/") and nome.endswith(".json")):
                    continue
                d = json.loads(z.read(nome))
                if d.get("type") != "forge:add_spawns":
                    continue
                spawners = d["spawners"] if isinstance(d["spawners"], list) else [d["spawners"]]
                for s in spawners:
                    total_antes += s["weight"]
                    s["weight"] = max(1, round(s["weight"] * FATOR))
                    total_depois += s["weight"]
                if isinstance(d["biomes"], dict) and d["biomes"].get("type") == "forge:any":
                    d["biomes"] = "#minecraft:is_overworld"
                destino = os.path.join(DATAPACK, nome[len("data/"):])
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                with open(destino, "w", encoding="utf-8") as f:
                    json.dump(d, f, indent=2)
                    f.write("\n")
    print(f"peso de nascimento dos dois mods: {total_antes} -> {total_depois}")


def configs(pasta_config):
    for arquivo, trocas in AJUSTES.items():
        texto = open(os.path.join(pasta_config, arquivo), encoding="utf-8").read()
        for padrao, novo in trocas:
            texto, n = re.subn(padrao, novo, texto)
            assert n, f"{arquivo}: não achei {padrao}"
        destino = os.path.join(CONFIG, arquivo)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(texto)
        print("config:", arquivo)


if __name__ == "__main__":
    biome_modifiers(sys.argv[1])
    configs(sys.argv[2])
