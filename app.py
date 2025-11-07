# app.py
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

from state import S
import geometry
from video_io import pick_video_dialog, load_video, save_frame
from draw import draw_overlay_to_frame

PROX_DIST = 15
FPS_FALLBACK = 25.0

# helper to map canvas coords to original image coords
def canvas_to_image_coords(x, y, canvas):
    sx, sy = S.disp_off
    scale = S.disp_scale
    iw, ih = S.disp_size
    if x < sx: x = sx
    if x > sx + iw: x = sx + iw
    if y < sy: y = sy
    if y > sy + ih: y = sy + ih
    rx = x - sx
    ry = y - sy
    img_x = int(round(rx / scale))
    img_y = int(round(ry / scale))
    H, W = S.frame.shape[:2]
    img_x = max(0, min(W-1, img_x))
    img_y = max(0, min(H-1, img_y))
    return (img_x, img_y)

# mouse handlers (wrap earlier logic)
def on_canvas_click(event):
    x_img, y_img = canvas_to_image_coords(event.x, event.y, app.canvas)
    if S.ref_click_mode:
        if len(S.ref_click_points) < 2:
            S.ref_click_points.append((x_img,y_img))
            app.draw()
            if len(S.ref_click_points) == 2:
                S.ref_line = (S.ref_click_points[0], S.ref_click_points[1])
                S.ref_click_mode = False
                S.ref_click_points = []
                app.draw()
        return

    if not S.drag_mode:
        return

    if S.ref_line is not None:
        for idx, rp in enumerate(S.ref_line):
            if np.hypot(rp[0]-x_img, rp[1]-y_img) <= PROX_DIST:
                S.mouse_drag['dragging'] = True
                S.mouse_drag['which'] = 'ref'
                S.mouse_drag['ref_idx'] = idx
                return

    if S.ref_line is not None and S.def_offset is not None and S.att_offset is not None:
        theta = geometry.line_angle(S.ref_line[0], S.ref_line[1])
        normal = geometry.perpendicular_unit_vector(theta)
        origin = np.array(S.ref_line[0], dtype=float)
        def_center = origin + normal * S.def_offset
        att_center = origin + normal * S.att_offset
        ref_dir = geometry.unit_vector_from_angle(theta)
        L = 2000
        def_p0 = tuple((def_center - ref_dir*L).astype(int))
        def_p1 = tuple((def_center + ref_dir*L).astype(int))
        att_p0 = tuple((att_center - ref_dir*L).astype(int))
        att_p1 = tuple((att_center + ref_dir*L).astype(int))
        d_def = geometry.point_line_distance((x_img,y_img), def_p0, def_p1)
        d_att = geometry.point_line_distance((x_img,y_img), att_p0, att_p1)
        if d_def <= PROX_DIST and d_def <= d_att:
            S.mouse_drag['dragging'] = True
            S.mouse_drag['which'] = 'def'
            mouse_proj = float(np.dot(np.array([x_img-origin[0], y_img-origin[1]]), normal))
            S.mouse_drag['drag_start_proj'] = mouse_proj
            S.mouse_drag['start_offset'] = S.def_offset
            S.cross_def = (x_img,y_img)
            return
        if d_att <= PROX_DIST and d_att < d_def:
            S.mouse_drag['dragging'] = True
            S.mouse_drag['which'] = 'att'
            mouse_proj = float(np.dot(np.array([x_img-origin[0], y_img-origin[1]]), normal))
            S.mouse_drag['drag_start_proj'] = mouse_proj
            S.mouse_drag['start_offset'] = S.att_offset
            S.cross_att = (x_img,y_img)
            return

