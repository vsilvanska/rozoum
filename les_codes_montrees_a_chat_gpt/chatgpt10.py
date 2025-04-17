#bof

import tkinter as tk
import math

class MindMap:
    def __init__(self, root):
        # Frame pour contenir le canevas et les barres de défilement
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Ajouter un canevas dans le frame
        self.canvas = tk.Canvas(self.frame, width=600, height=400)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Ajouter des barres de défilement verticales et horizontales
        self.v_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)

        # Configurer la grille pour permettre l'extension du canevas
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.elements = []  # Liste des éléments
        self.selected_element = None  # Élément actuellement sélectionné
        self.lines = []  # Liste des lignes entre les éléments
        self.offset_x = 0  # Décalage en x pour le déplacement
        self.offset_y = 0  # Décalage en y pour le déplacement

        self.first_element_marker = None  # Référence pour le marqueur du premier élément

        # Lier la taille de la fenêtre pour redimensionner le canevas
        root.bind("<Configure>", self.resize_canvas)

        self.canvas.bind("<Button-1>", self.on_click)  # Clic gauche pour ajouter, sélectionner
        self.canvas.bind("<Button-3>", self.on_right_click)  # Clic droit pour supprimer
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Déplacement des éléments

    def resize_canvas(self, event):
        """Met à jour la taille du canevas lors du redimensionnement de la fenêtre"""
        width = event.width
        height = event.height
        self.canvas.config(width=width, height=height)

        # Redessiner les lignes et éléments si nécessaire pour s'assurer qu'ils restent dans les limites
        for elem in self.elements:
            self.canvas.coords(elem['id'], elem['x'] - 10, elem['y'] - 10, elem['x'] + 10, elem['y'] + 10)
        for line in self.lines:
            self.canvas.coords(line['id'], line['start']['x'], line['start']['y'], line['end']['x'], line['end']['y'])

        # Mettre à jour la position du marqueur du premier élément
        if self.first_element_marker:
            self.mettre_a_jour_marqueur_premier_element()

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

    def on_drag(self, event):
        """Déplace l'élément sélectionné"""
        if self.selected_element:
            dx = event.x - self.offset_x
            dy = event.y - self.offset_y
            self.deplacer_element(self.selected_element, dx, dy)
            self.offset_x = event.x
            self.offset_y = event.y

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
        self.offset_x = elem['x']
        self.offset_y = elem['y']
        print(f"Élément sélectionné à ({elem['x']}, {elem['y']})")

    def ajouter_element(self, x, y):
        """Ajoute un nouvel élément à la position donnée"""
        elem_id = self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="blue")
        self.elements.append({'x': x, 'y': y, 'id': elem_id})

        # Si c'est le premier élément, ajouter un marqueur pour le repérer
        if len(self.elements) == 1:
            self.marquer_premier_element(x, y)

        print(f"Élément ajouté en ({x}, {y})")

    def marquer_premier_element(self, x, y):
        """Ajoute un cercle pour marquer la position du premier élément"""
        if self.first_element_marker:
            self.canvas.delete(self.first_element_marker)  # Supprimer le marqueur précédent, le cas échéant

        # Position fixe du cercle dans le coin supérieur gauche de l'écran
        self.first_element_marker = self.canvas.create_oval(
            20, 20, 60, 60,  # Position fixe à (20, 20) dans le coin supérieur gauche
            outline="green", width=3, dash=(4, 2)
        )
        print(f"Premier élément marqué à ({x}, {y})")

    def mettre_a_jour_marqueur_premier_element(self):
        """Met à jour la position du marqueur du premier élément pour qu'il reste dans la vue"""
        if self.first_element_marker:
            # Calculer les décalages du défilement
            x_scroll = self.canvas.xview()[0] * self.canvas.winfo_width()
            y_scroll = self.canvas.yview()[0] * self.canvas.winfo_height()

            # Calculer la position du marqueur en tenant compte du défilement
            self.canvas.coords(self.first_element_marker, x_scroll + 20, y_scroll + 20, x_scroll + 60, y_scroll + 60)

            # Vérifier si l'élément est visible
            first_element = self.elements[0] if self.elements else None
            if first_element:
                elem_bbox = self.canvas.bbox(first_element['id'])
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # Si l'élément est visible à l'écran
                if (elem_bbox[0] > 0 and elem_bbox[2] < canvas_width and
                    elem_bbox[1] > 0 and elem_bbox[3] < canvas_height):
                    self.canvas.delete(self.first_element_marker)  # Supprimer le marqueur si l'élément est visible
                else:
                    self.afficher_cercle_pointeur(first_element)

    def afficher_cercle_pointeur(self, first_element):
        """Affiche le cercle pointant vers la direction du premier élément"""
        # Calculer la direction du premier élément
        x1, y1 = first_element['x'], first_element['y']
        canvas_center_x = self.canvas.winfo_width() // 2
        canvas_center_y = self.canvas.winfo_height() // 2

        # Calculer les coordonnées du cercle de direction
        angle = math.atan2(y1 - canvas_center_y, x1 - canvas_center_x)
        pointer_x = canvas_center_x + math.cos(angle) * 50
        pointer_y = canvas_center_y + math.sin(angle) * 50

        # Redessiner le cercle pointer
        if self.first_element_marker:
            self.canvas.coords(self.first_element_marker, pointer_x - 10, pointer_y - 10, pointer_x + 10, pointer_y + 10)

    def supprimer_element(self, elem):
        """Supprime un élément et ses lignes associées"""
        self.canvas.delete(elem['id'])  # Supprime l'élément

        # Supprimer les lignes associées
        for line in self.lines[:]:
            if line['start'] == elem or line['end'] == elem:
                self.canvas.delete(line['id'])  # Supprime la ligne
                self.lines.remove(line)  # Supprime la ligne de la liste
        print(f"Élément supprimé à ({elem['x']}, {elem['y']})")

        # Supprime l'élément de la liste
        self.elements.remove(elem)

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

    def deplacer_element(self, elem, dx, dy):
        """Déplace un élément"""
        self.canvas.move(elem['id'], dx, dy)
        elem['x'] += dx
        elem['y'] += dy
        # Met à jour les lignes qui relient cet élément
        for line in self.lines:
            if line['start'] == elem:
                self.canvas.coords(line['id'], elem['x'], elem['y'], line['end']['x'], line['end']['y'])
            elif line['end'] == elem:
                self.canvas.coords(line['id'], line['start']['x'], line['start']['y'], elem['x'], elem['y'])

# Création de la fenêtre principale
root = tk.Tk()
root.title("MindMap")
app = MindMap(root)
root.mainloop()
