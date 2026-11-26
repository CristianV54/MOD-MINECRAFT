# Aparece 4 blocos à frente se houver espaço; senão, em cima do jogador.
tag @s add tp_cs_invocador
execute positioned ^ ^ ^4 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run function terras_partidas:coracao/invocar
execute unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..8] run function terras_partidas:coracao/invocar
tag @s remove tp_cs_invocador
