# Invoca o Mestre Vellan perto do jogador que rodou a função, sem deixar ele enterrado.
# Tenta 3 blocos à frente; se ali tiver bloco no pé ou na cabeça, tenta 2 blocos à frente;
# se também estiver ocupado, ele aparece no mesmo lugar do jogador (que sempre está livre).
tag @s add tp_vellan_alvo
execute rotated ~ 0 positioned ^ ^ ^3 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run summon minecraft:marker ~ ~ ~ {Tags:["tp_vellan_spawn"]}
execute unless entity @e[type=minecraft:marker,tag=tp_vellan_spawn] rotated ~ 0 positioned ^ ^ ^2 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run summon minecraft:marker ~ ~ ~ {Tags:["tp_vellan_spawn"]}
execute unless entity @e[type=minecraft:marker,tag=tp_vellan_spawn] run summon minecraft:marker ~ ~ ~ {Tags:["tp_vellan_spawn"]}
execute as @e[type=minecraft:marker,tag=tp_vellan_spawn,limit=1,sort=nearest] at @s run easy_npc preset import_new data terras_partidas:easy_npc/preset/humanoid/mestre_vellan.npc.snbt ~ ~ ~
kill @e[type=minecraft:marker,tag=tp_vellan_spawn]
tag @s remove tp_vellan_alvo
