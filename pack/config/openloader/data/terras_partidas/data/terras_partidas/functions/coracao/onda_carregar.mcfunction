# Aviso: 1,5 s de partículas no chão antes da onda.
scoreboard players remove @s tp_cs_onda 1
particle minecraft:witch ~ ~0.2 ~ 2.5 0 2.5 0 25
execute if score @s tp_cs_onda matches 29 run playsound minecraft:block.beacon.power_select hostile @a[distance=..32] ~ ~ ~ 1 0.5
execute if score @s tp_cs_onda matches 29 run title @a[distance=..12] actionbar {"text":"Onda do Selo! Afaste-se dele!","color":"red","bold":true}
execute if score @s tp_cs_onda matches 0 run function terras_partidas:coracao/onda
