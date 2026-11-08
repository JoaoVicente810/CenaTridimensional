"""Pequeno framework de cena inspirado na arquitetura do livro Stemkoski e Pascale."""
from __future__ import annotations

import os
import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def identity():
    return np.identity(4, dtype=np.float32)


def translation(v):
    m = identity()
    m[0:3, 3] = np.asarray(v, dtype=np.float32)
    return m


def scaling(v):
    if isinstance(v, (int, float)):
        v = [v, v, v]
    m = identity()
    m[0, 0], m[1, 1], m[2, 2] = v
    return m


def rotation_x(a):
    c, s = np.cos(a), np.sin(a)
    m = identity()
    m[1, 1], m[1, 2] = c, -s
    m[2, 1], m[2, 2] = s, c
    return m


def rotation_y(a):
    c, s = np.cos(a), np.sin(a)
    m = identity()
    m[0, 0], m[0, 2] = c, s
    m[2, 0], m[2, 2] = -s, c
    return m


def rotation_z(a):
    c, s = np.cos(a), np.sin(a)
    m = identity()
    m[0, 0], m[0, 1] = c, -s
    m[1, 0], m[1, 1] = s, c
    return m


def perspective(fov_degrees, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov_degrees) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def look_at(eye, target, up=(0, 1, 0)):
    eye = np.asarray(eye, dtype=np.float32)
    target = np.asarray(target, dtype=np.float32)
    up = np.asarray(up, dtype=np.float32)
    forward = target - eye
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up)
    side /= np.linalg.norm(side)
    true_up = np.cross(side, forward)
    m = identity()
    m[0, :3] = side
    m[1, :3] = true_up
    m[2, :3] = -forward
    m[0, 3] = -np.dot(side, eye)
    m[1, 3] = -np.dot(true_up, eye)
    m[2, 3] = np.dot(forward, eye)
    return m


def upload_matrix(location, matrix):
    glUniformMatrix4fv(location, 1, GL_TRUE, np.asarray(matrix, dtype=np.float32))


class ShaderProgram:
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, "r", encoding="utf-8") as f:
            vertex_source = f.read()
        with open(fragment_path, "r", encoding="utf-8") as f:
            fragment_source = f.read()
        self.program = compileProgram(
            compileShader(vertex_source, GL_VERTEX_SHADER),
            compileShader(fragment_source, GL_FRAGMENT_SHADER),
        )
        self._locations = {}

    def use(self):
        glUseProgram(self.program)

    def loc(self, name):
        if name not in self._locations:
            self._locations[name] = glGetUniformLocation(self.program, name)
        return self._locations[name]

    def mat4(self, name, value):
        upload_matrix(self.loc(name), value)

    def vec3(self, name, value):
        glUniform3f(self.loc(name), float(value[0]), float(value[1]), float(value[2]))

    def integer(self, name, value):
        glUniform1i(self.loc(name), int(value))

    def scalar(self, name, value):
        glUniform1f(self.loc(name), float(value))


class Geometry:
    """Malha armazenada em VBO/VAO; cada vértice possui posição, normal e UV."""
    def __init__(self, vertices):
        data = np.asarray(vertices, dtype=np.float32)
        self.vertex_count = len(data)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        stride = 8 * 4
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)


def _push_triangle(out, a, b, c, normal, uv_a=(0, 0), uv_b=(1, 0), uv_c=(1, 1)):
    for p, uv in ((a, uv_a), (b, uv_b), (c, uv_c)):
        out.append([p[0], p[1], p[2], normal[0], normal[1], normal[2], uv[0], uv[1]])


def box_geometry():
    out = []
    faces = [
        # normal, four corners ordered for two triangles
        ((1, 0, 0),  ((.5,-.5,-.5),(.5,.5,-.5),(.5,.5,.5),(.5,-.5,.5))),
        ((-1, 0, 0), ((-.5,-.5,.5),(-.5,.5,.5),(-.5,.5,-.5),(-.5,-.5,-.5))),
        ((0, 1, 0),  ((-.5,.5,-.5),(-.5,.5,.5),(.5,.5,.5),(.5,.5,-.5))),
        ((0, -1, 0), ((-.5,-.5,.5),(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5))),
        ((0, 0, 1),  ((.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5),(-.5,-.5,.5))),
        ((0, 0, -1), ((-.5,-.5,-.5),(-.5,.5,-.5),(.5,.5,-.5),(.5,-.5,-.5))),
    ]
    uv = ((0,0),(0,1),(1,1),(1,0))
    for normal, q in faces:
        _push_triangle(out, q[0], q[1], q[2], normal, uv[0], uv[1], uv[2])
        _push_triangle(out, q[0], q[2], q[3], normal, uv[0], uv[2], uv[3])
    return Geometry(out)


