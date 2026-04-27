import math
import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from app_info import APP_CREATOR, APP_VERSION


def resource_path(relative_path):
    """Retourne le bon chemin en mode Python normal ou en .exe PyInstaller."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base_path / relative_path


class Application(ctk.CTk):
    """Fenetre principale : interface, calculs MOA et affichages graphiques."""

    def __init__(self):
        super().__init__()

        self.title(f"Calculateur de MOA - Version {APP_VERSION} - {APP_CREATOR}")
        self.geometry("1280x740")
        self.minsize(1280, 740)
        self.iconbitmap(resource_path("gui/assets/ico_exe.ico"))
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
            "violet": "#a78bfa",
            "cyan": "#00b4d8",
            "blue": "#0057b7",
            "red": "#e63946",
            "green": "#06d6a0",
        }

        self.configure(fg_color=self.colors["bg"])

        self.distance_values = (20, 50, 100, 200, 300)
        self.range_modes = {
            "Courte portee": (20, 50, 100),
            "Longue portee": (100, 200, 300),
        }
        self.distance_modes = {
            "Imperial system": {"suffix": "yd", "cm_per_unit": 91.44},
            "Metric system": {"suffix": "m", "cm_per_unit": 100.0},
        }
        self.distance_mode = tk.StringVar(value="Imperial system")
        self.range_mode = tk.StringVar(value="Courte portee")
        self.distance_colors = {
            20: self.colors["violet"],
            50: self.colors["cyan"],
            100: self.colors["blue"],
            200: self.colors["red"],
            300: self.colors["green"],
        }

        # Images embarquees dans l'exe : resource_path marche aussi hors PyInstaller.
        self.reference_image_paths = [
            resource_path(f"gui/assets/M_{index:02}.png")
            for index in range(1, 9)
        ]
        self.reference_image_paths = [
            path for path in self.reference_image_paths if path.exists()
        ]
        if not self.reference_image_paths:
            raise FileNotFoundError("Aucune image M_01.png a M_08.png trouvee.")

        self.current_image_index = 0
        self.reference_image_path = self.reference_image_paths[self.current_image_index]
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
        self.torso_follow_mouse = True
        self.torso_mouse_center = None

        # Reglage manuel du cercle jaune de tete sur l'image d'origine M_01.png.
        # Modifie ces 4 valeurs si le cercle ne va pas exactement du menton a la cime.
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

        # Conversion pixels -> centimetres basee sur la hauteur de tete de reference.
        self.head_reference_height_px = self.head_bottom_px - self.head_top_px
        self.pixel_per_cm = (
            self.head_reference_height_px * self.image_scale
        ) / self.head_height_cm

        self.init_ui()

    def init_ui(self):
        """Construit la navigation principale puis affiche l'accueil."""
        self.sidebar_min_width = 136
        self.sidebar_max_width = 176
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

        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.pack(side="bottom", fill="x", padx=10, pady=(0, 14))

        self.sidebar_version = ctk.CTkLabel(
            self.sidebar_footer,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["muted"],
        )
        self.sidebar_version.pack()

        self.sidebar_creator = ctk.CTkLabel(
            self.sidebar_footer,
            text=APP_CREATOR,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors["line_soft"],
        )
        self.sidebar_creator.pack()

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
            text=(
                "Entrez la precision de l'arme pour visualiser le diametre du "
                "groupement en courte ou longue portee, en yards ou en metres reels."
            ),
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
            height=190,
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
            width=120,
        )
        self.MOA_Entry.pack(side="left", padx=(0, 8))
        self.MOA_Entry.bind("<Return>", lambda _event: self.calculer_moa())

        ctk.CTkButton(
            input_row,
            text="Calculer",
            height=32,
            width=100,
            command=self.calculer_moa,
        ).pack(side="left")

        selectors_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        selectors_frame.pack(fill="x", padx=12, pady=(0, 6))
        selectors_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            selectors_frame,
            text="Systeme",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["muted"],
            width=62,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6))

        self.unit_selector = ctk.CTkSegmentedButton(
            selectors_frame,
            values=list(self.distance_modes.keys()),
            variable=self.distance_mode,
            command=self.on_distance_mode_changed,
        )
        self.unit_selector.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        ctk.CTkLabel(
            selectors_frame,
            text="Portee",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["muted"],
            width=52,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 6))

        self.range_selector = ctk.CTkSegmentedButton(
            selectors_frame,
            values=list(self.range_modes.keys()),
            variable=self.range_mode,
            command=self.on_range_mode_changed,
        )
        self.range_selector.grid(row=1, column=1, sticky="ew", pady=(0, 6))

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
            "groupement apparent s'ouvre. Une arme a 2 MOA ne devient pas moins "
            "precise a 300 metres ou 300 yards ; le meme angle couvre simplement "
            "un cercle plus grand."
        )
        ctk.CTkLabel(
            self.result_frame,
            text=moa_note,
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text"],
            justify="left",
            wraplength=650,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self.legend_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.legend_frame.pack(fill="x", padx=14, pady=(0, 10))
        self.update_distance_legend()

    def get_distance_config(self):
        return self.distance_modes[self.distance_mode.get()]

    def get_active_distances(self):
        return self.range_modes[self.range_mode.get()]

    def get_max_active_distance(self):
        return max(self.get_active_distances())

    def format_distance_label(self, distance):
        unit = self.get_distance_config()["suffix"]
        return f"{distance} {unit}"

    def update_distance_legend(self):
        if not hasattr(self, "legend_frame"):
            return

        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        for distance in self.get_active_distances():
            item = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            item.pack(side="left", padx=(0, 14), pady=(0, 4))

            ctk.CTkFrame(
                item,
                width=20,
                height=3,
                fg_color=self.distance_colors[distance],
            ).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(
                item,
                text=self.format_distance_label(distance),
                font=ctk.CTkFont(size=12),
                text_color=self.colors["muted"],
            ).pack(side="left")

    def on_distance_mode_changed(self, _value=None):
        self.refresh_active_display()

    def on_range_mode_changed(self, _value=None):
        self.refresh_active_display()

    def parse_moa_value(self, show_error=False):
        raw_moa = self.MOA_Entry.get().strip().replace(",", ".")
        if show_error:
            self.error_label.configure(text="")

        try:
            moa = float(raw_moa)
            if moa <= 0:
                raise ValueError
        except ValueError:
            if show_error:
                self.error_label.configure(text="Veuillez entrer un nombre positif valide.")
            return None

        return moa

    def build_active_diameters(self, moa):
        return {
            distance: self.calculate_diameter(moa, distance)
            for distance in self.get_active_distances()
        }

    def reset_diagram_values(self):
        if not hasattr(self, "value_labels"):
            return

        for item in self.value_labels.values():
            self.canvas.itemconfig(item, text="-- cm")

    def refresh_active_display(self, show_error=False):
        self.update_distance_legend()
        if hasattr(self, "head_circles"):
            self.update_visible_photo_circles()

        moa = self.parse_moa_value(show_error=show_error)
        if moa is None:
            self.current_diameters = None
            self.reset_diagram_values()
            if hasattr(self, "distance_labels"):
                self.update_diagram_layout()
            if hasattr(self, "canvas_photo"):
                self.update_photo_layout()
            return

        self.current_diameters = self.build_active_diameters(moa)
        if hasattr(self, "distance_labels"):
            self.update_diagram_layout()
        if hasattr(self, "canvas_photo"):
            self.update_photo_circles(self.current_diameters)

    def create_diagram(self):
        """Cree le schema horizontal qui compare les distances choisies."""
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
        self.diagram_x = {0: 80, 20: 200, 50: 310, 100: 420, 200: 585, 300: 750}

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

        self.diagram_targets = {}
        for distance in self.distance_values:
            self.diagram_targets[distance] = self.canvas.create_oval(
                0,
                0,
                1,
                1,
                fill=self.distance_colors[distance],
                outline="",
            )

        self.distance_labels = {}
        self.distance_labels[0] = self.canvas.create_text(
            self.diagram_x[0],
            192,
            text="0",
            fill="#f5f7fb",
            font=("Arial", 10),
        )
        for distance in self.distance_values:
            self.distance_labels[distance] = self.canvas.create_text(
                self.diagram_x[distance],
                192,
                text=self.format_distance_label(distance),
                fill="#f5f7fb",
                font=("Arial", 10),
            )

        self.value_labels = {}
        for distance in self.distance_values:
            self.value_labels[distance] = self.canvas.create_text(
                self.diagram_x[distance],
                216,
                text="-- cm",
                fill="#f5f7fb",
                font=("Arial", 10, "bold"),
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

    def update_visible_photo_circles(self):
        active_distances = set(self.get_active_distances())
        for distance in self.distance_values:
            state = "normal" if distance in active_distances else "hidden"
            if hasattr(self, "head_circles"):
                self.canvas_photo.itemconfig(self.head_circles[distance], state=state)
            if hasattr(self, "torso_circles"):
                self.canvas_photo.itemconfig(self.torso_circles[distance], state=state)

    def update_image_selector_label(self):
        if not hasattr(self, "image_number_item"):
            return

        total = len(self.reference_image_paths)
        self.canvas_photo.itemconfig(
            self.image_number_item,
            text=f"M_{self.current_image_index + 1:02} / M_{total:02}",
        )

    def update_image_navigation_layout(self):
        if not hasattr(self, "image_number_item"):
            return

        bottom_y = self.photo_offset_y + self.image_height - 22
        left_x = self.photo_offset_x + 28
        right_x = self.photo_offset_x + self.image_width - 28
        center_x = self.photo_offset_x + self.image_width / 2

        self.canvas_photo.coords(self.image_prev_item, left_x, bottom_y)
        self.canvas_photo.coords(self.image_next_item, right_x, bottom_y)
        self.canvas_photo.coords(self.image_number_item, center_x, bottom_y)

        self.canvas_photo.tag_raise(self.image_prev_item)
        self.canvas_photo.tag_raise(self.image_next_item)
        self.canvas_photo.tag_raise(self.image_number_item)

    def create_image_navigation(self):
        self.image_prev_item = self.canvas_photo.create_text(
            0,
            0,
            text="<",
            fill=self.colors["red"],
            font=("Arial", 32, "bold"),
            tags=("image_nav", "image_prev"),
        )
        self.image_number_item = self.canvas_photo.create_text(
            0,
            0,
            text="",
            fill=self.colors["line_soft"],
            font=("Arial", 12, "bold"),
            tags=("image_nav", "image_number"),
        )
        self.image_next_item = self.canvas_photo.create_text(
            0,
            0,
            text=">",
            fill=self.colors["red"],
            font=("Arial", 32, "bold"),
            tags=("image_nav", "image_next"),
        )
        self.canvas_photo.tag_bind(
            "image_prev",
            "<Button-1>",
            lambda _event: self.change_reference_image(-1),
        )
        self.canvas_photo.tag_bind(
            "image_next",
            "<Button-1>",
            lambda _event: self.change_reference_image(1),
        )
        self.canvas_photo.tag_bind(
            "image_nav",
            "<Enter>",
            lambda _event: self.canvas_photo.configure(cursor="hand2"),
        )
        self.canvas_photo.tag_bind(
            "image_nav",
            "<Leave>",
            lambda _event: self.canvas_photo.configure(cursor=""),
        )
        self.update_image_selector_label()

    def change_reference_image(self, direction):
        total = len(self.reference_image_paths)
        self.current_image_index = (self.current_image_index + direction) % total
        self.reference_image_path = self.reference_image_paths[self.current_image_index]
        self.image_original = Image.open(self.reference_image_path)
        self.image_original_width, self.image_original_height = self.image_original.size
        self.update_image_selector_label()
        self.update_photo_layout()

    def create_photo_canvas(self):
        photo_header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        photo_header.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            photo_header,
            text="Impact projete sur la silhouette",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"],
        ).pack(side="left")

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
        self.head_circles = {}
        self.torso_circles = {}
        for distance in self.distance_values:
            self.head_circles[distance] = self.canvas_photo.create_oval(
                head_x1,
                head_y1,
                head_x2,
                head_y2,
                outline=self.distance_colors[distance],
                width=2,
            )
            self.torso_circles[distance] = self.canvas_photo.create_oval(
                torso_x1,
                torso_y1,
                torso_x2,
                torso_y2,
                outline=self.distance_colors[distance],
                width=1,
            )

        self.create_image_navigation()

        legend = ctk.CTkFrame(self.right_frame, fg_color=self.colors["panel_alt"], corner_radius=8)
        legend.pack(fill="x", padx=14, pady=(0, 12))

        for text, color in (
            ("Tete", "#f9c74f"),
            ("Coeur", "#d8a928"),
        ):
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=10, pady=8)
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
        self.canvas_photo.bind("<Motion>", self.update_torso_mouse_center)
        self.canvas_photo.bind("<Leave>", self.reset_torso_mouse_center)
        self.update_visible_photo_circles()
        self.after(50, self.update_photo_layout)

    def afficher_explication(self):
        """Affiche la legende detaillee et les limites d'interpretation du MOA."""
        self.clear_main_frame()

        panel = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["panel"],
            corner_radius=10,
        )
        panel.pack(fill="both", expand=True)

        scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color=self.colors["panel_alt"],
            scrollbar_button_hover_color=self.colors["line"],
        )
        scroll.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            scroll,
            text="Legende et conditions d'interpretation du MOA",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", pady=(0, 10))

        def add_section(title, body):
            ctk.CTkLabel(
                scroll,
                text=title,
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color=self.colors["line_soft"],
            ).pack(anchor="w", pady=(14, 6))
            ctk.CTkLabel(
                scroll,
                text=body,
                font=ctk.CTkFont(size=14),
                text_color=self.colors["text"],
                justify="left",
                wraplength=900,
            ).pack(anchor="w", fill="x")

        add_section(
            "Definition",
            "Le MOA (Minute Of Angle) est une unite angulaire utilisee pour mesurer "
            "la precision d'une arme a feu. Elle correspond a la dispersion d'un "
            "projectile unique, une balle, autour d'un point vise.\n\n"
            "En pratique, un groupement de 1 MOA correspond a environ 2,66 cm a "
            "100 yards, et environ 2,91 cm a 100 metres. Une meme valeur de MOA "
            "donne donc un diametre proportionnel a la distance choisie.",
        )

        add_section(
            "Munitions a dispersion",
            "Dans le cas des munitions a dispersion, comme les cartouches a grenaille, "
            "le MOA n'est pas une mesure adaptee. Ces munitions produisent une gerbe "
            "de projectiles et non un impact unique. La notion de precision est alors "
            "remplacee par des notions de diametre de gerbe et de densite d'impact.\n\n"
            "Cependant, dans un souci de coherence et de comparaison entre differentes "
            "categories d'armes, un MOA equivalent peut etre utilise. Cette valeur est "
            "une approximation permettant de representer la dispersion globale sous "
            "forme angulaire, mais elle ne constitue pas une mesure rigoureuse.",
        )

        table = ctk.CTkFrame(scroll, fg_color=self.colors["panel_alt"], corner_radius=8)
        table.pack(fill="x", pady=(16, 8))

        headers = ("Categorie d'arme", "MOA moyen", "Remarque")
        rows = (
            ("Arme de poing", "5 a 15 MOA", "Tres dependant du tireur"),
            ("Fusil d'epaule (semi-auto)", "2 a 4 MOA", "Standard militaire / civil"),
            ("Fusil a pompe", "4 a 6 MOA (slug)\n30 a 80 MOA equiv. (grenaille)", "Tres variable"),
            ("Fusil a verrou", "0.5 a 1.5 MOA", "Haute precision"),
        )

        for column in range(3):
            table.grid_columnconfigure(column, weight=1, uniform="moa_table")

        for column, text in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["line_soft"],
                anchor="w",
            ).grid(row=0, column=column, sticky="ew", padx=10, pady=(10, 6))

        for row_index, row in enumerate(rows, start=1):
            row_color = self.colors["panel"] if row_index % 2 else "#1d2533"
            for column, text in enumerate(row):
                cell = ctk.CTkFrame(table, fg_color=row_color, corner_radius=4)
                cell.grid(row=row_index, column=column, sticky="nsew", padx=4, pady=3)
                ctk.CTkLabel(
                    cell,
                    text=text,
                    font=ctk.CTkFont(size=13, weight="bold" if column == 1 else "normal"),
                    text_color=self.colors["line_soft"] if column == 1 else self.colors["text"],
                    justify="left",
                    anchor="w",
                    wraplength=260,
                ).pack(anchor="w", fill="x", padx=8, pady=8)

        add_section(
            "Conditions de reference",
            "Les valeurs de MOA indiquees sont valables dans des conditions ideales :\n\n"
            "- Tireur parfaitement stable et experimente, sans erreur humaine\n"
            "- Arme correctement entretenue et en bon etat\n"
            "- Munitions de qualite constante\n"
            "- Conditions meteorologiques clementes, sans vent significatif\n"
            "- Distance de tir maitrisee et environnement controle",
        )

        add_section(
            "Facteurs influencant le MOA",
            "Le MOA reel peut varier de maniere significative selon de nombreux "
            "parametres.\n\n"
            "1. L'arme : qualite du canon, usure, rigidite, longueur, type de canon "
            "et systeme de fonctionnement.\n\n"
            "2. Les munitions : regularite de fabrication, type de projectile, charge "
            "propulsive et qualite globale de la cartouche.\n\n"
            "3. Le systeme de visee : qualite de l'optique ou des organes de visee, "
            "reglage du zero et stabilite du montage.\n\n"
            "4. Le tireur : position de tir, maitrise du depart du coup, gestion du "
            "recul et experience globale.\n\n"
            "5. L'environnement : vent, temperature, humidite, pression atmospherique "
            "et conditions de luminosite.",
        )

        add_section(
            "Formule utilisee",
            "Diametre = tan((MOA / 60) degres) x distance",
        )

        add_section(
            "Conclusion",
            "Le MOA est une mesure utile pour comparer la precision des armes tirant "
            "des projectiles uniques. Dans le cas des armes a dispersion, il doit etre "
            "interprete avec prudence et considere comme un outil simplifie de "
            "comparaison plutot qu'une donnee physique exacte.",
        )

    def clear_main_frame(self):
        """Vide la zone centrale avant d'afficher une autre page."""
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
        button_pad = 10 if compact else 14
        self.button1.pack_configure(padx=button_pad)
        self.button2.pack_configure(padx=button_pad)

    def calculer_moa(self):
        """Valide la saisie puis met a jour le schema et la silhouette."""
        self.refresh_active_display(show_error=True)

    def calculate_diameter(self, moa, distance):
        """Convertit une valeur MOA en diametre de groupement en centimetres."""
        distance_cm = distance * self.get_distance_config()["cm_per_unit"]
        angle_radians = math.radians(moa / 60)
        return round(math.tan(angle_radians) * distance_cm, 2)

    def scaled_photo_coords(self, x1, y1, x2, y2):
        scale = self.image_scale
        return (
            self.photo_offset_x + x1 * scale,
            self.photo_offset_y + y1 * scale,
            self.photo_offset_x + x2 * scale,
            self.photo_offset_y + y2 * scale,
        )

    def update_torso_mouse_center(self, event):
        if not self.torso_follow_mouse:
            return

        self.torso_mouse_center = (event.x, event.y)
        if self.current_diameters:
            self.update_photo_circles(self.current_diameters)

    def reset_torso_mouse_center(self, _event=None):
        self.torso_mouse_center = None
        if self.current_diameters:
            self.update_photo_circles(self.current_diameters)

    def update_photo_layout(self, _event=None):
        """Redimensionne l'image sans perdre l'echelle pixels/centimetres."""
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
        self.update_image_navigation_layout()

        head_coords = self.scaled_photo_coords(*self.head_oval)
        torso_coords = self.scaled_photo_coords(*self.torso_oval)
        self.canvas_photo.coords(self.head_reference_circle, *head_coords)
        self.canvas_photo.coords(self.torso_reference_circle, *torso_coords)

        if self.current_diameters:
            self.update_photo_circles(self.current_diameters)
            return

        for item in self.head_circles.values():
            self.canvas_photo.coords(item, *head_coords)
        for item in self.torso_circles.values():
            self.canvas_photo.coords(item, *torso_coords)
        self.update_visible_photo_circles()

    def update_diagram_layout(self, _event=None):
        """Repositionne le schema quand la fenetre change de taille."""
        if not hasattr(self, "canvas"):
            return

        width = max(self.canvas.winfo_width(), 320)
        height = max(self.canvas.winfo_height(), 120)
        margin_x = max(54, min(140, int(width * 0.08)))
        line_width = width - (margin_x * 2)

        top_space = 44
        bottom_space = 48
        self.diagram_center_y = max(top_space + 18, min(height - bottom_space, int(height * 0.46)))
        max_distance = self.get_max_active_distance()
        self.diagram_x = {0: margin_x}
        for distance in self.distance_values:
            self.diagram_x[distance] = margin_x + int(line_width * (distance / max_distance))
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
            self.diagram_x[max_distance],
            self.diagram_center_y,
        )
        self.canvas.coords(self.moa_title, width / 2, 20)

        active_distances = set(self.get_active_distances())
        compact_labels = width < 620
        for index, (distance, item) in enumerate(self.distance_labels.items()):
            state = "normal" if distance == 0 or distance in active_distances else "hidden"
            self.canvas.itemconfig(item, state=state)
            y = label_y - 12 if compact_labels and index % 2 else label_y
            self.canvas.coords(item, self.diagram_x[distance], y)
            if distance:
                self.canvas.itemconfig(item, text=self.format_distance_label(distance))

        for index, (distance, item) in enumerate(self.value_labels.items()):
            state = "normal" if distance in active_distances else "hidden"
            self.canvas.itemconfig(item, state=state)
            y = value_y - 12 if compact_labels and index % 2 else value_y
            self.canvas.coords(item, self.diagram_x[distance], y)

        if self.current_diameters:
            self.update_diagram(self.current_diameters)
            return

        default_radiuses = {
            distance: max(5, 8 + distance / 14)
            for distance in self.get_active_distances()
        }
        self.update_diagram_shapes(default_radiuses)

    def update_diagram(self, diameters):
        if not hasattr(self, "canvas"):
            return

        active_diameters = {
            distance: diameters[distance]
            for distance in self.get_active_distances()
            if distance in diameters
        }
        if len(active_diameters) != len(self.get_active_distances()):
            self.current_diameters = None
            return

        self.current_diameters = active_diameters
        self.update_visible_photo_circles()

        # Le schema est volontairement plafonne pour rester lisible.
        wanted_scale = 4
        max_diameter = max(active_diameters.values())
        scale = min(wanted_scale, (self.diagram_max_radius * 2) / max_diameter)

        radiuses = {
            distance: max(6, (diameter * scale) / 2)
            for distance, diameter in active_diameters.items()
        }

        self.update_diagram_shapes(radiuses)

        for distance, item in self.value_labels.items():
            if distance in active_diameters:
                self.canvas.itemconfig(item, text=f"{active_diameters[distance]:.2f} cm")

    def update_diagram_shapes(self, radiuses):
        center_y = self.diagram_center_y

        max_distance = self.get_max_active_distance()
        radius_max = radiuses[max_distance]
        self.canvas.coords(
            self.ligne_haut,
            self.diagram_x[0],
            center_y,
            self.diagram_x[max_distance],
            center_y - radius_max,
        )
        self.canvas.coords(
            self.ligne_bas,
            self.diagram_x[0],
            center_y,
            self.diagram_x[max_distance],
            center_y + radius_max,
        )

        active_distances = set(self.get_active_distances())
        for distance, item in self.diagram_targets.items():
            if distance not in active_distances:
                self.canvas.itemconfig(item, state="hidden")
                continue

            self.canvas.itemconfig(item, state="normal")
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
        """Dessine les cercles MOA sur la tete et sur la zone suivie par la souris."""
        self.current_diameters = diameters

        circle_groups = (
            (
                self.head_center,
                False,
                self.head_circles,
            ),
            (
                self.torso_mouse_center,
                True,
                self.torso_circles,
            ),
        )

        for center, is_canvas_position, items in circle_groups:
            if center is None:
                center_x = self.photo_offset_x + self.torso_center[0] * self.image_scale
                center_y = self.photo_offset_y + self.torso_center[1] * self.image_scale
            elif is_canvas_position:
                center_x = center[0]
                center_y = center[1]
            else:
                center_x = self.photo_offset_x + center[0] * self.image_scale
                center_y = self.photo_offset_y + center[1] * self.image_scale

            for distance, item in items.items():
                if distance not in diameters:
                    continue
                diameter_px = diameters[distance] * self.pixel_per_cm
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
