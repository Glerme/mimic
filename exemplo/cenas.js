//@comum
      // Ranking em contagem regressiva (16:9), estilo vetorial + LONGO.ranking. O cenário muda a cada posição
      // e a lista vai empilhando à direita: quem chegou atrasado entende onde o vídeo está.
      const GUIA = { pele: "#8d5a3b", roupa: "#2f9e6b", calca: "#2c3548", cabelo: "curto", corCabelo: "#1c1410" };
      const ITENS = [["3", "Guepardo", "110 km/h em terra"], ["2", "Águia-real", "300 km/h no mergulho"], ["1", "Falcão-peregrino", "389 km/h no mergulho"]];
      // a lista até a posição "ate": as anteriores já aparecem no quadro 0 da cena, a nova entra no tempo t
      function lista(ate, t) { return LONGO.ranking(S, tl, { itens: ITENS.slice(0, ate + 1).map((x, i) => [i < ate ? 0 : t].concat(x)) }); }
      function guia(L) {
        const q = ESTILO.pessoa(L.act, Object.assign({ x: 480, y: 960, s: 1.4 }, GUIA));
        q.vivo(tl, 0, D, 5); q.fala(tl, S, 0, D - 0.1); q.atua(tl, 0, { humor: "feliz", bracos: "mostra", virar: 0.6 });
        return q;
      }

//@cena s01
      // Gancho: a promessa do ranking e a provocação do primeiro lugar.
      const L = ESTILO.cena(S, tl, D, { fundo: "estudio" });
      const q = guia(L);
      ESTILO.titulo(S, 1240, 330, "Os 3 animais mais rápidos", { fundo: "#ffd34d", tamanho: 84, rot: -2, caixa: false, sub: "do mundo", tamSub: 44 });
      const p = ESTILO.titulo(S, 1240, 600, "O campeão não é quem você pensa", { fundo: "#d8433a", cor: "#ffffff", tamanho: 46, rot: 1.5, caixa: false });
      ESTILO.entra(tl, p, S.at("E o campeão"));
      q.atua(tl, S.at("E o campeão"), { humor: "surpreso", bracos: "apontaCima", virar: 0.6 });

//@cena s02
      const L = ESTILO.cena(S, tl, D, { fundo: "dia", nuvens: true });
      const q = guia(L);
      R.enter(tl, S);
      ESTILO.titulo(S, 480, 200, "O mais veloz em terra", { fundo: "#e8702a", cor: "#ffffff", tamanho: 50, rot: -2, caixa: false });
      lista(0, S.at("guepardo") - 0.05);
      q.atua(tl, S.at("guepardo"), { humor: "alegre", bracos: "aponta", virar: 0.7 });

//@cena s03
      const L = ESTILO.cena(S, tl, D, { fundo: "tarde" });
      const q = guia(L);
      R.enter(tl, S);
      const d = ESTILO.titulo(S, 480, 200, "Ela mergulha do alto", { fundo: "#3cc4d6", tamanho: 50, rot: -2, caixa: false });
      ESTILO.entra(tl, d, S.at("Ela não"));
      lista(1, S.at("águia-real") - 0.05);
      q.atua(tl, S.at("Ela não"), { humor: "pensativo", bracos: "ombros", virar: 0.5 });

//@cena s04
      const L = ESTILO.cena(S, tl, D, { fundo: "noite", estrelas: true });
      const q = guia(L);
      R.enter(tl, S);
      lista(2, S.at("falcão-peregrino") - 0.05);
      q.atua(tl, S.at("falcão-peregrino"), { humor: "surpreso", bracos: "comemora", virar: 0.6, pula: 1 });
      const b = ESTILO.titulo(S, 480, 200, "O mais rápido voa", { fundo: "#f4f1ea", tamanho: 50, rot: -2, caixa: false });
      ESTILO.entra(tl, b, S.at("voa") - 0.3);
      ESTILO.confete(tl, D, L.fg, S.at("voa"), { n: 70 });
