# Roda todo tick como o chefe.
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
