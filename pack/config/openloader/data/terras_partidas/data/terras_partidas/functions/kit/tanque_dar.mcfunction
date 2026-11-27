# Kit da classe Tanque. Gerado por tools/gerar_missoes.py.
tag @s add tp_kit_recebido
give @s minecraft:shield 1
give @s minecraft:iron_helmet 1
give @s minecraft:iron_chestplate 1
give @s minecraft:iron_leggings 1
give @s minecraft:iron_boots 1
give @s epicfight:iron_spear 1
give @s epicfight:skillbook{ skill:"epicfight:parrying" } 1
give @s minecraft:cooked_beef 12
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]
