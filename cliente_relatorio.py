import requests

id_produto = input("Digite o ID do produto: ")

url_flask = f"http://localhost:5000/detalhes/{id_produto}"
url_node = f"http://localhost:3000/estoque/{id_produto}"

try:

    resposta_fiscal = requests.get(url_flask)
    resposta_estoque = requests.get(url_node)

    dados_fiscais = resposta_fiscal.json()
    dados_estoque = resposta_estoque.json()

    produto_completo = {
        "id": id_produto,
        "nome": dados_estoque["nome"],
        "preco": dados_fiscais["preco"],
        "estoque": dados_estoque["estoque"]
    }

    print("\nRELATORIO")
    print(
        f'ID: {produto_completo["id"]} | '
        f'Nome: {produto_completo["nome"]} | '
        f'Preco: R$ {produto_completo["preco"]} | '
        f'Estoque: {produto_completo["estoque"]}'
    )

except:
    print("Erro ao conectar aos servidores")