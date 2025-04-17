#bof

import tkinter as tk

class MindMap:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)  # Canevas qui s'adapte à la taille de la fenêtre

        self.elements = []  # Liste des éléments (éléments sont des dicts)
        self.selected_element = None  # Élément sélectionné
        self.lines = []  # Liste des lignes de connexion

        # Créer un menu contextuel
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Ajouter du texte", command=self.ajouter_texte)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)

        # Liaison des événements
        self.canvas.bind("<Button-1>", self.on_click)  # Clic gauche pour ajouter et sélectionner
        self.canvas.bind("<Button-3>", self.on_right_click)  # Clic droit pour ouvrir le menu contextuel
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Déplacement des éléments

    def on_click(self, event):
        """Gestion du clic gauche : Ajouter un élément ou sélectionner un élément existant"""
        # Vérifie si on a cliqué sur un élément existant
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                if self.selected_element is None:
                    self.selectionner(elem)
                else:
                    # Relier les deux éléments
                    self.relier_elements(self.selected_element, elem)
                    self.selected_element = None
                return

        # Si aucun élément n'est trouvé, ajoute un nouvel élément
        self.ajouter_element(event.x, event.y)

    def on_right_click(self, event):
        """Gère le clic droit pour afficher le menu contextuel"""
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                self.selected_element = elem
                self.context_menu.post(event.x_root, event.y_root)  # Affiche le menu contextuel
                return

    def on_drag(self, event):
        """Déplace un élément sélectionné"""
        if self.selected_element:
            dx = event.x - self.selected_element['x']
            dy = event.y - self.selected_element['y']
            self.deplacer_element(self.selected_element, dx, dy)

    def is_within_element(self, x, y, elem):
        """Vérifie si un clic se trouve à l'intérieur de l'élément"""
        return elem['x'] - elem['width'] // 2 <= x <= elem['x'] + elem['width'] // 2 and elem['y'] - elem['height'] // 2 <= y <= elem['y'] + elem['height'] // 2

    def selectionner(self, elem):
        """Sélectionne un élément et le met en surbrillance"""
        if self.selected_element:
            self.canvas.itemconfig(self.selected_element['id'], outline='black')  # Retour à l'état initial

        # Sélectionne le nouvel élément
        self.selected_element = elem
        self.canvas.itemconfig(elem['id'], outline='red', width=3)  # Changer la couleur pour la sélection
        print(f"Élément sélectionné à ({elem['x']}, {elem['y']})")

    def ajouter_element(self, x, y):
        """Ajoute un nouvel élément (rectangle + texte) à la position donnée"""
        text_id = self.canvas.create_text(x, y, text="Cliquez pour éditer", fill="black", anchor="center")
        bbox = self.canvas.bbox(text_id)  # Obtenir la taille du texte
        width = bbox[2] - bbox[0] + 20  # Ajouter un peu d'espace autour du texte
        height = bbox[3] - bbox[1] + 10  # Ajouter un peu d'espace autour du texte
        elem_id = self.canvas.create_rectangle(x - width // 2, y - height // 2, x + width // 2, y + height // 2, fill="blue")

        # Ajout de l'élément dans la liste
        self.elements.append({'x': x, 'y': y, 'id': elem_id, 'text_id': text_id, 'text': "Cliquez pour éditer", 'width': width, 'height': height})
        print(f"Élément ajouté en ({x}, {y})")

    def supprimer_element(self):
        """Supprime l'élément sélectionné"""
        if self.selected_element:
            self.canvas.delete(self.selected_element['id'])  # Supprime l'élément
            self.canvas.delete(self.selected_element['text_id'])  # Supprime le texte

            # Supprimer les lignes associées
            for line in self.lines[:]:
                if line['start'] == self.selected_element or line['end'] == self.selected_element:
                    self.canvas.delete(line['id'])  # Supprime la ligne
                    self.lines.remove(line)  # Supprime la ligne de la liste
            print(f"Élément supprimé à ({self.selected_element['x']}, {self.selected_element['y']})")

            # Supprime l'élément de la liste
            self.elements.remove(self.selected_element)
            self.selected_element = None

    def ajouter_texte(self):
        """Permet d'ajouter ou modifier le texte d'un élément"""
        if self.selected_element:
            self.modifier_texte(self.selected_element)

    def modifier_texte(self, elem):
        """Permet de modifier le texte d'un élément en affichant un champ de texte"""
        def save_texte():
            new_text = text_entry.get()  # Récupère le texte entré
            self.canvas.itemconfig(elem['text_id'], text=new_text)  # Met à jour le texte de l'élément
            elem['text'] = new_text  # Met à jour le texte dans la liste de l'élément
            self.redimensionner_element(elem)  # Redimensionne l'élément pour ajuster au texte
            text_entry.destroy()  # Ferme le champ de texte
            save_button.destroy()  # Ferme le bouton de sauvegarde

        # Créer un champ de texte pour entrer du texte
        text_entry = tk.Entry(root)
        text_entry.insert(0, elem['text'])
        text_entry.pack(pady=5)  # Ajoute un peu d'espace autour du champ de texte
        text_entry.focus_set()

        # Créer un bouton pour sauvegarder le texte
        save_button = tk.Button(root, text="Sauvegarder", command=save_texte)
        save_button.pack(pady=5)  # Ajoute un peu d'espace autour du bouton

    def redimensionner_element(self, elem):
        """Redimensionne l'élément en fonction de son texte"""
        bbox = self.canvas.bbox(elem['text_id'])  # Obtenir la taille du texte
        width = bbox[2] - bbox[0] + 20  # Ajouter un peu d'espace autour du texte
        height = bbox[3] - bbox[1] + 10  # Ajouter un peu d'espace autour du texte
        elem['width'] = width
        elem['height'] = height
        self.canvas.coords(elem['id'], elem['x'] - width // 2, elem['y'] - height // 2, elem['x'] + width // 2, elem['y'] + height // 2)

    def deplacer_element(self, elem, dx, dy):
        """Déplace l'élément sélectionné"""
        self.canvas.move(elem['id'], dx, dy)
        elem['x'] += dx
        elem['y'] += dy
        self.canvas.move(elem['text_id'], dx, dy)  # Déplace le texte avec l'élément

    def relier_elements(self, elem1, elem2):
        """Relie deux éléments avec une ligne"""
        line_id = self.canvas.create_line(
            elem1['x'], elem1['y'], elem2['x'], elem2['y'], 
            fill="black", width=2, dash=(4, 2)  # Couleur noire et ligne pointillée
        )
        self.lines.append({'start': elem1, 'end': elem2, 'id': line_id})

# Création de la fenêtre principale
root = tk.Tk()
root.title("MindMap")
app = MindMap(root)
root.mainloop()
