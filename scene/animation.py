"""Roteiro temporal da animação do carrinho e do boneco."""
from __future__ import annotations

import math

import numpy as np


CYCLE_LENGTH = 17.0


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def lerp(a, b, t):
    return a + (b - a) * t


def cart_path(t):
    p0 = np.array([-7.2, 0.85], dtype=np.float32)
    p1 = np.array([-0.65, 0.85], dtype=np.float32)
    p2 = np.array([4.65, -2.45], dtype=np.float32)
    if t < 3.7:
        u = smoothstep(t / 3.7)
        pos, tangent = p0 + (p1 - p0) * u, p1 - p0
        distance = np.linalg.norm(p1 - p0) * u
    elif t < 5.2:
        pos, tangent, distance = p1, p1 - p0, np.linalg.norm(p1 - p0)
    elif t < 8.5:
        u = smoothstep((t - 5.2) / 3.3)
        pos, tangent = p1 + (p2 - p1) * u, p2 - p1
        distance = np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) * u
    elif t < 11.0:
        pos, tangent = p2, p2 - p1
        distance = np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1)
    elif t < 15.0:
        u = smoothstep((t - 11.0) / 4.0)
        pos, tangent = p2 + (p0 - p2) * u, p0 - p2
        distance = (np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) +
                    np.linalg.norm(p2 - p0) * u)
    else:
        pos, tangent = p0, p0 - p2
        distance = np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) + np.linalg.norm(p2 - p0)
    return pos, tangent, distance


def update_animation(sim_time, cart, character, torso, arms, legs, wheels, cargo):
    t = sim_time % CYCLE_LENGTH
    pos, tangent, distance = cart_path(t)
    cart.position = np.array([pos[0], 0, pos[1]], dtype=np.float32)
    cart.rotation[1] = math.atan2(-float(tangent[1]), float(tangent[0]))
    roll = -distance / 0.38
    for tire, hub in wheels:
        tire.rotation[2] = roll
        hub.rotation[2] = roll

    walk = 0.0
    if 5.2 <= t <= 8.5:
        walk = math.sin((t - 5.2) * 7.0)
        character.position = np.array([2.25, 0, lerp(0.9, 1.75, smoothstep((t - 5.2) / 3.3))], dtype=np.float32)
    elif 8.5 < t <= 11.0:
        character.position = np.array([2.25, 0, 1.75], dtype=np.float32)
    elif 11.0 < t < 15.0:
        character.position = np.array([2.25, 0, lerp(1.75, 0.9, smoothstep((t - 11) / 4))], dtype=np.float32)
    else:
        character.position = np.array([2.25, 0, 0.9], dtype=np.float32)
    character.rotation[1] = -math.pi / 2 + (0.20 * math.sin(t * 1.8) if t < 3.7 else 0.0)
    torso.rotation[2] = 0.035 * math.sin(t * 2.0)

    if t < 3.7:
        wave = 0.05 * math.sin(t * 2.8)
        arms[0].rotation[2] = 0.10 + wave
        arms[1].rotation[2] = -0.10 - wave
    elif t < 5.2:
        u = smoothstep((t - 3.7) / 1.5)
        arms[0].rotation[2] = lerp(0.1, -math.pi * 0.88, u)
        arms[1].rotation[2] = lerp(-0.1, math.pi * 0.88, u)
    elif t < 8.5:
        u = smoothstep((t - 5.2) / 0.55)
        arms[0].rotation[2] = lerp(-math.pi * 0.88, 0.10, u)
        arms[1].rotation[2] = lerp(math.pi * 0.88, 1.38, u)
    elif t < 11.0:
        arms[0].rotation[2] = 0.10
        arms[1].rotation[2] = 1.38
    else:
        wave = 0.35 * math.sin((t - 11.0) * 4.0)
        arms[0].rotation[2] = 0.25 + wave
        arms[1].rotation[2] = -0.25 - wave

    legs[0].rotation[2] = 0.38 * walk
    legs[1].rotation[2] = -0.38 * walk

    cart_x, cart_z = float(pos[0]), float(pos[1])
    if t < 8.5:
        cargo.position = np.array([cart_x - 0.32, 1.36, cart_z], dtype=np.float32)
    elif t < 11.0:
        u = smoothstep((t - 8.5) / 2.5)
        start = np.array([cart_x - 0.32, 1.36, cart_z], dtype=np.float32)
        end = np.array([6.8, 0.98, -2.45], dtype=np.float32)
        cargo.position = start + (end - start) * u
    else:
        cargo.position = np.array([6.8, 0.98, -2.45], dtype=np.float32)
