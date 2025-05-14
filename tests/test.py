import tkinter as tk
import customtkinter as ctk
import json
import os

# Classe principale de la carte mentale
class MindMap:
    def __init__(self, root, filename):
        self.root = root
        self.filename = filename

        # Création du canvas
        self.canvas = ctk.CTkCanvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.elements = []
        self.lines = []
        self.selected_element = None
        self.link_start = None

        # Menu contextuel (clic droit)
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)
        self.context_menu.add_command(label="Modifier texte", command=self.modifier_texte)
        self.context_menu.add_command(label="Relier", command=self.preparer_lien)

        # Événements souris
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        # Chargement du fichier si existant
        self.charger()

    # Fonctions identiques à la version précédente (voir détails dans ton code initial)
    def on_click(self, event):
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                if self.link_start:
                    self.relier_elements(self.link_start, elem)
                    self.link_start = None
                else:
                    self.selectionner(elem)
                return
        self.ajouter_element(event.x, event.y, "Nouveau")

    def on_right_click(self, event):
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                self.selected_element = elem
                self.context_menu.post(event.x_root, event.y_root)
                return

    def on_drag(self, event):
        if self.selected_element:
            dx = event.x - self.selected_element['x']
            dy = event.y - self.selected_element['y']
            self.deplacer_element(self.selected_element, dx, dy)

    def is_within_element(self, x, y, elem):
        return (elem['x'] - elem['width']//2 <= x <= elem['x'] + elem['width']//2 and
                elem['y'] - elem['height']//2 <= y <= elem['y'] + elem['height']//2)

    def selectionner(self, elem):
        self.selected_element = elem

    def ajouter_element(self, x, y, text):
        width, height = self.calculer_taille_texte(text)
        elem_id = self.canvas.create_rectangle(x - width//2, y - height//2, x + width//2, y + height//2, fill="lightblue")
        text_id = self.canvas.create_text(x, y, text=text, fill="black")
        self.elements.append({'x': x, 'y': y, 'id': elem_id, 'text_id': text_id, 'text': text, 'width': width, 'height': height})
        self.canvas.tag_lower(elem_id)
        self.sauvegarder()

    def calculer_taille_texte(self, text):
        lines = text.split('\n')
        max_width = max(len(line) for line in lines) * 7 + 20
        height = len(lines) * 20 + 10
        return max_width, height

    def modifier_texte(self):
        if self.selected_element:
            def save_texte():
                new_text = text_entry.get("1.0", "end-1c")
                self.canvas.itemconfig(self.selected_element['text_id'], text=new_text)
                self.selected_element['text'] = new_text
                self.redimensionner_element(self.selected_element)
                text_entry.destroy()
                save_button.destroy()
                self.sauvegarder()

            text_entry = tk.Text(self.root, height=2, width=20)
            text_entry.insert("1.0", self.selected_element['text'])
            text_entry.pack()
            save_button = ctk.CTkButton(self.root, text="Sauvegarder", command=save_texte)
            save_button.pack()

    def redimensionner_element(self, elem):
        width, height = self.calculer_taille_texte(elem['text'])
        elem['width'] = width
        elem['height'] = height
        self.canvas.coords(elem['id'], elem['x'] - width//2, elem['y'] - height//2, elem['x'] + width//2, elem['y'] + height//2)
        self.canvas.coords(elem['text_id'], elem['x'], elem['y'])

    def deplacer_element(self, elem, dx, dy):
        self.canvas.move(elem['id'], dx, dy)
        self.canvas.move(elem['text_id'], dx, dy)
        elem['x'] += dx
        elem['y'] += dy
        self.mettre_a_jour_lignes()
        self.sauvegarder()

    def preparer_lien(self):
        self.link_start = self.selected_element

    def relier_elements(self, elem1, elem2):
        if elem1 != elem2:
            line_id = self.canvas.create_line(elem1['x'], elem1['y'], elem2['x'], elem2['y'], fill="black", width=2)
            self.lines.append({'start': elem1, 'end': elem2, 'id': line_id})
            self.canvas.tag_lower(line_id)
            self.sauvegarder()

    def mettre_a_jour_lignes(self):
        for line in self.lines:
            self.canvas.coords(line['id'], line['start']['x'], line['start']['y'], line['end']['x'], line['end']['y'])

    def supprimer_element(self):
        if self.selected_element:
            lignes_a_supprimer = [line for line in self.lines if line['start'] == self.selected_element or line['end'] == self.selected_element]
            for line in lignes_a_supprimer:
                self.canvas.delete(line['id'])
                self.lines.remove(line)

            self.canvas.delete(self.selected_element['id'])
            self.canvas.delete(self.selected_element['text_id'])
            self.elements.remove(self.selected_element)
            self.selected_element = None
            self.sauvegarder()

    def charger(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.elements = []
                self.lines = []
                self.canvas.delete("all")

                for elem in data.get("elements", []):
                    self.ajouter_element(elem['x'], elem['y'], elem['text'])

                for line in data.get("lines", []):
                    start = self.elements[line["start_index"]]
                    end = self.elements[line["end_index"]]
                    self.relier_elements(start, end)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def sauvegarder(self):
        data = {
            "elements": [{"x": e['x'], "y": e['y'], "text": e['text']} for e in self.elements],
            "lines": [
                {
                    "start_index": self.elements.index(l['start']),
                    "end_index": self.elements.index(l['end'])
                } for l in self.lines
            ]
        }
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

# Interface d’accueil mise à jour
class Accueil:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x500")
        self.root.title("Accueil - Cartes mentales")

        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.title = ctk.CTkLabel(self.main_frame, text="Bienvenue !", font=("Arial", 22))
        self.title.pack(pady=10)

        self.filename_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Nom de la carte (sans .json)")
        self.filename_entry.pack(pady=10)

        self.bouton_nouveau = ctk.CTkButton(self.main_frame, text="Créer une nouvelle mind map", command=self.creer)
        self.bouton_nouveau.pack(pady=5)

        self.bouton_fichiers = ctk.CTkButton(self.main_frame, text="Les fichiers existants", command=self.afficher_fichiers)
        self.bouton_fichiers.pack(pady=10)

        self.fichiers_frame = None  # Contiendra la liste des fichiers plus tard

    # Création d’un nouveau fichier vide
    def creer(self):
        filename = self.filename_entry.get().strip()
        if filename:
            fichier = filename + ".json"
            if not os.path.exists(fichier):
                with open(fichier, "w") as f:
                    json.dump({"elements": [], "lines": []}, f)
            self.ouvrir_mindmap(fichier)

    # Affiche la liste des fichiers dans un nouveau cadre
    def afficher_fichiers(self):
        if self.fichiers_frame:
            self.fichiers_frame.destroy()

        self.fichiers_frame = ctk.CTkScrollableFrame(self.main_frame, height=300)
        self.fichiers_frame.pack(pady=10, fill="both", expand=True)

        fichiers = [f for f in os.listdir() if f.endswith(".json")]

        if not fichiers:
            msg = ctk.CTkLabel(self.fichiers_frame, text="Aucun fichier trouvé.")
            msg.pack(pady=10)
            return

        for fichier in fichiers:
            ligne = ctk.CTkFrame(self.fichiers_frame)
            ligne.pack(fill="x", padx=10, pady=5)

            nom = ctk.CTkLabel(ligne, text=fichier, anchor="w")
            nom.pack(side="left", expand=True)

            bouton_modifier = ctk.CTkButton(ligne, text="Modifier", width=80,
                                            command=lambda f=fichier: self.ouvrir_mindmap(f))
            bouton_modifier.pack(side="right", padx=5)

            bouton_supprimer = ctk.CTkButton(ligne, text="Supprimer", width=80,
                                             fg_color="red", hover_color="#aa0000",
                                             command=lambda f=fichier: self.supprimer_fichier(f))
            bouton_supprimer.pack(side="right", padx=5)

    # Supprime un fichier .json et actualise la liste
    def supprimer_fichier(self, fichier):
        if os.path.exists(fichier):
            os.remove(fichier)
            self.afficher_fichiers()

    # Lance la mind map
    def ouvrir_mindmap(self, fichier):
        self.main_frame.destroy()
        self.root.geometry("900x600")
        MindMap(self.root, fichier)

# Lancement de l’application
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    app = Accueil(root)
    root.mainloop()
