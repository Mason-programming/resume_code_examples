#pragma once
#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <vector>
#include <grpcpp/grpcpp.h>
#include "usd_sync.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReaderWriter;
using grpc::Status;
using usd_sync::USDSync;
using usd_sync::USDUpdateRequest;
using usd_sync::USDUpdateResponse;
using usd_sync::WatchRequest;

class USDSyncServiceImpl final : public USDSync::Serice
{ 

    public: 

        Status SendUSDUpdate(ServerContext* context, const USDUpdateRequest* request,
                         USDUpdateResponse* response) override {

        std::lock_guard<std::mutex> lock(mutex_);
        std::string message = "USD Updated: " + request->usd_file_path();
        std::cout << "📡 Received USD update: " << request->usd_file_path() << std::endl;


        // Notify all connected clients
        for (auto& stream : clients_) {
            stream->Write(USDUpdateResponse{message});
        }

        response->set_message("USD update received.");
        return Status::OK;
        }



}
