from flask import Flask, jsonify

app = Flask(__name__)

produtos_fiscais = {
    "1": {
        "preco": 2500.0,
        "categoria": "Laptops"
    },
    "2": {
        "preco": 1200.0,
        "categoria": "Monitores"
    }
}

@app.route('/detalhes/<id>', methods=['GET'])
def detalhes(id):
    if id in produtos_fiscais:
        return jsonify(produtos_fiscais[id])

    return jsonify({"erro": "Produto nao encontrado"}), 404

app.run(host='0.0.0.0', port=5000, debug=True)