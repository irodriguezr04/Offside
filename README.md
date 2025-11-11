## ⚽🎥 Offside

Bienvenido a la wiki del proyecto **Offside**.

Esta aplicación permite analizar jugadas de fútbol para ayudar a determinar si un jugador está en posición adelantada (*offside*). 

## 🔍 Qué hace
- Carga un vídeo (MP4, AVI, MOV, etc.)
- Rectifica la imagen (homografía) para transformar a vista cenital del campo
- Permite definir una línea de referencia
- Dibuja líneas paralelas y proyecta distancias
- Muestra claramente si un jugador está *OFFSIDE* o *ON-SIDE*

## 📁 Archivos principales
| Archivo | Descripción |
|----------|-------------|
| `app.py` | Interfaz gráfica y control general (Tkinter) |
| `draw.py` | Dibujo de líneas, overlays y HUD |
| `geometry.py` | Cálculos geométricos (ángulos, proyecciones, distancias) |
| `state.py` | Estado global de la aplicación |
| `video_io.py` | Carga de vídeos y guardado de frames |

## 🚀 Instalación

Sigue estos pasos para instalar y ejecutar el proyecto **Offside**.

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/irodriguezr04/Offside.git
cd Offside
```

### 2️⃣ Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate    # o venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### 3️⃣ Ejecutar la aplicación
```bash
cd src
python app.py
```

## 🎮 Controles y Atajos
| Acción | Tecla / Botón |
|--------|----------------|
| Cargar vídeo | Botón `Cargar vídeo` |
| Rectificar (homografía) | `H` o botón `Rectificar` |
| Definir línea de referencia | `R` o botón `Línea de referencia` |
| Activar arrastre de líneas | `L` o botón `Arrastre de Líneas` |
| Cambiar lado del gol | `C` o botón `Cambiar Lado` |
| Guardar frame | `G` o botón `Guardar Frame` |
| Borrar todo | `B` o botón `Borrar` |
| Avanzar 1 frame | `D` |
| Retroceder 1 frame | `A` |
| Avanzar 10 frames | `W` |
| Retroceder 10 frames | `S` |
| Play / Pausa | `Espacio` |
| Salir | `Q` |

💡 Consejo: activa el modo de arrastre después de definir la línea de referencia para ajustar las líneas con precisión.

## 🧠 Cómo usar las herramientas principales

### 🟥 1. Rectificación (Homografía)

La rectificación corrige la perspectiva para que las líneas del campo parezcan paralelas desde una vista cenital.

1. Pulsa **Rectificar (H)** o presiona `H`.  
2. Haz **4 clics** sobre la imagen en este orden: **Top-Left → Top-Right → Bottom-Right → Bottom-Left**.  
   Selecciona un rectángulo real del campo (por ejemplo, las 4 esquinas del área o una zona rectangular del césped).  
3. Cuando se calcule correctamente la homografía, aparecerá un mensaje de confirmación.  
4. Desde este momento, las mediciones y líneas se basan en la vista rectificada.  
5. Para desactivar la rectificación, usa **Borrar (B)**, que también limpia la homografía.

📏 **Consejo:** si las líneas del campo del vídeo no son perfectamente paralelas, la rectificación ayuda a eliminar ese error visual.

---

### 🟩 2. Línea de Referencia

La línea de referencia define la **dirección base** de las líneas paralelas que determinan la posición del jugador.

1. Pulsa **Línea de Referencia (R)** o presiona `R`.  
2. Haz **dos clics** sobre el campo para marcar los extremos de la línea de referencia (por ejemplo, la línea del área o el último defensor).  
3. Esa línea se usará como guía para dibujar las líneas de ataque y defensa.  
4. Una vez marcada, puedes seguir con el modo de **arrastre** para ajustar las líneas paralelas.

💡 **Consejo:** elige una línea clara del campo (horizontal respecto a la portería) para mejorar la precisión visual.

---

### 🟦 3. Arrastre de Líneas

Permite mover las líneas paralelas para ajustar la posición del jugador y el defensor.

1. Pulsa **Arrastre de Líneas (L)** o presiona `L`.  
2. Haz clic y arrastra con el ratón las líneas mostradas en pantalla.
3. La aplicación mostrará automáticamente si el atacante está **OFFSIDE** o **ON-SIDE** según la posición relativa.  
4. Puedes reajustarlas tantas veces como quieras o redefinir la línea de referencia si cambias de jugada.

💡 **Tip:** tras activar la **rectificación**, las líneas se moverán en un plano corregido, evitando errores de perspectiva.
