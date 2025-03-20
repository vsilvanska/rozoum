import tkinter as tk
import json

class MindMap:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.elements = []  # Liste des éléments
        self.lines = []  # Liste des connexions
        self.selected_element = None  # Élément sélectionné
        self.filename = "mindmap.json"  # Fichier de sauvegarde

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Ajouter du texte", command=self.ajouter_texte)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)

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
            self.redessiner_connexions()

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
        elem = {'x': x, 'y': y, 'id': elem_id, 'text_id': text_id, 'text': text, 'width': width, 'height': height}
        self.elements.append(elem)
        self.sauvegarder()
        return elem

    def supprimer_element(self):
        if self.selected_element:
            self.canvas.delete(self.selected_element['id'])
            self.canvas.delete(self.selected_element['text_id'])
            self.elements.remove(self.selected_element)
            self.lines = [line for line in self.lines if line['start'] != self.selected_element and line['end'] != self.selected_element]
            self.redessiner_connexions()
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
        text_entry.pack(pady=5)
        text_entry.focus_set()
        save_button = tk.Button(self.root, text="Sauvegarder", command=save_texte)
        save_button.pack(pady=5)

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
        self.sauvegarder()

    def relier_elements(self, elem1, elem2):
        print(f"Relier ({elem1['x']}, {elem1['y']}) et ({elem2['x']}, {elem2['y']})")
        line_id = self.canvas.create_line(
            elem1['x'], elem1['y'], elem2['x'], elem2['y'], 
            fill="black", width=2, dash=(4, 2)
        )
        self.lines.append({'start': elem1, 'end': elem2, 'id': line_id})
        print(f"Ligne ajoutée entre ({elem1['x']}, {elem1['y']}) et ({elem2['x']}, {elem2['y']})")
        self.sauvegarder()

    def redessiner_connexions(self):
        for line in self.lines:
            self.canvas.coords(line['id'], line['start']['x'], line['start']['y'], line['end']['x'], line['end']['y'])

    def sauvegarder(self):
        data = {'elements': self.elements, 'lines': [{'start': self.elements.index(line['start']), 'end': self.elements.index(line['end'])} for line in self.lines]}
        with open(self.filename, "w") as f:
            json.dump(data, f)

    def charger(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.elements = []
                    self.lines = []
                    for elem in data.get('elements', []):
                        self.ajouter_element(elem['x'], elem['y'], elem.get('text', ''))
                    for line in data.get('lines', []):
                        self.relier_elements(self.elements[line['start']], self.elements[line['end']])
        except (FileNotFoundError, json.JSONDecodeError, IndexError):
            pass

root = tk.Tk()
root.title("MindMap")
app = MindMap(root)
root.mainloop()
