# Ficha do formato: ranking em contagem regressiva

Exemplo de ficha, escrita a partir de `skills/videos-longos/exemplos/ranking.mp4` (um vídeo do próprio kit).
O episódio desta pasta (os 3 animais mais rápidos) foi feito em cima dela. Pra refazer o teste:

```bash
python3 skills/mimic/scripts/analisar.py skills/videos-longos/exemplos/ranking.mp4 --nome ranking-desertos
python3 ferramentas/produzir.py skills/mimic/exemplo
python3 skills/mimic/scripts/comparar.py referencias/ranking-desertos skills/mimic/exemplo/out/exemplo.mp4
```

1. **Resumo:** ranking de 3 posições em contagem regressiva, com apresentador desenhado e a lista empilhando à direita.
2. **Tela e duração:** 16:9, 30 s.
3. **Gancho (0 a 5,8 s):** título amarelo grande com o tema ("Os 3 maiores..."). Aos 2,5 s entra um cartão vermelho
   com a provocação sobre o 1º lugar. Tipo: promessa + lacuna (você acha que sabe, mas não sabe).
4. **Estrutura:**
   - 0,0 s gancho: tema e provocação;
   - 5,8 s 3º lugar: nome e um número;
   - 11,5 s 2º lugar: nome, número e uma frase que quebra uma crença;
   - 18,6 s 1º lugar: a surpresa, o número, a frase final e o pedido de comentário.
5. **Ritmo:** 4 planos, um por posição (5,8 s, 5,6 s, 7,2 s, 11,4 s). 1 corte a cada 10 s. 1,3 mudança de tela a
   cada 10 s (é um formato calmo). 2,16 palavras por segundo. Uma pausa de 0,6 s antes do 2º lugar.
6. **Visual:** vetorial chapado. Cada posição tem um cenário de cor diferente (magenta de estúdio, pôr do sol laranja,
   noite azul, dia azul-claro). Apresentador de corpo inteiro à esquerda, ocupando 1/3 da altura. Imagem com vinheta leve.
   Paleta: `#ffd34d` (amarelo dos cartões), `#d8433a` (vermelho da provocação), `#1b2440` (azul-escuro), `#ffffff`.
7. **Texto na tela:**
   - título do tema: cartão amarelo inclinado 2 graus, no terço de cima, à direita;
   - lista do ranking: à direita, cada item com o número grande, o nome e o dado embaixo. O item novo entra amarelo
     e os anteriores ficam escuros;
   - um cartão pequeno em cima, à esquerda, com a ideia daquela posição;
   - legenda: embaixo, branca com contorno escuro, caixa alta, até 5 palavras por vez.
8. **Movimento:** corte seco entre as posições, com o cenário trocando. Os cartões entram com um pulo curto na
   palavra em que a voz diz o nome. O apresentador aponta pro item novo e comemora no 1º lugar. Confete na frase final.
9. **Som:** uma voz, tom de curiosidade. Trilha calma por baixo o tempo todo. Um "whoosh" em cada troca de posição,
   um "boom" no 1º lugar e um "ding" na palavra da surpresa.
10. **Fecho:** repete a surpresa em uma frase e pede comentário ("você sabia?").
11. **Por que funciona:** a provocação do gancho só se resolve no fim; a lista na tela mostra quanto falta; cada
    posição traz um número fácil de repetir.
12. **O que não dá pra copiar igual:** nada. É um formato todo desenhado, e o kit tem as mesmas peças
    (`LONGO.ranking` e o estilo vetorial).
