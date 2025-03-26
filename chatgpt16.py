import tkinter as tk
import json
import random
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import PhotoImage

class MindMap:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.elements = []
        self.selected_element = None
        self.lines = []
        self.filename = "mindmap.json"

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)
        self.context_menu.add_command(label="Modifier texte", command=self.ajouter_texte)
        self.context_menu.add_command(label="Changer couleur", command=self.changer_couleur)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        self.charger()

    def on_click(self, event):
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
        # Créer l'élément texte avec couleur noire
        text_id = self.canvas.create_text(x, y, text=text, fill="black", anchor="center", font=("Arial", 12))
        
        # Calculer la taille de l'élément pour ajuster la taille du rectangle
        bbox = self.canvas.bbox(text_id)  # Récupère la bounding box du texte
        width = bbox[2] - bbox[0] + 20   # Largeur de l'élément avec une petite marge
        height = bbox[3] - bbox[1] + 10  # Hauteur de l'élément avec une petite marge
        
        # Créer le rectangle qui contiendra le texte
        elem_id = self.canvas.create_rectangle(x - width // 2, y - height // 2, x + width // 2, y + height // 2, fill="lightblue")
        
        # Ajouter l'élément à la liste, avec ses propriétés et son ID de texte
        elem = {
            'x': x, 'y': y, 'id': elem_id, 'text_id': text_id, 'text': text,
            'width': width, 'height': height, 'color': 'lightblue'
        }
        
        # Ajouter l'élément dans la liste des éléments
        self.elements.append(elem)
        
        # Sauvegarder l'état actuel dans un fichier JSON
        self.sauvegarder()
        
        # Vérification d'affichage du texte
        print(f"Texte ajouté: {text} à ({x}, {y}) avec ID: {text_id}")


    def supprimer_element(self):
        if self.selected_element:
            self.supprimer_lignes_par_element(self.selected_element)
            self.canvas.delete(self.selected_element['id'])
            self.canvas.delete(self.selected_element['text_id'])
            self.elements.remove(self.selected_element)
            self.selected_element = None
            self.sauvegarder()

    def ajouter_texte(self):
        if self.selected_element:
            self.modifier_texte(self.selected_element)

    def modifier_texte(self, elem):
        def save_texte():
            new_text = text_entry.get()
            self.canvas.itemconfig(elem['text_id'], text=new_text)
            elem['text'] = new_text
            self.redimensionner_element(elem)
            text_entry.destroy()
            save_button.destroy()
            self.sauvegarder()

        text_entry = tk.Entry(self.root)
        text_entry.insert(0, elem['text'])
        text_entry.pack()
        text_entry.focus_set()
        save_button = tk.Button(self.root, text="Sauvegarder", command=save_texte)
        save_button.pack()

    def redimensionner_element(self, elem):
        bbox = self.canvas.bbox(elem['text_id'])
        width = bbox[2] - bbox[0] + 20
        height = bbox[3] - bbox[1] + 10
        elem['width'] = width
        elem['height'] = height
        self.canvas.coords(elem['id'], elem['x'] - width // 2, elem['y'] - height // 2, elem['x'] + width // 2, elem['y'] + height // 2)

    def deplacer_element(self, elem, dx, dy):
        self.canvas.move(elem['id'], dx, dy)
        self.canvas.move(elem['text_id'], dx, dy)
        elem['x'] += dx
        elem['y'] += dy
        self.mettre_a_jour_lignes()
        self.sauvegarder()

    def relier_elements(self, elem1, elem2):
        line_id = self.canvas.create_line(elem1['x'], elem1['y'], elem2['x'], elem2['y'], fill="black", width=2)
        self.lines.append({'start': elem1, 'end': elem2, 'id': line_id})
        self.sauvegarder()

    def supprimer_lignes_par_element(self, elem):
        lignes_a_supprimer = [line for line in self.lines if line['start'] == elem or line['end'] == elem]
        for line in lignes_a_supprimer:
            self.canvas.delete(line['id'])
            self.lines.remove(line)

    def mettre_a_jour_lignes(self):
        for line in self.lines:
            self.canvas.coords(line['id'], line['start']['x'], line['start']['y'], line['end']['x'], line['end']['y'])

    def charger(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                element_map = {}  # Dictionnaire pour retrouver les éléments

                # Charger les éléments
                for elem in data.get("elements", []):
                    new_elem = self.ajouter_element(elem['x'], elem['y'], elem['text'])
                    element_map[(elem['x'], elem['y'])] = new_elem

                # Charger les connexions
                for line in data.get("lines", []):
                    start = element_map.get((line['start']['x'], line['start']['y']))
                    end = element_map.get((line['end']['x'], line['end']['y']))
                    if start and end:
                        self.relier_elements(start, end)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def sauvegarder(self):
        data = {"elements": [{"x": e['x'], "y": e['y'], "text": e['text'], "color": e['color']} for e in self.elements],
                "lines": [{"start": {"x": l['start']['x'], "y": l['start']['y']}, "end": {"x": l['end']['x'], "y": l['end']['y']}} for l in self.lines]}
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    def changer_couleur(self):
        if self.selected_element:
            color = self.generer_couleur_aleatoire()
            self.canvas.itemconfig(self.selected_element['id'], fill=color)
            self.selected_element['color'] = color
            self.sauvegarder()

    def generer_couleur_aleatoire(self):
        return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

if __name__ == "__main__":
    root = tk.Tk()
    app = MindMap(root)
    root.mainloop()
