# draw.py
import cv2
import numpy as np
from state import S
from geometry import (line_angle, perpendicular_unit_vector,
                      unit_vector_from_angle, extend_line_to_image_from_center,
                      project_point_on_vector_scalar)

# Colors (BGR)
COLOR_DEF = (0, 0, 255)
COLOR_ATT = (255, 0, 0)
COLOR_REF = (0, 255, 0)
AXIS_COLOR = (200,200,0)
THICK = 2

def lighten_color(bgr, factor=0.6):
    r = tuple(min(255, int(c + (255-c)*factor)) for c in bgr)
    return r

def draw_overlay_to_frame(frame_bgr):
    out = frame_bgr.copy()
    h,w = out.shape[:2]

    # show reference click points while selecting
    for i,p in enumerate(S.ref_click_points):
        cv2.circle(out, p, 6, COLOR_REF, -1)
        cv2.putText(out, f"P{i+1}:({p[0]},{p[1]})", (p[0]+8, p[1]+8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_REF,1)

    # reference line
    if S.ref_line is not None:
        cv2.line(out, S.ref_line[0], S.ref_line[1], COLOR_REF, 2)
        cv2.circle(out, S.ref_line[0], 5, COLOR_REF, -1); cv2.circle(out, S.ref_line[1], 5, COLOR_REF, -1)
        ang = line_angle(S.ref_line[0], S.ref_line[1])
        cv2.putText(out, f"Ref angle: {int((ang*180.0/3.14159))} deg", (10, 64),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_REF, 2)

    # parallel lines if offsets exist
    if S.ref_line is not None and S.def_offset is not None and S.att_offset is not None:
        theta = line_angle(S.ref_line[0], S.ref_line[1])
        normal = perpendicular_unit_vector(theta)
        ref_dir = unit_vector_from_angle(theta)
        origin = np.array(S.ref_line[0], dtype=float)

        # def
        def_center = origin + normal * S.def_offset
        def_p0, def_p1 = extend_line_to_image_from_center(def_center, ref_dir, w, h)
        cv2.line(out, def_p0, def_p1, COLOR_DEF, THICK)

        # att
        att_center = origin + normal * S.att_offset
        att_p0, att_p1 = extend_line_to_image_from_center(att_center, ref_dir, w, h)
        cv2.line(out, att_p0, att_p1, COLOR_ATT, THICK)

        # projections and long guides
        origin_tuple = (int(origin[0]), int(origin[1]))
        def_proj = project_point_on_vector_scalar((def_center[0], def_center[1]), origin_tuple, normal)
        att_proj = project_point_on_vector_scalar((att_center[0], att_center[1]), origin_tuple, normal)

        length = max(w,h) * 2
        ref_dir_unit = ref_dir
        def_p_long0 = (int(def_center[0] - ref_dir_unit[0]*length), int(def_center[1] - ref_dir_unit[1]*length))
        def_p_long1 = (int(def_center[0] + ref_dir_unit[0]*length), int(def_center[1] + ref_dir_unit[1]*length))
        att_p_long0 = (int(att_center[0] - ref_dir_unit[0]*length), int(att_center[1] - ref_dir_unit[1]*length))
        att_p_long1 = (int(att_center[0] + ref_dir_unit[0]*length), int(att_center[1] + ref_dir_unit[1]*length))
        cv2.line(out, def_p_long0, def_p_long1, (0,0,150), 1, lineType=cv2.LINE_AA)
        cv2.line(out, att_p_long0, att_p_long1, (150,0,0), 1, lineType=cv2.LINE_AA)

        if S.goal_left:
            is_off = att_proj < def_proj
        else:
            is_off = att_proj > def_proj
        txt = "OFFSIDE" if is_off else "ON-SIDE"
        col = (0,0,255) if is_off else (0,255,0)
        cv2.putText(out, txt, (10, 160), cv2.FONT_HERSHEY_DUPLEX, 1.5, col, 2)

        # crosshairs persistent
        if S.cross_def is not None:
            mx,my = S.cross_def
            cv2.line(out, (0, my), (w-1, my), (100,100,255), 1, lineType=cv2.LINE_AA)
            cv2.line(out, (mx, my), (mx, 0), (100,100,255), 1, lineType=cv2.LINE_AA)
        if S.cross_att is not None:
            mx,my = S.cross_att
            cv2.line(out, (0, my), (w-1, my), (255,100,100), 1, lineType=cv2.LINE_AA)
            cv2.line(out, (mx, my), (mx, 0), (255,100,100), 1, lineType=cv2.LINE_AA)

    # HUD
    cv2.putText(out, f"Frame {S.cur_idx}/{S.total}", (out.shape[1]-190, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0),2)
    cv2.putText(out, f"GOAL: {'LEFT' if S.goal_left else 'RIGHT'}", (10, out.shape[0]-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255),2)
    mode_txt = "DRAG: ON (L)" if S.drag_mode else "DRAG: OFF (L)"
    cv2.putText(out, mode_txt, (10, out.shape[0]-32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255),2)
    if S.ref_click_mode:
        cv2.putText(out, "REF MODE: Click 2 endpoints", (200, out.shape[0]-32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255),2)

    return out