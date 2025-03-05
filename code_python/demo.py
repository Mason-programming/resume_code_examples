"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""




#-----------------------------------------
import os
import re
import logging

from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def gather_mesh_and_ptex_paths(usd_stage_path):
    """
    Gathers selected meshes from a USD Stage and finds corresponding ptex files.
    If a ptex file is not found, assigns a grey material.
    """
    logging.info("Processing USD stage: %s", usd_stage_path)

    pattern = r"[0-9]"
    mesh_and_ptex_paths = {}

    # Open USD stage
    stage = Usd.Stage.Open(usd_stage_path)
    if not stage:
        logging.error("Failed to open USD stage.")
        return {}

    # Get all mesh prims that end with "_geo"
    mesh_prims = [
        prim for prim in stage.Traverse() if prim.IsA(UsdGeom.Mesh) and prim.GetName().endswith("_geo")
    ]

    if not mesh_prims:
        logging.warning("No valid meshes found in the USD scene.")
        return {}

    for mesh_prim in mesh_prims:
        mesh_name = mesh_prim.GetName()
        element_name = re.sub(pattern, "", mesh_name)  # Remove numbers
        ptex_path = f"/textures/{element_name}/{mesh_name}.ptx"  # Example ptex path logic

        if os.path.exists(ptex_path):
            mesh_and_ptex_paths[mesh_name] = ptex_path
        else:
            logging.warning(f"Ptex not found for {mesh_name}. Assigning grey material.")
            assign_grey_material(stage, mesh_prim)

    return mesh_and_ptex_paths


def assign_grey_material(stage, mesh_prim):
    """
    Assigns a grey USD Lambert-like material to a mesh prim.
    """
    material_path = f"/Materials/{mesh_prim.GetName()}_greyMat"
    material = UsdShade.Material.Define(stage, material_path)
    shader = UsdShade.Shader.Define(stage, material_path + "/Shader")

    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.5, 0.5, 0.5))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)

    material.CreateSurfaceOutput("mdl").ConnectToSource(shader, "outputs:surface")

    UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)


def process_ptex_data(mesh_data):
    """
    Process ptex data for selected meshes and extracts color values.
    """
    rgb_values = {}
    for mesh, ptex_path in mesh_data.items():
        color_value = extract_ptex_color(ptex_path)
        converted_color = convert_pixel_to_display_color(color_value)

        if converted_color not in rgb_values:
            rgb_values[converted_color] = [mesh]
        else:
            rgb_values[converted_color].append(mesh)

    return rgb_values


def extract_ptex_color(ptex_path):
    """
    Simulated ptex color extraction. Returns a solid color (0.8, 0.6, 0.4) for now.
    """
    return (0.8, 0.6, 0.4)  # Placeholder color


def convert_pixel_to_display_color(pixel_value):
    """
    Converts pixel value to display color.
    """
    gamma = 2.2
    converted_pixel = [pow(channel / 255.0, gamma) for channel in pixel_value]
    return tuple(converted_pixel)


def create_lambert_shader(stage, shader_name, rgb_values):
    """
    Creates USD Lambert shaders based on RGB values and assigns them.
    """
    for rgb_tuple, mesh_names in rgb_values.items():
        material_path = f"/Materials/{shader_name}"
        material = UsdShade.Material.Define(stage, material_path)
        shader = UsdShade.Shader.Define(stage, material_path + "/Shader")

        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*rgb_tuple))
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)

        material.CreateSurfaceOutput("mdl").ConnectToSource(shader, "outputs:surface")

        for mesh_name in mesh_names:
            mesh_prim = stage.GetPrimAtPath(f"/Meshes/{mesh_name}")
            if mesh_prim:
                UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)

#-----------------------        