import tkinter as tk
import customtkinter as ctk
import json
import os

# Classe principale de la carte mentale
class MindMap:
    def __init__(self, root, filename):
        self.root = root
        self.filename = filename

        # Création du canvas dans un CTkScrollableFrame
        self.scrollable_frame = ctk.CTkScrollableFrame(root, width=800, height=600)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.bouton_retour = ctk.CTkButton(
            self.scrollable_frame, text="⬅️ Retour au menu",
            command=self.retour_accueil, fg_color="#d32f2f", hover_color="#b71c1c",  # Rouge élégant
            width=160, height=35, corner_radius=10
        )
        self.bouton_retour.pack(pady=10)


        self.canvas = ctk.CTkCanvas(self.scrollable_frame, bg="white", width=2000, height=2000)  # Large canvas pour permettre le défilement
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
        elem_id = self.canvas.create_rectangle(
            x - width//2, y - height//2, x + width//2, y + height//2,
            fill="#e3f2fd", outline="#2196f3", width=2  # Bleu clair, bord bleu officiel
        )
        text_id = self.canvas.create_text(
            x, y, text=text, fill="#1a237e", font=("Arial", 12, "bold")  # Bleu très foncé
        )
        self.elements.append({
            'x': x, 'y': y, 'id': elem_id, 'text_id': text_id,
            'text': text, 'width': width, 'height': height
        })
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

            text_entry = tk.Text(self.root, height=4, width=30, font=("Arial", 12))
            text_entry.insert("1.0", self.selected_element['text'])
            text_entry.pack(pady=10)

            save_button = ctk.CTkButton(
                self.root, text="💾 Sauvegarder", command=save_texte,
                width=150, height=35, corner_radius=10,
                fg_color="#4caf50", hover_color="#45a049"
            )
            save_button.pack(pady=5)

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
            line_id = self.canvas.create_line(
                elem1['x'], elem1['y'], elem2['x'], elem2['y'],
                fill="#455a64", width=2, smooth=True  # Gris-bleu élégant
            )
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

    def retour_accueil(self):
        # Détruire tous les widgets de la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        # Recharger l'accueil
        Accueil(self.root)



