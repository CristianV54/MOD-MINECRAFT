#!/usr/bin/env python3
"""Chefe final do SealCraft: O Coração do Selo, e a sequência de vitória.

Quando o Arauto morre (missão "Chefe Final: O Arauto"), o núcleo dele racha e de dentro
sai o mal que o Selo prendia de verdade. Tudo aqui é datapack (funções + conquistas),
usando um esqueleto Wither como corpo, com armadura de netherita enfeitada de ametista.

Fases (vida máxima 500):
  1. Passo do Vazio: a cada ~10 s ele some e aparece nas costas do jogador mais próximo.
  2. (60% da vida) Invoca 4 Sombras dos Guardiões. Enquanto elas vivem, ele não toma dano.
     Também passa a soltar Ondas do Selo: aviso de 1,5 s no chão e depois dano em volta.
  3. (25% da vida) Desesperado: mais rápido, mais forte e ataca com o dobro de frequência.

Vitória: conquista de desafio "O Selo Restaurado" (completa a missão), título na tela,
fogos, amanhecer, o Mestre Vellan aparece e faz o discurso final, Coroa do Selo,
título "[Guardião do Selo]" no nome e créditos no chat.

Uso: python3 tools/gerar_chefe_final.py
"""
import json
import os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(RAIZ, "pack", "config", "openloader", "data", "terras_partidas", "data")
NS = os.path.join(DATA, "terras_partidas")
FUNC = os.path.join(NS, "functions", "coracao")

VIDA = 500
NOME = '{"text":"O Coração do Selo","color":"light_purple","bold":true}'
TRIM = '{material:"minecraft:amethyst",pattern:"minecraft:ward"}'
SEM_ATRIBUTOS = "AttributeModifiers:[]"   # a armadura é só visual; a defesa vem dos atributos do chefe


def peca(item):
    return f'{{id:"minecraft:{item}",Count:1b,tag:{{Trim:{TRIM},{SEM_ATRIBUTOS}}}}}'


CHEFE_NBT = (
    '{Tags:["coracao_selo"],CustomName:\'' + NOME + '\',CustomNameVisible:1b,PersistenceRequired:1b,'
    f'Health:{VIDA}f,'
    'Attributes:['
    f'{{Name:"minecraft:generic.max_health",Base:{VIDA}d}},'
    '{Name:"minecraft:generic.armor",Base:10d},'
    '{Name:"minecraft:generic.armor_toughness",Base:4d},'
    '{Name:"minecraft:generic.attack_damage",Base:11d},'
    '{Name:"minecraft:generic.movement_speed",Base:0.29d},'
    '{Name:"minecraft:generic.knockback_resistance",Base:1d},'
    '{Name:"minecraft:generic.follow_range",Base:64d}],'
    'HandItems:[{id:"epicfight:netherite_longsword",Count:1b,tag:{Enchantments:[{id:"minecraft:fire_aspect",lvl:1s}]}},{}],'
    'HandDropChances:[0f,0f],'
    f'ArmorItems:[{peca("netherite_boots")},{peca("netherite_leggings")},{peca("netherite_chestplate")},{peca("netherite_helmet")}],'
    'ArmorDropChances:[0f,0f,0f,0f]}'
)

# Zumbi invisível com armadura de couro roxa: só a armadura aparece, flutuando.
# (Vex não serve: um mod do pacote troca os vex por outra versão e perde a marcação.)
def _couro(item):
    return f'{{id:"minecraft:leather_{item}",Count:1b,tag:{{display:{{color:4194432}}}}}}'


SOMBRA_NBT = ('{Tags:["sombra_selo"],CustomName:\'{"text":"Sombra do Guardião","color":"dark_purple"}\','
              'Health:24f,PersistenceRequired:1b,IsBaby:0b,CanPickUpLoot:0b,'
              'Attributes:[{Name:"minecraft:generic.max_health",Base:24d},{Name:"minecraft:generic.movement_speed",Base:0.27d}],'
              'ActiveEffects:[{Id:14,Amplifier:0b,Duration:999999,ShowParticles:0b}],'
              f'ArmorItems:[{_couro("boots")},{_couro("leggings")},{_couro("chestplate")},{_couro("helmet")}],'
              'ArmorDropChances:[0f,0f,0f,0f]}')

