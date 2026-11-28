#!/usr/bin/env python3
"""Gera as árvores de habilidades das classes (mod Pufferfish's Skills).

Uso:  python3 tools/gerar_habilidades.py
Saída: datapack em pack/config/openloader/data/terras_partidas/data/terras_partidas/puffish_skills/

Cada classe tem uma árvore própria, trancada até o jogador escolher a classe no livro de missões
(a missão da classe roda "/puffish_skills category unlock"). Abra a árvore com a tecla K.
"""
import json
import math
import os
import shutil

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pack", "config", "openloader", "data",
                    "terras_partidas", "data", "terras_partidas", "puffish_skills")
NS = "terras_partidas"

# Experiência: monstros dão XP pela experiência que soltam + vida máxima.
# A curva é bem mais lenta que a primeira versão: as árvores ficaram muito maiores e o
# jogador (principalmente o Mago, que mata vários monstros de uma vez) completava tudo cedo.
FONTE_ABATES = {
    "type": "puffish_skills:kill_entity",
    "data": {
        "variables": {
            "xp_solta": {"operations": [{"type": "get_dropped_experience"}]},
            "vida_max": {"operations": [{"type": "get_killed_living_entity"}, {"type": "get_max_health"}]},
        },
        "experience": "xp_solta + vida_max / 10",
        "anti_farming": {"limit_per_chunk": 15, "reset_after_seconds": 300},
    },
}
# Classe: 1 ponto inicial + até 30 níveis + 1 ponto por chefe (31 na campanha) = ~62; a árvore custa 55.
EXPERIENCIA = {
    "experience_per_level": {"type": "expression", "data": {"expression": "60 + level * 35"}},
    "level_limit": 30,
    "sources": [FONTE_ABATES],
}
# Gerais: 1 ponto inicial + até 50 níveis (+ bônus de missões); cada árvore custa 51.
EXP_COMBATE = {
    "experience_per_level": {"type": "expression", "data": {"expression": "40 + level * 25"}},
    "level_limit": 50,
    "sources": [FONTE_ABATES],
}


def attr(atributo, valor):
    return {"type": "puffish_skills:attribute",
            "data": {"attribute": atributo, "value": valor, "operation": "addition"}}


ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def num(v):
    """1.5 -> '1,5'; 2.0 -> '2'."""
    return f"{v:g}".replace(".", ",")


def serie(base, nome, n, desc, atributo, valor, inicio=1):
    """n habilidades iguais e baratas: 'Nome I', 'Nome II'..."""
    return [(f"{base}_{i}", f"{nome} {ROMANOS[i - 1]}", desc, attr(atributo, valor))
            for i in range(inicio, inicio + n)]


def apice(sid, titulo, desc, *recompensas):
    return (sid, titulo, desc, list(recompensas))


# Atalhos de atributos
DANO, VIDA, ARMADURA, DUREZA = ("minecraft:generic.attack_damage", "minecraft:generic.max_health",
                                "minecraft:generic.armor", "minecraft:generic.armor_toughness")
VEL_ATAQUE, VEL, EMPURRAO, REPULSAO = ("minecraft:generic.attack_speed", "minecraft:generic.movement_speed",
                                       "minecraft:generic.knockback_resistance", "minecraft:generic.attack_knockback")
SORTE = "minecraft:generic.luck"
CRIT, DANO_CRIT, ROUBO, ESQUIVA = ("attributeslib:crit_chance", "attributeslib:crit_damage",
                                   "attributeslib:life_steal", "attributeslib:dodge_chance")
PERFURAR, RASGAR, CURA, XP = ("attributeslib:armor_pierce", "attributeslib:armor_shred",
                              "attributeslib:healing_received", "attributeslib:experience_gained")
FOLEGO, REC_FOLEGO, IMPACTO, ATORDOAR = ("epicfight:staminar", "epicfight:stamina_regen", "epicfight:impact",
                                         "epicfight:stun_armor")
ISB = "irons_spellbooks:"