class Accueil:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x600")
        self.root.title("Accueil - Cartes mentales")

        ctk.set_appearance_mode("light")  # Mode par défaut (clair)
        ctk.set_default_color_theme("blue")

        # Main frame for content
        self.main_frame = ctk.CTkFrame(root, corner_radius=25, fg_color="#f5f5f5")  # Gris clair
        self.main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Header frame for title
        self.header = ctk.CTkFrame(self.main_frame, fg_color="#e0e0e0", corner_radius=15)  # Gris léger
        self.header.pack(fill="x", pady=20)

        # Title label with a formal color
        self.title = ctk.CTkLabel(self.header, text="Bienvenue dans l'application de cartes mentales", font=("Arial", 24, "bold"), text_color="#333333")  # Gris foncé
        self.title.pack(pady=10)

        # Button to create a new mind map with professional colors
        self.bouton_nouveau = ctk.CTkButton(self.main_frame, text="🌟 Créer une nouvelle mind map", command=self.afficher_creation_fichier,
                                            width=250, height=45, corner_radius=12, hover_color="#4b8df8", fg_color="#5c85d6")  # Bleu plus professionnel
        self.bouton_nouveau.pack(pady=10)

        # Button to show existing files with a different, muted color
        self.bouton_fichiers = ctk.CTkButton(self.main_frame, text="📁 Les fichiers existants", command=self.afficher_fichiers,
                                             width=250, height=45, corner_radius=12, hover_color="#58a64d", fg_color="#6dbf6a")  # Vert olive
        self.bouton_fichiers.pack(pady=10)

        # Frame for the file name entry, initially hidden
        self.filename_frame = ctk.CTkFrame(self.main_frame)
        self.filename_frame.pack(pady=10, fill="x")
        self.filename_entry = ctk.CTkEntry(self.filename_frame, placeholder_text="Nom de la carte (sans .json)", height=40, width=280, corner_radius=10)
        self.filename_entry.pack(padx=20, fill="x")

        # Button for creating a new mind map with a professional style
        self.bouton_creer = ctk.CTkButton(self.filename_frame, text="Créer", command=self.creer, width=200, height=40, corner_radius=10, fg_color="#4caf50", hover_color="#45a049")  # Vert classique
        self.bouton_creer.pack(pady=10)

        # Frame for displaying existing files, initially hidden
        self.fichiers_frame = ctk.CTkFrame(self.main_frame)
        self.fichiers_frame.pack(pady=10, fill="x")

    def afficher_creation_fichier(self):
        """Afficher les champs pour entrer le nom du fichier quand l'utilisateur veut créer un nouveau fichier."""
        # Masquer les autres éléments et afficher le champ pour créer un fichier
        self.fichiers_frame.pack_forget()  # Masque les fichiers existants
        self.filename_frame.pack(fill="x", pady=20)  # Affiche le champ de création de fichier

    def afficher_fichiers(self):
        """Afficher la liste des fichiers existants."""
        # Masquer le champ de création de fichier et afficher les fichiers existants
        self.filename_frame.pack_forget()  # Masque le champ pour créer un fichier
        self.fichiers_frame.pack(fill="x", pady=20)  # Affiche la liste des fichiers existants

        # Vider la frame des fichiers existants avant de la remplir
        for widget in self.fichiers_frame.winfo_children():
            widget.destroy()

        fichiers = [f for f in os.listdir() if f.endswith(".json")]

        if not fichiers:
            msg = ctk.CTkLabel(self.fichiers_frame, text="Aucun fichier trouvé.", font=("Arial", 14), text_color="#333333")
            msg.pack(pady=10)
            return

        # Dynamically add each file to the frame with professional style
        for fichier in fichiers:
            ligne = ctk.CTkFrame(self.fichiers_frame)
            ligne.pack(fill="x", padx=20, pady=8)

            # File name label with a muted color
            nom = ctk.CTkLabel(ligne, text=fichier, anchor="w", font=("Arial", 14), text_color="#4b4b4b")  # Gris clair
            nom.pack(side="left", expand=True)

            # Buttons for modifying, renaming, and deleting files with formal colors
            bouton_modifier = ctk.CTkButton(ligne, text="🖊️ Modifier", width=90, corner_radius=10, fg_color="#4b8df8", hover_color="#4b8df8",
                                            command=lambda f=fichier: self.ouvrir_mindmap(f))
            bouton_modifier.pack(side="right", padx=8)

            bouton_renommer = ctk.CTkButton(ligne, text="📝 Renommer", width=90, corner_radius=10, fg_color="#4caf50", hover_color="#45a049",
                                            command=lambda f=fichier: self.renommer_fichier(f))
            bouton_renommer.pack(side="right", padx=8)

            bouton_supprimer = ctk.CTkButton(ligne, text="🗑️ Supprimer", width=90, corner_radius=10, fg_color="red", hover_color="#cc1f1f",
                                             command=lambda f=fichier: self.supprimer_fichier(f))
            bouton_supprimer.pack(side="right", padx=8)

    def creer(self):
        filename = self.filename_entry.get().strip()
        if filename:
            fichier = filename + ".json"
            if not os.path.exists(fichier):
                with open(fichier, "w") as f:
                    json.dump({"elements": [], "lines": []}, f)
            self.ouvrir_mindmap(fichier)

    def supprimer_fichier(self, fichier):
        if os.path.exists(fichier):
            os.remove(fichier)
            self.afficher_fichiers()

    def renommer_fichier(self, fichier):
        popup = tk.Toplevel(self.root)
        popup.title("Renommer le fichier")
        popup.geometry("300x150")

        label = ctk.CTkLabel(popup, text="Nouveau nom (sans .json):", font=("Arial", 14), text_color="#333333")
        label.pack(pady=10)

        entry = ctk.CTkEntry(popup, font=("Arial", 12), height=35)
        entry.insert(0, fichier.replace(".json", ""))
        entry.pack(pady=5)

        def valider():
            nouveau_nom = entry.get().strip()
            if nouveau_nom:
                nouveau_fichier = nouveau_nom + ".json"
                if not os.path.exists(nouveau_fichier):
                    os.rename(fichier, nouveau_fichier)
                    popup.destroy()
                    self.afficher_fichiers()

        bouton_valider = ctk.CTkButton(popup, text="Valider", command=valider, width=150, height=35, corner_radius=10, fg_color="#4caf50", hover_color="#45a049")
        bouton_valider.pack(pady=10)

    def ouvrir_mindmap(self, fichier):
        self.main_frame.destroy()
        self.root.geometry("900x600")
        MindMap(self.root, fichier)


if __name__ == "__main__":
    root = ctk.CTk()
    app = Accueil(root)
    root.mainloop()