COROA = ('minecraft:golden_helmet{display:{Name:\'{"text":"Coroa do Selo","color":"gold","bold":true,"italic":false}\','
         'Lore:[\'{"text":"Usada pelos sete guardiões.","color":"gray","italic":true}\','
         '\'{"text":"Agora é sua, Guardião do Selo.","color":"light_purple","italic":true}\']},'
         'Trim:{material:"minecraft:amethyst",pattern:"minecraft:eye"},Unbreakable:1b,'
         'Enchantments:[{id:"minecraft:protection",lvl:4s},{id:"minecraft:respiration",lvl:3s}],'
         'AttributeModifiers:['
         '{AttributeName:"minecraft:generic.armor",Name:"coroa",Amount:4d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568129],Slot:"head"},'
         '{AttributeName:"minecraft:generic.armor_toughness",Name:"coroa",Amount:3d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568130],Slot:"head"},'
         '{AttributeName:"minecraft:generic.max_health",Name:"coroa",Amount:6d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568131],Slot:"head"}]}')

VELLAN = '{"text":"[Mestre Vellan] ","color":"gold"}'


def fala(texto, cor="white"):
    return f'tellraw @s ["",{VELLAN},{{"text":"{texto}","color":"{cor}"}}]'


def fogos(dx, dz, cores):
    return (f'summon minecraft:firework_rocket ~{dx} ~1 ~{dz} {{LifeTime:18,FireworksItem:{{id:"minecraft:firework_rocket",Count:1b,'
            f'tag:{{Fireworks:{{Explosions:[{{Type:1,Flicker:1b,Trail:1b,Colors:[I;{cores}],FadeColors:[I;16777215]}}]}}}}}}}}')


ROXO, OURO, LILAS = "11141290", "16755200", "13421823"