def on_canvas_move(event):
    x_img, y_img = canvas_to_image_coords(event.x, event.y, app.canvas)
    if S.mouse_drag['dragging']:
        if S.mouse_drag['which'] == 'ref':
            pts = list(S.ref_line)
            idx = S.mouse_drag['ref_idx']
            pts[idx] = (x_img,y_img)
            S.ref_line = (pts[0], pts[1])
        else:
            theta = geometry.line_angle(S.ref_line[0], S.ref_line[1])
            normal = geometry.perpendicular_unit_vector(theta)
            origin = np.array(S.ref_line[0], dtype=float)
            mouse_proj_now = float(np.dot(np.array([x_img-origin[0], y_img-origin[1]]), normal))
            start_proj = S.mouse_drag.get('drag_start_proj', None)
            start_off = S.mouse_drag.get('start_offset', None)
            if start_proj is None or start_off is None:
                if S.mouse_drag['which'] == 'def':
                    S.def_offset = mouse_proj_now
                else:
                    S.att_offset = mouse_proj_now
            else:
                new_off = start_off + (mouse_proj_now - start_proj)
                if S.mouse_drag['which'] == 'def':
                    S.def_offset = float(new_off)
                else:
                    S.att_offset = float(new_off)
            if S.mouse_drag['which'] == 'def':
                S.cross_def = (x_img,y_img)
            else:
                S.cross_att = (x_img,y_img)
        app.draw()

