# Invoca o Gabriel, o Guardião dos Dragões, perto do jogador que rodou a função, sem deixar ele enterrado.
# Mesmo jeito do Mestre Vellan: 3 blocos à frente, senão 2, senão no lugar do jogador.
execute rotated ~ 0 positioned ^ ^ ^3 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run summon minecraft:marker ~ ~ ~ {Tags:["tp_gabriel_spawn"]}
execute unless entity @e[type=minecraft:marker,tag=tp_gabriel_spawn] rotated ~ 0 positioned ^ ^ ^2 if block ~ ~ ~ #terras_partidas:passavel if block ~ ~1 ~ #terras_partidas:passavel run summon minecraft:marker ~ ~ ~ {Tags:["tp_gabriel_spawn"]}
execute unless entity @e[type=minecraft:marker,tag=tp_gabriel_spawn] run summon minecraft:marker ~ ~ ~ {Tags:["tp_gabriel_spawn"]}
execute as @e[type=minecraft:marker,tag=tp_gabriel_spawn,limit=1,sort=nearest] at @s run easy_npc preset import_new data terras_partidas:easy_npc/preset/humanoid/gabriel.npc.snbt ~ ~ ~
kill @e[type=minecraft:marker,tag=tp_gabriel_spawn]
playsound minecraft:item.armor.equip_netherite neutral @s ~ ~ ~ 1 0.8
tellraw @s ["",{"text":"Gabriel","color":"aqua","bold":true},{"text":": Então é você. Venha, precisamos conversar.","color":"white"}]
