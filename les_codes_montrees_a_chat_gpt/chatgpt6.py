#AJOUTER, CHOISIR, SUPPRIMER ET RELIER LES ELEMENTS


import tkinter as tk

class MindMap:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=600, height=400)
        self.canvas.pack()

        self.elements = []  # Liste des éléments
        self.selected_element = None  # Élément actuellement sélectionné
        self.lines = []  # Liste des lignes entre les éléments

        self.canvas.bind("<Button-1>", self.on_click)  # Clic gauche pour ajouter, sélectionner
        self.canvas.bind("<Button-3>", self.on_right_click)  # Clic droit pour supprimer

    def on_click(self, event):
        """Gère les clics gauche pour ajouter, sélectionner ou relier des éléments"""
        # Vérifie si un élément existe déjà à l'endroit cliqué
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
        """Gère les clics droit pour supprimer un élément"""
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                self.supprimer_element(elem)
                return

    def is_within_element(self, x, y, elem):
        """Vérifie si les coordonnées sont dans un élément"""
        return elem['x'] - 10 <= x <= elem['x'] + 10 and elem['y'] - 10 <= y <= elem['y'] + 10

    def selectionner(self, elem):
        """Sélectionne un élément"""
        # Si un autre élément est sélectionné, le désélectionner
        if self.selected_element:
            self.canvas.itemconfig(self.selected_element['id'], outline='black')  # Retour à l'état initial

        # Sélectionne le nouvel élément
        self.selected_element = elem
        self.canvas.itemconfig(elem['id'], outline='red', width=3)  # Change la couleur pour le sélection
        print(f"Élément sélectionné à ({elem['x']}, {elem['y']})")

    def ajouter_element(self, x, y):
        """Ajoute un nouvel élément à la position donnée"""
        elem_id = self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="blue")
        self.elements.append({'x': x, 'y': y, 'id': elem_id})
        print(f"Élément ajouté en ({x}, {y})")

    def supprimer_element(self, elem):
        """Supprime un élément"""
        self.canvas.delete(elem['id'])
        # Supprimer les lignes associées
        self.lines = [line for line in self.lines if line['start'] != elem and line['end'] != elem]
        for line in self.lines:
            self.canvas.delete(line['id'])
        self.elements.remove(elem)
        print(f"Élément supprimé à ({elem['x']}, {elem['y']})")

    def relier_elements(self, elem1, elem2):
        """Relie deux éléments avec une ligne"""
        print(f"Relier ({elem1['x']}, {elem1['y']}) et ({elem2['x']}, {elem2['y']})")  # Debugging
        # Dessiner la ligne entre les deux éléments
        line_id = self.canvas.create_line(
            elem1['x'], elem1['y'], elem2['x'], elem2['y'], 
            fill="black", width=2, dash=(4, 2)  # Couleur noire et ligne pointillée
        )
        self.lines.append({'start': elem1, 'end': elem2, 'id': line_id})
        print(f"Ligne ajoutée entre ({elem1['x']}, {elem1['y']}) et ({elem2['x']}, {elem2['y']})")

# Formation de la fenêtre principale
root = tk.Tk()
root.title("MindMap")
app = MindMap(root)
root.mainloop()