# Cada árvore: raiz + ramos. Cada ramo tem várias habilidades baratas (1 ponto) e termina
# num ápice (3 pontos), mais forte. Classes: 6 ramos de 6+1. Gerais: 5 ramos de 7+1.
CLASSES = {
    "guerreiro": {
        "titulo": "Guerreiro", "icone": "epicfight:iron_longsword", "fundo": "minecraft:textures/block/stone_bricks.png",
        "descricao": "Luta de frente, com espada e armadura.",
        "raiz": ("treino", "Treino de Guerreiro", "+1 de dano corpo a corpo", "minecraft:iron_sword", attr(DANO, 1.0)),
        "ramos": [
            ("Força", "minecraft:iron_axe",
             serie("forca", "Força", 6, "+0,5 de dano", DANO, 0.5)
             + [apice("golpe_brutal", "Golpe Brutal", "+30% de dano crítico", attr(DANO_CRIT, 0.3))]),
            ("Vigor", "minecraft:golden_apple",
             serie("vigor", "Vigor", 6, "+1 de vida (meio coração)", VIDA, 1.0)
             + [apice("sede_de_sangue", "Sede de Sangue", "Recupera 5% do dano causado como vida", attr(ROUBO, 0.05))]),
            ("Ritmo", "minecraft:feather",
             serie("ritmo", "Ritmo", 4, "+2,5% de velocidade de ataque", VEL_ATAQUE, 0.1)
             + serie("folego", "Fôlego de Batalha", 2, "+1 de fôlego máximo", FOLEGO, 1.0)
             + [apice("mestre_de_armas", "Mestre de Armas", "+5% de chance de crítico e +1 de dano",
                      attr(CRIT, 0.05), attr(DANO, 1.0))]),
            ("Couraça", "minecraft:iron_chestplate",
             serie("couraca", "Couraça", 4, "+1 de armadura", ARMADURA, 1.0)
             + serie("tempera", "Têmpera", 2, "+1 de resistência da armadura", DUREZA, 1.0)
             + [apice("aco_vivo", "Aço Vivo", "+2 de armadura e +2 de resistência da armadura",
                      attr(ARMADURA, 2.0), attr(DUREZA, 2.0))]),
            ("Impacto", "minecraft:anvil",
             serie("impacto", "Impacto", 4, "+0,5 de impacto (atordoa mais)", IMPACTO, 0.5)
             + serie("empurrao", "Empurrão", 2, "+0,25 de repulsão nos golpes", REPULSAO, 0.25)
             + [apice("quebra_guarda", "Quebra-Guarda", "Ignora 3 pontos de armadura do inimigo", attr(PERFURAR, 3.0))]),
            ("Fúria", "minecraft:blaze_powder",
             serie("furia", "Fúria", 4, "+2% de chance de crítico", CRIT, 0.02)
             + serie("colera", "Cólera", 2, "+5% de dano crítico", DANO_CRIT, 0.05)
             + [apice("campeao", "Fúria do Campeão", "Acerta +1 inimigo por golpe e +1 de dano",
                      attr("epicfight:max_strikes", 1.0), attr(DANO, 1.0))]),
        ],
    },
    "tanque": {
        "titulo": "Tanque", "icone": "minecraft:shield", "fundo": "minecraft:textures/block/iron_block.png",
        "descricao": "Aguenta pancada e protege os aliados.",
        "raiz": ("muralha", "Muralha", "+4 de vida (2 corações)", "minecraft:iron_chestplate", attr(VIDA, 4.0)),
        "ramos": [
            ("Couraça", "minecraft:iron_chestplate",
             serie("couraca", "Couraça", 6, "+1 de armadura", ARMADURA, 1.0)
             + [apice("pele_de_aco", "Pele de Aço", "+3 de resistência da armadura", attr(DUREZA, 3.0))]),
            ("Firmeza", "minecraft:anvil",
             serie("firmeza", "Firmeza", 6, "+5% de resistência a empurrão", EMPURRAO, 0.05)
             + [apice("inabalavel", "Inabalável", "+4 de resistência a atordoamento", attr(ATORDOAR, 4.0))]),
            ("Vitalidade", "minecraft:glistering_melon_slice",
             serie("vitalidade", "Vitalidade", 6, "+1 de vida (meio coração)", VIDA, 1.0)
             + [apice("sangue_forte", "Sangue Forte", "+20% de cura recebida", attr(CURA, 0.2))]),
            ("Bastião", "minecraft:amethyst_shard",
             serie("bastiao", "Bastião", 4, "+0,5 de resistência da armadura", DUREZA, 0.5)
             + serie("anti_magia", "Anti-Magia", 2, "+2% de resistência a magia", ISB + "spell_resist", 0.02)
             + [apice("muralha_arcana", "Muralha Arcana", "+8% de resistência a magia", attr(ISB + "spell_resist", 0.08))]),
            ("Revide", "minecraft:iron_sword",
             serie("revide", "Revide", 4, "+0,5 de dano", DANO, 0.5)
             + serie("baque", "Baque", 2, "+0,5 de impacto (atordoa mais)", IMPACTO, 0.5)
             + [apice("vinganca_de_ferro", "Vingança de Ferro", "Recupera 4% do dano causado como vida e +1 de dano",
                      attr(ROUBO, 0.04), attr(DANO, 1.0))]),
            ("Resistência", "minecraft:sugar",
             serie("resistencia", "Resistência", 4, "+1 de fôlego máximo", FOLEGO, 1.0)
             + serie("respiro", "Respiro", 2, "+5% de recuperação de fôlego", REC_FOLEGO, 0.05)
             + [apice("folego_de_gigante", "Fôlego de Gigante", "+20% de recuperação de fôlego e +2 de fôlego",
                      attr(REC_FOLEGO, 0.2), attr(FOLEGO, 2.0))]),
        ],
    },
    "assassino": {
        "titulo": "Assassino", "icone": "epicfight:iron_dagger", "fundo": "minecraft:textures/block/black_concrete.png",
        "descricao": "Rápido, preciso e difícil de acertar.",
        "raiz": ("passos_leves", "Passos Leves", "+5% de velocidade de movimento", "minecraft:leather_boots",
                 attr(VEL, 0.005)),
        "ramos": [
            ("Lâmina", "epicfight:iron_dagger",
             serie("lamina", "Lâmina", 6, "+2% de chance de crítico", CRIT, 0.02)
             + [apice("golpe_fatal", "Golpe Fatal", "+40% de dano crítico", attr(DANO_CRIT, 0.4))]),
            ("Sombra", "minecraft:ender_eye",
             serie("sombra", "Sombra", 6, "+1,5% de chance de esquivar", ESQUIVA, 0.015)
             + [apice("vulto", "Vulto", "+8% de velocidade e +3% de esquiva", attr(VEL, 0.008), attr(ESQUIVA, 0.03))]),
            ("Fôlego", "minecraft:sugar",
             serie("folego", "Fôlego", 6, "+1 de fôlego máximo", FOLEGO, 1.0)
             + [apice("segundo_ar", "Segundo Ar", "+30% de recuperação de fôlego", attr(REC_FOLEGO, 0.3))]),
            ("Ponto Fraco", "minecraft:spider_eye",
             serie("brecha", "Brecha", 4, "Ignora 0,5 de armadura do inimigo", PERFURAR, 0.5)
             + serie("corte", "Corte Fundo", 2, "+5% de dano crítico", DANO_CRIT, 0.05)
             + [apice("ponto_fraco", "Ponto Fraco", "Ignora 10% da armadura do inimigo", attr(RASGAR, 0.1))]),
            ("Passos", "minecraft:leather_boots",
             serie("passo", "Passo Ligeiro", 6, "+2% de velocidade de movimento", VEL, 0.002)
             + [apice("passo_fantasma", "Passo Fantasma", "+5% de velocidade e +5% de velocidade de ataque",
                      attr(VEL, 0.005), attr(VEL_ATAQUE, 0.2))]),
            ("Duas Lâminas", "minecraft:iron_sword",
             serie("mao_esquerda", "Mão Esquerda", 3, "+2,5% de velocidade de ataque da mão secundária",
                   "epicfight:offhand_attack_speed", 0.1)
             + serie("mao_direita", "Mão Direita", 3, "+2,5% de velocidade de ataque", VEL_ATAQUE, 0.1)
             + [apice("danca_das_adagas", "Dança das Adagas", "+20% de dano crítico e 3% de roubo de vida",
                      attr(DANO_CRIT, 0.2), attr(ROUBO, 0.03))]),
        ],
    },
    "mago": {
        "titulo": "Mago", "icone": "irons_spellbooks:copper_spell_book", "fundo": "minecraft:textures/block/purple_concrete.png",
        "descricao": "Domina a magia do Iron's Spells.",
        "raiz": ("iniciado", "Iniciado", "+25 de mana máxima", "minecraft:lapis_lazuli", attr(ISB + "max_mana", 25.0)),
        "ramos": [
            ("Poder", "minecraft:blaze_powder",
             serie("poder", "Poder", 6, "+2% de poder mágico", ISB + "spell_power", 0.02)
             + [apice("arquimago", "Arquimago", "+10% de poder mágico", attr(ISB + "spell_power", 0.1))]),
            ("Reserva", "minecraft:lapis_lazuli",
             serie("reserva", "Reserva", 6, "+15 de mana máxima", ISB + "max_mana", 15.0)
             + [apice("poco_de_mana", "Poço de Mana", "+75 de mana máxima", attr(ISB + "max_mana", 75.0))]),
            ("Fluxo", "minecraft:experience_bottle",
             serie("fluxo", "Fluxo", 6, "+5% de recuperação de mana", ISB + "mana_regen", 0.05)
             + [apice("mare_arcana", "Maré Arcana", "+20% de recuperação de mana", attr(ISB + "mana_regen", 0.2))]),
            ("Pressa", "minecraft:clock",
             serie("pressa", "Pressa", 4, "-2% no tempo de recarga dos feitiços", ISB + "cooldown_reduction", 0.02)
             + serie("palavra_rapida", "Palavra Rápida", 2, "-3% no tempo de conjuração", ISB + "cast_time_reduction", 0.03)
             + [apice("conjuracao_rapida", "Conjuração Rápida", "-6% de recarga e -6% de tempo de conjuração",
                      attr(ISB + "cooldown_reduction", 0.06), attr(ISB + "cast_time_reduction", 0.06))]),
            ("Elementos", "minecraft:nether_star",
             [("escola_fogo", "Escola do Fogo", "+4% de poder dos feitiços de fogo", attr(ISB + "fire_spell_power", 0.04)),
              ("escola_gelo", "Escola do Gelo", "+4% de poder dos feitiços de gelo", attr(ISB + "ice_spell_power", 0.04)),
              ("escola_raio", "Escola do Raio", "+4% de poder dos feitiços de raio", attr(ISB + "lightning_spell_power", 0.04)),
              ("escola_natureza", "Escola da Natureza", "+4% de poder dos feitiços da natureza", attr(ISB + "nature_spell_power", 0.04)),
              ("escola_ender", "Escola do Ender", "+4% de poder dos feitiços do Ender", attr(ISB + "ender_spell_power", 0.04)),
              ("escola_sagrada", "Escola Sagrada", "+4% de poder dos feitiços sagrados", attr(ISB + "holy_spell_power", 0.04)),
              apice("mestre_dos_elementos", "Mestre dos Elementos",
                    "+6% de poder dos feitiços de sangue, evocação e eldritch",
                    attr(ISB + "blood_spell_power", 0.06), attr(ISB + "evocation_spell_power", 0.06),
                    attr(ISB + "eldritch_spell_power", 0.06))]),
            ("Guardião", "minecraft:amethyst_shard",
             serie("barreira", "Barreira", 2, "+2% de resistência a magia", ISB + "spell_resist", 0.02)
             + serie("corpo_firme", "Corpo Firme", 2, "+1 de vida (meio coração)", VIDA, 1.0)
             + [("passo_arcano", "Passo Arcano", "+10% de velocidade andando enquanto conjura", attr(ISB + "casting_movespeed", 0.1)),
                ("chamado", "Chamado", "+10% de dano das criaturas invocadas", attr(ISB + "summon_damage", 0.1)),
                apice("escudo_arcano", "Escudo Arcano", "+8% de resistência a magia e +2 de vida",
                      attr(ISB + "spell_resist", 0.08), attr(VIDA, 2.0))]),
        ],
    },
    "cacador": {
        "titulo": "Caçador", "icone": "minecraft:bow", "fundo": "minecraft:textures/block/moss_block.png",
        "descricao": "Ataca de longe e se move pelo mundo.",
        "raiz": ("olho_de_falcao", "Olho de Falcão", "+10% de dano de flecha", "minecraft:spyglass",
                 attr("attributeslib:arrow_damage", 0.1)),
        "ramos": [
            ("Pontaria", "minecraft:arrow",
             serie("pontaria", "Pontaria", 6, "+4% de dano de flecha", "attributeslib:arrow_damage", 0.04)
             + [apice("tiro_certeiro", "Tiro Certeiro", "+10% de chance de crítico", attr(CRIT, 0.1))]),
            ("Corda", "minecraft:string",
             serie("corda", "Corda", 6, "+5% de velocidade para puxar o arco", "attributeslib:draw_speed", 0.05)
             + [apice("flecha_veloz", "Flecha Veloz", "+30% de velocidade da flecha", attr("attributeslib:arrow_velocity", 0.3))]),
            ("Rastreador", "minecraft:leather_boots",
             serie("rastreador", "Rastreador", 4, "+2% de velocidade de movimento", VEL, 0.002)
             + serie("couro_curtido", "Couro Curtido", 2, "+1 de vida (meio coração)", VIDA, 1.0)
             + [apice("sobrevivente", "Sobrevivente", "+3 de vida e +4% de esquiva", attr(VIDA, 3.0), attr(ESQUIVA, 0.04))]),
            ("Olho de Águia", "minecraft:spyglass",
             serie("mira", "Mira Fina", 4, "+5% de dano crítico", DANO_CRIT, 0.05)
             + serie("ponta_de_aco", "Ponta de Aço", 2, "Ignora 0,5 de armadura do inimigo", PERFURAR, 0.5)
             + [apice("cacador_de_chefes", "Caçador de Chefes", "Cada acerto tira mais 3% da vida atual do alvo",
                      attr("attributeslib:current_hp_damage", 0.03))]),
            ("Faro", "minecraft:emerald",
             serie("faro", "Faro", 4, "+0,5 de sorte (baús melhores)", SORTE, 0.5)
             + serie("trilha", "Trilha", 2, "+5% de experiência ganha", XP, 0.05)
             + [apice("instinto", "Instinto", "+2 de sorte e +10% de experiência", attr(SORTE, 2.0), attr(XP, 0.1))]),
            ("Faca de Caça", "epicfight:iron_dagger",
             serie("faca", "Faca", 3, "+0,5 de dano corpo a corpo", DANO, 0.5)
             + serie("reflexo", "Reflexo", 3, "+2,5% de velocidade de ataque", VEL_ATAQUE, 0.1)
             + [apice("recuo_agil", "Recuo Ágil", "+5% de esquiva e +4% de velocidade",
                      attr(ESQUIVA, 0.05), attr(VEL, 0.004))]),
        ],
    },
}