def cylinder_z_geometry(segments=24):
    """Cilindro com eixo Z, adequado às rodas cujo eixo atravessa a carroceria."""
    out = []
    for i in range(segments):
        a0 = 2 * np.pi * i / segments
        a1 = 2 * np.pi * (i + 1) / segments
        p0 = (np.cos(a0)*.5, np.sin(a0)*.5, -.5)
        p1 = (np.cos(a1)*.5, np.sin(a1)*.5, -.5)
        p2 = (np.cos(a1)*.5, np.sin(a1)*.5, .5)
        p3 = (np.cos(a0)*.5, np.sin(a0)*.5, .5)
        n0 = (np.cos(a0), np.sin(a0), 0)
        n1 = (np.cos(a1), np.sin(a1), 0)
        # side quad
        for p, n, uv in ((p0,n0,(i/segments,0)),(p1,n1,((i+1)/segments,0)),
                         (p2,n1,((i+1)/segments,1)),(p0,n0,(i/segments,0)),
                         (p2,n1,((i+1)/segments,1)),(p3,n0,(i/segments,1))):
            out.append([*p,*n,*uv])
        # caps
        for z, normal in ((-.5,(0,0,-1)),(.5,(0,0,1))):
            center = (0,0,z)
            if z < 0:
                tri = (center, p1, p0)
            else:
                tri = (center, p3, p2)
            for p in tri:
                out.append([*p,*normal,0.5,0.5])
    return Geometry(out)


def sphere_geometry(rings=12, sectors=18):
    out = []
    for i in range(rings):
        lat0 = -np.pi/2 + np.pi*i/rings
        lat1 = -np.pi/2 + np.pi*(i+1)/rings
        for j in range(sectors):
            lon0 = 2*np.pi*j/sectors
            lon1 = 2*np.pi*(j+1)/sectors
            pts = []
            for lat, lon in ((lat0,lon0),(lat0,lon1),(lat1,lon1),(lat1,lon0)):
                n = (np.cos(lat)*np.cos(lon), np.sin(lat), np.cos(lat)*np.sin(lon))
                pts.append((n, (j/sectors, i/rings)))
            for idx in (0,2,1,0,3,2):
                n, uv = pts[idx]
                out.append([n[0]*.5,n[1]*.5,n[2]*.5,*n,*uv])
    return Geometry(out)


class Texture:
    def __init__(self, path):
        from PIL import Image
        image = Image.open(path).convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.width, self.height = image.size
        pixels = image.tobytes()
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, pixels)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D, 0)


class Node:
    """Nó hierárquico do grafo de cena: filhos herdam a transformação do pai."""
    def __init__(self, name="node"):
        self.name = name
        self.position = np.zeros(3, dtype=np.float32)
        self.rotation = np.zeros(3, dtype=np.float32)  # X, Y, Z em radianos
        self.scale = np.ones(3, dtype=np.float32)
        self.parent = None
        self.children = []

    def add(self, child):
        if child.parent is not None:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)
        return child

    def local_matrix(self):
        return (translation(self.position) @ rotation_y(self.rotation[1]) @
                rotation_x(self.rotation[0]) @ rotation_z(self.rotation[2]) @ scaling(self.scale))

    def world_matrix(self):
        if self.parent is None:
            return self.local_matrix()
        return self.parent.world_matrix() @ self.local_matrix()

    def descendants(self):
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.descendants())
        return result


class Group(Node):
    pass


class Mesh(Node):
    def __init__(self, name, geometry, color, texture=None, casts_shadow=True):
        super().__init__(name)
        self.geometry = geometry
        self.color = np.asarray(color, dtype=np.float32)
        self.texture = texture
        self.casts_shadow = casts_shadow


class Scene(Group):
    def __init__(self):
        super().__init__("scene")

    def meshes(self):
        return [node for node in self.descendants() if isinstance(node, Mesh)]


