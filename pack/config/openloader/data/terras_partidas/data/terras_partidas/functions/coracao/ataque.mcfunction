scoreboard players set @s tp_cs_ciclo 0
execute at @p[distance=..24,gamemode=!spectator] rotated ~ 0 positioned ^ ^ ^-2 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run function terras_partidas:coracao/passo_do_vazio
execute if score @s tp_cs_fase matches 2.. run scoreboard players set @s tp_cs_onda 30