ARQUIVOS = {
    # ------------------------------------------------------------------ preparação
    "carregar": f"""# Placar e time usados pelo chefe final.
scoreboard objectives add tp_cs_t dummy
scoreboard objectives add tp_cs_vida dummy
scoreboard objectives add tp_cs_ciclo dummy
scoreboard objectives add tp_cs_fase dummy
scoreboard objectives add tp_cs_onda dummy
team add tp_guardiao
team modify tp_guardiao prefix {{"text":"[Guardião do Selo] ","color":"gold"}}
""",
    "tick": """# Só trabalha durante o despertar, a luta e a celebração.
execute as @a[tag=tp_cs_despertar] at @s run function terras_partidas:coracao/despertar_passo
execute as @e[type=minecraft:wither_skeleton,tag=coracao_selo] at @s run function terras_partidas:coracao/chefe
execute if score #luta tp_cs_vida matches 1 run function terras_partidas:coracao/vigia
execute as @a[tag=tp_cs_vitoria] at @s run function terras_partidas:coracao/vitoria_passo
""",
    # ------------------------------------------------------------------ despertar
    "despertar": """# Chamado pela recompensa automática da missão do Arauto (ou pela missão de chamar de novo).
# Não faz nada se o jogador já derrotou o Coração.
execute unless entity @s[advancements={terras_partidas:selo_restaurado=true}] unless entity @s[tag=tp_cs_despertar] unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] run function terras_partidas:coracao/despertar_iniciar
""",
    "despertar_iniciar": """tag @s add tp_cs_despertar
scoreboard players set @s tp_cs_t 0
""",
    "despertar_passo": f"""scoreboard players add @s tp_cs_t 1
execute if score @s tp_cs_t matches 1 run effect give @s minecraft:darkness 7 0 true
execute if score @s tp_cs_t matches 1 run title @s times 10 60 10
execute if score @s tp_cs_t matches 1 run title @s subtitle {{"text":"Algo se mexe dentro do núcleo do Arauto...","color":"gray"}}
execute if score @s tp_cs_t matches 1 run title @s title {{"text":"Ainda não acabou","color":"dark_purple"}}
execute if score @s tp_cs_t matches 1 run playsound minecraft:block.amethyst_block.break master @s ~ ~ ~ 1 0.5
execute if score @s tp_cs_t matches 1..100 run particle minecraft:reverse_portal ^ ^1 ^4 0.4 0.8 0.4 0.05 6
execute if score @s tp_cs_t matches 20 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 40 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 50 run tellraw @s {{"text":"???: Trezentos anos... trezentos anos presa dentro daquela máquina.","color":"dark_purple","italic":true}}
execute if score @s tp_cs_t matches 60 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 75 run tellraw @s {{"text":"???: Os guardiões me chamavam de mal antigo. Eu era o que dava força ao Selo.","color":"dark_purple","italic":true}}
execute if score @s tp_cs_t matches 80 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.8
execute if score @s tp_cs_t matches 95 run tellraw @s {{"text":"???: E você acabou de me libertar.","color":"light_purple","italic":true}}
execute if score @s tp_cs_t matches 110 run function terras_partidas:coracao/invocar_aqui
execute if score @s tp_cs_t matches 110.. run tag @s remove tp_cs_despertar
""",
    "invocar_aqui": """# Aparece 4 blocos à frente se houver espaço; senão, em cima do jogador.
tag @s add tp_cs_invocador
execute positioned ^ ^ ^4 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run function terras_partidas:coracao/invocar
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..8] run function terras_partidas:coracao/invocar
tag @s remove tp_cs_invocador
""",
    "invocar": f"""summon minecraft:wither_skeleton ~ ~ ~ {CHEFE_NBT}
scoreboard players set @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..1] tp_cs_fase 1
scoreboard players set @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..1] tp_cs_ciclo 100
scoreboard players set #luta tp_cs_vida 1
scoreboard players set #ultimo tp_cs_vida {VIDA}
bossbar add terras_partidas:coracao {NOME}
bossbar set terras_partidas:coracao color purple
bossbar set terras_partidas:coracao style notched_10
bossbar set terras_partidas:coracao max {VIDA}
bossbar set terras_partidas:coracao value {VIDA}
particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 1
particle minecraft:dragon_breath ~ ~1 ~ 1 1 1 0.05 120
playsound minecraft:entity.wither.spawn hostile @a[distance=..64] ~ ~ ~ 1 1.2
title @a[distance=..64] times 10 50 15
title @a[distance=..64] subtitle {{"text":"O mal que o Selo prendia","color":"gray"}}
title @a[distance=..64] title {NOME}
""",
    # ------------------------------------------------------------------ luta
    "chefe": """# Roda todo tick como o chefe.
execute store result score @s tp_cs_vida run data get entity @s Health
scoreboard players operation #ultimo tp_cs_vida = @s tp_cs_vida
execute store result bossbar terras_partidas:coracao value run scoreboard players get @s tp_cs_vida
bossbar set terras_partidas:coracao players @a[distance=..64]
tag @a[distance=..64] add tp_cs_lutador
particle minecraft:dragon_breath ~ ~1.2 ~ 0.35 0.6 0.35 0.01 2
particle minecraft:end_rod ~ ~1 ~ 0.5 0.8 0.5 0.02 1
execute if score @s tp_cs_fase matches 1 if score @s tp_cs_vida matches ..300 run function terras_partidas:coracao/fase2
execute if score @s tp_cs_fase matches 2 if score @s tp_cs_vida matches ..125 run function terras_partidas:coracao/fase3
scoreboard players add @s tp_cs_ciclo 1
execute if score @s tp_cs_fase matches 3 run scoreboard players add @s tp_cs_ciclo 1
execute if score @s tp_cs_ciclo matches 200.. run function terras_partidas:coracao/ataque
execute if score @s tp_cs_onda matches 1.. run function terras_partidas:coracao/onda_carregar
execute if entity @e[type=minecraft:zombie,tag=sombra_selo,distance=..48] run function terras_partidas:coracao/escudo
""",
    "ataque": """scoreboard players set @s tp_cs_ciclo 0
execute at @p[distance=..24,gamemode=!spectator] rotated ~ 0 positioned ^ ^ ^-2 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run function terras_partidas:coracao/passo_do_vazio
execute if score @s tp_cs_fase matches 2.. run scoreboard players set @s tp_cs_onda 30
""",
    "passo_do_vazio": """# Executado como o chefe, já na posição de destino (2 blocos atrás do jogador).
execute at @s run particle minecraft:portal ~ ~1 ~ 0.3 0.8 0.3 0.4 60
tp @s ~ ~ ~ facing entity @p
particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.8 0.3 0.05 50
playsound minecraft:entity.enderman.teleport hostile @a[distance=..32] ~ ~ ~ 1 0.6
title @a[distance=..6] actionbar {"text":"O Coração apareceu atrás de você!","color":"light_purple"}
""",
    "onda_carregar": """# Aviso: 1,5 s de partículas no chão antes da onda.
scoreboard players remove @s tp_cs_onda 1
particle minecraft:witch ~ ~0.2 ~ 2.5 0 2.5 0 25
execute if score @s tp_cs_onda matches 29 run playsound minecraft:block.beacon.power_select hostile @a[distance=..32] ~ ~ ~ 1 0.5
execute if score @s tp_cs_onda matches 29 run title @a[distance=..12] actionbar {"text":"Onda do Selo! Afaste-se dele!","color":"red","bold":true}
execute if score @s tp_cs_onda matches 0 run function terras_partidas:coracao/onda
""",
    "onda": """particle minecraft:sonic_boom ~ ~1 ~ 0 0 0 0 1
particle minecraft:explosion ~ ~0.5 ~ 2.5 0.3 2.5 0 12
playsound minecraft:entity.warden.sonic_boom hostile @a[distance=..32] ~ ~ ~ 1 1.2
execute as @a[distance=..5,gamemode=!creative,gamemode=!spectator] run damage @s 9 minecraft:magic by @e[type=minecraft:wither_skeleton,tag=coracao_selo,limit=1,sort=nearest]
effect give @a[distance=..5] minecraft:slowness 3 1
""",
    "escudo": """effect give @s minecraft:resistance 1 4 true
particle minecraft:enchant ~ ~1 ~ 0.6 1 0.6 0.5 10
title @a[distance=..24] actionbar {"text":"Ele está protegido! Mate as Sombras dos Guardiões.","color":"dark_purple"}
""",
    "fase2": f"""scoreboard players set @s tp_cs_fase 2
title @a[distance=..64] times 5 50 15
title @a[distance=..64] subtitle {{"text":"Mate as sombras para quebrar o escudo dele","color":"gray"}}
title @a[distance=..64] title {{"text":"Sombras dos Guardiões","color":"dark_purple"}}
playsound minecraft:entity.evoker.prepare_summon hostile @a[distance=..64] ~ ~ ~ 1 0.7
summon minecraft:zombie ~2 ~ ~ {SOMBRA_NBT}
summon minecraft:zombie ~-2 ~ ~ {SOMBRA_NBT}
summon minecraft:zombie ~ ~ ~2 {SOMBRA_NBT}
summon minecraft:zombie ~ ~ ~-2 {SOMBRA_NBT}
""",
    "fase3": """scoreboard players set @s tp_cs_fase 3
effect give @s minecraft:speed infinite 0 true
effect give @s minecraft:strength infinite 0 true
title @a[distance=..64] times 5 50 15
title @a[distance=..64] subtitle {"text":"Ele está desesperado. Não pare agora!","color":"gray"}
title @a[distance=..64] title {"text":"O Coração racha","color":"red"}
playsound minecraft:block.amethyst_cluster.break hostile @a[distance=..64] ~ ~ ~ 1 0.5
particle minecraft:dragon_breath ~ ~1 ~ 1.5 1 1.5 0.05 150
""",
    "vigia": """# Reserva: se o chefe sumir já quase morto sem a conquista disparar (morte por fogo,
# queda, etc.), a vitória acontece do mesmo jeito.
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] run bossbar set terras_partidas:coracao players
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] if score #ultimo tp_cs_vida matches ..60 as @a[tag=tp_cs_lutador,limit=1] at @s run function terras_partidas:coracao/vitoria
""",
    # ------------------------------------------------------------------ vitória
    "vitoria": """# Conquista (quem matou) ou reserva da vigia. Vale para todos que estavam na luta.
scoreboard players set #luta tp_cs_vida 0
bossbar remove terras_partidas:coracao
kill @e[type=minecraft:zombie,tag=sombra_selo]
tag @s add tp_cs_lutador
advancement grant @a[tag=tp_cs_lutador] only terras_partidas:selo_restaurado
scoreboard players set @a[tag=tp_cs_lutador] tp_cs_t 0
tag @a[tag=tp_cs_lutador] add tp_cs_vitoria
tag @a remove tp_cs_lutador
""",
    "vitoria_passo": "\n".join([
        "scoreboard players add @s tp_cs_t 1",
        "execute if score @s tp_cs_t matches 1 run effect give @s minecraft:resistance 30 4 true",
        "execute if score @s tp_cs_t matches 1 run effect give @s minecraft:regeneration 10 2 true",
        "execute if score @s tp_cs_t matches 1 run time set 23500",
        "execute if score @s tp_cs_t matches 1 run weather clear",
        "execute if score @s tp_cs_t matches 1 run title @s times 20 120 40",
        'execute if score @s tp_cs_t matches 1 run title @s subtitle {"text":"Você conseguiu.","color":"white"}',
        'execute if score @s tp_cs_t matches 1 run title @s title {"text":"O SELO FOI RESTAURADO","color":"gold","bold":true}',
        "execute if score @s tp_cs_t matches 1 run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1",
        "execute if score @s tp_cs_t matches 1 run playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 0.8",
        "execute if score @s tp_cs_t matches 1 run particle minecraft:end_rod ~ ~1 ~ 2 2 2 0.1 200",
        f"execute if score @s tp_cs_t matches 10 run {fogos(3, 2, ROXO + ',' + LILAS)}",
        f"execute if score @s tp_cs_t matches 25 run {fogos(-3, 1, OURO)}",
        f"execute if score @s tp_cs_t matches 40 run {fogos(1, -3, ROXO + ',' + OURO)}",
        f"execute if score @s tp_cs_t matches 55 run {fogos(-2, -2, LILAS)}",
        f"execute if score @s tp_cs_t matches 70 run {fogos(2, 3, OURO + ',' + LILAS)}",
        f"execute if score @s tp_cs_t matches 85 run {fogos(-3, 3, ROXO)}",
        "execute if score @s tp_cs_t matches 140 run function terras_partidas:rechamar_vellan",
        "execute if score @s tp_cs_t matches 140 run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 1.4",
        "execute if score @s tp_cs_t matches 160 run " + fala("Você conseguiu. Eu senti o Selo se fechar lá de longe."),
        "execute if score @s tp_cs_t matches 230 run " + fala("Trezentos anos atrás, sete guardiões criaram o Selo. Hoje, um único caçador terminou o trabalho."),
        "execute if score @s tp_cs_t matches 310 run " + fala("Preciso te contar a verdade. Você enfrentou seis guardiões... mas éramos sete. Eu sou o sétimo."),
        "execute if score @s tp_cs_t matches 390 run " + fala("Fiquei escondido na Ordem, esperando alguém forte o bastante. Esperei trezentos anos. Valeu cada dia."),
        "execute if score @s tp_cs_t matches 470 run " + fala("Esta coroa era nossa, dos sete. Agora ela é sua, Guardião do Selo.", "yellow"),
        f"execute if score @s tp_cs_t matches 480 run give @s {COROA}",
        "execute if score @s tp_cs_t matches 480 run team join tp_guardiao @s",
        "execute if score @s tp_cs_t matches 480 run playsound minecraft:item.totem.use master @s ~ ~ ~ 0.8 1",
        "execute if score @s tp_cs_t matches 480 run title @s times 10 70 20",
        'execute if score @s tp_cs_t matches 480 run title @s subtitle {"text":"Seu novo título aparece ao lado do seu nome","color":"gray"}',
        'execute if score @s tp_cs_t matches 480 run title @s title {"text":"Guardião do Selo","color":"gold"}',
        "execute if score @s tp_cs_t matches 600 run function terras_partidas:coracao/creditos",
        "execute if score @s tp_cs_t matches 600.. run tag @s remove tp_cs_vitoria",
    ]) + "\n",
    "creditos": """playsound minecraft:music_disc.otherside record @s ~ ~ ~ 0.6 1
tellraw @s ""
tellraw @s {"text":"═══════════  S E A L C R A F T  ═══════════","color":"gold","bold":true}
tellraw @s ["",{"text":"Uma aventura de ","color":"gray"},{"selector":"@s","color":"yellow"}]
tellraw @s ""
tellraw @s {"text":"Fragmentos recuperados: 19 de 19","color":"light_purple"}
tellraw @s {"text":"Guardiões libertados: 6 de 6","color":"light_purple"}
tellraw @s {"text":"O Coração do Selo: derrotado","color":"light_purple"}
tellraw @s ""
tellraw @s {"text":"História, missões e tradução: equipe SealCraft","color":"gray"}
tellraw @s {"text":"Mods: obrigado aos autores de Epic Fight, Cataclysm, Mowzie's Mobs, Iron's Spells, Blue Skies, Aquamirae e todos os outros.","color":"gray"}
tellraw @s ""
tellraw @s {"text":"Obrigado por jogar!","color":"gold","bold":true}
tellraw @s {"text":"Os Desafios Lendários continuam no livro de missões.","color":"gray","italic":true}
tellraw @s {"text":"═══════════════════════════════════════","color":"gold","bold":true}
""",
    # ------------------------------------------------------------------ teste rápido
    "testar": """# Para testar sem jogar até o Ato 5 (precisa de cheats): /function terras_partidas:coracao/testar
advancement revoke @s only terras_partidas:selo_restaurado
item replace entity @s armor.head with minecraft:netherite_helmet{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.chest with minecraft:netherite_chestplate{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.legs with minecraft:netherite_leggings{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.feet with minecraft:netherite_boots{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
give @s minecraft:netherite_sword{Enchantments:[{id:"minecraft:sharpness",lvl:5s}]}
give @s minecraft:golden_apple 8
give @s minecraft:cooked_beef 16
tellraw @s {"text":"Teste do chefe final: o Coração do Selo desperta em 5 segundos.","color":"yellow"}
function terras_partidas:coracao/despertar
""",
}