class Camera:
    def __init__(self, aspect):
        self.position = np.array([11.5, 8.5, 13.5], dtype=np.float32)
        direction = -self.position
        self.yaw = float(np.arctan2(direction[2], direction[0]))
        self.pitch = float(np.arctan2(direction[1], np.linalg.norm(direction[[0,2]])))
        self.aspect = aspect
        self.speed = 8.0
        self.look_speed = 1.5

    def front(self):
        return np.array([
            np.cos(self.pitch)*np.cos(self.yaw),
            np.sin(self.pitch),
            np.cos(self.pitch)*np.sin(self.yaw)
        ], dtype=np.float32)

    def view_matrix(self):
        return look_at(self.position, self.position + self.front())

    def projection_matrix(self):
        return perspective(52.0, self.aspect, 0.1, 100.0)

    def update(self, keys, dt):
        front = self.front()
        right = np.cross(front, np.array([0,1,0], dtype=np.float32))
        right /= max(np.linalg.norm(right), 1e-6)
        distance = self.speed * dt
        if keys[ord('w')]: self.position += front * distance
        if keys[ord('s')]: self.position -= front * distance
        if keys[ord('a')]: self.position -= right * distance
        if keys[ord('d')]: self.position += right * distance
        if keys[ord('q')]: self.position[1] += distance
        if keys[ord('e')]: self.position[1] -= distance


class DirectionalLight:
    def __init__(self, direction=(-0.7, -1.0, -0.45), color=(1.0, 0.92, 0.78)):
        self.direction = np.asarray(direction, dtype=np.float32)
        self.direction /= np.linalg.norm(self.direction)
        self.color = np.asarray(color, dtype=np.float32)

    def light_space_matrix(self):
        center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        eye = center - self.direction * 18.0
        view = look_at(eye, center)
        left, right, bottom, top, near, far = -12.0, 12.0, -10.0, 10.0, 0.1, 45.0
        proj = identity()
        proj[0,0] = 2.0/(right-left)
        proj[1,1] = 2.0/(top-bottom)
        proj[2,2] = -2.0/(far-near)
        proj[0,3] = -(right+left)/(right-left)
        proj[1,3] = -(top+bottom)/(top-bottom)
        proj[2,3] = -(far+near)/(far-near)
        return proj @ view


class ShadowMap:
    def __init__(self, resolution=2048):
        self.resolution = resolution
        self.fbo = glGenFramebuffers(1)
        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32F, resolution, resolution,
                     0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1,1,1,1])
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D,
                               self.depth_texture, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer de shadow mapping inválido: {hex(status)}")


class Renderer:
    def __init__(self, width, height, shader_dir, shadow_resolution=2048):
        self.width, self.height = width, height
        self.scene_shader = ShaderProgram(os.path.join(shader_dir, "scene.vert"),
                                          os.path.join(shader_dir, "scene.frag"))
        self.depth_shader = ShaderProgram(os.path.join(shader_dir, "depth.vert"),
                                         os.path.join(shader_dir, "depth.frag"))
        self.shadow_map = ShadowMap(shadow_resolution)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_MULTISAMPLE)

    def render(self, scene, camera, light):
        meshes = scene.meshes()
        light_space = light.light_space_matrix()

        # 1) Shadow pass: registra a profundidade vista pela luz direcional.
        glViewport(0, 0, self.shadow_map.resolution, self.shadow_map.resolution)
        glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_map.fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.depth_shader.use()
        self.depth_shader.mat4("uLightSpace", light_space)
        for mesh in meshes:
            if mesh.casts_shadow:
                self.depth_shader.mat4("uModel", mesh.world_matrix())
                mesh.geometry.draw()

        # 2) Passagem principal: material, textura, iluminação e consulta da sombra.
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shader = self.scene_shader
        shader.use()
        shader.mat4("uView", camera.view_matrix())
        shader.mat4("uProjection", camera.projection_matrix())
        shader.mat4("uLightSpace", light_space)
        shader.vec3("uCameraPosition", camera.position)
        shader.vec3("uLightDirection", light.direction)
        shader.vec3("uLightColor", light.color)
        shader.vec3("uAmbientColor", [0.28, 0.30, 0.34])
        shader.scalar("uShadowStrength", 0.72)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_map.depth_texture)
        shader.integer("uShadowMap", 1)

        for mesh in meshes:
            shader.mat4("uModel", mesh.world_matrix())
            shader.vec3("uBaseColor", mesh.color)
            if mesh.texture is not None:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, mesh.texture.texture_id)
                shader.integer("uTexture", 0)
                shader.integer("uUseTexture", 1)
            else:
                shader.integer("uUseTexture", 0)
            mesh.geometry.draw()

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, 0)
        glActiveTexture(GL_TEXTURE0)
