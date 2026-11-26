# Título dado pela missão "Mestre Caçador" (capítulo Caçadas).
team add tp_mestre_cacador
team modify tp_mestre_cacador prefix {"text":"[Mestre Caçador] ","color":"gold"}
team join tp_mestre_cacador @s
playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1
title @s times 10 70 20
title @s subtitle {"text":"Todas as feras antigas foram derrotadas","color":"gray"}
title @s title {"text":"Mestre Caçador","color":"gold","bold":true}
