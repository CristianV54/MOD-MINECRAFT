# Só faz algo enquanto existe jogador novo esperando o Mestre (custo quase zero no resto do tempo).
execute as @a[tag=tp_novo_jogador] at @s run function terras_partidas:boas_vindas/esperar
