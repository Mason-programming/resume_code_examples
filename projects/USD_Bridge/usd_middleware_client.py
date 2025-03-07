import grpc
import usd_middleware_pb2
import usd_middleware_pb2_grpc
import bpy  # For Blender (Modify for other DCCs)

class USDClient:
    def __init__(self, dcc_name):
        self.channel = grpc.insecure_channel("localhost:50052")
        self.stub = usd_middleware_pb2_grpc.USDMiddlewareStub(self.channel)
        self.dcc_name = dcc_name

    def send_usd_update(self, usd_file):
        """Sends USD file updates to middleware"""
        response = self.stub.SendUSDUpdate(
            usd_middleware_pb2.USDUpdateRequest(usd_file_path=usd_file, dcc_name=self.dcc_name)
        )
        print(response.message)

    def watch_for_updates(self):
        """Listens for USD updates"""
        print(f"👀 {self.dcc_name} is watching for USD updates...")
        for update in self.stub.SubscribeToUSDUpdates(usd_middleware_pb2.WatchRequest(dcc_name=self.dcc_name)):
            usd_file = update.message.replace("USD Updated: ", "")
            print(f"📥 {self.dcc_name} received USD update: {usd_file}")
            self.reload_usd(usd_file)

    def reload_usd(self, usd_file):
        """ Reloads USD file in Blender """
        bpy.ops.wm.usd_import(filepath=usd_file)
        print(f"✅ Reloaded USD in Blender: {usd_file}")

if __name__ == "__main__":
    client = USDClient("Blender")
    client.watch_for_updates()
