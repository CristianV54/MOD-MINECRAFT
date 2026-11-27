# Cerca de 5 segundos depois de entrar: o Mestre Vellan aparece 3 blocos à frente do jogador.
tag @s remove tp_novo_jogador
function terras_partidas:vellan/aparecer
playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 1.2
title @s times 10 70 20
title @s subtitle {"text":"O Mestre Vellan quer falar com você","color":"gray"}
title @s title {"text":"SealCraft","color":"gold","bold":true}
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Clique em mim com o botão direito para conversar e escolher sua classe.","color":"white"}]
