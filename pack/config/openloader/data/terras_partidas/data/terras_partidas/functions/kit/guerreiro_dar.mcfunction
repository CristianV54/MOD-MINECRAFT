# Kit da classe Guerreiro. Gerado por tools/gerar_missoes.py.
tag @s add tp_kit_recebido
give @s epicfight:iron_longsword 1
give @s minecraft:chainmail_helmet 1
give @s minecraft:chainmail_chestplate 1
give @s minecraft:chainmail_leggings 1
give @s minecraft:chainmail_boots 1
give @s minecraft:potion{ Potion:"minecraft:strength" } 2
give @s minecraft:cooked_beef 12
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]