def salvar(rel, conteudo):
    caminho = os.path.join(NS, rel)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        if isinstance(conteudo, str):
            f.write(conteudo)
        else:
            json.dump(conteudo, f, ensure_ascii=False, indent=2)
            f.write("\n")


def adicionar_na_tag(tag, funcao):
    caminho = os.path.join(DATA, "minecraft", "tags", "functions", f"{tag}.json")
    d = json.load(open(caminho, encoding="utf-8"))
    if funcao not in d["values"]:
        d["values"].append(funcao)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write('{ "values": [' + ", ".join(f'"{v}"' for v in d["values"]) + '] }\n')


def main():
    for nome, texto in ARQUIVOS.items():
        salvar(f"functions/coracao/{nome}.mcfunction", texto)
    salvar("tags/blocks/passavel.json", {"values": [
        "minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:light",
        "minecraft:grass", "minecraft:fern", "minecraft:snow", "minecraft:fire", "minecraft:soul_fire"]})
    salvar("advancements/selo_restaurado.json", {
        "display": {
            "icon": {"item": "minecraft:nether_star"},
            "title": {"text": "O Selo Restaurado", "color": "gold"},
            "description": {"text": "Derrote o Coração do Selo e termine a história do SealCraft", "color": "light_purple"},
            "frame": "challenge", "show_toast": True, "announce_to_chat": True, "hidden": True,
            "background": "minecraft:textures/block/amethyst_block.png",
        },
        "criteria": {"vitoria": {"trigger": "minecraft:impossible"}},
    })
    salvar("advancements/coracao_derrotado.json", {
        "criteria": {"matou": {"trigger": "minecraft:player_killed_entity", "conditions": {
            "entity": [{"condition": "minecraft:entity_properties", "entity": "this",
                        "predicate": {"type": "minecraft:wither_skeleton", "nbt": "{Tags:[\"coracao_selo\"]}"}}]}}},
        "rewards": {"function": "terras_partidas:coracao/vitoria_conquista"},
    })
    # A conquista de matar precisa ser revogada para poder disparar de novo num teste.
    salvar("functions/coracao/vitoria_conquista.mcfunction",
           "advancement revoke @s only terras_partidas:coracao_derrotado\nfunction terras_partidas:coracao/vitoria\n")
    adicionar_na_tag("load", "terras_partidas:coracao/carregar")
    adicionar_na_tag("tick", "terras_partidas:coracao/tick")
    print("chefe final:", len(ARQUIVOS) + 1, "funções")


if __name__ == "__main__":
    main()
