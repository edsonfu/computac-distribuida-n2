import grpc
import file_processor_pb2
import file_processor_pb2_grpc
import subprocess
import os
import time
from concurrent import futures

def log(service, filename, msg, success):
    with open("server.log", "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "ERROR"
        f.write(f"[{timestamp}] {status} - Service: {service}, File: {filename}, Message: {msg}\n")
    print(f"[{timestamp}] {status} - {service} - {msg}")

class FileProcessorServicer(file_processor_pb2_grpc.FileProcessorServiceServicer):

    def CompressPDF(self, request_iterator, context):
        input_path = "/tmp/input.pdf"
        output_path = "/tmp/output_compressed.pdf"

        with open(input_path, "wb") as f:
            for chunk in request_iterator:
                f.write(chunk.content)

        cmd = f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile={output_path} {input_path} 2>/dev/null"
        ret = subprocess.call(cmd, shell=True)

        if ret != 0 or not os.path.exists(output_path):
            log("CompressPDF", input_path, "Falha na compressao", False)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Erro ao comprimir PDF")
            return

        with open(output_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                yield file_processor_pb2.FileChunk(content=data)

        os.remove(input_path)
        os.remove(output_path)
        log("CompressPDF", input_path, "Compressao concluida", True)

    def ConvertToTXT(self, request_iterator, context):
        input_path = "/tmp/input_pdf.pdf"
        output_path = "/tmp/output_txt.txt"

        with open(input_path, "wb") as f:
            for chunk in request_iterator:
                f.write(chunk.content)

        cmd = f"pdftotext {input_path} {output_path} 2>/dev/null"
        ret = subprocess.call(cmd, shell=True)

        if ret != 0 or not os.path.exists(output_path):
            log("ConvertToTXT", input_path, "Falha na conversao", False)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Erro ao converter PDF")
            return

        with open(output_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                yield file_processor_pb2.FileChunk(content=data)

        os.remove(input_path)
        os.remove(output_path)
        log("ConvertToTXT", input_path, "Conversao concluida", True)

    def ConvertImageFormat(self, request_iterator, context):
        input_path = "/tmp/input_img"
        output_path = "/tmp/output_img.png"

        with open(input_path, "wb") as f:
            for chunk in request_iterator:
                f.write(chunk.content)

        cmd = f"convert {input_path} {output_path} 2>/dev/null"
        ret = subprocess.call(cmd, shell=True)

        if ret != 0 or not os.path.exists(output_path):
            log("ConvertImageFormat", input_path, "Falha na conversao", False)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Erro ao converter formato")
            return

        with open(output_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                yield file_processor_pb2.FileChunk(content=data)

        os.remove(input_path)
        os.remove(output_path)
        log("ConvertImageFormat", input_path, "Conversao de formato concluida", True)

    def ResizeImage(self, request_iterator, context):
        input_path = "/tmp/input_resize.jpg"
        output_path = "/tmp/output_resize.jpg"
        width, height = 800, 600

        with open(input_path, "wb") as f:
            for chunk in request_iterator:
                f.write(chunk.content)

        cmd = f"convert {input_path} -resize {width}x{height} {output_path} 2>/dev/null"
        ret = subprocess.call(cmd, shell=True)

        if ret != 0 or not os.path.exists(output_path):
            log("ResizeImage", input_path, "Falha no redimensionamento", False)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Erro ao redimensionar")
            return

        with open(output_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                yield file_processor_pb2.FileChunk(content=data)

        os.remove(input_path)
        os.remove(output_path)
        log("ResizeImage", input_path, "Redimensionamento concluido", True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_processor_pb2_grpc.add_FileProcessorServiceServicer_to_server(FileProcessorServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor integrado (Entrega 1 e 2) rodando na porta 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
