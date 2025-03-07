import grpc
import time
import redis
import usd_sync_pb2
import usd_sync_pb2_grpc
from concurrent import futures

# Redis setup for Pub/Sub
redis_client = redis.Redis(host="localhost", port=6379, db=0)

class USDMiddlewareServer(usd_middleware_pb2_grpc.USDMiddlewareServicer):
    def SendUSDUpdate(self, request, context):
        """Receives USD file updates and notifies all subscribers"""
        print(f"📡 Received USD update from {request.dcc_name}: {request.usd_file_path}")

        # Publish update to Redis
        redis_client.publish("usd_updates", request.usd_file_path)

        return usd_middleware_pb2.USDUpdateResponse(message="USD update sent.")

    def SubscribeToUSDUpdates(self, request, context):
        """Allows DCCs to subscribe for updates"""
        pubsub = redis_client.pubsub()
        pubsub.subscribe("usd_updates")

        print(f"👀 {request.dcc_name} is watching for USD updates...")

        for message in pubsub.listen():
            if message["type"] == "message":
                usd_file = message["data"].decode("utf-8")
                print(f"🔄 Sending USD update to {request.dcc_name}: {usd_file}")
                yield usd_middleware_pb2.USDUpdateResponse(message=f"USD Updated: {usd_file}")

# Run the server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    usd_middleware_pb2_grpc.add_USDMiddlewareServicer_to_server(USDMiddlewareServer(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("🚀 USD Middleware Server Running on port 50052...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
