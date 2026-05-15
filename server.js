const express = require('express');
const axios = require('axios');

const app = express();

const produtos_estoque = {

    "1": {
        "nome": "Dell XPS 13",
        "estoque": 10
    },

    "2": {
        "nome": "Monitor LG 29",
        "estoque": 5
    }
};

app.get('/estoque/:id', (req, res) => {

    const id = req.params.id;

    if (produtos_estoque[id]) {
        return res.json(produtos_estoque[id]);
    }

    res.status(404).json({
        erro: "Produto nao encontrado"
    });
});


app.get('/api/full-info/:id', async (req, res) => {

    const id = req.params.id;

    try {

        const dadosNode = produtos_estoque[id];

        if (!dadosNode) {
            return res.status(404).json({
                erro: "Produto nao encontrado"
            });
        }

        const respostaFlask = await axios.get(
            `http://localhost:5000/detalhes/${id}`
        );

        const dadosFlask = respostaFlask.data;

        const produtoCompleto = {
            id: id,
            nome: dadosNode.nome,
            estoque: dadosNode.estoque,
            preco: dadosFlask.preco,
            categoria: dadosFlask.categoria
        };

        res.json(produtoCompleto);

    } catch (erro) {

        res.status(500).json({
            erro: "Erro ao conectar com Flask"
        });
    }
});

app.listen(3000, () => {
    console.log("Servidor Node rodando na porta 3000");
});