---
name: mimic
description: Copia o FORMATO de qualquer vídeo a partir do link (YouTube, Shorts, Reels, TikTok, X) ou de um arquivo, e faz um vídeo novo nesse formato com o assunto da pessoa - mesmo gancho, mesma estrutura, mesmo ritmo de cortes, mesmo jeito de legenda, cor e movimento, com texto, imagem e voz próprios. Mede o original (planos, cortes, fala com tempo, som), lê os quadros, escreve a ficha do formato, produz na esteira do kit e compara com o original até bater. Use quando pedirem "copia o formato desse vídeo", "faz um igual a esse", "quero um vídeo nesse estilo", "modela esse vídeo", "faz um parecido com esse reels", ou quando mandarem um link de vídeo junto com um pedido de vídeo, mesmo sem citar a skill.
---

# Mimic: copiar o formato de um vídeo

Um vídeo que funciona tem duas partes: o **conteúdo** (o assunto, as palavras, as imagens, a voz) e o **formato**
(como abre, em quantas partes se divide, de quanto em quanto tempo corta, onde fica o texto, como as coisas entram,
como fecha). O formato não tem dono e é ele que segura a pessoa. Esta skill tira o formato de um vídeo e monta um
vídeo novo, com o assunto da pessoa, em cima dele.

O **kit** é a pasta que tem `ferramentas/produzir.py` (se esta skill foi instalada com `ferramentas/instalar_skills.py`,
o caminho está em `kit.txt`). Fale com a pessoa em português do Brasil. Código e nomes técnicos ficam em inglês.

## O que se copia e o que nunca se copia

| Copia (formato) | Nunca copia (conteúdo) |
|---|---|
| duração, tela (9:16, 16:9), número de planos e o tempo de cada um | imagem, filmagem, personagem ou rosto do original |
| o tipo de gancho e em que segundo ele acaba | o texto do original, nem traduzido, nem com sinônimo |
| a ordem das partes (gancho, virada, prova, fecho) | a voz, a música e os efeitos do original |
| velocidade da fala (palavras por segundo) e as pausas | logo, marca, @ ou nome do canal |
| lugar, tamanho e jeito da legenda e dos títulos | o assunto (o vídeo novo é sobre o assunto da pessoa) |
| paleta, tipo de fundo, tipo de movimento e de transição | |

O `original.mp4` fica só na pasta `referencias/` da pessoa, como referência. Nenhum pedaço dele entra no vídeo novo.

## Antes de começar

Precisa de duas coisas da pessoa: **o vídeo** (link ou arquivo) e **o assunto** do vídeo novo. Se faltar o assunto,
pergunte uma vez. O resto você decide.

## Passo a passo

### 1. Medir

```bash
python3 skills/mimic/scripts/analisar.py "<link-ou-arquivo>" --nome <slug-da-referencia>
```

Cria `referencias/<slug>/` com `ficha.json` (os números) e `quadros/` (as folhas). Leva de 1 a 3 minutos.

- Link que não baixa (Instagram costuma pedir login): peça pra pessoa baixar o vídeo e mandar o arquivo. Não insista
  no link e nunca peça senha ou cookie.
- Vídeo com mais de 3 minutos: avise que você vai copiar o formato dos primeiros minutos e a estrutura geral; se for
  vídeo longo de YouTube, a produção segue a skill `videos-longos` (capítulo por capítulo).

### 2. Olhar de verdade

Leia nesta ordem, sem pular:

1. `ficha.json`: tela, duração, `ritmo`, `mudancas`, `fala` (palavras por segundo, `gancho_3s`, `pausas`), `som`.
   - `ritmo.cortes_por_10s` conta corte seco (troca de plano).
   - `ritmo.mudancas_por_10s` conta toda vez que a tela muda de verdade: algo entra, sai, o fundo troca, a câmera
     dá zoom. Vídeo de motion quase não tem corte e vive disso. **É o número que manda no ritmo.** A lista
     `mudancas` diz o segundo de cada uma.
   - A transcrição pode errar nome próprio e marca: vale o que está escrito na tela.