def on_canvas_release(event):
    S.mouse_drag['dragging'] = False
    S.mouse_drag['which'] = None
    S.mouse_drag['ref_idx'] = None
    S.mouse_drag['drag_start_proj'] = None
    S.mouse_drag['start_offset'] = None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Offside Detector")
        top_bar = tk.Frame(root)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        left_buttons = tk.Frame(top_bar)
        left_buttons.pack(side=tk.LEFT, anchor=tk.W)

        b_load = tk.Button(left_buttons, text="Cargar vídeo", command=self.pick_and_load)
        b_load.pack(side=tk.LEFT, padx=4, pady=4)

        self.b_ref = tk.Button(left_buttons, text="Línea de Referencia (R)", command=self.start_ref_mode)
        self.b_ref.pack(side=tk.LEFT, padx=4, pady=4)

        self.b_drag = tk.Button(left_buttons, text="Arrastre de Líneas (L)", command=self.toggle_drag)
        self.b_drag.pack(side=tk.LEFT, padx=4, pady=4)

        b_save = tk.Button(left_buttons, text="Guardar frame (G)", command=save_frame)
        b_save.pack(side=tk.LEFT, padx=4, pady=4)

        b_reset = tk.Button(left_buttons, text="Borrar (B)", command=self.reset_all)
        b_reset.pack(side=tk.LEFT, padx=4, pady=4)

        self.b_goal = tk.Button(left_buttons, text="Cambiar Lado (C)", command=self.toggle_goal)
        self.b_goal.pack(side=tk.LEFT, padx=4, pady=4)

        info_text = "A = -1 frame | D = +1 frame | W = +10 frames | S = -10 frames | Space = play/pause | Q = salir"
        info_label = tk.Label(top_bar, text=info_text, anchor=tk.E, justify=tk.RIGHT)
        info_label.pack(side=tk.RIGHT, padx=8, pady=8)

        self.canvas = tk.Canvas(root, width=800, height=450, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", lambda e: on_canvas_click(e))
        self.canvas.bind("<B1-Motion>", lambda e: on_canvas_move(e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: on_canvas_release(e))
        root.bind("<Key>", self.on_key)

        self.update_loop()

    def pick_and_load(self):
        path = pick_video_dialog(self.root)
        if path:
            ok = load_video(path, app=self)
            if not ok:
                messagebox.showerror("Error", "No se pudo cargar el vídeo.")

    def start_ref_mode(self):
        S.ref_click_mode = True
        S.ref_click_points = []
        print("REF MODE ON: haz 2 clics en la línea de referencia")

    def toggle_drag(self):
        S.drag_mode = not S.drag_mode
        if S.drag_mode:
            if S.ref_line is not None and S.def_offset is None and S.att_offset is None:
                S.def_offset = 60.0
                S.att_offset = -60.0
                print("Se han inicializado las líneas paralelas (offsets por defecto). Ahora puedes arrastrar.")
        self.b_drag.config(relief=tk.SUNKEN if S.drag_mode else tk.RAISED)

    def toggle_pause(self):
        S.paused = not S.paused

    def step_forward(self):
        if S.cap is None: return
        S.paused = True
        new = min(S.total-1, S.cur_idx+1)
        S.cap.set(cv2.CAP_PROP_POS_FRAMES, new)
        ret, f = S.cap.read()
        if ret: S.frame = f; S.cur_idx = new
        self.draw()

    def step_back(self):
        if S.cap is None: return
        S.paused = True
        new = max(0, S.cur_idx-1)
        S.cap.set(cv2.CAP_PROP_POS_FRAMES, new)
        ret, f = S.cap.read()
        if ret: S.frame = f; S.cur_idx = new
        self.draw()

    def step_forw10(self):
        if S.cap is None: return
        S.paused = True
        new = min(S.total-1, S.cur_idx+10)
        S.cap.set(cv2.CAP_PROP_POS_FRAMES, new)
        ret, f = S.cap.read()
        if ret: S.frame = f; S.cur_idx = new
        self.draw()

    def step_back10(self):
        if S.cap is None: return
        S.paused = True
        new = max(0, S.cur_idx-10)
        S.cap.set(cv2.CAP_PROP_POS_FRAMES, new)
        ret, f = S.cap.read()
        if ret: S.frame = f; S.cur_idx = new
        self.draw()

    def reset_all(self):
        S.ref_line = None
        S.def_offset = None
        S.att_offset = None
        S.ref_click_mode = False
        S.ref_click_points = []
        S.cross_def = None
        S.cross_att = None
        self.draw()

    def toggle_goal(self):
        S.goal_left = not S.goal_left
        self.b_goal.config(relief=tk.SUNKEN if not S.goal_left else tk.RAISED)

    def on_key(self, event):
        k = event.keysym.lower()
        if k == 'space':
            self.toggle_pause()
        elif k == 'd':
            self.step_forward()
        elif k == 'a':
            self.step_back()
        elif k == 'w':
            self.step_forw10()
        elif k == 's':
            self.step_back10()
        elif k == 'r':
            self.start_ref_mode()
        elif k == 'l':
            self.toggle_drag()
        elif k == 'b':
            self.reset_all()
        elif k == 'g':
            save_frame()
        elif k == 'c':
            self.toggle_goal()
        elif k == 'q':
            self.root.quit()

    def draw(self):
        if S.frame is None:
            return
        frame_disp = draw_overlay_to_frame(S.frame)
        frame_h, frame_w = frame_disp.shape[:2]
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        scale_w = cw / frame_w
        scale_h = ch / frame_h
        scale = min(scale_w, scale_h, 1.0)
        new_w = int(round(frame_w * scale))
        new_h = int(round(frame_h * scale))
        off_x = (cw - new_w) // 2
        off_y = (ch - new_h) // 2
        resized = cv2.resize(frame_disp, (new_w, new_h), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
        canvas_img = np.zeros((ch, cw, 3), dtype=np.uint8)
        canvas_img[off_y:off_y+new_h, off_x:off_x+new_w] = resized
        img_rgb = cv2.cvtColor(canvas_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        S.photo = ImageTk.PhotoImage(image=img_pil)
        S.disp_scale = scale
        S.disp_off = (off_x, off_y)
        S.disp_size = (new_w, new_h)
        self.canvas.create_image(0,0, image=S.photo, anchor=tk.NW)

    def update_loop(self):
        if S.cap is not None and not S.paused:
            ret, f = S.cap.read()
            if not ret:
                S.paused = True
            else:
                S.frame = f.copy()
                S.cur_idx = int(S.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
        if S.frame is not None:
            self.draw()
        ms = int(1000.0 / (S.fps or FPS_FALLBACK))
        self.root.after(max(10, ms), self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()