import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import math


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration générale de la fenêtre
        self.title("MOA Calculateur")
        self.geometry("1000x800")
        self.minsize(1000, 750)
        self.iconbitmap("gui/assets/buste_knight.ico")
        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("blue")  # thème : blue / green / dark-blue

        # 1024 x 1536
        self.h = int(1024 / 4)
        self.l= int(1536 /4)

        self.image_king = Image.open("gui/assets/knight.png").resize((self.h, self.l))
        self.image_tk = ImageTk.PhotoImage(self.image_king)

        # Appel à la méthode d'interface
        self.init_ui()

    def init_ui(self):
        # Exemple : barre latérale
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.button1 = ctk.CTkButton(self.sidebar, text="Accueil", command=self.afficher_accueil)
        self.button1.pack(pady=(20, 10))

        self.button2 = ctk.CTkButton(self.sidebar, text="Paramètres", command=self.afficher_parametres)
        self.button2.pack(pady=10)

        # Zone principale (où les pages changent)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.afficher_accueil()

    def afficher_accueil(self):
        self.clear_main_frame()   

        self.Bot_frame = ctk.CTkFrame(self.main_frame)
        self.Bot_frame.pack(pady=5, side = "bottom", expand=True, fill="both")

        self.Top_frame = ctk.CTkFrame(master =self.main_frame, height=200)
        self.Top_frame.pack(pady=5, side ="bottom", expand="False", fill="both")

        self.draw_frame = ctk.CTkFrame(master = self.Bot_frame, height=200)
        self.draw_frame.pack(pady=5, padx=5, side ="bottom", expand="False", fill="both")

        self.left_frame = ctk.CTkFrame(master = self.Bot_frame)
        self.left_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        self.right_frame = ctk.CTkFrame(master = self.Bot_frame)
        self.right_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        #* ------------------------------------------------------- Canevas Knith ------------------------------------------------------
        self.canvas_photo = tk.Canvas(self.right_frame, width=self.h, height=self.l, bg="black", highlightthickness=0)
        self.canvas_photo.pack(padx=10, pady=10)

        self.tk_img = ImageTk.PhotoImage(self.image_king)
        self.canvas_photo.create_image(0, 0, image=self.tk_img, anchor="nw")

        #* ------------- cercel de centrage tette -------------
        self.canvas_photo.create_oval(90,40,140,100,outline="yellow", width=2)
        # Hauteur = 140 -40 = 100px
        # hauteur moyenne tete  = 26cm
        # 100px = 26cm ratio = 1px = 2.30cm

        self.cercle_100 = self.canvas_photo.create_oval(90,40,140,100, outline="#0057b7" ,width=2)
        self.cercle_200 = self.canvas_photo.create_oval(90,40,140,100, outline="#e63946" ,width=2)
        self.cercle_300 = self.canvas_photo.create_oval(90,40,140,100, outline="#06d6a0" ,width=2)
        # centre de la tete; X = 90+25 = 115, Y = 40+30 = 70




        label = ctk.CTkLabel(self.Top_frame, text="MOA Calculateur", font=ctk.CTkFont(size=20))
        sous_label = ctk.CTkLabel(self.Top_frame, text="Minute Of Angle", font=ctk.CTkFont(size=10))

        MOA_Label = ctk.CTkLabel(self.left_frame, text="MOA /100 Yards")
        self.MOA_Entry = ctk.CTkEntry(self.left_frame, placeholder_text="MOA ex (4.5)")                
        MOA_BP = ctk.CTkButton(self.left_frame, text="Calculer", command=self.calculer_moa)


        self.canvas = ctk.CTkCanvas(master = self.draw_frame, width=800, height=200, bg="#8C8C8C")
        self.canvas.pack(pady=10, padx=10, side ="top", expand="False")

        # Créer les cercles cibles
        self.cible_300 = self.canvas.create_oval(690, 52, 710, 148, fill="#06d6a0", tags="cible_300")
        self.cible_200 = self.canvas.create_oval(492, 68, 508, 132, fill="#e63946", tags="cible_200")
        self.cible_100 = self.canvas.create_oval(295, 84, 305, 116, fill="#0057b7", tags="cible_100") 

        # Créer les lignes avec des tags pour pouvoir les modifier
        self.canvas.create_line(100, 100, 700, 100, width=3, fill="#f77f00", tags="ligne_centrale")
        self.ligne_haut = self.canvas.create_line(100, 100, 700, 52, width=3, fill="#f9c74f", tags="ligne_haut")
        self.ligne_bas = self.canvas.create_line(100, 100, 700, 148, width=3, fill="#f9c74f", tags="ligne_bas")

        self.canvas.create_text(100, 160, text="0 yd", fill="white", font=("Arial", 10))
        self.canvas.create_text(300, 160, text="100 yd", fill="white", font=("Arial", 10))
        self.label_100 = self.canvas.create_text(300, 180, text="Rayon a 100 yd", fill="white", font=("Arial", 10))
        self.canvas.create_text(500, 160, text="200 yd", fill="white", font=("Arial", 10))
        self.label_200 = self.canvas.create_text(500, 180, text="Rayon a 200 yd", fill="white", font=("Arial", 10))
        self.canvas.create_text(700, 160, text="300 yd", fill="white", font=("Arial", 10))
        self.label_300 = self.canvas.create_text(700, 180, text="Rayon a 300 yd", fill="white", font=("Arial", 10))

        self.canvas.create_text(400, 10, text="MOA", fill="yellow", font=("Arial", 12, "italic"))


        label.pack(pady=0)
        sous_label.pack(pady=(0, 20))
        MOA_Label.pack(pady=0)
        self.MOA_Entry.pack(pady=(0, 10))
        MOA_BP.pack(pady=20, )


    def afficher_parametres(self):
        self.clear_main_frame()
        label = ctk.CTkLabel(self.main_frame, text="Paramètres", font=ctk.CTkFont(size=20))
        label.pack(pady=20)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


    def calculer_moa(self):
        print("BP MOA a été pressé = Calculer")
        try:
            MOA = self.MOA_Entry.get()
            MOA = float(MOA)
            diametre_moa_100 = 2*math.tan((MOA/60)*(math.pi/180))*91.44 #* 100 yards
            diametre_moa_200 = 2*math.tan((MOA/60)*(math.pi/180))*(91.44*2) #* 200 yards
            diametre_moa_300 = 2*math.tan((MOA/60)*(math.pi/180))*(91.44*3) #* 300 yards
            diametre_moa_100 = round(diametre_moa_100, 2)
            diametre_moa_200 = round(diametre_moa_200, 2)
            diametre_moa_300 = round(diametre_moa_300, 2)

            print("MOA = ", MOA)
            print("dia_moa_100 = ", diametre_moa_100, 'cm')
            print("dia_moa_200 = ", diametre_moa_200, 'cm')
            print("dia_moa_300 = ", diametre_moa_300, 'cm')

            
            dia_moa_100 = diametre_moa_100*100
            dia_moa_200 = diametre_moa_200*100
            dia_moa_300 = diametre_moa_300*100

            # Calculer les nouvelles positions des lignes
            h100 = 100 - dia_moa_100/2
            b100 = 100 + dia_moa_100/2
            h200 = 100 - dia_moa_200/2
            b200 = 100 + dia_moa_200/2
            h300 = 100 - dia_moa_300/2
            b300 = 100 + dia_moa_300/2
            
            # Mettre à jour les lignes sur le canvas
            self.canvas.coords(self.ligne_haut, 100, 100, 700, h300)
            self.canvas.coords(self.ligne_bas, 100, 100, 700, b300)
            self.canvas.coords(self.cible_100, 290, h100, 310, b100)
            self.canvas.coords(self.cible_200, 490, h200, 510, b200)
            self.canvas.coords(self.cible_300, 690, h300, 710, b300)

            self.canvas.itemconfig(self.label_100, text=f"{dia_moa_100:.1f} cm")
            self.canvas.itemconfig(self.label_200, text=f"{dia_moa_200:.1f} cm")
            self.canvas.itemconfig(self.label_300, text=f"{dia_moa_300:.1f} cm")

            #Centre x 115, y 70
            x1_100 = 115 - ((dia_moa_100*2.30)/2)
            x2_100 = 115 + ((dia_moa_100*2.30)/2)
            y1_100 = 70 - ((dia_moa_100*2.30)/2)
            y2_100 = 70 + ((dia_moa_100*2.30)/2)

            x1_200 = 115 - ((dia_moa_200*2.30)/2)
            x2_200 = 115 + ((dia_moa_200*2.30)/2)
            y1_200 = 70 - ((dia_moa_200*2.30)/2)
            y2_200 = 70 + ((dia_moa_200*2.30)/2)

            x1_300 = 115 - ((dia_moa_300*2.30)/2)
            x2_300 = 115 + ((dia_moa_300*2.30)/2)
            y1_300 = 70 - ((dia_moa_300*2.30)/2)
            y2_300 = 70 + ((dia_moa_300*2.30)/2)

            print("X1_100",(dia_moa_100/2.30)/2)
            print("X1_200",(dia_moa_200/2.30)/2)
            print("X1_300",(dia_moa_300/2.30)/2)
# 90,40,140,100


            self.canvas_photo.coords(self.cercle_100,x1_100,y1_100,x2_100,y2_100)
            self.canvas_photo.coords(self.cercle_200,x1_200,y1_200,x2_200,y2_200)
            self.canvas_photo.coords(self.cercle_300,x1_300,y1_300,x2_300,y2_300)


            print(f"300 : haut={h300:.1f}, bas={b300:.1f}")
            print(f"200 : haut={h200:.1f}, bas={b200:.1f}")            
            print(f"100: haut={h100:.1f}, bas={b100:.1f}")
            
        except ValueError:
            print("Erreur : Veuillez entrer un nombre valide")
        except Exception as e:
            print(f"Erreur : {e}")
        

def lancer_app():
    app = Application()
    app.mainloop()
