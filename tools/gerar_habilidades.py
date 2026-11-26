#!/usr/bin/env python3
"""Gera as árvores de habilidades das classes (mod Pufferfish's Skills).

Uso:  python3 tools/gerar_habilidades.py
Saída: datapack em pack/config/openloader/data/terras_partidas/data/terras_partidas/puffish_skills/

Cada classe tem uma árvore própria, trancada até o jogador escolher a classe no livro de missões
(a missão da classe roda "/puffish_skills category unlock"). Abra a árvore com a tecla K.
"""
import json
import os
import shutil

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pack", "config", "openloader", "data",
                    "terras_partidas", "data", "terras_partidas", "puffish_skills")
NS = "terras_partidas"

# Experiência: monstros dão XP pela experiência que soltam + vida máxima.
EXPERIENCIA = {
    "experience_per_level": {"type": "expression", "data": {"expression": "40 + level * 25"}},
    "level_limit": 20,
    "sources": [{
        "type": "puffish_skills:kill_entity",
        "data": {
            "variables": {
                "xp_solta": {"operations": [{"type": "get_dropped_experience"}]},
                "vida_max": {"operations": [{"type": "get_killed_living_entity"}, {"type": "get_max_health"}]},
            },
            "experience": "xp_solta + vida_max / 10",
            "anti_farming": {"limit_per_chunk": 15, "reset_after_seconds": 300},
        },
    }],
}


def attr(atributo, valor):
    return {"type": "puffish_skills:attribute",
            "data": {"attribute": atributo, "value": valor, "operation": "addition"}}


