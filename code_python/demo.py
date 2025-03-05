"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""





#-----------------------------------------
"""
Convert shaders to Lambert shaders 
"""
import os
import re
import logging

import maya.cmds as cmds
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def gather_mesh_and_ptex_paths(usd_stage_path):
    """
    Gathers selected meshes in Maya and their corresponding ptex files.
    Uses USD to extract mesh names and find ptex paths.
    If a ptex file is not found, assigns a grey Lambert material.
    """
    logging.info("Processing USD Stage: %s", usd_stage_path)

    pattern = r"[0-9]"
    mesh_and_ptex_paths = {}

    # Load the USD Stage
    stage = Usd.Stage.Open(usd_stage_path)
    if not stage:
        logging.error("Failed to open USD stage.")
        return {}

    # Get selected Maya meshes
    selected_meshes = [mesh for mesh in cmds.ls(sl=True, dag=True) or [] if mesh.endswith("_geo")]

    if not selected_meshes:
        logging.warning("No valid geometry selected in Maya.")
        return {}

    for selected_mesh in selected_meshes:
        mesh_prim = stage.GetPrimAtPath(f"/Meshes/{selected_mesh}")
        if not mesh_prim or not mesh_prim.IsA(UsdGeom.Mesh):
            logging.warning(f"Mesh {selected_mesh} not found in USD stage.")
            continue

        # Remove numerical suffix
        element_name = re.sub(pattern, "", selected_mesh)

        # Construct PTex path
        ptex_path = f"/textures/{element_name}/{selected_mesh}.ptx"

        if os.path.exists(ptex_path):
            mesh_and_ptex_paths[selected_mesh] = ptex_path
        else:
            logging.warning(f"Ptex not found for {selected_mesh}. Assigning grey Lambert.")
            create_grey_lambert_shader(selected_mesh)

    return mesh_and_ptex_paths


def create_grey_lambert_shader(mesh_name):
    """
    Creates and assigns a grey Lambert shader in Maya.
    """
    shader_name = f"{mesh_name}_grey_lambert"
    lambert_shader = cmds.shadingNode("lambert", name=shader_name, asShader=True)
    shader_group = cmds.sets(name=f"{shader_name}SG", renderable=True, empty=True, noSurfaceShader=True)

    cmds.connectAttr(f"{lambert_shader}.outColor", f"{shader_group}.surfaceShader")
    cmds.setAttr(f"{lambert_shader}.color", 0.5, 0.5, 0.5, type="double3")
    cmds.sets(mesh_name, forceElement=shader_group)


def process_ptex_data(mesh_data):
    """
    Processes PTex data and assigns materials based on extracted colors.
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
    Simulates PTex color extraction. (Placeholder value for now).
    """
    return (0.8, 0.6, 0.4)  # Simulated solid color


def convert_pixel_to_display_color(pixel_value):
    """
    Converts a PTex pixel value to display color using gamma correction.
    """
    gamma = 2.2
    return tuple(pow(channel / 255.0, gamma) for channel in pixel_value)


def create_lambert_shader(shader_name, rgb_values):
    """
    Creates and assigns Lambert shaders based on extracted PTex colors.
    """
    for rgb_tuple, meshes in rgb_values.items():
        color_values = list(rgb_tuple)
        cmds.select(meshes, r=True)

        # Create Lambert Shader
        lambert_shader = cmds.shadingNode("lambert", name=shader_name, asShader=True)
        shader_group = cmds.sets(name=f"{shader_name}SG", renderable=True, empty=True, noSurfaceShader=True)

        cmds.connectAttr(f"{lambert_shader}.outColor", f"{shader_group}.surfaceShader")
        cmds.setAttr(f"{lambert_shader}.color", color_values[0], color_values[1], color_values[2], type="double3")
        cmds.sets(meshes, forceElement=shader_group)

#-----------------------        