#!/usr/bin/env python3
"""Traduz as placas escritas dentro das estruturas dos mods.

O texto de uma placa fica gravado no arquivo .nbt da estrutura, então não passa pelo
sistema de tradução do jogo. Este script lê as estruturas dos .jar, troca o texto das
placas listadas em TRADUCOES e salva uma cópia no datapack do pacote, no mesmo caminho
do arquivo original. O datapack carrega depois dos mods, então a cópia vale no lugar.

Uso: python3 tools/traduzir_placas.py <pasta com os .jar dos mods>

Placas que não estão em TRADUCOES (números de quebra-cabeça, nomes próprios, árabe)
ficam como estão. Cada linha de placa cabe ~15 letras.
"""
import glob
import gzip
import io
import json
import os
import sys
import zipfile

import nbtlib

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATAPACK = os.path.join(RAIZ, "pack", "config", "openloader", "data", "terras_partidas", "data")
R = "==============="
T = "---------------"

# texto original (linhas não vazias, unidas por " / ") -> 4 linhas novas
TRADUCOES = {
    # Towns and Towers
    "Hey I'm working / on this. Go away. / Check next / update":
        ["Ei, ainda estou", "construindo.", "Volte na", "próxima versão"],
    "Special / Thanks / for / Builders": ["Agradecimento", "especial", "aos", "construtores"],
    "If you walk with / the fungus, / you'll never be / out of spores.":
        ["Quem anda com", "os fungos", "nunca fica", "sem esporos."],
    "Curious, aren't / we? Here's / something for / your troubles...":
        ["Curioso, hein?", "Tome aqui algo", "pelo seu", "trabalho..."],
    # YUNG's Better Desert Temples (créditos)
    "HedwigOwls / as / Ra / (bird of prey)": ["HedwigOwls", "como", "Rá", "(ave de rapina)"],
    "EoMoTTy / as / Anubis / (kind of...)": ["EoMoTTy", "como", "Anúbis", "(mais ou menos)"],
    "Dodo_3737 / as / Thoth / (but dodo)": ["Dodo_3737", "como", "Thoth", "(mas dodô)"],
    # Outras
    "What the h*ll / are you doing / here?": ["Que diabos", "você está", "fazendo aqui?", ""],
    '"Blessed are / those who walk / the unbeaten / path"':
        ['"Felizes os que', "andam pelo", "caminho nunca", 'trilhado"'],
    '"17236151OWO" / To claim prize': ['"17236151OWO"', "Para pegar", "o prêmio", ""],
    f"{T} / You are an / All Star / {T}": [T, "Você é uma", "estrela", T],
    f"{T} / Ride of the / Fireflies / {T}": [T, "Cavalgada dos", "Vaga-lumes", T],
    f"{T} / Pipse / Free! / {T}": [T, "Pipse", "Grátis!", T],
    f"{T} / Kocke Kola / Free! / {T}": [T, "Kocke Kola", "Grátis!", T],
    # Dungeons Arise: nomes dos quadros da galeria
    f"{R} / The / Creation shard / {R}": [R, "O Fragmento", "da Criação", R],
    f"{R} / One ring to  / rule them all / {R}": [R, "Um anel para", "todos governar", R],
    f"{R} / Depths of / Hathsin / {R}": [R, "Profundezas", "de Hathsin", R],
    f"{R} / A spoonful of / flies / {R}": [R, "Uma colherada", "de moscas", R],
    f"{R} / Words of the / Elder / {R}": [R, "Palavras do", "Ancião", R],
    f"{R} / Weakest / Ancestor / {R}": [R, "O Ancestral", "Mais Fraco", R],
    f"{R} / Unidentified / Frogging Object / {R}": [R, "Objeto Voador", "Não Sapificado", R],
    f"{R} / To narrow to be / a painting / {R}": [R, "Estreito demais", "para um quadro", R],
    f"{R} / To narrow to  / be a painting 2 / {R}": [R, "Estreito demais", "pra um quadro 2", R],
    f"{R} / Time to go / Outside / {R}": [R, "Hora de sair", "lá fora", R],
    f"{R} / Throwing / Frash Bang!! / {R}": [R, "Jogando uma", "Bomba de Luz!!", R],
    f"{R} / The touch of our / amphibian God / {R}": [R, "O toque do deus", "anfíbio", R],
    f"{R} / The good, the bad / and the frog / {R}": [R, "O bom, o mau", "e o sapo", R],
    f"{R} / The Fate of / Froggus / {R}": [R, "O Destino de", "Froggus", R],
    f"{R} / The End / Ship / {R}": [R, "O Navio", "do End", R],
    f"{R} / The Blind Eye / {R}": [R, "O Olho Cego", "", R],
    f"{R} / The All-seeing / Eye / {R}": [R, "O Olho que", "Tudo Vê", R],
    f"{R} / The / Watcher / {R}": [R, "O", "Vigia", R],
    f"{R} / The / Impostor / {R}": [R, "O", "Impostor", R],
    f"{R} / The / Harvest / {R}": [R, "A", "Colheita", R],
    f"{R} / Stingy Situation! / {R}": [R, "Que Picada!", "", R],
    f"{R} / Skeleton before / the Update / {R}": [R, "Esqueleto antes", "da Atualização", R],
    f"{R} / Reindordt The / Wise / {R}": [R, "Reindordt,", "o Sábio", R],
    f"{R} / Radiant  / Knights / {R}": [R, "Cavaleiros", "Radiantes", R],
    f"{R} / Our home / {R}": [R, "Nosso lar", "", R],
    f"{R} / Olloch The / Faithful / {R}": [R, "Olloch,", "o Fiel", R],
    f"{R} / Old Palace / {R}": [R, "Palácio Antigo", "", R],
    f"{R} / Next Home / Frogithiru / {R}": [R, "Próximo Lar:", "Frogithiru", R],
    f"{R} / Mountains / Cabin / {R}": [R, "Cabana nas", "Montanhas", R],
    f"{R} / Mechanical / Painting / {R}": [R, "Quadro", "Mecânico", R],
    f"{R} / Lucy in the Sky / with Diamonds / {R}": [R, "Lucy no Céu", "com Diamantes", R],
    f"{R} / Little / Octopus / {R}": [R, "Pequeno", "Polvo", R],
    f"{R} / Knowledge is / Power / {R}": [R, "Conhecimento", "é Poder", R],
    f"{R} / Kinda / Sword / {R}": [R, "Quase uma", "Espada", R],
    f"{R} / Killer / Elephant / {R}": [R, "Elefante", "Assassino", R],
    f"{R} / I am a Stick! / Pattern, help. / {R}": [R, "Sou um Graveto!", "Socorro!", R],
    f"{R} / Hut in the / Swamp / {R}": [R, "Cabana no", "Pântano", R],
    f"{R} / Hot place / not for us / {R}": [R, "Lugar quente", "não é pra nós", R],
    f"{R} / Gate 3 / {R}": [R, "Portão 3", "", R],
    f"{R} / Froggy Mountain / Breakdown / {R}": [R, "Colapso na", "Montanha Sapo", R],
    f"{R} / Frogging the / Plants / {R}": [R, "Sapeando as", "Plantas", R],
    f"{R} / Frogal  / Red and Blue / {R}": [R, "Sapo", "Vermelho e Azul", R],
    f"{R} / Frog before / Heaven / {R}": [R, "Sapo antes", "do Paraíso", R],
    f"{R} / Forger of / Stars / {R}": [R, "Forjador de", "Estrelas", R],
    f"{R} / Eye of the / Universe / {R}": [R, "Olho do", "Universo", R],
    f"{R} / Exist for  / Love / {R}": [R, "Existir por", "Amor", R],
    f"{R} / Emerald / Eyes / {R}": [R, "Olhos de", "Esmeralda", R],
    f"{R} / Cliffside Caves / {R}": [R, "Cavernas do", "Penhasco", R],
    f"{R} / Celeste / Mountain / {R}": [R, "Montanha", "Celeste", R],
    f"{R} / Cauldron of  / the witch / {R}": [R, "Caldeirão", "da Bruxa", R],
    f"{R} / Capybara's / Blessing / {R}": [R, "Bênção da", "Capivara", R],
    f"{R} / Blessed by / The Storm / {R}": [R, "Abençoado pela", "Tempestade", R],
    f"{R} / Bikini / Bottom / {R}": [R, "Fenda do", "Biquíni", R],
    f"{R} / A bow under a / red cloud / {R}": [R, "Um arco sob uma", "nuvem vermelha", R],
    f"{R} / A beacon of / Hope / {R}": [R, "Um farol de", "Esperança", R],
    f"{R} / A Melony / Meal / {R}": [R, "Uma Refeição", "de Melancia", R],
    f"{R} / A Golem's / Love Letter / {R}": [R, "Carta de Amor", "de um Golem", R],
}


