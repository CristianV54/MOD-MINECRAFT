scoreboard players add @s tp_cs_t 1
execute if score @s tp_cs_t matches 1 run effect give @s minecraft:darkness 7 0 true
execute if score @s tp_cs_t matches 1 run title @s times 10 60 10
execute if score @s tp_cs_t matches 1 run title @s subtitle {"text":"Algo se mexe dentro do núcleo do Arauto...","color":"gray"}
execute if score @s tp_cs_t matches 1 run title @s title {"text":"Ainda não acabou","color":"dark_purple"}
execute if score @s tp_cs_t matches 1 run playsound minecraft:block.amethyst_block.break master @s ~ ~ ~ 1 0.5
execute if score @s tp_cs_t matches 1..100 run particle minecraft:reverse_portal ^ ^1 ^4 0.4 0.8 0.4 0.05 6
execute if score @s tp_cs_t matches 20 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 40 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 50 run tellraw @s {"text":"???: Trezentos anos... trezentos anos presa dentro daquela máquina.","color":"dark_purple","italic":true}
execute if score @s tp_cs_t matches 60 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.6
execute if score @s tp_cs_t matches 75 run tellraw @s {"text":"???: Os guardiões me chamavam de mal antigo. Eu era o que dava força ao Selo.","color":"dark_purple","italic":true}
execute if score @s tp_cs_t matches 80 run playsound minecraft:entity.warden.heartbeat master @s ~ ~ ~ 1 0.8
execute if score @s tp_cs_t matches 95 run tellraw @s {"text":"???: E você acabou de me libertar.","color":"light_purple","italic":true}
execute if score @s tp_cs_t matches 110 run function terras_partidas:coracao/invocar_aqui
execute if score @s tp_cs_t matches 110.. run tag @s remove tp_cs_despertar
