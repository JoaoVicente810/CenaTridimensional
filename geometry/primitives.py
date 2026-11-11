"""Construtores de malhas geométricas primitivas."""
from __future__ import annotations

import numpy as np

from engine import Geometry


def _push_triangle(out, a, b, c, normal, uv_a=(0, 0), uv_b=(1, 0), uv_c=(1, 1)):
    for p, uv in ((a, uv_a), (b, uv_b), (c, uv_c)):
        out.append([p[0], p[1], p[2], normal[0], normal[1], normal[2], uv[0], uv[1]])


def box_geometry():
    out = []
    faces = [
        ((1, 0, 0),  ((.5,-.5,-.5),(.5,.5,-.5),(.5,.5,.5),(.5,-.5,.5))),
        ((-1, 0, 0), ((-.5,-.5,.5),(-.5,.5,.5),(-.5,.5,-.5),(-.5,-.5,-.5))),
        ((0, 1, 0),  ((-.5,.5,-.5),(-.5,.5,.5),(.5,.5,.5),(.5,.5,-.5))),
        ((0, -1, 0), ((-.5,-.5,.5),(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5))),
        ((0, 0, 1),  ((.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5),(-.5,-.5,.5))),
        ((0, 0, -1), ((-.5,-.5,-.5),(-.5,.5,-.5),(.5,.5,-.5),(.5,-.5,-.5))),
    ]
    uv = ((0,0),(0,1),(1,1),(1,0))
    for normal, corners in faces:
        _push_triangle(out, corners[0], corners[1], corners[2], normal, uv[0], uv[1], uv[2])
        _push_triangle(out, corners[0], corners[2], corners[3], normal, uv[0], uv[2], uv[3])
    return Geometry(out)


def cylinder_z_geometry(segments=24):
    """Cilindro com eixo Z, adequado às rodas."""
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
        for p, n, uv in ((p0,n0,(i/segments,0)), (p1,n1,((i+1)/segments,0)),
                         (p2,n1,((i+1)/segments,1)), (p0,n0,(i/segments,0)),
                         (p2,n1,((i+1)/segments,1)), (p3,n0,(i/segments,1))):
            out.append([*p, *n, *uv])
        for z, normal in ((-.5,(0,0,-1)), (.5,(0,0,1))):
            center = (0, 0, z)
            tri = (center, p1, p0) if z < 0 else (center, p3, p2)
            for p in tri:
                out.append([*p, *normal, 0.5, 0.5])
    return Geometry(out)


def sphere_geometry(rings=12, sectors=18):
    out = []
    for i in range(rings):
        lat0 = -np.pi/2 + np.pi*i/rings
        lat1 = -np.pi/2 + np.pi*(i+1)/rings
        for j in range(sectors):
            lon0 = 2*np.pi*j/sectors
            lon1 = 2*np.pi*(j+1)/sectors
            points = []
            for lat, lon in ((lat0,lon0), (lat0,lon1), (lat1,lon1), (lat1,lon0)):
                normal = (np.cos(lat)*np.cos(lon), np.sin(lat), np.cos(lat)*np.sin(lon))
                points.append((normal, (j/sectors, i/rings)))
            for index in (0, 2, 1, 0, 3, 2):
                normal, uv = points[index]
                out.append([normal[0]*.5, normal[1]*.5, normal[2]*.5, *normal, *uv])
    return Geometry(out)