# Árvores gerais: liberadas para todo mundo desde o começo, cada uma sobe de um jeito.
EXP_MINERACAO = {
    "experience_per_level": {"type": "expression", "data": {"expression": "25 + level * 15"}},
    "level_limit": 50,
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
    "experience_per_level": {"type": "expression", "data": {"expression": "25 + level * 15"}},
    "level_limit": 50,
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
        "descricao": "Para todos. Sobe derrotando monstros.", "experiencia": EXP_COMBATE,
        "raiz": ("guerreiro_nato", "Instinto de Luta", "+1 de dano corpo a corpo", "minecraft:iron_sword", attr(DANO, 1.0)),
        "ramos": [
            ("Golpes", "minecraft:iron_sword",
             serie("golpes", "Golpes Firmes", 7, "+0,5 de dano", DANO, 0.5)
             + [apice("carrasco", "Carrasco", "+10% de chance e +20% de dano crítico", attr(CRIT, 0.1), attr(DANO_CRIT, 0.2))]),
            ("Agilidade", "minecraft:feather",
             serie("agil", "Mãos Rápidas", 5, "+2,5% de velocidade de ataque", VEL_ATAQUE, 0.1)
             + serie("alcance", "Alcance", 2, "+0,25 de alcance de ataque", "forge:entity_reach", 0.25)
             + [apice("dancarino", "Dança da Lâmina", "+10% de velocidade de ataque e +20% de recuperação de fôlego",
                      attr(VEL_ATAQUE, 0.4), attr(REC_FOLEGO, 0.2))]),
            ("Sangue", "minecraft:redstone",
             serie("sede", "Sede", 5, "Recupera 1% do dano causado como vida", ROUBO, 0.01)
             + serie("empurrao", "Empurrão", 2, "+0,25 de repulsão nos golpes", REPULSAO, 0.25)
             + [apice("predador", "Predador", "+4% de roubo de vida e +1 de dano", attr(ROUBO, 0.04), attr(DANO, 1.0))]),
            ("Impacto", "minecraft:anvil",
             serie("impacto", "Impacto", 5, "+0,5 de impacto (atordoa mais)", IMPACTO, 0.5)
             + serie("perfurar", "Perfurar", 2, "Ignora 0,5 de armadura do inimigo", PERFURAR, 0.5)
             + [apice("quebra_escudos", "Quebra-Escudos", "Ignora 10% da armadura do inimigo", attr(RASGAR, 0.1))]),
            ("Fúria", "minecraft:blaze_powder",
             serie("furia", "Fúria", 5, "+1,5% de chance de crítico", CRIT, 0.015)
             + serie("colera", "Cólera", 2, "+4% de dano crítico", DANO_CRIT, 0.04)
             + [apice("golpe_final", "Golpe Final", "Cada acerto tira mais 2% da vida atual do alvo",
                      attr("attributeslib:current_hp_damage", 0.02))]),
        ],
    },
    "mineracao": {
        "titulo": "Mineração", "icone": "minecraft:iron_pickaxe", "fundo": "minecraft:textures/block/deepslate.png",
        "descricao": "Para todos. Sobe minerando (minérios valem muito mais).", "experiencia": EXP_MINERACAO,
        "raiz": ("minerador", "Minerador", "+10% de velocidade de mineração", "minecraft:iron_pickaxe",
                 attr("attributeslib:mining_speed", 0.1)),
        "ramos": [
            ("Picareta", "minecraft:diamond_pickaxe",
             serie("braco_forte", "Braço Forte", 7, "+6% de velocidade de mineração", "attributeslib:mining_speed", 0.06)
             + [apice("escavadora", "Escavadora", "+25% de velocidade de mineração", attr("attributeslib:mining_speed", 0.25))]),
            ("Alcance", "minecraft:spyglass",
             serie("braco_longo", "Braço Longo", 6, "+0,25 de alcance para quebrar e colocar blocos", "forge:block_reach", 0.25)
             + [("passo_firme", "Passo Firme", "Sobe meio bloco sem pular", attr("forge:step_height_addition", 0.5)),
                apice("arquiteto", "Arquiteto", "+1 de alcance para quebrar e colocar blocos", attr("forge:block_reach", 1.0))]),
            ("Sorte", "minecraft:emerald",
             serie("olho_treinado", "Olho Treinado", 7, "+0,5 de sorte (baús e pescaria melhores)", SORTE, 0.5)
             + [apice("garimpeiro", "Garimpeiro", "+2 de sorte", attr(SORTE, 2.0))]),
            ("Sabedoria", "minecraft:experience_bottle",
             serie("sabedoria", "Sabedoria", 7, "+4% de experiência ganha", XP, 0.04)
             + [apice("mente_afiada", "Mente Afiada", "+15% de experiência ganha", attr(XP, 0.15))]),
            ("Couro de Mineiro", "minecraft:leather_chestplate",
             serie("couro_mineiro", "Couro de Mineiro", 4, "+0,5 de armadura", ARMADURA, 0.5)
             + serie("pele_de_pedra", "Pele de Pedra", 3, "+0,5 de resistência da armadura", DUREZA, 0.5)
             + [apice("peito_de_ferro", "Peito de Ferro", "+2 de armadura", attr(ARMADURA, 2.0))]),
        ],
    },
    "vida": {
        "titulo": "Vida", "icone": "minecraft:golden_apple", "fundo": "minecraft:textures/block/moss_block.png",
        "descricao": "Para todos. Sobe comendo e sobrevivendo a dano.", "experiencia": EXP_VIDA,
        "raiz": ("resistente", "Resistente", "+2 de vida (1 coração)", "minecraft:golden_apple", attr(VIDA, 2.0)),
        "ramos": [
            ("Coração", "minecraft:red_dye",
             serie("coracao", "Coração Forte", 7, "+1 de vida (meio coração)", VIDA, 1.0)
             + [apice("coracao_de_dragao", "Coração de Dragão", "+4 de vida (2 corações) e +10% de cura recebida",
                      attr(VIDA, 4.0), attr(CURA, 0.1))]),
            ("Couro", "minecraft:leather",
             serie("pele_grossa", "Pele Grossa", 5, "+0,5 de armadura", ARMADURA, 0.5)
             + serie("casca", "Casca", 2, "+0,5 de resistência da armadura", DUREZA, 0.5)
             + [apice("muralha_viva", "Muralha Viva", "+2 de armadura e +2 de resistência da armadura",
                      attr(ARMADURA, 2.0), attr(DUREZA, 2.0))]),
            ("Viajante", "minecraft:leather_boots",
             serie("pes_leves", "Pés Leves", 4, "+2% de velocidade de movimento", VEL, 0.002)
             + serie("nadador", "Nadador", 2, "+10% de velocidade de nado", "forge:swim_speed", 0.1)
             + [("escalador", "Escalador", "Sobe meio bloco sem pular", attr("forge:step_height_addition", 0.5)),
                apice("andarilho", "Andarilho", "+5% de velocidade e +20% de velocidade de nado",
                      attr(VEL, 0.005), attr("forge:swim_speed", 0.2))]),
            ("Cura", "minecraft:glistering_melon_slice",
             serie("cura", "Cura Rápida", 7, "+3% de cura recebida", CURA, 0.03)
             + [apice("renascer", "Renascer", "Cura acima da vida máxima vira escudo (até 10% da vida)",
                      attr("attributeslib:overheal", 0.1))]),
            ("Fôlego", "minecraft:sugar",
             serie("pulmao", "Pulmão", 5, "+0,5 de fôlego máximo", FOLEGO, 0.5)
             + serie("ar_fresco", "Ar Fresco", 2, "+3% de recuperação de fôlego", REC_FOLEGO, 0.03)
             + [apice("pulmao_de_ferro", "Pulmão de Ferro", "+10% de recuperação de fôlego e +2 de fôlego",
                      attr(REC_FOLEGO, 0.1), attr(FOLEGO, 2.0))]),
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
    # os ramos saem da raiz como raios, espalhados em volta dela (o primeiro aponta para cima)
    n_ramos = len(cls["ramos"])
    for r, (nome_ramo, icone_ramo, lista) in enumerate(cls["ramos"]):
        angulo = -math.pi / 2 + 2 * math.pi * r / n_ramos
        anterior = rid
        for i, (sid, tit, desc, rec) in enumerate(lista, 1):
            e_apice = i == len(lista)
            recs = rec if isinstance(rec, list) else [rec]
            assert sid not in definicoes, f"{chave}: id repetido {sid}"
            definicoes[sid] = {"title": tit, "description": f"{desc}\nRamo: {nome_ramo}",
                               "icon": icone(icone_ramo),
                               "frame": quadro("challenge" if e_apice else "task"),
                               "rewards": recs, "cost": 3 if e_apice else 1}
            skills[sid] = {"definition": sid, "x": round(math.cos(angulo) * 32 * i),
                           "y": round(math.sin(angulo) * 32 * i)}
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
