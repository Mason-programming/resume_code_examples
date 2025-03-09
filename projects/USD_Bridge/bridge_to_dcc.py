import os 
import sys 
import bpy
# Determine the absolute path to the 'modules' directory
modules_path = os.path.join(os.path.dirname(__file__), 'modules')
c_path = os.path.join(modules_path, "grpc","_cython") 
sys.path.append(modules_path)
sys.path.append(c_path)
#from concurrent import futures
class BlenderUSDService:

    def __init__(self, usd_file, source): 
        self.usd_file = usd_file 
        self.source = source 
        self.get_current(self.source)

    def SendUSDUpdate(self, request, context):
        """Loads the updated USD file inside Blender"""
        usd_file = request.usd_file_path
        print(f"📥 Blender received USD update: {usd_file}")
        bpy.ops.wm.usd_import(filepath=usd_file)  # Load USD in Blender

    def is_usd_loaded(self): 

        # Determine 
        for obj in bpy.data.objects: 
            for modifier in obj.odifiers: 
                if modifer.type == "MESH_SEQUENCE_CACHE" and modifier.cache_file: 
                    cache_file_path = bpy.path.abspath(modifier.cache_file.filepath)
                    if cache_file_path.lower().endswith('.usd'):
                        print(f"USD file loaded: {cache_file_path}")
                        return True
        return False 
    
    def get_current(self, source): 
        
        if is_usd_loaded(): 
            pass 

        else: 
            bpy.ops.wm.usd_import(filepath=usd_file)  # Load USD in Blender


    def conform_animation(self): 
        pass 

if __name__ == "__main__":
    serve()


