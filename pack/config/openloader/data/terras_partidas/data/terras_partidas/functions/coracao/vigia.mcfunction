# Reserva: se o chefe sumir já quase morto sem a conquista disparar (morte por fogo,
# queda, etc.), a vitória acontece do mesmo jeito.
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] run bossbar set terras_partidas:coracao players
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] if score #ultimo tp_cs_vida matches ..60 as @a[tag=tp_cs_lutador,limit=1] at @s run function terras_partidas:coracao/vitoria
