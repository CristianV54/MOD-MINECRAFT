scoreboard players add @s tp_cs_t 1
execute if score @s tp_cs_t matches 1 run effect give @s minecraft:resistance 30 4 true
execute if score @s tp_cs_t matches 1 run effect give @s minecraft:regeneration 10 2 true
execute if score @s tp_cs_t matches 1 run time set 23500
execute if score @s tp_cs_t matches 1 run weather clear
execute if score @s tp_cs_t matches 1 run title @s times 20 120 40
execute if score @s tp_cs_t matches 1 run title @s subtitle {"text":"Você conseguiu.","color":"white"}
execute if score @s tp_cs_t matches 1 run title @s title {"text":"O SELO FOI RESTAURADO","color":"gold","bold":true}
execute if score @s tp_cs_t matches 1 run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1
execute if score @s tp_cs_t matches 1 run playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 0.8
execute if score @s tp_cs_t matches 1 run particle minecraft:end_rod ~ ~1 ~ 2 2 2 0.1 200
execute if score @s tp_cs_t matches 10 run summon minecraft:firework_rocket ~3 ~1 ~2 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;11141290,13421823],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 25 run summon minecraft:firework_rocket ~-3 ~1 ~1 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;16755200],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 40 run summon minecraft:firework_rocket ~1 ~1 ~-3 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;11141290,16755200],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 55 run summon minecraft:firework_rocket ~-2 ~1 ~-2 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;13421823],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 70 run summon minecraft:firework_rocket ~2 ~1 ~3 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;16755200,13421823],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 85 run summon minecraft:firework_rocket ~-3 ~1 ~3 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1,Flicker:1b,Trail:1b,Colors:[I;11141290],FadeColors:[I;16777215]}]}}}}
execute if score @s tp_cs_t matches 140 run function terras_partidas:rechamar_vellan
execute if score @s tp_cs_t matches 140 run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 1.4
execute if score @s tp_cs_t matches 160 run tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Você conseguiu. Eu senti o Selo se fechar lá de longe.","color":"white"}]
execute if score @s tp_cs_t matches 230 run tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Trezentos anos atrás, sete guardiões criaram o Selo. Hoje, um único caçador terminou o trabalho.","color":"white"}]
execute if score @s tp_cs_t matches 310 run tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Preciso te contar a verdade. Você enfrentou seis guardiões... mas éramos sete. Eu sou o sétimo.","color":"white"}]
execute if score @s tp_cs_t matches 390 run tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Fiquei escondido na Ordem, esperando alguém forte o bastante. Esperei trezentos anos. Valeu cada dia.","color":"white"}]
execute if score @s tp_cs_t matches 470 run tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Esta coroa era nossa, dos sete. Agora ela é sua, Guardião do Selo.","color":"yellow"}]
execute if score @s tp_cs_t matches 480 run give @s minecraft:golden_helmet{display:{Name:'{"text":"Coroa do Selo","color":"gold","bold":true,"italic":false}',Lore:['{"text":"Usada pelos sete guardiões.","color":"gray","italic":true}','{"text":"Agora é sua, Guardião do Selo.","color":"light_purple","italic":true}']},Trim:{material:"minecraft:amethyst",pattern:"minecraft:eye"},Unbreakable:1b,Enchantments:[{id:"minecraft:protection",lvl:4s},{id:"minecraft:respiration",lvl:3s}],AttributeModifiers:[{AttributeName:"minecraft:generic.armor",Name:"coroa",Amount:4d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568129],Slot:"head"},{AttributeName:"minecraft:generic.armor_toughness",Name:"coroa",Amount:3d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568130],Slot:"head"},{AttributeName:"minecraft:generic.max_health",Name:"coroa",Amount:6d,Operation:0,UUID:[I;1397051766,1129268549,1094799955,1347568131],Slot:"head"}]}
execute if score @s tp_cs_t matches 480 run team join tp_guardiao @s
execute if score @s tp_cs_t matches 480 run playsound minecraft:item.totem.use master @s ~ ~ ~ 0.8 1
execute if score @s tp_cs_t matches 480 run title @s times 10 70 20
execute if score @s tp_cs_t matches 480 run title @s subtitle {"text":"Seu novo título aparece ao lado do seu nome","color":"gray"}
execute if score @s tp_cs_t matches 480 run title @s title {"text":"Guardião do Selo","color":"gold"}
execute if score @s tp_cs_t matches 600 run function terras_partidas:coracao/creditos
execute if score @s tp_cs_t matches 600.. run tag @s remove tp_cs_vitoria
