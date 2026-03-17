import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import ImageGrab, Image

# Настройки оформления
BG_DARK = "#1a1a1a"
PANEL_DARK = "#202020"
ACCENT_BLUE = "#0078d4"

class StandardPaint(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Paint Pro")
        self.geometry("1200x850")
        self.configure(fg_color=BG_DARK)

        # Параметры рисования
        self.current_color = "#000000"
        self.brush_thickness = 5
        self.eraser_mode = False
        self.canvas_w, self.canvas_h = 945, 591
        self.old_x, self.old_y = None, None

        self.setup_ui()

    def setup_ui(self):
        # --- Верхняя панель (Файл и Холст) ---
        self.top_bar = ctk.CTkFrame(self, height=50, fg_color=BG_DARK, corner_radius=0)
        self.top_bar.pack(side="top", fill="x")
        
        ctk.CTkButton(self.top_bar, text="💾 СОХРАНИТЬ", width=150, fg_color=ACCENT_BLUE, 
                      command=self.save_file).pack(side="left", padx=10)
        
        ctk.CTkButton(self.top_bar, text="⚙️ Размер холста", width=140, height=30, fg_color="#333333", 
                      command=self.ask_new_size).pack(side="left", padx=5)

        ctk.CTkButton(self.top_bar, text="🗑️ Очистить всё", width=120, height=30, fg_color="#552222", 
                      command=lambda: self.canvas.delete("all")).pack(side="right", padx=10)

        # --- Боковая панель инструментов ---
        self.side_bar = ctk.CTkFrame(self, width=80, fg_color=PANEL_DARK, corner_radius=0)
        self.side_bar.pack(side="left", fill="y", padx=2, pady=2)

        self.btn_brush = ctk.CTkButton(self.side_bar, text="🖌️", width=50, height=50, fg_color=ACCENT_BLUE, command=self.activate_brush)
        self.btn_brush.pack(pady=15)
        
        self.btn_eraser = ctk.CTkButton(self.side_bar, text="🧽", width=50, height=50, fg_color="#333333", command=self.activate_eraser)
        self.btn_eraser.pack(pady=5)

        ctk.CTkLabel(self.side_bar, text="Размер", font=("Arial", 11)).pack(pady=(30,0))
        self.thickness_slider = ctk.CTkSlider(self.side_bar, from_=1, to=100, orientation="vertical", width=20, command=self.change_thickness)
        self.thickness_slider.set(self.brush_thickness)
        self.thickness_slider.pack(pady=15, expand=True)

        # --- Нижняя панель (Цвета) ---
        self.color_bar = ctk.CTkFrame(self, height=70, fg_color=PANEL_DARK, corner_radius=0)
        self.color_bar.pack(side="bottom", fill="x")

        # Быстрые цвета
        quick_colors = ["#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
        for color in quick_colors:
            btn = ctk.CTkButton(self.color_bar, text="", width=25, height=25, fg_color=color, corner_radius=12, 
                                command=lambda c=color: self.set_active_color(c))
            btn.pack(side="left", padx=6)
        
        ctk.CTkButton(self.color_bar, text="Палитра", width=100, command=self.choose_custom_color).pack(side="right", padx=20)

        # --- Область холста ---
        self.work_area = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.work_area.pack(fill="both", expand=True)
        
        self.canvas_container = tk.Frame(self.work_area, bg="#333333", padx=1, pady=1)
        self.canvas_container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.canvas = tk.Canvas(self.canvas_container, width=self.canvas_w, height=self.canvas_h, 
                                bg="white", highlightthickness=0, cursor="pencil")
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    # --- Методы логики ---
    def set_active_color(self, color):
        self.current_color = color
        self.activate_brush()

    def change_thickness(self, value):
        self.brush_thickness = int(value)

    def activate_brush(self):
        self.eraser_mode = False
        self.btn_brush.configure(fg_color=ACCENT_BLUE)
        self.btn_eraser.configure(fg_color="#333333")

    def activate_eraser(self):
        self.eraser_mode = True
        self.btn_eraser.configure(fg_color=ACCENT_BLUE)
        self.btn_brush.configure(fg_color="#333333")

    def choose_custom_color(self):
        color = colorchooser.askcolor(title="Выберите цвет")[1]
        if color:
            self.set_active_color(color)

    def ask_new_size(self):
        # Простое окно ввода
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("250x180")
        dialog.title("Размер")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Ширина x Высота (px)").pack(pady=10)
        w_entry = ctk.CTkEntry(dialog, placeholder_text="945", width=150); w_entry.pack()
        h_entry = ctk.CTkEntry(dialog, placeholder_text="591", width=150); h_entry.pack(pady=5)
        
        def apply():
            try:
                self.canvas_w = int(w_entry.get())
                self.canvas_h = int(h_entry.get())
                self.canvas.config(width=self.canvas_w, height=self.canvas_h)
                self.canvas.delete("all")
                dialog.destroy()
            except: pass
            
        ctk.CTkButton(dialog, text="Применить", command=apply).pack(pady=10)

    def on_press(self, event):
        self.old_x, self.old_y = event.x, event.y

    def on_move(self, event):
        if self.old_x and self.old_y:
            draw_color = "white" if self.eraser_mode else self.current_color
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width=self.brush_thickness, fill=draw_color, 
                                    capstyle=tk.ROUND, smooth=True)
            self.old_x, self.old_y = event.x, event.y

    def on_release(self, event):
        self.old_x, self.old_y = None, None

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG Image", "*.png"), ("Icon File", "*.ico")])
        if file_path:
            # Получаем координаты холста на экране
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            img = ImageGrab.grab().crop((x, y, x + self.canvas_w, y + self.canvas_h))
            
            if file_path.endswith(".ico"):
                img.convert("RGBA").save(file_path, format="ICO", sizes=[(256, 256)])
            else:
                img.save(file_path)
            messagebox.showinfo("Paint Pro", "Файл успешно сохранен!")

if __name__ == "__main__":
    app = StandardPaint()
    app.mainloop()