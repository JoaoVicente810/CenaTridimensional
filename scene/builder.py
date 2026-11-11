"""Monta o pátio, o carrinho, o boneco e a carga transportada."""
from __future__ import annotations

import os

import numpy as np

from engine import Group, Mesh, Scene, Texture
from geometry import box_geometry, cylinder_z_geometry, sphere_geometry


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def add_mesh(parent, name, geometry, color, position=(0, 0, 0), scale=(1, 1, 1),
             rotation=(0, 0, 0), texture=None, casts_shadow=True):
    mesh = Mesh(name, geometry, color, texture, casts_shadow)
    mesh.position = np.asarray(position, dtype=np.float32)
    mesh.scale = np.asarray(scale, dtype=np.float32)
    mesh.rotation = np.asarray(rotation, dtype=np.float32)
    parent.add(mesh)
    return mesh


def make_scene():
    scene = Scene()
    box = box_geometry()
    wheel_geo = cylinder_z_geometry(28)
    sphere = sphere_geometry(14, 20)
    floor_texture = Texture(os.path.join(PROJECT_DIR, "assets", "textures", "asphalt.png"))

    add_mesh(scene, "piso-texturizado", box, (1, 1, 1), (0, -0.16, 0),
             (20, 0.32, 14), texture=floor_texture, casts_shadow=False)
    add_mesh(scene, "plataforma-de-entrega", box, (0.20, 0.25, 0.29),
             (6.8, 0.22, -2.45), (2.0, 0.44, 1.45))
    add_mesh(scene, "tampo-plataforma", box, (0.55, 0.58, 0.58),
             (6.8, 0.47, -2.45), (2.0, 0.08, 1.45))

    cart = Group("carrinho-de-carga")
    scene.add(cart)
    dark = (0.075, 0.095, 0.12)
    blue = (0.12, 0.36, 0.72)
    add_mesh(cart, "chassi", box, dark, (0, 0.62, 0), (2.25, 0.28, 0.98))
    add_mesh(cart, "carroceria-inferior", box, blue, (-0.28, 0.89, 0), (1.35, 0.46, 1.08))
    add_mesh(cart, "caixa-carga-frontal", box, (0.16, 0.43, 0.76),
             (-0.30, 1.18, 0), (1.26, 0.12, 1.0))
    add_mesh(cart, "cabine", box, (0.10, 0.31, 0.62), (0.67, 1.28, 0), (0.86, 0.94, 0.92))
    add_mesh(cart, "para-brisa", box, (0.10, 0.18, 0.23),
             (0.68, 1.47, 0.468), (0.56, 0.48, 0.026))
    add_mesh(cart, "janela-traseira", box, (0.10, 0.18, 0.23),
             (0.20, 1.47, -0.468), (0.20, 0.48, 0.026))
    add_mesh(cart, "teto-cabine", box, (0.07, 0.25, 0.52),
             (0.66, 1.78, 0), (0.94, 0.14, 1.02))
    add_mesh(cart, "para-choque-frontal", box, (0.68, 0.72, 0.72),
             (1.18, 0.58, 0), (0.18, 0.22, 1.12))
    add_mesh(cart, "para-choque-traseiro", box, (0.68, 0.72, 0.72),
             (-1.15, 0.58, 0), (0.18, 0.22, 1.12))
    for z in (-0.42, 0.42):
        add_mesh(cart, "farol", sphere, (1.0, 0.86, 0.48), (1.13, 0.88, z), (0.16, 0.14, 0.10))
        add_mesh(cart, "lanterna-traseira", box, (0.86, 0.12, 0.07),
                 (-1.18, 0.78, z), (0.07, 0.18, 0.16))

    wheels = []
    for x in (-0.72, 0.78):
        for z in (-0.57, 0.57):
            tire = add_mesh(cart, "roda", wheel_geo, (0.035, 0.04, 0.045),
                            (x, 0.36, z), (0.76, 0.76, 0.22))
            hub = add_mesh(cart, "cubo-roda", wheel_geo, (0.55, 0.58, 0.60),
                           (x, 0.36, z * 1.19), (0.34, 0.34, 0.045))
            wheels.append((tire, hub))

    character = Group("boneco-de-blocos")
    scene.add(character)
    torso = Group("tronco-articulado")
    torso.position = np.array([0.0, 1.15, 0.0], dtype=np.float32)
    character.add(torso)
    skin = (0.93, 0.65, 0.39)
    shirt = (0.92, 0.43, 0.10)
    pants = (0.12, 0.23, 0.34)
    add_mesh(torso, "tronco", box, shirt, (0, 0, 0), (0.62, 0.76, 0.34))
    add_mesh(torso, "cinto", box, (0.08, 0.09, 0.12), (0, -0.43, 0), (0.64, 0.12, 0.36))
    add_mesh(torso, "cabeca", box, skin, (0, 0.66, 0), (0.48, 0.48, 0.42))
    add_mesh(torso, "cabelo", box, (0.10, 0.07, 0.05), (0, 0.91, 0), (0.50, 0.12, 0.44))
    for ex in (-0.115, 0.115):
        add_mesh(torso, "olho", sphere, (0.025, 0.025, 0.02),
                 (ex, 0.70, 0.215), (0.065, 0.065, 0.035))
    add_mesh(torso, "boca", box, (0.35, 0.08, 0.06), (0, 0.54, 0.222), (0.13, 0.035, 0.025))

    arms = []
    for side in (-1, 1):
        shoulder = Group("ombro-esquerdo" if side < 0 else "ombro-direito")
        shoulder.position = np.array([side * 0.37, 0.25, 0], dtype=np.float32)
        torso.add(shoulder)
        add_mesh(shoulder, "junta-ombro", sphere, skin, (0, 0, 0), (0.22, 0.22, 0.22))
        add_mesh(shoulder, "braco-superior", box, shirt, (0, -0.31, 0), (0.19, 0.52, 0.20))
        forearm = Group("antebraco")
        forearm.position = np.array([0, -0.55, 0], dtype=np.float32)
        shoulder.add(forearm)
        add_mesh(forearm, "antebraco-manga", box, shirt, (0, -0.19, 0), (0.17, 0.40, 0.18))
        add_mesh(forearm, "mao", sphere, skin, (0, -0.42, 0), (0.19, 0.19, 0.19))
        arms.append(shoulder)

    legs = []
    for side in (-1, 1):
        hip = Group("perna-esquerda" if side < 0 else "perna-direita")
        hip.position = np.array([side * 0.19, -0.49, 0], dtype=np.float32)
        torso.add(hip)
        add_mesh(hip, "calca", box, pants, (0, -0.30, 0), (0.24, 0.58, 0.25))
        add_mesh(hip, "sapato", box, (0.045, 0.055, 0.07), (0.055, -0.62, 0.08), (0.32, 0.16, 0.42))
        legs.append(hip)

    cargo = Group("carga-transportada")
    scene.add(cargo)
    add_mesh(cargo, "volume-carga", box, (0.72, 0.43, 0.18), (0, 0, 0), (0.82, 0.82, 0.82))
    for z in (-0.21, 0.21):
        add_mesh(cargo, "faixa-da-carga", box, (0.16, 0.18, 0.20),
                 (0, 0, z), (0.10, 0.84, 0.035))

    return scene, cart, character, torso, arms, legs, wheels, cargo
