# state.py
from typing import Optional, Tuple

# Estado global compartido

class State:
    cap = None
    frame = None # ultimo frame BGR (numpy) (original resolution)
    photo = None # PhotoImage para tkinter
    cur_idx = 0
    total = 0
    fps = 25.0
    paused = True

    # referencia / lineas
    ref_line = None # ((x0,y0),(x1,y1)) coords in original frame space
    def_offset = None
    att_offset = None

    ref_click_mode = False
    ref_click_points = []

    drag_mode = False
    mouse_drag = { 'dragging': False, 'which': None, 'ref_idx': None,
    'drag_start_proj': None, 'start_offset': None }

    cross_def = None
    cross_att = None

    goal_left = True

    # display transform (set in App.draw)
    disp_scale = 1.0
    disp_off = (0,0) # offset (x,y) in canvas where the top-left of the resized image is placed
    disp_size = (0,0) # (w,h) of the resized image on canvas

    # --- HOMOGRAFÍA / RECTIFICACIÓN ---
    homography = None # 3x3 numpy array (cv2) o None
    homography_inv = None # inversa para transformar de vuelta
    rectify_click_mode = False
    rectify_click_points = [] # hasta 4 puntos en imagen original (TL,TR,BR,BL)
    rectify_dst_size = (1000, 600) # tamaño del plano rectificado destino (w,h)

S = State()