# Cada habilidade: (id, título, descrição, ícone, recompensa, custo)
# Cada classe: raiz + 3 ramos de 4 habilidades (a 4ª é o "ápice", mais forte e mais cara).
CLASSES = {
    "guerreiro": {
        "titulo": "Guerreiro", "icone": "epicfight:iron_longsword", "fundo": "minecraft:textures/block/stone_bricks.png",
        "descricao": "Luta de frente, com espada e armadura.",
        "raiz": ("treino", "Treino de Guerreiro", "+1 de dano corpo a corpo", "minecraft:iron_sword",
                 attr("minecraft:generic.attack_damage", 1.0)),
        "ramos": [
            ("Força", "minecraft:iron_axe", [
                ("forca_1", "Força I", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("forca_2", "Força II", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("forca_3", "Força III", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("golpe_brutal", "Golpe Brutal", "+25% de dano crítico", attr("attributeslib:crit_damage", 0.25)),
            ]),
            ("Vigor", "minecraft:golden_apple", [
                ("vigor_1", "Vigor I", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("vigor_2", "Vigor II", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("vigor_3", "Vigor III", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("sede_de_sangue", "Sede de Sangue", "Recupera 5% do dano causado como vida", attr("attributeslib:life_steal", 0.05)),
            ]),
            ("Ritmo", "minecraft:feather", [
                ("ritmo_1", "Ritmo I", "+5% de velocidade de ataque", attr("minecraft:generic.attack_speed", 0.2)),
                ("ritmo_2", "Ritmo II", "+5% de velocidade de ataque", attr("minecraft:generic.attack_speed", 0.2)),
                ("folego_1", "Fôlego de Batalha", "+2 de fôlego máximo", attr("epicfight:staminar", 2.0)),
                ("mestre_de_armas", "Mestre de Armas", "+5% de chance de crítico e +1 de dano",
                 [attr("attributeslib:crit_chance", 0.05), attr("minecraft:generic.attack_damage", 1.0)]),
            ]),
        ],
    },
    "tanque": {
        "titulo": "Tanque", "icone": "minecraft:shield", "fundo": "minecraft:textures/block/iron_block.png",
        "descricao": "Aguenta pancada e protege os aliados.",
        "raiz": ("muralha", "Muralha", "+4 de vida (2 corações)", "minecraft:iron_chestplate",
                 attr("minecraft:generic.max_health", 4.0)),
        "ramos": [
            ("Couraça", "minecraft:iron_chestplate", [
                ("couraca_1", "Couraça I", "+2 de armadura", attr("minecraft:generic.armor", 2.0)),
                ("couraca_2", "Couraça II", "+2 de armadura", attr("minecraft:generic.armor", 2.0)),
                ("couraca_3", "Couraça III", "+2 de armadura", attr("minecraft:generic.armor", 2.0)),
                ("pele_de_aco", "Pele de Aço", "+4 de resistência da armadura", attr("minecraft:generic.armor_toughness", 4.0)),
            ]),
            ("Firmeza", "minecraft:anvil", [
                ("firmeza_1", "Firmeza I", "+10% de resistência a empurrão", attr("minecraft:generic.knockback_resistance", 0.1)),
                ("firmeza_2", "Firmeza II", "+10% de resistência a empurrão", attr("minecraft:generic.knockback_resistance", 0.1)),
                ("firmeza_3", "Firmeza III", "+10% de resistência a empurrão", attr("minecraft:generic.knockback_resistance", 0.1)),
                ("inabalavel", "Inabalável", "+4 de resistência a atordoamento", attr("epicfight:stun_armor", 4.0)),
            ]),
            ("Vitalidade", "minecraft:glistering_melon_slice", [
                ("vitalidade_1", "Vitalidade I", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("vitalidade_2", "Vitalidade II", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("vitalidade_3", "Vitalidade III", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("regeneracao", "Sangue Forte", "+20% de cura recebida", attr("attributeslib:healing_received", 0.2)),
            ]),
        ],
    },
    "assassino": {
        "titulo": "Assassino", "icone": "epicfight:iron_dagger", "fundo": "minecraft:textures/block/black_concrete.png",
        "descricao": "Rápido, preciso e difícil de acertar.",
        "raiz": ("passos_leves", "Passos Leves", "+5% de velocidade de movimento", "minecraft:leather_boots",
                 attr("minecraft:generic.movement_speed", 0.005)),
        "ramos": [
            ("Lâmina", "epicfight:iron_dagger", [
                ("lamina_1", "Lâmina I", "+5% de chance de crítico", attr("attributeslib:crit_chance", 0.05)),
                ("lamina_2", "Lâmina II", "+5% de chance de crítico", attr("attributeslib:crit_chance", 0.05)),
                ("lamina_3", "Lâmina III", "+5% de chance de crítico", attr("attributeslib:crit_chance", 0.05)),
                ("golpe_fatal", "Golpe Fatal", "+40% de dano crítico", attr("attributeslib:crit_damage", 0.4)),
            ]),
            ("Sombra", "minecraft:ender_eye", [
                ("sombra_1", "Sombra I", "+3% de chance de esquivar", attr("attributeslib:dodge_chance", 0.03)),
                ("sombra_2", "Sombra II", "+3% de chance de esquivar", attr("attributeslib:dodge_chance", 0.03)),
                ("sombra_3", "Sombra III", "+3% de chance de esquivar", attr("attributeslib:dodge_chance", 0.03)),
                ("vulto", "Vulto", "+10% de velocidade de movimento", attr("minecraft:generic.movement_speed", 0.01)),
            ]),
            ("Fôlego", "minecraft:sugar", [
                ("folego_1", "Fôlego I", "+2 de fôlego máximo", attr("epicfight:staminar", 2.0)),
                ("folego_2", "Fôlego II", "+2 de fôlego máximo", attr("epicfight:staminar", 2.0)),
                ("folego_3", "Fôlego III", "+2 de fôlego máximo", attr("epicfight:staminar", 2.0)),
                ("segundo_ar", "Segundo Ar", "+30% de recuperação de fôlego", attr("epicfight:stamina_regen", 0.3)),
            ]),
        ],
    },
    "mago": {
        "titulo": "Mago", "icone": "irons_spellbooks:copper_spell_book", "fundo": "minecraft:textures/block/purple_concrete.png",
        "descricao": "Domina a magia do Iron's Spells.",
        "raiz": ("iniciado", "Iniciado", "+25 de mana máxima", "minecraft:lapis_lazuli",
                 attr("irons_spellbooks:max_mana", 25.0)),
        "ramos": [
            ("Poder", "minecraft:blaze_powder", [
                ("poder_1", "Poder I", "+5% de poder mágico", attr("irons_spellbooks:spell_power", 0.05)),
                ("poder_2", "Poder II", "+5% de poder mágico", attr("irons_spellbooks:spell_power", 0.05)),
                ("poder_3", "Poder III", "+5% de poder mágico", attr("irons_spellbooks:spell_power", 0.05)),
                ("arquimago", "Arquimago", "+15% de poder mágico", attr("irons_spellbooks:spell_power", 0.15)),
            ]),
            ("Fluxo", "minecraft:experience_bottle", [
                ("fluxo_1", "Fluxo I", "+10% de recuperação de mana", attr("irons_spellbooks:mana_regen", 0.1)),
                ("fluxo_2", "Fluxo II", "+10% de recuperação de mana", attr("irons_spellbooks:mana_regen", 0.1)),
                ("fluxo_3", "Fluxo III", "+10% de recuperação de mana", attr("irons_spellbooks:mana_regen", 0.1)),
                ("poco_de_mana", "Poço de Mana", "+100 de mana máxima", attr("irons_spellbooks:max_mana", 100.0)),
            ]),
            ("Pressa", "minecraft:clock", [
                ("pressa_1", "Pressa I", "-5% no tempo de recarga dos feitiços", attr("irons_spellbooks:cooldown_reduction", 0.05)),
                ("pressa_2", "Pressa II", "-5% no tempo de recarga dos feitiços", attr("irons_spellbooks:cooldown_reduction", 0.05)),
                ("pressa_3", "Pressa III", "-5% no tempo de recarga dos feitiços", attr("irons_spellbooks:cooldown_reduction", 0.05)),
                ("conjuracao_rapida", "Conjuração Rápida", "-15% no tempo de conjuração", attr("irons_spellbooks:cast_time_reduction", 0.15)),
            ]),
        ],
    },
    "cacador": {
        "titulo": "Caçador", "icone": "minecraft:bow", "fundo": "minecraft:textures/block/moss_block.png",
        "descricao": "Ataca de longe e se move pelo mundo.",
        "raiz": ("olho_de_falcao", "Olho de Falcão", "+10% de dano de flecha", "minecraft:spyglass",
                 attr("attributeslib:arrow_damage", 0.1)),
        "ramos": [
            ("Pontaria", "minecraft:arrow", [
                ("pontaria_1", "Pontaria I", "+10% de dano de flecha", attr("attributeslib:arrow_damage", 0.1)),
                ("pontaria_2", "Pontaria II", "+10% de dano de flecha", attr("attributeslib:arrow_damage", 0.1)),
                ("pontaria_3", "Pontaria III", "+10% de dano de flecha", attr("attributeslib:arrow_damage", 0.1)),
                ("tiro_certeiro", "Tiro Certeiro", "+10% de chance de crítico", attr("attributeslib:crit_chance", 0.1)),
            ]),
            ("Corda", "minecraft:string", [
                ("corda_1", "Corda I", "+10% de velocidade para puxar o arco", attr("attributeslib:draw_speed", 0.1)),
                ("corda_2", "Corda II", "+10% de velocidade para puxar o arco", attr("attributeslib:draw_speed", 0.1)),
                ("corda_3", "Corda III", "+10% de velocidade para puxar o arco", attr("attributeslib:draw_speed", 0.1)),
                ("flecha_veloz", "Flecha Veloz", "+30% de velocidade da flecha", attr("attributeslib:arrow_velocity", 0.3)),
            ]),
            ("Rastreador", "minecraft:leather_boots", [
                ("rastreador_1", "Rastreador I", "+3% de velocidade de movimento", attr("minecraft:generic.movement_speed", 0.003)),
                ("rastreador_2", "Rastreador II", "+3% de velocidade de movimento", attr("minecraft:generic.movement_speed", 0.003)),
                ("rastreador_3", "Rastreador III", "+2 de vida (1 coração)", attr("minecraft:generic.max_health", 2.0)),
                ("sobrevivente", "Sobrevivente", "+4 de vida e +5% de esquiva",
                 [attr("minecraft:generic.max_health", 4.0), attr("attributeslib:dodge_chance", 0.05)]),
            ]),
        ],
    },
}


# Árvores gerais: liberadas para todo mundo desde o começo, cada uma sobe de um jeito.
EXP_MINERACAO = {
    "experience_per_level": {"type": "expression", "data": {"expression": "30 + level * 20"}},
    "level_limit": 20,
    "sources": [{
        "type": "puffish_skills:mine_block",
        "data": {
            "variables": {
                "dureza": {"operations": [{"type": "get_mined_block_state"}, {"type": "get_block"}, {"type": "get_hardness"}]},
                "minerio": {"operations": [{"type": "get_mined_block_state"},
                                           {"type": "puffish_skills:test", "data": {"block": "#forge:ores"}},
                                           {"type": "puffish_skills:switch", "data": {"true": 1, "false": 0}}]},
            },
            "experience": "min(dureza, 5) * 0.4 + minerio * 7",
        },
    }],
}
EXP_VIDA = {
    "experience_per_level": {"type": "expression", "data": {"expression": "30 + level * 20"}},
    "level_limit": 20,
    "sources": [
        {"type": "puffish_skills:take_damage",
         "data": {"variables": {"dano": {"operations": [{"type": "get_taken_damage"}]}},
                  "experience": "min(dano, 20) * 1.5"}},
        {"type": "puffish_skills:eat_food",
         "data": {"variables": {"comida": {"operations": [{"type": "get_eaten_item_stack"}, {"type": "get_item"}, {"type": "get_nutrition"}]}},
                  "experience": "comida * 1.5"}},
    ],
}

GERAIS = {
    "combate": {
        "titulo": "Combate", "icone": "minecraft:iron_sword", "fundo": "minecraft:textures/block/polished_blackstone_bricks.png",
        "descricao": "Para todos. Sobe derrotando monstros.", "experiencia": EXPERIENCIA,
        "raiz": ("guerreiro_nato", "Instinto de Luta", "+1 de dano corpo a corpo", "minecraft:iron_sword",
                 attr("minecraft:generic.attack_damage", 1.0)),
        "ramos": [
            ("Golpes", "minecraft:iron_sword", [
                ("golpes_1", "Golpes Firmes I", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("golpes_2", "Golpes Firmes II", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("golpes_3", "Golpes Firmes III", "+1 de dano", attr("minecraft:generic.attack_damage", 1.0)),
                ("golpes_4", "Perfurar Armadura", "Ignora 2 pontos de armadura do inimigo", attr("attributeslib:armor_pierce", 2.0)),
                ("carrasco", "Carrasco", "+15% de chance e +25% de dano crítico",
                 [attr("attributeslib:crit_chance", 0.15), attr("attributeslib:crit_damage", 0.25)]),
            ]),
            ("Agilidade", "minecraft:feather", [
                ("agil_1", "Mãos Rápidas I", "+5% de velocidade de ataque", attr("minecraft:generic.attack_speed", 0.2)),
                ("agil_2", "Mãos Rápidas II", "+5% de velocidade de ataque", attr("minecraft:generic.attack_speed", 0.2)),
                ("agil_3", "Alcance", "+0,5 de alcance de ataque", attr("forge:entity_reach", 0.5)),
                ("agil_4", "Fôlego de Batalha", "+3 de fôlego máximo", attr("epicfight:staminar", 3.0)),
                ("dancarino", "Dança da Lâmina", "+10% de velocidade de ataque e +20% de recuperação de fôlego",
                 [attr("minecraft:generic.attack_speed", 0.4), attr("epicfight:stamina_regen", 0.2)]),
            ]),
            ("Sangue", "minecraft:redstone", [
                ("sangue_1", "Empurrão", "+0,5 de repulsão nos ataques", attr("minecraft:generic.attack_knockback", 0.5)),
                ("sangue_2", "Sede I", "Recupera 2% do dano causado como vida", attr("attributeslib:life_steal", 0.02)),
                ("sangue_3", "Sede II", "Recupera mais 2% do dano causado como vida", attr("attributeslib:life_steal", 0.02)),
                ("sangue_4", "Impacto", "+2 de impacto (atordoa mais os inimigos)", attr("epicfight:impact", 2.0)),
                ("predador", "Predador", "+5% de roubo de vida e +2 de dano",
                 [attr("attributeslib:life_steal", 0.05), attr("minecraft:generic.attack_damage", 2.0)]),
            ]),
        ],
    },
    "mineracao": {
        "titulo": "Mineração", "icone": "minecraft:iron_pickaxe", "fundo": "minecraft:textures/block/deepslate.png",
        "descricao": "Para todos. Sobe minerando (minérios valem muito mais).", "experiencia": EXP_MINERACAO,
        "raiz": ("minerador", "Minerador", "+10% de velocidade de mineração", "minecraft:iron_pickaxe",
                 attr("attributeslib:mining_speed", 0.1)),
        "ramos": [
            ("Picareta", "minecraft:diamond_pickaxe", [
                ("pic_1", "Braço Forte I", "+10% de velocidade de mineração", attr("attributeslib:mining_speed", 0.1)),
                ("pic_2", "Braço Forte II", "+10% de velocidade de mineração", attr("attributeslib:mining_speed", 0.1)),
                ("pic_3", "Braço Forte III", "+15% de velocidade de mineração", attr("attributeslib:mining_speed", 0.15)),
                ("pic_4", "Braço de Ferro", "+15% de velocidade de mineração", attr("attributeslib:mining_speed", 0.15)),
                ("escavadora", "Escavadora", "+30% de velocidade de mineração", attr("attributeslib:mining_speed", 0.3)),
            ]),
            ("Alcance", "minecraft:spyglass", [
                ("alc_1", "Braço Longo I", "+0,5 de alcance para quebrar e colocar blocos", attr("forge:block_reach", 0.5)),
                ("alc_2", "Braço Longo II", "+0,5 de alcance para quebrar e colocar blocos", attr("forge:block_reach", 0.5)),
                ("alc_3", "Passo Firme", "Sobe meio bloco sem pular", attr("forge:step_height_addition", 0.5)),
                ("alc_4", "Braço Longo III", "+1 de alcance para quebrar e colocar blocos", attr("forge:block_reach", 1.0)),
                ("arquiteto", "Arquiteto", "+1,5 de alcance para quebrar e colocar blocos", attr("forge:block_reach", 1.5)),
            ]),
            ("Sorte", "minecraft:emerald", [
                ("sorte_1", "Olho Treinado I", "+1 de sorte (baús e pescaria melhores)", attr("minecraft:generic.luck", 1.0)),
                ("sorte_2", "Sabedoria I", "+10% de experiência ganha", attr("attributeslib:experience_gained", 0.1)),
                ("sorte_3", "Olho Treinado II", "+1 de sorte", attr("minecraft:generic.luck", 1.0)),
                ("sorte_4", "Sabedoria II", "+15% de experiência ganha", attr("attributeslib:experience_gained", 0.15)),
                ("garimpeiro", "Garimpeiro", "+2 de sorte e +25% de experiência ganha",
                 [attr("minecraft:generic.luck", 2.0), attr("attributeslib:experience_gained", 0.25)]),
            ]),
        ],
    },
    "vida": {
        "titulo": "Vida", "icone": "minecraft:golden_apple", "fundo": "minecraft:textures/block/moss_block.png",
        "descricao": "Para todos. Sobe comendo e sobrevivendo a dano.", "experiencia": EXP_VIDA,
        "raiz": ("resistente", "Resistente", "+2 de vida (1 coração)", "minecraft:golden_apple",
                 attr("minecraft:generic.max_health", 2.0)),
        "ramos": [
            ("Coração", "minecraft:red_dye", [
                ("cor_1", "Coração Forte I", "+2 de vida", attr("minecraft:generic.max_health", 2.0)),
                ("cor_2", "Coração Forte II", "+2 de vida", attr("minecraft:generic.max_health", 2.0)),
                ("cor_3", "Coração Forte III", "+2 de vida", attr("minecraft:generic.max_health", 2.0)),
                ("cor_4", "Cura Rápida", "+15% de cura recebida", attr("attributeslib:healing_received", 0.15)),
                ("imortal", "Coração de Dragão", "+6 de vida (3 corações) e +15% de cura recebida",
                 [attr("minecraft:generic.max_health", 6.0), attr("attributeslib:healing_received", 0.15)]),
            ]),
            ("Couro", "minecraft:leather", [
                ("couro_1", "Pele Grossa I", "+1 de armadura", attr("minecraft:generic.armor", 1.0)),
                ("couro_2", "Pele Grossa II", "+1 de armadura", attr("minecraft:generic.armor", 1.0)),
                ("couro_3", "Raiz no Chão", "+10% de resistência a empurrão", attr("minecraft:generic.knockback_resistance", 0.1)),
                ("couro_4", "Pele Grossa III", "+2 de resistência da armadura", attr("minecraft:generic.armor_toughness", 2.0)),
                ("muralha_viva", "Muralha Viva", "+2 de armadura e +2 de resistência da armadura",
                 [attr("minecraft:generic.armor", 2.0), attr("minecraft:generic.armor_toughness", 2.0)]),
            ]),
            ("Viajante", "minecraft:leather_boots", [
                ("via_1", "Pés Leves I", "+3% de velocidade de movimento", attr("minecraft:generic.movement_speed", 0.003)),
                ("via_2", "Nadador", "+25% de velocidade de nado", attr("forge:swim_speed", 0.25)),
                ("via_3", "Pés Leves II", "+3% de velocidade de movimento", attr("minecraft:generic.movement_speed", 0.003)),
                ("via_4", "Escalador", "Sobe meio bloco sem pular", attr("forge:step_height_addition", 0.5)),
                ("andarilho", "Andarilho", "+5% de velocidade e +25% de velocidade de nado",
                 [attr("minecraft:generic.movement_speed", 0.005), attr("forge:swim_speed", 0.25)]),
            ]),
        ],
    },
}


def icone(item):
    return {"type": "item", "data": {"item": item}}


def quadro(tipo):
    return {"type": "advancement", "data": {"frame": tipo}}


def gerar_classe(chave, cls):
    definicoes, skills, conexoes = {}, {}, []
    rid, rtit, rdesc, ricon, rrec = cls["raiz"]
    definicoes[rid] = {"title": rtit, "description": rdesc, "icon": icone(ricon), "frame": quadro("goal"),
                       "rewards": [rrec], "cost": 1}
    skills[rid] = {"definition": rid, "x": 0, "y": 0, "root": True}
    # três ramos saindo da raiz: para cima-esquerda, para cima e para cima-direita
    direcoes = [(-1, -1), (0, -1), (1, -1)]
    for (nome_ramo, icone_ramo, lista), (dx, dy) in zip(cls["ramos"], direcoes):
        anterior = rid
        for i, (sid, tit, desc, rec) in enumerate(lista, 1):
            apice = i == len(lista)
            recs = rec if isinstance(rec, list) else [rec]
            definicoes[sid] = {"title": tit, "description": f"{desc}\nRamo: {nome_ramo}",
                               "icon": icone(icone_ramo),
                               "frame": quadro("challenge" if apice else "task"),
                               "rewards": recs, "cost": 2 if apice else 1}
            skills[sid] = {"definition": sid, "x": dx * 34 * i, "y": dy * 34 * i}
            conexoes.append([anterior, sid])
            anterior = sid
    categoria = {
        "title": cls["titulo"],
        "description": cls["descricao"],
        "icon": icone(cls["icone"]),
        "background": {"texture": cls["fundo"], "width": 16, "height": 16, "position": "tile"},
        "unlocked_by_default": bool(cls.get("experiencia")),
        "starting_points": 1,
    }
    return categoria, definicoes, skills, {"normal": {"bidirectional": conexoes}}


def main():
    if os.path.isdir(RAIZ):
        shutil.rmtree(RAIZ)
    os.makedirs(RAIZ)

    def salvar(caminho, dados):
        caminho = os.path.join(RAIZ, caminho)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    salvar("config.json", {"version": 3, "categories": list(GERAIS) + list(CLASSES)})
    for chave, cls in list(GERAIS.items()) + list(CLASSES.items()):
        categoria, definicoes, skills, conexoes = gerar_classe(chave, cls)
        salvar(f"categories/{chave}/category.json", categoria)
        salvar(f"categories/{chave}/definitions.json", definicoes)
        salvar(f"categories/{chave}/skills.json", skills)
        salvar(f"categories/{chave}/connections.json", conexoes)
        salvar(f"categories/{chave}/experience.json", cls.get("experiencia", EXPERIENCIA))
        print(f"árvore {chave}: {len(skills)} habilidades, {sum(d['cost'] for d in definicoes.values())} pontos para completar")


if __name__ == "__main__":
    main()
