import tkinter as tk
import json

class MindMap:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.elements = []  # Liste des éléments
        self.selected_element = None  # Élément sélectionné
        self.lines = []  # Liste des connexions
        self.filename = "mindmap.json"  # Fichier de sauvegarde

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        # Charger les éléments et les lignes à partir du fichier JSON
        self.charger()

    def charger(self):
        """Charge les éléments et les lignes depuis un fichier JSON."""
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):  # Vérifie que c'est un dictionnaire
                    print("Erreur : le fichier JSON n'est pas au bon format.")
                    return

                elements = data.get("elements", [])
                lines = data.get("lines", [])
                
                for elem in elements:
                    if isinstance(elem, dict):
                        self.ajouter_element(elem['x'], elem['y'], elem['text'])
                
                for line in lines:
                    if isinstance(line, dict):
                        self.relier_elements_by_coords(line['start'], line['end'])

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erreur lors du chargement : {e}")

    def sauvegarder(self):
        """Sauvegarde les éléments et les lignes dans un fichier JSON."""
        with open(self.filename, "w") as f:
            data = {
                "elements": [{'x': elem['x'], 'y': elem['y'], 'text': elem['text']} for elem in self.elements],
                "lines": [{'start': {'x': line['start']['x'], 'y': line['start']['y']},
                           'end': {'x': line['end']['x'], 'y': line['end']['y']}} for line in self.lines]
            }
            json.dump(data, f)

    def on_click(self, event):
        """Gère les clics gauche pour ajouter, sélectionner ou relier des éléments"""
        for elem in self.elements:
            if self.is_within_element(event.x, event.y, elem):
                if self.selected_element is None:
                    self.selectionner(elem)
                else:
                    self.relier_elements(self.selected_element, elem)
                    self.selected_element = None
                return
        self.ajouter_element(event.x, event.y, "Nouveau texte")

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
        return (elem['x'] - elem['width'] // 2 <= x <= elem['x'] + elem['width'] // 2 and
                elem['y'] - elem['height'] // 2 <= y <= elem['y'] + elem['height'] // 2)

    def selectionner(self, elem):
        if self.selected_element:
            self.canvas.itemconfig(self.selected_element['id'], outline='black')
        self.selected_element = elem
        self.canvas.itemconfig(elem['id'], outline='red', width=3)

    def ajouter_element(self, x, y, text):
        text_id = self.canvas.create_text(x, y, text=text, fill="black", anchor="center")
        bbox = self.canvas.bbox(text_id)
        width = bbox[2] - bbox[0] + 20
        height = bbox[3] - bbox[1] + 10
        elem_id = self.canvas.create_rectangle(x - width // 2, y - height // 2, x + width // 2, y + height // 2, fill="blue")
        self.elements.append({'x': x, 'y': y, 'id': elem_id, 'text_id': text_id, 'text': text, 'width': width, 'height': height})
        self.sauvegarder()  # Appel à sauvegarder()

    def supprimer_element(self):
        if self.selected_element:
            self.canvas.delete(self.selected_element['id'])
            self.canvas.delete(self.selected_element['text_id'])
            self.elements.remove(self.selected_element)
            self.selected_element = None
            self.sauvegarder()

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
        self.sauvegarder()

    def relier_elements_by_coords(self, start, end):
        """Crée une ligne à partir des coordonnées sauvegardées"""
        line_id = self.canvas.create_line(
            start['x'], start['y'], end['x'], end['y'], 
            fill="black", width=2, dash=(4, 2)  # Couleur noire et ligne pointillée
        )
        self.lines.append({'start': start, 'end': end, 'id': line_id})

    def deplacer_element(self, elem, dx, dy):
        self.canvas.move(elem['id'], dx, dy)
        self.canvas.move(elem['text_id'], dx, dy)
        elem['x'] += dx
        elem['y'] += dy
        self.sauvegarder()


# Formation de la fenêtre principale
root = tk.Tk()
root.title("MindMap")
app = MindMap(root)
root.mainloop()
