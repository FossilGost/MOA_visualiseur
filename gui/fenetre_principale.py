import math
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculateur de MOA")
        self.geometry("1280x860")
        self.minsize(500,500)
        self.iconbitmap("gui/assets/buste_knight.ico")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.colors = {
            "bg": "#0f141c",
            "panel": "#171d27",
            "panel_alt": "#202838",
            "text": "#f5f7fb",
            "muted": "#a8b3c7",
            "line": "#f77f00",
            "line_soft": "#f9c74f",
            "blue": "#0057b7",
            "red": "#e63946",
            "green": "#06d6a0",
        }

        self.configure(fg_color=self.colors["bg"])

        self.reference_image_path = "gui/assets/M_01.png"
        self.image_original = Image.open(self.reference_image_path)
        self.image_original_width, self.image_original_height = self.image_original.size
        self.image_height = 500
        self.image_scale = self.image_height / self.image_original_height
        self.image_width = int(self.image_original_width * self.image_scale)
        self.resample_filter = getattr(Image, "Resampling", Image).LANCZOS
        self.image_king = self.image_original.resize(
            (self.image_width, self.image_height),
            self.resample_filter,
        )
        self.tk_img = None
        self.current_diameters = None
        self.photo_offset_x = 0
        self.photo_offset_y = 0
        self.max_photo_width = 520
        self.max_photo_height = 680
        self.max_photo_panel_width = 460

        # Réglage manuel du cercle jaune de tête sur l'image d'origine M_01.png.
        # Modifie ces 4 valeurs si le cercle ne va pas exactement du menton à la cime.
        # x = horizontal, y = vertical, en pixels sur l'image originale.
        self.head_left_px = 100
        self.head_right_px = 164
        self.head_top_px = 22
        self.head_bottom_px = 110

        self.head_oval = (
            self.head_left_px,
            self.head_top_px,
            self.head_right_px,
            self.head_bottom_px,
        )
        self.head_center = (
            (self.head_left_px + self.head_right_px) / 2,
            (self.head_top_px + self.head_bottom_px) / 2,
        )
        self.torso_oval = (156, 178, 194, 216)
        self.torso_center = (175, 197)
        self.head_height_cm = 26
        self.head_reference_height_px = self.head_bottom_px - self.head_top_px
        self.pixel_per_cm = (
            self.head_reference_height_px * self.image_scale
        ) / self.head_height_cm

        self.init_ui()

    def init_ui(self):
        self.sidebar_min_width = 118
        self.sidebar_max_width = 160
        self.sidebar = ctk.CTkFrame(
            self,
            width=self.sidebar_max_width,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        self.sidebar.pack(side="left", fill="y", padx=(8, 10), pady=10)
        self.sidebar.pack_propagate(False)

        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="MOA",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text"],
        )
        self.sidebar_title.pack(pady=(20, 2))
        self.sidebar_subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Minute of Angle",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["muted"],
        )
        self.sidebar_subtitle.pack(pady=(0, 22))

        self.button1 = ctk.CTkButton(
            self.sidebar,
            text="Accueil",
            height=34,
            command=self.afficher_accueil,
        )
        self.button1.pack(fill="x", padx=12, pady=(0, 8))

        self.button2 = ctk.CTkButton(
            self.sidebar,
            text="Explication",
            height=34,
            command=self.afficher_explication,
        )
        self.button2.pack(fill="x", padx=12, pady=8)

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg"],
            corner_radius=0,
        )
        self.main_frame.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

        self.bind("<Configure>", self.update_sidebar_layout)
        self.afficher_accueil()

    def afficher_accueil(self):
        self.clear_main_frame()

        self.header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        self.header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            self.header_frame,
            text="Calculateur de dispersion en MOA",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=18, pady=(14, 2))
        ctk.CTkLabel(
            self.header_frame,
            text="Entrez la précision de l'arme pour visualiser le diamètre du groupement à 100, 200 et 300 yards.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["muted"],
            wraplength=780,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.left_frame = ctk.CTkFrame(
            self.content_frame,
            width=720,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.left_frame.pack_propagate(False)

        self.right_frame = ctk.CTkFrame(
            self.content_frame,
            width=self.max_photo_panel_width,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        self.right_frame.pack(side="right", fill="y", expand=False, padx=(0, 0))
        self.right_frame.pack_propagate(False)

        self.create_controls()
        self.create_photo_canvas()
        self.create_diagram()

    def create_controls(self):
        form_frame = ctk.CTkFrame(
            self.left_frame,
            height=112,
            fg_color=self.colors["panel_alt"],
            corner_radius=8,
        )
        form_frame.pack(fill="x", padx=14, pady=(12, 8))
        form_frame.pack_propagate(False)

        ctk.CTkLabel(
            form_frame,
            text="Valeur de MOA",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            form_frame,
            text="Exemple : 1, 2.5 ou 4.5",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["muted"],
        ).pack(anchor="w", padx=12, pady=(0, 6))

        input_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=12, pady=(0, 6))

        self.MOA_Entry = ctk.CTkEntry(
            input_row,
            placeholder_text="MOA",
            height=32,
        )
        self.MOA_Entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.MOA_Entry.bind("<Return>", lambda _event: self.calculer_moa())

        ctk.CTkButton(
            input_row,
            text="Calculer",
            height=32,
            width=100,
            command=self.calculer_moa,
        ).pack(side="right")

        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ffb4a2",
        )
        self.error_label.pack(anchor="w", padx=12, pady=(0, 4))

        self.result_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color=self.colors["panel_alt"],
            corner_radius=8,
        )
        self.result_frame.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            self.result_frame,
            text="À retenir",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        moa_note = (
            "Le MOA est une mesure d'angle : plus la distance augmente, plus le "
            "groupement apparent s'ouvre. Une arme à 2 MOA ne devient pas moins "
            "précise à 300 yards ; le même angle couvre simplement un cercle plus grand."
        )
        ctk.CTkLabel(
            self.result_frame,
            text=moa_note,
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"],
            justify="left",
            wraplength=650,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        legend_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        legend_frame.pack(fill="x", padx=14, pady=(0, 10))

        for text, color in (
            ("100 yd = 91,44 m", self.colors["blue"]),
            ("200 yd = 182,88 m", self.colors["red"]),
            ("300 yd = 274,32 m = 0,274 km", self.colors["green"]),
        ):
            item = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item.pack(side="left", padx=(0, 18))

            ctk.CTkFrame(item, width=22, height=3, fg_color=color).pack(
                side="left", padx=(0, 6)
            )
            ctk.CTkLabel(
                item,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["muted"],
            ).pack(side="left")

    def create_diagram(self):
        self.draw_frame = ctk.CTkFrame(
            self.left_frame,
            height=230,
            fg_color=self.colors["panel_alt"],
            corner_radius=8,
        )
        self.draw_frame.pack(fill="x", expand=False, padx=14, pady=(0, 14))
        self.draw_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.draw_frame,
            text="Visualisation de l'ouverture angulaire",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=(14, 8))

        self.canvas = tk.Canvas(
            master=self.draw_frame,
            width=800,
            height=160,
            bg="#121821",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, pady=(0, 12), padx=14)

        self.diagram_center_y = 120
        self.diagram_max_radius = 68
        self.diagram_x = {0: 80, 100: 310, 200: 530, 300: 750}

        self.ligne_centrale = self.canvas.create_line(
            self.diagram_x[0],
            self.diagram_center_y,
            self.diagram_x[300],
            self.diagram_center_y,
            width=3,
            fill=self.colors["line"],
        )
        self.ligne_haut = self.canvas.create_line(
            self.diagram_x[0],
            self.diagram_center_y,
            self.diagram_x[300],
            86,
            width=3,
            fill=self.colors["line_soft"],
        )
        self.ligne_bas = self.canvas.create_line(
            self.diagram_x[0],
            self.diagram_center_y,
            self.diagram_x[300],
            154,
            width=3,
            fill=self.colors["line_soft"],
        )

        self.cible_100 = self.canvas.create_oval(
            298, 108, 322, 132, fill=self.colors["blue"], outline=""
        )
        self.cible_200 = self.canvas.create_oval(
            512, 102, 548, 138, fill=self.colors["red"], outline=""
        )
        self.cible_300 = self.canvas.create_oval(
            728, 98, 772, 142, fill=self.colors["green"], outline=""
        )

        self.distance_labels = {}
        for distance, text in ((0, "0 yd"), (100, "100 yd"), (200, "200 yd"), (300, "300 yd")):
            self.distance_labels[distance] = self.canvas.create_text(
                self.diagram_x[distance],
                192,
                text=text,
                fill="#f5f7fb",
                font=("Arial", 10),
            )

        self.label_100 = self.canvas.create_text(
            self.diagram_x[100], 216, text="-- cm", fill="#f5f7fb", font=("Arial", 10, "bold")
        )
        self.label_200 = self.canvas.create_text(
            self.diagram_x[200], 216, text="-- cm", fill="#f5f7fb", font=("Arial", 10, "bold")
        )
        self.label_300 = self.canvas.create_text(
            self.diagram_x[300], 216, text="-- cm", fill="#f5f7fb", font=("Arial", 10, "bold")
        )

        self.moa_title = self.canvas.create_text(
            415,
            24,
            text="MOA",
            fill="#f9c74f",
            font=("Arial", 13, "italic"),
        )
        self.canvas.bind("<Configure>", self.update_diagram_layout)
        self.after(50, self.update_diagram_layout)

    def create_photo_canvas(self):
        ctk.CTkLabel(
            self.right_frame,
            text="Impact projeté sur la silhouette",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        self.canvas_photo = tk.Canvas(
            self.right_frame,
            width=self.image_width,
            height=self.image_height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas_photo.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.tk_img = ImageTk.PhotoImage(self.image_king)
        self.photo_image_item = self.canvas_photo.create_image(0, 0, image=self.tk_img, anchor="nw")

        head_x1, head_y1, head_x2, head_y2 = self.scaled_photo_coords(*self.head_oval)
        torso_x1, torso_y1, torso_x2, torso_y2 = self.scaled_photo_coords(*self.torso_oval)

        self.head_reference_circle = self.canvas_photo.create_oval(
            head_x1,
            head_y1,
            head_x2,
            head_y2,
            outline="#f9c74f",
            width=2,
        )
        self.torso_reference_circle = self.canvas_photo.create_oval(
            torso_x1,
            torso_y1,
            torso_x2,
            torso_y2,
            outline="#d8a928",
            width=1,
        )
        self.cercle_100 = self.canvas_photo.create_oval(
            head_x1, head_y1, head_x2, head_y2, outline=self.colors["blue"], width=2
        )
        self.cercle_200 = self.canvas_photo.create_oval(
            head_x1, head_y1, head_x2, head_y2, outline=self.colors["red"], width=2
        )
        self.cercle_300 = self.canvas_photo.create_oval(
            head_x1, head_y1, head_x2, head_y2, outline=self.colors["green"], width=2
        )
        self.torso_cercle_100 = self.canvas_photo.create_oval(
            torso_x1, torso_y1, torso_x2, torso_y2, outline="#174f8f", width=1
        )
        self.torso_cercle_200 = self.canvas_photo.create_oval(
            torso_x1, torso_y1, torso_x2, torso_y2, outline="#9f2430", width=1
        )
        self.torso_cercle_300 = self.canvas_photo.create_oval(
            torso_x1, torso_y1, torso_x2, torso_y2, outline="#05906f", width=1
        )

        legend = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        legend.pack(anchor="w", padx=14, pady=(0, 12))

        for text, color in (
            ("Tête : zone principale", "#f9c74f"),
            ("Cœur : zone secondaire", "#d8a928"),
        ):
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(anchor="w", pady=(0, 3))
            ctk.CTkFrame(item, width=18, height=3, fg_color=color).pack(
                side="left", padx=(0, 6)
            )
            ctk.CTkLabel(
                item,
                text=text,
                font=ctk.CTkFont(size=12),
            text_color=self.colors["muted"],
            ).pack(side="left")

        self.canvas_photo.bind("<Configure>", self.update_photo_layout)
        self.after(50, self.update_photo_layout)

    def afficher_explication(self):
        self.clear_main_frame()

        panel = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        panel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            panel,
            text="Comprendre le MOA des armes",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=22, pady=(22, 10))

        explanation = (
            "Le MOA signifie Minute of Angle, ou minute d'angle. C'est une unité "
            "angulaire utilisée pour décrire la précision d'une arme, le réglage "
            "d'une lunette ou la taille d'un groupement. Comme il s'agit d'un angle, "
            "le cercle couvert augmente avec la distance : une même valeur de MOA "
            "donne un diamètre deux fois plus grand à 200 yards qu'à 100 yards, et "
            "trois fois plus grand à 300 yards.\n\n"
            "En pratique, un groupement de 1 MOA correspond à environ 2,91 cm de "
            "diamètre à 100 yards. Une arme annoncée à 2 MOA regroupe donc ses tirs "
            "dans un cercle d'environ 5,82 cm à 100 yards, si les conditions de tir "
            "et les munitions sont régulières."
        )

        ctk.CTkLabel(
            panel,
            text=explanation,
            font=ctk.CTkFont(size=15),
            text_color=self.colors["text"],
            justify="left",
            wraplength=780,
        ).pack(anchor="w", padx=22, pady=(0, 18))

        ctk.CTkLabel(
            panel,
            text="Formule utilisée",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=22, pady=(6, 8))

        ctk.CTkLabel(
            panel,
            text="Diamètre = 2 x tan((MOA / 60) degrés) x distance",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["muted"],
            justify="left",
            wraplength=780,
        ).pack(anchor="w", padx=22, pady=(0, 22))

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def update_sidebar_layout(self, event=None):
        if event is not None and event.widget is not self:
            return

        width = max(self.winfo_width(), 1)
        sidebar_width = int(width * 0.085)
        sidebar_width = max(self.sidebar_min_width, min(self.sidebar_max_width, sidebar_width))
        self.sidebar.configure(width=sidebar_width)

        compact = sidebar_width <= 130
        self.sidebar_title.configure(font=ctk.CTkFont(size=22 if compact else 24, weight="bold"))
        self.sidebar_subtitle.configure(
            text="MOA" if compact else "Minute of Angle",
            font=ctk.CTkFont(size=10 if compact else 11),
        )
        button_pad = 8 if compact else 12
        self.button1.pack_configure(padx=button_pad)
        self.button2.pack_configure(padx=button_pad)

    def calculer_moa(self):
        raw_moa = self.MOA_Entry.get().strip().replace(",", ".")
        self.error_label.configure(text="")

        try:
            moa = float(raw_moa)
            if moa <= 0:
                raise ValueError
        except ValueError:
            self.error_label.configure(text="Veuillez entrer un nombre positif valide.")
            return

        diameters = {
            100: self.calculate_diameter(moa, 100),
            200: self.calculate_diameter(moa, 200),
            300: self.calculate_diameter(moa, 300),
        }

        self.update_diagram(diameters)
        self.update_photo_circles(diameters)

    def calculate_diameter(self, moa, yards):
        distance_cm = yards * 91.44
        angle_radians = math.radians(moa / 60)
        return round(2 * math.tan(angle_radians) * distance_cm, 2)

    def scaled_photo_coords(self, x1, y1, x2, y2):
        scale = self.image_scale
        return (
            self.photo_offset_x + x1 * scale,
            self.photo_offset_y + y1 * scale,
            self.photo_offset_x + x2 * scale,
            self.photo_offset_y + y2 * scale,
        )

    def update_photo_layout(self, _event=None):
        available_width = max(self.canvas_photo.winfo_width(), 80)
        available_height = max(self.canvas_photo.winfo_height(), 160)
        fit_width = min(available_width, self.max_photo_width)
        fit_height = min(available_height, self.max_photo_height)
        scale_x = fit_width / self.image_original_width
        scale_y = fit_height / self.image_original_height
        self.image_scale = min(scale_x, scale_y)
        self.image_width = max(1, int(self.image_original_width * self.image_scale))
        self.image_height = max(1, int(self.image_original_height * self.image_scale))
        self.photo_offset_x = (available_width - self.image_width) / 2
        self.photo_offset_y = (available_height - self.image_height) / 2
        self.pixel_per_cm = (
            self.head_reference_height_px * self.image_scale
        ) / self.head_height_cm

        resized = self.image_original.resize(
            (self.image_width, self.image_height),
            self.resample_filter,
        )
        self.tk_img = ImageTk.PhotoImage(resized)
        self.canvas_photo.itemconfig(self.photo_image_item, image=self.tk_img)
        self.canvas_photo.coords(
            self.photo_image_item,
            self.photo_offset_x,
            self.photo_offset_y,
        )

        head_coords = self.scaled_photo_coords(*self.head_oval)
        torso_coords = self.scaled_photo_coords(*self.torso_oval)
        self.canvas_photo.coords(self.head_reference_circle, *head_coords)
        self.canvas_photo.coords(self.torso_reference_circle, *torso_coords)

        if self.current_diameters:
            self.update_photo_circles(self.current_diameters)
            return

        for item in (self.cercle_100, self.cercle_200, self.cercle_300):
            self.canvas_photo.coords(item, *head_coords)
        for item in (self.torso_cercle_100, self.torso_cercle_200, self.torso_cercle_300):
            self.canvas_photo.coords(item, *torso_coords)

    def update_diagram_layout(self, _event=None):
        width = max(self.canvas.winfo_width(), 320)
        height = max(self.canvas.winfo_height(), 120)
        margin_x = max(54, min(140, int(width * 0.08)))
        line_width = width - (margin_x * 2)

        top_space = 44
        bottom_space = 48
        self.diagram_center_y = max(top_space + 18, min(height - bottom_space, int(height * 0.46)))
        self.diagram_x = {
            0: margin_x,
            100: margin_x + int(line_width / 3),
            200: margin_x + int((line_width * 2) / 3),
            300: width - margin_x,
        }
        self.diagram_max_radius = max(
            8,
            min(
                72,
                self.diagram_center_y - top_space,
                height - self.diagram_center_y - bottom_space,
            ),
        )

        label_y = height - 38
        value_y = height - 18

        self.canvas.coords(
            self.ligne_centrale,
            self.diagram_x[0],
            self.diagram_center_y,
            self.diagram_x[300],
            self.diagram_center_y,
        )
        self.canvas.coords(self.moa_title, width / 2, 20)

        for distance, item in self.distance_labels.items():
            self.canvas.coords(item, self.diagram_x[distance], label_y)

        self.canvas.coords(self.label_100, self.diagram_x[100], value_y)
        self.canvas.coords(self.label_200, self.diagram_x[200], value_y)
        self.canvas.coords(self.label_300, self.diagram_x[300], value_y)

        if self.current_diameters:
            self.update_diagram(self.current_diameters)
            return

        default_radiuses = {100: 12, 200: 18, 300: 24}
        self.update_diagram_shapes(default_radiuses)

    def update_diagram(self, diameters):
        self.current_diameters = diameters
        wanted_scale = 4
        max_diameter = max(diameters.values())
        scale = min(wanted_scale, (self.diagram_max_radius * 2) / max_diameter)

        radiuses = {
            distance: max(6, (diameter * scale) / 2)
            for distance, diameter in diameters.items()
        }

        self.update_diagram_shapes(radiuses)

        self.canvas.itemconfig(self.label_100, text=f"{diameters[100]:.2f} cm")
        self.canvas.itemconfig(self.label_200, text=f"{diameters[200]:.2f} cm")
        self.canvas.itemconfig(self.label_300, text=f"{diameters[300]:.2f} cm")

    def update_diagram_shapes(self, radiuses):
        center_y = self.diagram_center_y

        radius_300 = radiuses[300]
        self.canvas.coords(
            self.ligne_haut,
            self.diagram_x[0],
            center_y,
            self.diagram_x[300],
            center_y - radius_300,
        )
        self.canvas.coords(
            self.ligne_bas,
            self.diagram_x[0],
            center_y,
            self.diagram_x[300],
            center_y + radius_300,
        )

        for distance, item in (
            (100, self.cible_100),
            (200, self.cible_200),
            (300, self.cible_300),
        ):
            radius = radiuses[distance]
            center_x = self.diagram_x[distance]
            ellipse_width = max(5, radius * 0.36)
            self.canvas.coords(
                item,
                center_x - ellipse_width,
                center_y - radius,
                center_x + ellipse_width,
                center_y + radius,
            )

    def update_photo_circles(self, diameters):
        self.current_diameters = diameters
        max_diameter_px = max(diameters.values()) * self.pixel_per_cm
        head_center_x = self.photo_offset_x + self.head_center[0] * self.image_scale
        head_center_y = self.photo_offset_y + self.head_center[1] * self.image_scale
        canvas_width = max(self.canvas_photo.winfo_width(), 1)
        canvas_height = max(self.canvas_photo.winfo_height(), 1)
        head_visible_radius = max(
            18,
            min(
                head_center_x - 8,
                canvas_width - head_center_x - 8,
                head_center_y - 8,
                canvas_height - head_center_y - 8,
            ),
        )
        max_visible_radius = max(
            18,
            min(
                self.image_width * 0.42,
                self.image_height * 0.22,
                self.canvas_photo.winfo_width() * 0.28,
                head_visible_radius,
            ),
        )
        visual_scale = min(1, (max_visible_radius * 2) / max_diameter_px)

        circle_groups = (
            (
                self.head_center,
                {
                    100: self.cercle_100,
                    200: self.cercle_200,
                    300: self.cercle_300,
                },
            ),
            (
                self.torso_center,
                {
                    100: self.torso_cercle_100,
                    200: self.torso_cercle_200,
                    300: self.torso_cercle_300,
                },
            ),
        )

        for center, items in circle_groups:
            center_x = self.photo_offset_x + center[0] * self.image_scale
            center_y = self.photo_offset_y + center[1] * self.image_scale

            for distance, item in items.items():
                diameter_px = diameters[distance] * self.pixel_per_cm * visual_scale
                radius = diameter_px / 2
                self.canvas_photo.coords(
                    item,
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                )


def lancer_app():
    app = Application()
    app.mainloop()
