"""Pátio de Operações - carrinho de carga + boneco de blocos.
Execução: python main.py
"""
from __future__ import annotations

import math
import os
import sys
import pygame
import numpy as np
from OpenGL.GL import *

from engine import (
    Camera, DirectionalLight, Geometry, Group, Mesh, Renderer, Scene, Texture,
    box_geometry, cylinder_z_geometry, sphere_geometry,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT = 1280, 760
CYCLE_LENGTH = 17.0


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def lerp(a, b, t):
    return a + (b - a) * t


def add_mesh(parent, name, geometry, color, position=(0,0,0), scale=(1,1,1),
             rotation=(0,0,0), texture=None, casts_shadow=True):
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
    floor_texture = Texture(os.path.join(BASE_DIR, "assets", "asphalt.png"))

    # Pátio: piso texturizado (as faixas amarelas e delimitações brancas foram removidas)
    add_mesh(scene, "piso-texturizado", box, (1,1,1), (0,-0.16,0),
             (20,0.32,14), texture=floor_texture, casts_shadow=False)
    
    """
    # [REMOVIDO A PEDIDO DO USUÁRIO]: Faixas da rota principal, secundária e limites
    yellow = (0.95, 0.72, 0.08)
    white = (0.82, 0.86, 0.86)
    for x in np.arange(-8.5, 7.8, 1.25):
        add_mesh(scene, "faixa-amarela", box, yellow, (float(x),0.012,1.65),
                 (0.62,0.025,0.075), casts_shadow=False)
    for z in np.arange(-3.6, 1.0, 1.25):
        add_mesh(scene, "faixa-amarela", box, yellow, (5.5,0.013,float(z)),
                 (0.075,0.026,0.62), casts_shadow=False)
    for x in (5.6, 7.6):
        add_mesh(scene, "limite-doca", box, white, (x,0.018,-2.45),
                 (0.055,0.03,2.0), casts_shadow=False)
    for z in (-3.45, -1.45):
        add_mesh(scene, "limite-doca", box, white, (6.6,0.018,z),
                 (2.05,0.03,0.055), casts_shadow=False)
    """

    # Plataforma de recebimento da carga mantida.
    add_mesh(scene, "plataforma-de-entrega", box, (0.20,0.25,0.29),
             (6.8,0.22,-2.45), (2.0,0.44,1.45))
    add_mesh(scene, "tampo-plataforma", box, (0.55,0.58,0.58),
             (6.8,0.47,-2.45), (2.0,0.08,1.45))

    """
    # [REMOVIDO A PEDIDO DO USUÁRIO]: Galpão ao fundo e caixas estáticas
    add_mesh(scene, "galpao-parede", box, (0.34,0.40,0.47),
             (0,1.75,-6.35), (12.5,3.5,0.42))
    add_mesh(scene, "galpao-telhado", box, (0.16,0.20,0.25),
             (0,3.58,-6.35), (13.0,0.22,1.0))
    for x in (-4.2, 0.0, 4.2):
        add_mesh(scene, "portao-galpao", box, (0.12,0.18,0.23),
                 (x,1.35,-6.08), (2.6,2.45,0.07))
        add_mesh(scene, "moldura-portao", box, (0.83,0.83,0.78),
                 (x,2.63,-6.02), (2.75,0.09,0.12))

    for pos in [(-7.4,0.55,-3.7), (-7.4,1.45,-3.7), (-6.25,0.55,-3.7),
                (8.6,0.55,-5.0), (8.6,1.45,-5.0)]:
        add_mesh(scene, "caixa-estoque", box, (0.58,0.34,0.16), pos,
                 (0.85,0.85,0.85))
        add_mesh(scene, "cinta-caixa", box, (0.16,0.20,0.24),
                 (pos[0],pos[1],pos[2]+0.435), (0.12,0.86,0.025))
    """

    # Carrinho como grupo hierárquico
    cart = Group("carrinho-de-carga")
    scene.add(cart)
    dark = (0.075,0.095,0.12)
    blue = (0.12,0.36,0.72)
    add_mesh(cart, "chassi", box, dark, (0,0.62,0), (2.25,0.28,0.98))
    add_mesh(cart, "carroceria-inferior", box, blue, (-0.28,0.89,0), (1.35,0.46,1.08))
    add_mesh(cart, "caixa-carga-frontal", box, (0.16,0.43,0.76),
             (-0.30,1.18,0), (1.26,0.12,1.0))
    add_mesh(cart, "cabine", box, (0.10,0.31,0.62),
             (0.67,1.28,0), (0.86,0.94,0.92))
    add_mesh(cart, "para-brisa", box, (0.10,0.18,0.23),
             (0.68,1.47,0.468), (0.56,0.48,0.026))
    add_mesh(cart, "janela-traseira", box, (0.10,0.18,0.23),
             (0.20,1.47,-0.468), (0.20,0.48,0.026))
    add_mesh(cart, "teto-cabine", box, (0.07,0.25,0.52),
             (0.66,1.78,0), (0.94,0.14,1.02))
    add_mesh(cart, "para-choque-frontal", box, (0.68,0.72,0.72),
             (1.18,0.58,0), (0.18,0.22,1.12))
    add_mesh(cart, "para-choque-traseiro", box, (0.68,0.72,0.72),
             (-1.15,0.58,0), (0.18,0.22,1.12))
    for z in (-0.42, 0.42):
        add_mesh(cart, "farol", sphere, (1.0,0.86,0.48), (1.13,0.88,z),
                 (0.16,0.14,0.10))
        add_mesh(cart, "lanterna-traseira", box, (0.86,0.12,0.07),
                 (-1.18,0.78,z), (0.07,0.18,0.16))

    wheels = []
    for x in (-0.72, 0.78):
        for z in (-0.57, 0.57):
            tire = add_mesh(cart, "roda", wheel_geo, (0.035,0.04,0.045),
                            (x,0.36,z), (0.76,0.76,0.22))
            hub = add_mesh(cart, "cubo-roda", wheel_geo, (0.55,0.58,0.60),
                           (x,0.36,z*1.19), (0.34,0.34,0.045))
            wheels.append((tire, hub))

    # Boneco de blocos
    character = Group("boneco-de-blocos")
    scene.add(character)
    torso = Group("tronco-articulado")
    torso.position = np.array([0.0,1.15,0.0], dtype=np.float32)
    character.add(torso)
    skin = (0.93,0.65,0.39)
    shirt = (0.92,0.43,0.10)
    pants = (0.12,0.23,0.34)
    add_mesh(torso, "tronco", box, shirt, (0,0,0), (0.62,0.76,0.34))
    add_mesh(torso, "cinto", box, (0.08,0.09,0.12), (0,-0.43,0), (0.64,0.12,0.36))
    head = add_mesh(torso, "cabeca", box, skin, (0,0.66,0), (0.48,0.48,0.42))
    add_mesh(torso, "cabelo", box, (0.10,0.07,0.05), (0,0.91,0), (0.50,0.12,0.44))
    for ex in (-0.115,0.115):
        add_mesh(torso, "olho", sphere, (0.025,0.025,0.02),
                 (ex,0.70,0.215), (0.065,0.065,0.035))
    add_mesh(torso, "boca", box, (0.35,0.08,0.06), (0,0.54,0.222), (0.13,0.035,0.025))

    arms = []
    for side in (-1,1):
        shoulder = Group("ombro-esquerdo" if side < 0 else "ombro-direito")
        shoulder.position = np.array([side*0.37,0.25,0], dtype=np.float32)
        torso.add(shoulder)
        add_mesh(shoulder, "junta-ombro", sphere, skin, (0,0,0), (0.22,0.22,0.22))
        add_mesh(shoulder, "braco-superior", box, shirt, (0,-0.31,0), (0.19,0.52,0.20))
        forearm = Group("antebraco")
        forearm.position = np.array([0,-0.55,0], dtype=np.float32)
        shoulder.add(forearm)
        add_mesh(forearm, "antebraco-manga", box, shirt, (0,-0.19,0), (0.17,0.40,0.18))
        add_mesh(forearm, "mao", sphere, skin, (0,-0.42,0), (0.19,0.19,0.19))
        arms.append(shoulder)

    legs = []
    for side in (-1,1):
        hip = Group("perna-esquerda" if side < 0 else "perna-direita")
        hip.position = np.array([side*0.19,-0.49,0], dtype=np.float32)
        torso.add(hip)
        add_mesh(hip, "calca", box, pants, (0,-0.30,0), (0.24,0.58,0.25))
        add_mesh(hip, "sapato", box, (0.045,0.055,0.07), (0.055,-0.62,0.08), (0.32,0.16,0.42))
        legs.append(hip)

    # Carga transportada (mantida)
    cargo = Group("carga-transportada")
    scene.add(cargo)
    add_mesh(cargo, "volume-carga", box, (0.72,0.43,0.18), (0,0,0), (0.82,0.82,0.82))
    for z in (-0.21,0.21):
        add_mesh(cargo, "faixa-da-carga", box, (0.16,0.18,0.20),
                 (0,0,z), (0.10,0.84,0.035))

    return scene, cart, character, torso, arms, legs, wheels, cargo


def cart_path(t):
    """Retorna posição XZ, direção e distância percorrida no ciclo."""
    p0 = np.array([-7.2, 0.85], dtype=np.float32)
    p1 = np.array([-0.65, 0.85], dtype=np.float32)
    p2 = np.array([4.65, -2.45], dtype=np.float32)
    if t < 3.7:
        u = smoothstep(t/3.7)
        pos = p0 + (p1-p0)*u
        tangent = p1-p0
        distance = np.linalg.norm(p1-p0)*u
    elif t < 5.2:
        pos, tangent, distance = p1, p1-p0, np.linalg.norm(p1-p0)
    elif t < 8.5:
        u = smoothstep((t-5.2)/3.3)
        pos = p1 + (p2-p1)*u
        tangent = p2-p1
        distance = np.linalg.norm(p1-p0) + np.linalg.norm(p2-p1)*u
    elif t < 11.0:
        pos, tangent = p2, p2-p1
        distance = np.linalg.norm(p1-p0)+np.linalg.norm(p2-p1)
    elif t < 15.0:
        u = smoothstep((t-11.0)/4.0)
        pos = p2 + (p0-p2)*u
        tangent = p0-p2
        distance = (np.linalg.norm(p1-p0)+np.linalg.norm(p2-p1)+
                    np.linalg.norm(p2-p0)*u)
    else:
        pos, tangent = p0, p0-p2
        distance = np.linalg.norm(p1-p0)+np.linalg.norm(p2-p1)+np.linalg.norm(p2-p0)
    return pos, tangent, distance


def update_animation(sim_time, cart, character, torso, arms, legs, wheels, cargo):
    t = sim_time % CYCLE_LENGTH
    pos, tangent, distance = cart_path(t)
    cart.position = np.array([pos[0],0,pos[1]], dtype=np.float32)
    cart.rotation[1] = math.atan2(-float(tangent[1]), float(tangent[0]))
    roll = -distance / 0.38
    for tire, hub in wheels:
        tire.rotation[2] = roll
        hub.rotation[2] = roll

    walk = 0.0
    if 5.2 <= t <= 8.5:
        walk = math.sin((t-5.2)*7.0)
        character.position = np.array([2.25,0,lerp(0.9,1.75,smoothstep((t-5.2)/3.3))], dtype=np.float32)
    elif 8.5 < t <= 11.0:
        character.position = np.array([2.25,0,1.75], dtype=np.float32)
    elif 11.0 < t < 15.0:
        character.position = np.array([2.25,0,lerp(1.75,0.9,smoothstep((t-11)/4))], dtype=np.float32)
    else:
        character.position = np.array([2.25,0,0.9], dtype=np.float32)
    character.rotation[1] = -math.pi/2 + (0.20*math.sin(t*1.8) if t < 3.7 else 0.0)
    torso.rotation[2] = 0.035*math.sin(t*2.0)

    if t < 3.7:
        wave = 0.20*math.sin(t*4.2)
        arms[0].rotation[2] = 0.10 + wave
        arms[1].rotation[2] = -0.10 - wave
    elif t < 5.2:
        u = smoothstep((t-3.7)/1.5)
        arms[0].rotation[2] = lerp(0.1, math.pi*0.88, u)
        arms[1].rotation[2] = lerp(-0.1, -math.pi*0.88, u)
    elif t < 8.5:
        u = smoothstep((t-5.2)/0.55)
        arms[0].rotation[2] = lerp(math.pi*0.88, 0.10, u)
        arms[1].rotation[2] = lerp(-math.pi*0.88, -1.38, u)
    elif t < 11.0:
        arms[0].rotation[2] = 0.10
        arms[1].rotation[2] = -1.38
    else:
        wave = 0.35*math.sin((t-11.0)*4.0)
        arms[0].rotation[2] = 0.25 + wave
        arms[1].rotation[2] = -0.25 - wave

    legs[0].rotation[2] = 0.38*walk
    legs[1].rotation[2] = -0.38*walk

    cart_x, cart_z = float(pos[0]), float(pos[1])
    if t < 8.5:
        cargo.position = np.array([cart_x-0.32,1.36,cart_z], dtype=np.float32)
    elif t < 11.0:
        u = smoothstep((t-8.5)/2.5)
        start = np.array([cart_x-0.32,1.36,cart_z], dtype=np.float32)
        end = np.array([6.8,0.98,-2.45], dtype=np.float32)
        cargo.position = start + (end-start)*u
    else:
        cargo.position = np.array([6.8,0.98,-2.45], dtype=np.float32)


def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                    pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Pátio de Operações | Carrinho + Boneco de Blocos")

    print("OpenGL:", glGetString(GL_VERSION).decode("utf-8", errors="replace"))
    scene, cart, character, torso, arms, legs, wheels, cargo = make_scene()
    camera = Camera(WIDTH / HEIGHT)
    light = DirectionalLight()
    renderer = Renderer(WIDTH, HEIGHT, os.path.join(BASE_DIR, "shaders"))

    clock = pygame.time.Clock()
    running = True
    paused = False
    sim_time = 0.0
    print("Controles: WASD mover câmera | Q/E subir/descer | setas olhar | ESPAÇO pausar | R reiniciar | ESC sair")

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    sim_time = 0.0
                elif event.key == pygame.K_LEFT:
                    camera.yaw -= 0.10
                elif event.key == pygame.K_RIGHT:
                    camera.yaw += 0.10
                elif event.key == pygame.K_UP:
                    camera.pitch = min(camera.pitch + 0.08, 1.35)
                elif event.key == pygame.K_DOWN:
                    camera.pitch = max(camera.pitch - 0.08, -1.35)

        keys = pygame.key.get_pressed()
        camera.update(keys, dt)
        if not paused:
            sim_time += dt
        update_animation(sim_time, cart, character, torso, arms, legs, wheels, cargo)
        renderer.render(scene, camera, light)
        pygame.display.flip()
        state = "PAUSADO" if paused else "EM EXECUÇÃO"
        pygame.display.set_caption(
            f"Pátio de Operações | {state} | tempo: {sim_time % CYCLE_LENGTH:04.1f}s"
        )

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()