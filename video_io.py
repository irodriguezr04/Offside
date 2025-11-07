# video_io.py
import os
import cv2
from tkinter import filedialog, messagebox
from state import S

FPS_FALLBACK = 25.0

def pick_video_dialog(parent=None):
    path = filedialog.askopenfilename(title="Selecciona un vídeo",
                                      filetypes=[("Vídeo", ("*.mp4","*.avi","*.mov","*.mkv")),("All","*.*")])
    return path

def load_video(path, app=None):
    """
    Carga vídeo en S.cap y deja primer frame en S.frame.
    Si app se pasa, pone el nombre en la ventana (title).
    Devuelve True/False.
    """
    if S.cap is not None:
        try:
            S.cap.release()
        except:
            pass
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        if app:
            messagebox.showerror("Error", f"No se puede abrir: {path}")
        return False
    S.cap = cap
    S.total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    S.fps = cap.get(cv2.CAP_PROP_FPS) or FPS_FALLBACK
    ret, frame = cap.read()
    if not ret:
        if app:
            messagebox.showerror("Error", "No se pudo leer el primer fotograma.")
        return False
    S.frame = frame.copy()
    S.cur_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
    S.paused = True
    if app:
        base = os.path.basename(path)
        app.root.title(f"Offside Detector - {base}")
    return True

def save_frame():
    if S.frame is None:
        messagebox.showinfo("Guardar", "No hay frame para guardar.")
        return None
    os.makedirs("frames", exist_ok=True)
    fname = f"frames/frame_{S.cur_idx:06d}.png"
    cv2.imwrite(fname, S.frame)
    messagebox.showinfo("Guardar", f"Guardado: {fname}")
    return fname