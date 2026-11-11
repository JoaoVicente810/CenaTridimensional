"""Ponto de entrada da aplicação do pátio de operações."""
from __future__ import annotations

import os
import sys

import pygame
from OpenGL.GL import GL_VERSION, glGetString

from engine import Camera, DirectionalLight, Renderer
from scene import make_scene, update_animation
from scene.animation import CYCLE_LENGTH


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT = 1280, 760


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
