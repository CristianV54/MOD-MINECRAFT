# Kit da classe Assassino. Gerado por tools/gerar_missoes.py.
tag @s add tp_kit_recebido
give @s epicfight:iron_dagger{ Enchantments:[ { id:"minecraft:sharpness", lvl:1s } ] } 1
give @s epicfight:iron_dagger{ Enchantments:[ { id:"minecraft:sharpness", lvl:1s } ] } 1
give @s minecraft:leather_helmet 1
give @s minecraft:chainmail_chestplate 1
give @s minecraft:leather_boots 1
give @s minecraft:potion{ Potion:"minecraft:swiftness" } 3
give @s epicfight:skillbook{ skill:"epicfight:step" } 1
give @s minecraft:ender_pearl 4
give @s minecraft:cooked_beef 12
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]
