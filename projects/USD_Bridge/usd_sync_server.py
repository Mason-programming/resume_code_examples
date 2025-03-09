import grpc
import time
import usd_sync_pb2
import usd_sync_pb2_grpc
from concurrent import futures

class USDServer(usd_sync_pb2_grpc.USDSyncServicer):
    def __init__(self):
        self.clients = []

    def SendUSDUpdate(self, request, context):
        """ Receives a USD file update and notifies all connected clients """
        print(f"📡 Received USD update: {request.usd_file_path}")
        for client in self.clients:
            client.write(usd_sync_pb2.USDUpdateResponse(message=f"USD Updated: {request.usd_file_path}"))
        return usd_sync_pb2.USDUpdateResponse(message="USD update received.")

    def WatchUSDUpdates(self, request, context):
        """ Clients subscribe for USD updates """
        self.clients.append(context)
        try:
            while True:
                time.sleep(1)  # Keep connection alive
        except:
            self.clients.remove(context)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    usd_sync_pb2_grpc.add_USDSyncServicer_to_server(USDServer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🚀 USD Sync Server is running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
