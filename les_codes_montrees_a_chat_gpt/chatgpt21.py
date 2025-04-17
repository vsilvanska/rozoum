import tkinter as tk
import customtkinter as ctk
import json

class MindMap:
    def __init__(self, root):
        self.root = root
        self.canvas = ctk.CTkCanvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.elements = []
        self.lines = []
        self.selected_element = None
        self.link_start = None
        self.filename = "mindmap.json"
        
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Supprimer", command=self.supprimer_element)
        self.context_menu.add_command(label="Modifier texte", command=self.modifier_texte)
        self.context_menu.add_command(label="Relier", command=self.preparer_lien)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        self.charger()
    
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
                
                # Charger les lignes après avoir ajouté tous les éléments
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



if __name__ == "__main__":
    root = ctk.CTk()
    app = MindMap(root)
    root.mainloop()
