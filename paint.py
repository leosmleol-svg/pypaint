import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import random
import os
from PIL import ImageGrab

# Цвета темы GitHub IDE
COLORS = {
    "bg": "#0d1117",
    "panel": "#161b22",
    "border": "#30363d",
    "accent": "#58a6ff",
    "text": "#c9d1d9",
    "green": "#238636", # Цвет кнопки Save
    "red": "#da3633"     # Цвет кнопки Clear
}

class PyPaint3D(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("pypaint.py - Advanced Editor (Paint 3D Brushes)")
        self.geometry("1200x900")
        self.configure(fg_color=COLORS["bg"])

        # Состояние
        self.current_color = "#58a6ff"
        self.brush_type = "marker" # marker, spray, pixel, eraser
        self.thickness = 5
        self.canvas_w, self.canvas_h = 900, 650
        self.lx, self.ly = None, None
        
        self.setup_ui()

    def setup_ui(self):
        # --- SIDEBAR (Инструменты в стиле Paint 3D) ---
        sidebar = ctk.CTkFrame(self, width=110, fg_color=COLORS["panel"], corner_radius=0, border_width=1, border_color=COLORS["border"])
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="BRUSHES", font=("Consolas", 12, "bold"), text_color=COLORS["text"]).pack(pady=20)

        # Кнопки выбора кистей
        brushes = [
            ("🖋️ Marker", "marker"), 
            ("💨 Spray", "spray"), 
            ("🟦 Pixel", "pixel"), 
            ("🧽 Eraser", "eraser")
        ]
        
        self.brush_btns = {}
        for text, b_type in brushes:
            btn = ctk.CTkButton(
                sidebar, 
                text=text, 
                anchor="w",
                fg_color="#30363d", 
                hover_color=COLORS["accent"], 
                text_color=COLORS["text"],
                font=("Consolas", 12),
                height=40,
                command=lambda t=b_type: self.set_brush(t)
            )
            btn.pack(pady=5, padx=10, fill="x")
            self.brush_btns[b_type] = btn
            
        # Подсветка активной кисти по умолчанию
        self.set_brush("marker")

        # Выбор цвета
        ctk.CTkLabel(sidebar, text="COLOR", font=("Consolas", 10), text_color="#8b949e").pack(pady=(20, 0))
        self.col_prev = tk.Button(sidebar, bg=self.current_color, width=5, height=2, relief="flat", command=self.pick_color)
        self.col_prev.pack(pady=5, padx=10, fill="x")

        # Размер
        ctk.CTkLabel(sidebar, text="SIZE", font=("Consolas", 10), text_color="#8b949e").pack(pady=(20, 0))
        self.size_sl = ctk.CTkSlider(sidebar, from_=1, to=50, orientation="vertical", width=16, height=250)
        self.size_sl.set(self.thickness)
        self.size_sl.pack(pady=10, expand=True)

        # --- MAIN AREA ---
        self.main_area = ctk.CTkFrame(self, fg_color="#010409", corner_radius=0)
        self.main_area.pack(expand=True, fill="both")

        # --- TOP TOOLBAR (Сохранить и Удалить) ---
        self.toolbar = ctk.CTkFrame(self.main_area, height=45, fg_color=COLORS["panel"], corner_radius=0, border_width=1, border_color=COLORS["border"])
        self.toolbar.pack(side="top", fill="x")
        
        # Кнопка Сохранить (Зеленая Commit Changes)
        self.btn_save = ctk.CTkButton(
            self.toolbar, 
            text="COMMIT (SAVE PNG)", 
            font=("Consolas", 12, "bold"),
            fg_color=COLORS["green"], 
            hover_color="#2ea043",
            width=160,
            command=self.save_image
        )
        self.btn_save.pack(side="left", padx=15)
        
        # Кнопка Удалить/Очистить (Красная Clear)
        self.btn_clear = ctk.CTkButton(
            self.toolbar, 
            text="DISCARD (CLEAR ALL)", 
            font=("Consolas", 12),
            fg_color=COLORS["red"], 
            hover_color="#f85149",
            width=160,
            command=self.clear_canvas
        )
        self.btn_clear.pack(side="right", padx=15)

        # --- ХОЛСТ С КУРСОРОМ "cross" ---
        self.canvas_frame = tk.Frame(self.main_area, bg=COLORS["border"], padx=1, pady=1)
        self.canvas_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.canv = tk.Canvas(
            self.canvas_frame, 
            width=self.canvas_w, 
            height=self.canvas_h, 
            bg="white", 
            highlightthickness=0,
            cursor="cross"
        )
        self.canv.pack()

        self.canv.bind("<Button-1>", self.reset_coords)
        self.canv.bind("<B1-Motion>", self.paint)

    # --- ЛОГИКА ---
    def set_brush(self, b_type):
        self.brush_type = b_type
        # Визуальная подсветка активной кнопки
        for b in self.brush_btns.values():
            b.configure(fg_color="#30363d")
        if b_type in self.brush_btns:
            self.brush_btns[b_type].configure(fg_color=COLORS["accent"])

    def pick_color(self):
        c = colorchooser.askcolor(initialcolor=self.current_color)[1]
        if c: 
            self.current_color = c
            self.col_prev.config(bg=c)
            if self.brush_type == "eraser":
                self.set_brush("marker")

    def reset_coords(self, e): self.lx, self.ly = e.x, e.y

    def paint(self, e):
        size = int(self.size_sl.get())
        # Определяем цвет отрисовки (белый для ластика)
        draw_color = "white" if self.brush_type == "eraser" else self.current_color
        
        if self.brush_type in ["marker", "eraser"]:
            # Обычная плавная линия
            self.canv.create_line(self.lx, self.ly, e.x, e.y, width=size, fill=draw_color, capstyle=tk.ROUND, smooth=True)
        
        elif self.brush_type == "spray":
            # Баллончик: рисуем случайные точки в радиусе `size`
            density = size * 2
            for _ in range(density):
                rx = random.randint(-size, size)
                ry = random.randint(-size, size)
                # Рисуем микро-овал (точку)
                self.canv.create_oval(e.x+rx, e.y+ry, e.x+rx+1, e.y+ry+1, fill=draw_color, outline=draw_color)
        
        elif self.brush_type == "pixel":
            # Пиксель-арт: рисуем четкие квадраты без сглаживания
            self.canv.create_rectangle(e.x-size/2, e.y-size/2, e.x+size/2, e.y+size/2, fill=draw_color, outline=draw_color)

        self.lx, self.ly = e.x, e.y

    # --- КНОПКИ УПРАВЛЕНИЯ ---
    def save_image(self):
        # Функция сохранения холста
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path:
            # Получаем экранные координаты холста
            x = self.canv.winfo_rootx()
            y = self.canv.winfo_rooty()
            # Делаем скриншот строго этой области
            ImageGrab.grab().crop((x, y, x + self.canvas_w, y + self.canvas_h)).save(file_path)
            messagebox.showinfo("IDE", "Changes committed to local workspace.")

    def clear_canvas(self):
        # Функция очистки (Удалить всё)
        if messagebox.askyesno("Discord changes?", "This will delete your art without saving. Proceed?"):
            self.canv.delete("all")

if __name__ == "__main__":
    PyPaint3D().mainloop()