import os 
import subprocess 
import sys
import shutil
import psutil
from pxr import Usd 


class dcc_bridge: 

    def __init__(self): 

        self.avaible_dccs = [] 
        self.usd_file = "" 
    
    
    def detection(self): 
        pass 

    def find_path_of_dccs(self): 
    
        """
        Dynamically finds the Blender executable path.
        Works for Windows, macOS, and Linux.
        """
        blender_exe = "blender"
        
        # Check common installation paths
        common_paths = {
            "Windows": [
                "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe",
                "C:/Program Files/Blender Foundation/Blender 3.6/blender.exe",
                "C:/Program Files/Blender Foundation/Blender 3.5/blender.exe",
                "C:/Program Files/Blender Foundation/Blender/blender.exe"
            ],
            "Darwin": ["/Applications/Blender.app/Contents/MacOS/Blender"],
            "Linux": ["/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender"]
        }

        platform = sys.platform

        if platform.startswith("win"):

            for path in common_paths["Windows"]:
                if os.path.exists(path):
                    return path

            return shutil.which("blender")  # Try finding it in system PATH
        elif platform.startswith("darwin"):

            return common_paths["Darwin"][0] if os.path.exists(common_paths["Darwin"][0]) else shutil.which("blender")

        elif platform.startswith("linux"):
            return next((path for path in common_paths["Linux"] if os.path.exists(path)), shutil.which("blender"))
        
        return None


    
    def blender_support(self, usd_file=""): 

        blender_path = self.find_path() 

        # Launch Blender and run the USD-enabling script inside it
        subprocess.Popen([blender_path, "--python-expr", 
            f"import os; import bpy; os.environ['BLENDER_USE_USD'] = '1'; bpy.ops.preferences.addon_enable(module='{self.usd_file}'); bpy.ops.wm.save_userpref()"])

        self.avaible_dccs.extend("blender")

    
    def load_stage(self, stage): 

        pass 



test = dcc_bridge() 

test.blender_support("")