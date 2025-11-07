# geometry.py
import math
import numpy as np

def line_angle(p0, p1):
    dx = p1[0]-p0[0]; dy = p1[1]-p0[1]
    return math.atan2(dy, dx)

def unit_vector_from_angle(theta):
    return np.array([math.cos(theta), math.sin(theta)], dtype=float)

def perpendicular_unit_vector(theta):
    return np.array([-math.sin(theta), math.cos(theta)], dtype=float)

def extend_line_to_image_from_center(center, direction_vec, w, h):
    length = max(w,h) * 3
    p0 = (int(center[0] - direction_vec[0]*length), int(center[1] - direction_vec[1]*length))
    p1 = (int(center[0] + direction_vec[0]*length), int(center[1] + direction_vec[1]*length))
    return p0, p1

def project_point_on_vector_scalar(pt, origin, vec):
    v = np.array([pt[0]-origin[0], pt[1]-origin[1]], dtype=float)
    return float(np.dot(v, vec))

def point_line_distance(pt, p0, p1):
    p = np.array(pt, dtype=float)
    a = np.array(p0, dtype=float)
    b = np.array(p1, dtype=float)
    if np.allclose(a,b):
        return np.linalg.norm(p - a)
    num = abs(np.cross(b - a, p - a))
    den = np.linalg.norm(b - a)
    return float(num / den)