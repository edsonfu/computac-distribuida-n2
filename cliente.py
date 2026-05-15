import grpc
import file_processor_pb2
import file_processor_pb2_grpc
import os
import requests
def enviar_arquivo(stub, metodo, input_path, output_path):
    """Envia arquivo para um metodo streaming e salva resposta"""
    def chunk_generator():
        with open(input_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                yield file_processor_pb2.FileChunk(content=data)
    
    response_stream = metodo(chunk_generator())
    with open(output_path, "wb") as out_f:
        for chunk in response_stream:
            out_f.write(chunk.content)

def main():
    print("==== Cliente Integrado (Entrega 1 e 2) ====")
    print("Escolha o servico:")
    print("1 - Comprimir PDF (gs)")
    print("2 - Converter PDF para TXT")
    print("3 - Converter formato de imagem (para PNG)")
    print("4 - Redimensionar imagem (800x600)")
    opcao = input("Opcao (1/2/3/4): ").strip()
    
    if opcao not in ['1','2','3','4']:
        print("Opcao invalida")
        return

    entrada = input("Caminho do arquivo de entrada: ").strip()
    if not os.path.exists(entrada):
        print("Arquivo nao encontrado")
        return

    # Define nome de saida padrao
    base, ext = os.path.splitext(entrada)
    if opcao == '1':
        saida = input("Caminho do PDF comprimido (Enter para padrao): ").strip()
        if not saida:
            saida = f"{base}_comprimido.pdf"
        metodo = "CompressPDF"
    elif opcao == '2':
        saida = input("Caminho do TXT de saida (Enter para padrao): ").strip()
        if not saida:
            saida = f"{base}.txt"
        metodo = "ConvertToTXT"
    elif opcao == '3':
        saida = input("Caminho da imagem PNG (Enter para padrao): ").strip()
        if not saida:
            saida = f"{base}_convertido.png"
        metodo = "ConvertImageFormat"
    else:
        saida = input("Caminho da imagem redimensionada (Enter para padrao): ").strip()
        if not saida:
            saida = f"{base}_redimensionado.jpg"
        metodo = "ResizeImage"

    channel = grpc.insecure_channel("localhost:50051")
    stub = file_processor_pb2_grpc.FileProcessorServiceStub(channel)

    metodo_map = {
        '1': stub.CompressPDF,
        '2': stub.ConvertToTXT,
        '3': stub.ConvertImageFormat,
        '4': stub.ResizeImage
    }

    print(f"Enviando {entrada} para {metodo}...")
    try:
        enviar_arquivo(stub, metodo_map[opcao], entrada, saida)
        print(f"Arquivo processado salvo em: {saida}")
    except grpc.RpcError as e:
        print(f"Erro RPC: {e.details()}")
    except Exception as e:
        print(f"Erro: {e}")

  
# No Codespaces, enquanto você testa localmente no terminal:
url_flask = "http://localhost:5000/api/data"
url_node = "http://localhost:3000/api/data"
def consumir_api(nome, url):
 try:
 response = requests.get(url)
 dados = response.json()
 print(f"--- Resposta do {nome} ---")
 print(f"Mensagem: {dados['mensagem']}")
 print(f"Tecnologia: {dados['tecnologia']}\n")
 except Exception as e:
 print(f"Erro ao conectar no {nome}: Servidor está rodando?")
if __name__ == "__main__":
 consumir_api("Flask", url_flask)
 consumir_api("Node", url_node)

if __name__ == "__main__":
    main()
