cat > server.cpp << 'EOF'
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <grpcpp/grpcpp.h>
#include "file_processor.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReaderWriter;
using grpc::Status;
using file_processor::FileChunk;
using file_processor::FileProcessorService;

std::string agora() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    char buf[20];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", std::localtime(&t));
    return std::string(buf);
}

void log(const std::string& servico, const std::string& arquivo, const std::string& msg, bool ok) {
    std::ofstream logfile("server.log", std::ios::app);
    std::string tipo = ok ? "SUCCESS" : "ERROR";
    if (logfile.is_open()) {
        logfile << "[" << agora() << "] " << tipo << " - Service: " << servico
                << ", File: " << arquivo << ", Message: " << msg << std::endl;
    }
    std::cout << "[" << agora() << "] " << tipo << " - " << servico << " - " << msg << std::endl;
}

class FileProcessorServiceImpl final : public FileProcessorService::Service {
public:
    Status ConvertToTXT(ServerContext* context,
                        ServerReaderWriter<FileChunk, FileChunk>* stream) override {
        std::string input_path = "/tmp/input_pdf.pdf";
        std::string output_path = "/tmp/output_txt.txt";

        std::ofstream input_file(input_path, std::ios::binary);
        if (!input_file) {
            log("ConvertToTXT", "", "Falha ao criar arquivo temporario", false);
            return Status(grpc::StatusCode::INTERNAL, "Erro interno");
        }

        FileChunk chunk;
        while (stream->Read(&chunk)) {
            input_file.write(chunk.content().data(), chunk.content().size());
        }
        input_file.close();

        std::string cmd = "pdftotext " + input_path + " " + output_path + " 2>/dev/null";
        int ret = system(cmd.c_str());
        if (ret != 0) {
            log("ConvertToTXT", input_path, "Falha no comando pdftotext", false);
            return Status(grpc::StatusCode::INTERNAL, "Conversao falhou");
        }

        std::ifstream output_file(output_path, std::ios::binary);
        if (!output_file) {
            log("ConvertToTXT", input_path, "Arquivo TXT nao gerado", false);
            return Status(grpc::StatusCode::INTERNAL, "Arquivo de saida ausente");
        }

        char buffer[1024];
        while (output_file.read(buffer, sizeof(buffer)) || output_file.gcount() > 0) {
            FileChunk out_chunk;
            out_chunk.set_content(buffer, output_file.gcount());
            if (!stream->Write(out_chunk)) break;
        }
        output_file.close();

        std::remove(input_path.c_str());
        std::remove(output_path.c_str());

        log("ConvertToTXT", input_path, "Conversao realizada", true);
        return Status::OK;
    }

    Status ConvertImageFormat(ServerContext* context,
                              ServerReaderWriter<FileChunk, FileChunk>* stream) override {
        std::string input_path = "/tmp/input_img";
        std::string output_format = "png";
        std::string output_path = "/tmp/output_img." + output_format;

        std::ofstream input_file(input_path, std::ios::binary);
        if (!input_file) {
            log("ConvertImageFormat", "", "Falha ao criar arquivo", false);
            return Status(grpc::StatusCode::INTERNAL, "Erro interno");
        }

        FileChunk chunk;
        while (stream->Read(&chunk)) {
            input_file.write(chunk.content().data(), chunk.content().size());
        }
        input_file.close();

        std::string cmd = "convert " + input_path + " " + output_path + " 2>/dev/null";
        int ret = system(cmd.c_str());
        if (ret != 0) {
            log("ConvertImageFormat", input_path, "Falha no convert", false);
            return Status(grpc::StatusCode::INTERNAL, "Conversao falhou");
        }

        std::ifstream output_file(output_path, std::ios::binary);
        if (!output_file) {
            log("ConvertImageFormat", input_path, "Arquivo convertido nao encontrado", false);
            return Status(grpc::StatusCode::INTERNAL, "Arquivo de saida ausente");
        }

        char buffer[1024];
        while (output_file.read(buffer, sizeof(buffer)) || output_file.gcount() > 0) {
            FileChunk out_chunk;
            out_chunk.set_content(buffer, output_file.gcount());
            if (!stream->Write(out_chunk)) break;
        }
        output_file.close();

        std::remove(input_path.c_str());
        std::remove(output_path.c_str());

        log("ConvertImageFormat", input_path, "Conversao concluida", true);
        return Status::OK;
    }

    Status ResizeImage(ServerContext* context,
                       ServerReaderWriter<FileChunk, FileChunk>* stream) override {
        std::string input_path = "/tmp/input_resize.jpg";
        std::string output_path = "/tmp/output_resize.jpg";
        int width = 800, height = 600;

        std::ofstream input_file(input_path, std::ios::binary);
        if (!input_file) {
            log("ResizeImage", "", "Falha ao criar arquivo", false);
            return Status(grpc::StatusCode::INTERNAL, "Erro interno");
        }

        FileChunk chunk;
        while (stream->Read(&chunk)) {
            input_file.write(chunk.content().data(), chunk.content().size());
        }
        input_file.close();

        std::string cmd = "convert " + input_path + " -resize " + std::to_string(width) + "x" + std::to_string(height) + " " + output_path + " 2>/dev/null";
        int ret = system(cmd.c_str());
        if (ret != 0) {
            log("ResizeImage", input_path, "Falha no redimensionamento", false);
            return Status(grpc::StatusCode::INTERNAL, "Resize falhou");
        }

        std::ifstream output_file(output_path, std::ios::binary);
        if (!output_file) {
            log("ResizeImage", input_path, "Arquivo redimensionado nao encontrado", false);
            return Status(grpc::StatusCode::INTERNAL, "Arquivo de saida ausente");
        }

        char buffer[1024];
        while (output_file.read(buffer, sizeof(buffer)) || output_file.gcount() > 0) {
            FileChunk out_chunk;
            out_chunk.set_content(buffer, output_file.gcount());
            if (!stream->Write(out_chunk)) break;
        }
        output_file.close();

        std::remove(input_path.c_str());
        std::remove(output_path.c_str());

        log("ResizeImage", input_path, "Redimensionamento concluido", true);
        return Status::OK;
    }
};

void RunServer() {
    std::string addr("0.0.0.0:50051");
    FileProcessorServiceImpl service;
    ServerBuilder builder;
    builder.AddListeningPort(addr, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Servidor rodando em " << addr << std::endl;
    server->Wait();
}

int main() {
    RunServer();
    return 0;
}