def plano(s):
    """Texto puro de uma linha de placa (as linhas são JSON de texto do Minecraft)."""
    try:
        d = json.loads(s)
    except ValueError:
        return s
    if isinstance(d, str):
        return d
    if isinstance(d, list):
        return "".join(plano(json.dumps(x)) for x in d)
    if isinstance(d, dict):
        return d.get("text", "") + "".join(plano(json.dumps(x)) for x in d.get("extra", []))
    return str(d)


def nova_linha(original, texto):
    """Mantém a cor e o estilo da linha original, trocando só o texto."""
    try:
        d = json.loads(original)
    except ValueError:
        d = None
    if isinstance(d, dict):
        d = {k: v for k, v in d.items() if k != "extra"}
        d["text"] = texto
        return json.dumps(d, ensure_ascii=False)
    return json.dumps(texto, ensure_ascii=False)


def traduzir_placa(be):
    """Troca o texto de uma placa se ele estiver em TRADUCOES. Devolve True se mudou."""
    mudou = False
    for lado in ("front_text", "back_text"):
        if lado not in be:
            continue
        msgs = be[lado]["messages"]
        chave = " / ".join(plano(str(m)) for m in msgs if plano(str(m)).strip())
        if chave in TRADUCOES:
            novas = TRADUCOES[chave]
            for i in range(4):
                msgs[i] = nbtlib.String(nova_linha(str(msgs[i]), novas[i]))
            mudou = True
    if "Text1" in be:
        linhas = [str(be[f"Text{i}"]) for i in range(1, 5) if f"Text{i}" in be]
        chave = " / ".join(plano(m) for m in linhas if plano(m).strip())
        if chave in TRADUCOES:
            for i, texto in enumerate(TRADUCOES[chave], 1):
                be[f"Text{i}"] = nbtlib.String(nova_linha(str(be.get(f"Text{i}", '""')), texto))
            mudou = True
    return mudou


def main(pasta_jars):
    usadas, arquivos, placas = set(), 0, 0
    for jar in sorted(glob.glob(os.path.join(pasta_jars, "*.jar"))):
        try:
            z = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        for nome in z.namelist():
            if not (nome.startswith("data/") and nome.endswith(".nbt") and "/structures/" in nome):
                continue
            bruto = z.read(nome)
            dados = gzip.decompress(bruto) if bruto[:2] == b"\x1f\x8b" else bruto
            if b"sign" not in dados:
                continue
            arq = nbtlib.File.parse(io.BytesIO(dados))
            mudou = 0
            for bloco in arq.get("blocks", []):
                be = bloco.get("nbt")
                if be is not None and traduzir_placa(be):
                    mudou += 1
            if not mudou:
                continue
            for lado in ("front_text", "back_text"):
                pass
            destino = os.path.join(DATAPACK, nome[len("data/"):])
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            arq.save(destino, gzipped=True)
            arquivos += 1
            placas += mudou
            print(f"{os.path.basename(jar)}: {nome} ({mudou} placa(s))")
    print(f"total: {placas} placas traduzidas em {arquivos} estruturas")


if __name__ == "__main__":
    main(sys.argv[1])