2. `quadros/visao.jpg`: o vídeo inteiro numa folha. Dá a estrutura.
3. Cada `quadros/plano-NN.jpg` (os tempos de cada quadro estão em `planos[].tempos` e a fala daquele plano em
   `planos[].fala`). É aqui que você vê layout, legenda, o que entra e quando.
4. Cada `quadros/corte-NN.jpg`: 6 quadros seguidos em volta do corte. Mostra se é corte seco, deslize, zoom, clarão.

Folha de meio em meio segundo não mostra tudo. Se precisar ver um momento mais de perto (uma entrada de texto, uma
transição), tire os quadros seguidos:

```bash
ffmpeg -v error -ss <segundo> -i referencias/<slug>/original.mp4 -frames:v 8 -vf "scale=216:-2,tile=8x1" -update 1 -y referencias/<slug>/quadros/zoom.jpg
```

### 3. Escrever a ficha do formato

Grave `referencias/<slug>/formato.md` com estas seções, nessa ordem, com números e sem adjetivo solto ("texto
branco de 90 px no terço de baixo", não "legenda bonita"):

1. **Resumo em uma frase:** o que é esse formato.
2. **Tela e duração.**
3. **Gancho:** o que aparece e o que se ouve nos 3 primeiros segundos, e que tipo de gancho é (pergunta, promessa,
   susto, número, cena no meio da ação).
4. **Estrutura:** as partes em ordem, com o segundo em que cada uma começa e a função dela.
5. **Ritmo:** planos, plano médio, cortes a cada 10 s, palavras por segundo, onde ficam as pausas.
6. **Visual:** fundo, paleta (3 a 5 cores em hex), personagens ou objetos, enquadramento. Pra tirar a cor certa
   de um ponto: `ffmpeg -v error -ss <segundo> -i referencias/<slug>/original.mp4 -frames:v 1 -vf "crop=8:8:<x>:<y>,scale=1:1" -f rawvideo -pix_fmt rgb24 - | xxd -p`
   (devolve o hex). Anote também se a imagem é limpa ou tem vinheta e grão.
7. **Texto na tela:** legenda (lugar, tamanho, cor, quantas palavras por vez, destaque) e títulos.
8. **Movimento:** como as coisas entram e saem, câmera, tipo de transição entre planos.
9. **Som:** voz (uma ou várias, tom), trilha (tem? clima?), efeitos e em que momentos caem.
10. **Fecho:** como termina e o que pede (comentar, seguir, parte 2).
11. **Por que funciona:** 3 linhas.
12. **O que não dá pra copiar igual:** seja direto (veja "Limites").

Um exemplo de ficha pronta está em `exemplo/formato.md` (e o episódio feito a partir dela, na mesma pasta).

Mostre o resumo, a estrutura e o item 12 pra pessoa em poucas linhas e siga. Não espere aprovação pra continuar.

### 4. Escolher a base no kit

Pegue a peça do kit que chega mais perto do que você viu. Não invente estilo do zero se um do kit resolve.

| O que o original mostra | Base no kit |
|---|---|
| bonecos ou personagens desenhados falando | `skills/animacao-bonecos` ou `estilos-animados` (vetorial, quadrinhos, massinha) |
| formas chapadas, ícones, texto grande, infográfico | `estilos-animados/estilos/vetorial` |
| cena 3D, câmera andando, clima de filme | `estilos-animados/estilos/3d-cinematografico` (ou `ps2`, `3d-estudio`) |
| história em primeira pessoa, só diálogo | `skills/historia-pov` |
| fotos antigas, recortes, papel, estilo documentário | `skills/colagem-explicativa` ou `videos-longos` (documentário de arquivo) |
| mapa, países, rotas | `skills/mapas-animados` |
| lista, ranking, linha do tempo | `skills/videos-longos` (`LONGO.ranking`, `LONGO.linha`) em qualquer tela |
| desenho em lousa, giz | `estilos-animados/estilos/quadro-negro` |
| pessoa real falando pra câmera | veja "Limites": a estrutura e os gráficos por cima são copiados; a pessoa tem que ser a própria |
| motion de interface: janelas de app, texto digitado, fundo em degradê, sem personagem | nenhuma base pronta: monte com as peças soltas do rig (`rig/RIG.md`: `R.div`, `R.el`, `R.enter`) e GSAP, com `"extras": []` |

Leia o `SKILL.md` da base escolhida (e o `ESTILO.md` do estilo) antes de escrever cena. As cores da paleta e o
jeito do texto que você mediu entram por cima da base.

### 5. Roteiro no mesmo molde

`python3 ferramentas/novo_episodio.py <slug> "Título" --formato <tela do original>` e escreva o `roteiro.txt`:

- **mesmo número de partes**, na mesma ordem e com a mesma função de cada uma;
- **mesmo tamanho:** palavras do roteiro = `fala.palavras_por_seg` x duração do original (margem de 10%);
- **mesmo tipo de gancho**, cabendo no mesmo tempo (`fala.gancho_3s` mostra quantas palavras cabem em 3 s);
- palavras 100% novas, sobre o assunto da pessoa. Nada de frase do original, nem traduzida;
- fecho do mesmo tipo (se o original pede comentário, o novo pede comentário);
- **a estrutura do original ganha da estrutura padrão do kit.** O modelo do `novo_episodio.py` e o
  `agentes/02-roteirista.md` pedem CTA cedo e "comenta aí": só use se o original tiver.

No `episodio.json`:

- `"voz_motor": "gratis"` no rascunho (voz paga só com OK da pessoa);
- `"lead"` = `fala.primeira_palavra_em` do original, e `"cauda"` = duração do original menos `fala.ultima_palavra_em`
  (o modelo vem com cauda 2.0, que estoura a duração);
- a duração só se confirma depois de narrar. Passou de 10%? Corte palavras e rode
  `python3 ferramentas/produzir.py episodios/<slug> --refazer narracao`. Parágrafo novo no roteiro vira pausa.

Original sem fala (`fala.palavras` igual a 0): o vídeo novo também não tem narração; o texto vai na tela, nos
mesmos tempos em que o texto do original aparece.

### 6. Cenas nos mesmos tempos

- Uma cena (`cenas` do `episodio.json`) por parte da estrutura. Dentro de cada cena, **uma mudança de tela pra
  cada item de `mudancas` do original, perto do mesmo segundo**: algo grande entra ou sai, o fundo troca, a câmera
  aproxima. Mexer um detalhe pequeno não conta. Se o original muda a tela 7 vezes a cada 10 s, o novo também.
- **O que a esteira põe sozinha e o original pode não ter.** Desligue no `episodio.json` o que não existir no original:

  | No original | No `episodio.json` |
  |---|---|
  | sem legenda embaixo (o texto é o próprio título) | `"legenda": false` |
  | legenda em outro lugar, tamanho ou cor | `"legenda": {"css": "bottom: 200px; font-size: 48px; color: #111; -webkit-text-stroke: 0; text-shadow: none", "caixa_alta": false, "cor_destaque": "#ff7a1a"}` |
  | imagem limpa, sem cantos escuros nem grão | `"acabamento": false` |
  | sem @ do canal na tela | `"selo": false` |
  | sem aviso de "segue o perfil" no meio | `"banner_em": []` |

  O @ que aparece vem do `config.json` da pessoa. Sem `config.json` sai `@SEUCANAL`: crie o config ou use `"selo": false`.
- Efeitos sonoros (`efeitos`): o kit tem `boom`, `click`, `ding`, `pop`, `swoosh` e `whoosh` (em `efeitos/`). Ponha
  nos mesmos tipos de momento em que o original usa (corte, entrada de texto, virada).
- Trilha: `"trilha": {"modo": "pad", "clima": "esperanca"}` (ou `tensao`, `calmo`, `misterio`) gera acordes na hora,
  grátis. Se a pessoa tiver loops em `trilhas/`, use o modo `biblioteca` (`trilhas/LEIA.md`). Nunca a música do original.
- Títulos no lugar e no tamanho que você anotou no item 7 da ficha. Meça o tamanho pela altura da letra no quadro
  do original em relação à altura da tela, e use a mesma proporção.
- A primeira cena é a mais parecida de todas: é a que a pessoa vai comparar primeiro.

### 7. Produzir e comparar

```bash
python3 ferramentas/produzir.py episodios/<slug> --ate montar
(cd episodios/<slug>/projeto && npx -y hyperframes@0.8.229 snapshot . --at 0.5,3,8,14 --no-end -o ../revisao/snap)   # troque os segundos pelos de `mudancas`; olhe antes de renderizar
python3 ferramentas/produzir.py episodios/<slug>
python3 skills/mimic/scripts/comparar.py referencias/<slug-da-referencia> episodios/<slug>/out/<video>.mp4
```

O `comparar.py` imprime a tabela (duração, planos, plano médio, cortes, mudanças de tela, palavras por segundo) e grava
`referencias/<slug>/comparacao.jpg`: em cima o original, embaixo o seu, nos mesmos 8 momentos. **Abra a folha.**
Pra cada par, confira: o texto está no mesmo lugar e do mesmo tamanho? O fundo tem o mesmo peso de cor? Tem a
mesma quantidade de coisa na tela? O momento é o mesmo tipo de momento (gancho com gancho, fecho com fecho)?

Corrija o que diferir e rode de novo. **No máximo 2 rodadas de correção**; depois disso mostre o vídeo e diga o que
ficou diferente e por quê.

### 8. Guardar o formato

O `formato.md` e o `cenas.js` do episódio viram molde. Quando a pessoa pedir "faz outro nesse formato", pule a
medição: leia `referencias/<slug>/formato.md`, copie o `cenas.js` e o `episodio.json` do episódio anterior e troque
só o roteiro e o conteúdo das cenas.

## Limites (diga antes, não depois)

- **Filmagem real, vídeo gerado por IA e 3D de estúdio caro não são recriados.** Você copia estrutura, ritmo,
  texto na tela e som; a imagem vira a versão do kit mais próxima. Avise no item 12 da ficha.
- **Pessoa falando pra câmera:** o kit não cria a pessoa. Ofereça: (a) a pessoa grava a fala dela e você monta os
  gráficos por cima no mesmo formato (`colagem-explicativa`, modo apresentador), ou (b) versão animada do formato.
- **Fonte:** sai a mais parecida entre as do kit, não a mesma.
- **Movimento muito rápido** (1 a 3 quadros) pode passar entre os quadros das folhas: use o comando de quadros
  seguidos do passo 2 nos cortes e nas entradas de texto.
- **Acabamento:** desfoque de movimento, 3D e interface detalhada de app saem mais simples. O que bate é a
  receita (estrutura, ritmo, lugar das coisas, cores); o polimento depende de quanto tempo se investe nas cenas.
- **Voz grátis** soa robótica: o ritmo da fala bate, o timbre não. Com ElevenLabs fica perto.
- **Cortes medidos pelo ffmpeg** (aparece em `cortes_medidos_com`) são aproximados: confira nas folhas.

## Regras

- Nada do original entra no vídeo novo: nem quadro, nem áudio, nem texto, nem marca.
- Baixe só vídeo público. Sem login, sem senha, sem cookie.
- Narração paga (ElevenLabs) e publicação só com OK da pessoa, como no resto do kit. O rascunho sai com voz grátis.
- Um render por vez. Feche os processos que abrir.
- Sem travessão em nada que aparece na tela.
