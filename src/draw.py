# draw.py
import cv2
import numpy as np
from state import S
from geometry import (line_angle, perpendicular_unit_vector,
                      unit_vector_from_angle, extend_line_to_image_from_center,
                      project_point_on_vector_scalar)
# import utilities to warp points
from video_io import warp_points

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

    # show rectify click points while selecting
    if S.rectify_click_mode:
        for i,p in enumerate(S.rectify_click_points):
            cv2.circle(out, p, 6, (255,255,0), -1)
            cv2.putText(out, f"R{i+1}:({p[0]},{p[1]})", (p[0]+8, p[1]+8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0),1)

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
        # Si hay homografía, trabajamos en el espacio rectificado
        if S.homography is not None:
            # transformar ref_line a vista rectificada
            ref0_rect, ref1_rect = warp_points([S.ref_line[0], S.ref_line[1]], S.homography)
            rect_w, rect_h = S.rectify_dst_size

            theta = line_angle(tuple(ref0_rect), tuple(ref1_rect))
            normal = perpendicular_unit_vector(theta)
            ref_dir = unit_vector_from_angle(theta)
            origin = np.array(ref0_rect, dtype=float)

            # def/att centers en espacio rectificado
            def_center_rect = origin + normal * S.def_offset
            att_center_rect = origin + normal * S.att_offset

            # extender líneas en espacio rectificado
            def_p0_rect, def_p1_rect = extend_line_to_image_from_center(def_center_rect, ref_dir, rect_w, rect_h)
            att_p0_rect, att_p1_rect = extend_line_to_image_from_center(att_center_rect, ref_dir, rect_w, rect_h)

            # transformar puntos de vuelta a imagen original para dibujar
            def_p0_img = tuple(warp_points([def_p0_rect], S.homography_inv)[0].astype(int))
            def_p1_img = tuple(warp_points([def_p1_rect], S.homography_inv)[0].astype(int))
            att_p0_img = tuple(warp_points([att_p0_rect], S.homography_inv)[0].astype(int))
            att_p1_img = tuple(warp_points([att_p1_rect], S.homography_inv)[0].astype(int))

            cv2.line(out, def_p0_img, def_p1_img, COLOR_DEF, THICK)
            cv2.line(out, att_p0_img, att_p1_img, COLOR_ATT, THICK)

            # proyecciones en espacio rectificado para decidir offside
            origin_tuple = (int(origin[0]), int(origin[1]))
            def_proj = project_point_on_vector_scalar((def_center_rect[0], def_center_rect[1]), origin_tuple, normal)
            att_proj = project_point_on_vector_scalar((att_center_rect[0], att_center_rect[1]), origin_tuple, normal)

            # dibujitos largos (en rectified) -- opcional, no los transformamos de vuelta para evitar sobrecarga
            length = max(rect_w, rect_h) * 2
            ref_dir_unit = ref_dir
            def_p_long0 = (int(def_center_rect[0] - ref_dir_unit[0]*length), int(def_center_rect[1] - ref_dir_unit[1]*length))
            def_p_long1 = (int(def_center_rect[0] + ref_dir_unit[0]*length), int(def_center_rect[1] + ref_dir_unit[1]*length))
            att_p_long0 = (int(att_center_rect[0] - ref_dir_unit[0]*length), int(att_center_rect[1] - ref_dir_unit[1]*length))
            att_p_long1 = (int(att_center_rect[0] + ref_dir_unit[0]*length), int(att_center_rect[1] + ref_dir_unit[1]*length))

        else:
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

        if S.homography is not None:
            if S.goal_left:
                is_off = att_proj < def_proj
            else:
                is_off = att_proj > def_proj
        else:
            if S.goal_left:
                is_off = att_proj < def_proj
            else:
                is_off = att_proj > def_proj

        txt = "OFFSIDE" if is_off else "ON-SIDE"
        col = (0,0,255) if is_off else (0,255,0)

        # --- draw label background (same as before) ---
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.5
        font_thickness = 2
        base_x = 10
        base_y = 160
        (text_w, text_h), baseline = cv2.getTextSize(txt, font, font_scale, font_thickness)
        pad_x = 10
        pad_y = 8
        rect_tl = (base_x - pad_x, base_y - text_h - pad_y)
        rect_br = (base_x + text_w + pad_x, base_y + baseline + pad_y)
        rect_tl = (max(0, rect_tl[0]), max(0, rect_tl[1]))
        rect_br = (min(w-1, rect_br[0]), min(h-1, rect_br[1]))
        cv2.rectangle(out, rect_tl, rect_br, (255,255,255), thickness=-1, lineType=cv2.LINE_AA)
        cv2.rectangle(out, rect_tl, rect_br, (40,40,40), thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(out, txt, (base_x, base_y), font, font_scale, col, font_thickness, lineType=cv2.LINE_AA)

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
    if S.rectify_click_mode:
        cv2.putText(out, "RECTIFY MODE: Click 4 corners (TL,TR,BR,BL)", (200, out.shape[0]-32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0),2)

    return out