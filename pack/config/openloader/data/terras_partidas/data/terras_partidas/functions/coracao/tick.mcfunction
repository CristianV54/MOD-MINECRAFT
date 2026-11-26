# Só trabalha durante o despertar, a luta e a celebração.
execute as @a[tag=tp_cs_despertar] at @s run function terras_partidas:coracao/despertar_passo
execute as @e[type=minecraft:wither_skeleton,tag=coracao_selo] at @s run function terras_partidas:coracao/chefe
execute if score #luta tp_cs_vida matches 1 run function terras_partidas:coracao/vigia
execute as @a[tag=tp_cs_vitoria] at @s run function terras_partidas:coracao/vitoria_passo
