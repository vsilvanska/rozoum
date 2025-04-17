#AJOUT DES ELEMENTS

import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import json
import os

class MindMap(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mind Map")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.elements = []  # Liste des éléments
        self.liaisons = []  # Liste des connexions
        self.selection = None  # Élément actuellement sélectionné pour la liaison

        self.menu = ctk.CTkFrame(self)
        self.menu.pack(fill="x")

        self.save_button = ctk.CTkButton(self.menu, text="💾 Sauvegarder", command=self.sauvegarder)
        self.save_button.pack(side="left", padx=10, pady=5)

        self.load_button = ctk.CTkButton(self.menu, text="📂 Ouvrir", command=self.ouvrir)
        self.load_button.pack(side="left", padx=10, pady=5)

        self.bind("<Button-1>", self.ajouter_ou_selectionner)  

        if os.path.exists("mind_map.json"):
            self.ouvrir("mind_map.json")

    def ajouter_ou_selectionner(self, event):
        """Ajoute un élément si aucun élément à cet endroit, sinon sélectionne un élément existant."""
        # Vérifie si l'utilisateur clique sur un élément existant
        for elem in self.elements:
            if self.est_dans_element(event.x, event.y, elem):
                self.selectionner(elem)
                return
        # Si aucun élément n'est cliqué, on ajoute un nouvel élément
        noeud = Element(self.canvas, event.x, event.y, self)
        self.elements.append(noeud)

    def est_dans_element(self, x, y, element):
        """Vérifie si les coordonnées (x, y) sont à l'intérieur de l'élément"""
        return (element.x - 60 <= x <= element.x + 60) and (element.y - 25 <= y <= element.y + 25)

    def lier(self, element1, element2):
        """Relie deux éléments par une ligne"""
        ligne = self.canvas.create_line(
            element1.x, element1.y, element2.x, element2.y, width=2, fill="black"
        )
        self.liaisons.append((element1, element2, ligne))
        element1.associer(element2)
        element2.associer(element1)

    def sauvegarder(self):
        """Sauvegarde la structure sous format JSON"""
        data = {
            "elements": [{"x": e.x, "y": e.y, "texte": e.label.cget("text")} for e in self.elements],
            "liaisons": [(self.elements.index(e1), self.elements.index(e2)) for e1, e2, _ in self.liaisons]
        }
        with open("mind_map.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("✅ Sauvegarde réussie !")

    def ouvrir(self, fichier=None):
        """Ouvre un fichier JSON contenant une structure"""
        if not fichier:
            fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
            if not fichier:
                return

        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "elements" not in data or "liaisons" not in data:
                print("⚠ Fichier invalide ! Réinitialisation...")
                return

            self.canvas.delete("all")  
            self.elements.clear()
            self.liaisons.clear()

            for elem in data["elements"]:
                noeud = Element(self.canvas, elem["x"], elem["y"], self, elem["texte"])
                self.elements.append(noeud)

            for e1, e2 in data["liaisons"]:
                self.lier(self.elements[e1], self.elements[e2])

            print("✅ Chargement effectué !")

        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠ Erreur lors de la lecture du fichier !")

    def selectionner(self, element):
        """Permet de relier deux éléments en cliquant sur eux"""
        if self.selection is None:
            self.selection = element
            print(f"📌 Élément sélectionné : {element.label.cget('text')}")
        else:
            if self.selection != element:
                print(f"🔗 Liaison : {self.selection.label.cget('text')} ↔ {element.label.cget('text')}")
                self.lier(self.selection, element)
            self.selection = None  # Réinitialiser la sélection

    def supprimer(self, element):
        """Supprime un élément et ses connexions"""
        self.canvas.delete(element.window)  # Supprime l'élément de la toile
        for liaison in self.liaisons:
            if element in liaison:
                self.canvas.delete(liaison[2])  # Supprime la ligne de liaison
                self.liaisons.remove(liaison)  # Retire la liaison de la liste
        self.elements.remove(element)  # Retire l'élément de la liste
        print(f"❌ Élément '{element.label.cget('text')}' supprimé")

    def demander_action(self, element):
        """Demande une action pour un élément sélectionné"""
        reponse = messagebox.askquestion(
            "Que voulez-vous faire ?",
            f"Que voulez-vous faire avec l'élément '{element.label.cget('text')}' ?\n\n"
            "1. Supprimer\n2. Sélectionner\n3. Annuler",
            icon='question'
        )
        if reponse == "yes":
            self.supprimer(element)
        elif reponse == "no":
            self.selectionner(element)
        # Si l'utilisateur annule, rien ne se passe

class Element:
    def __init__(self, canvas, x, y, mind_map, texte="Élément"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.mind_map = mind_map
        self.liaisons = []

        self.frame = ctk.CTkFrame(self.mind_map, width=120, height=50, corner_radius=8)
        self.label = ctk.CTkLabel(self.frame, text=texte)
        self.label.pack(expand=True)

        self.window = self.canvas.create_window(x, y, window=self.frame)

        self.frame.bind("<B1-Motion>", self.deplacer)  
        self.frame.bind("<Double-Button-1>", self.editer)  
        self.frame.bind("<Button-3>", self.selectionner_clic_droit)  # Clic droit pour sélectionner

    def deplacer(self, event):
        """Déplace un élément et met à jour les connexions"""
        self.x = event.x_root - self.mind_map.winfo_rootx()
        self.y = event.y_root - self.mind_map.winfo_rooty()
        self.canvas.coords(self.window, self.x, self.y)

        for noeud in self.liaisons:
            for (e1, e2, ligne) in self.mind_map.liaisons:
                if (e1 == self and e2 == noeud) or (e1 == noeud and e2 == self):
                    self.canvas.coords(ligne, self.x, self.y, noeud.x, noeud.y)

    def editer(self, event):
        """Modifier le texte"""
        nouveau = simpledialog.askstring("Modifier", "Nouveau texte :", initialvalue=self.label.cget("text"))
        if nouveau:
            self.label.configure(text=nouveau)

    def associer(self, element):
        """Ajoute une liaison entre deux éléments"""
        if element not in self.liaisons:
            self.liaisons.append(element)

    def selectionner_clic_droit(self, event):
        """Gestion du clic droit pour la sélection"""
        self.mind_map.demander_action(self)

if __name__ == "__main__":
    app = MindMap()
    app.mainloop()
