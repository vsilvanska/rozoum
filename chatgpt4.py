#AJOUT DES ELEMENTS

import customtkinter as ctk
import tkinter as tk

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Test des Clics")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.elements = []  # Liste des éléments
        self.selection = None  # Élément actuellement sélectionné
        self.selection_rectangle = None  # Rectangle de sélection

        self.bind("<Button-1>", self.ajouter_element)  # Clic gauche pour ajouter un élément
        self.bind("<Double-1>", self.selectionner_element)  # Double-clic pour sélectionner
        self.bind("<Button-3>", self.supprimer_element)  # Clic droit pour supprimer un élément

    def ajouter_element(self, event):
        """Ajoute un élément au clic gauche, sauf si un élément est déjà sélectionné"""
        # Si un élément est sélectionné, on annule la sélection et ne crée pas un nouvel élément
        if self.selection is not None:
            self.selection = None
            self.supprimer_rectangle_selection()
            return

        element = Element(self.canvas, event.x, event.y, self)
        self.elements.append(element)
        print(f"Élément ajouté en ({event.x}, {event.y})")

    def selectionner_element(self, event):
        """Sélectionne un élément avec un double-clic"""
        for elem in self.elements:
            if elem.est_dans_element(event.x, event.y):
                self.selectionner(elem)
                return
        print("Aucun élément sélectionné")

    def selectionner(self, element):
        """Sélectionne un élément"""
        self.selection = element
        print(f"Élément sélectionné à ({element.x}, {element.y})")
        
        # Créer un rectangle de sélection autour de l'élément
        self.supprimer_rectangle_selection()
        self.selection_rectangle = self.canvas.create_rectangle(
            element.x - 60, element.y - 25, element.x + 60, element.y + 25, 
            outline="red", width=3
        )

    def supprimer_rectangle_selection(self):
        """Supprimer le rectangle de sélection s'il existe"""
        if self.selection_rectangle is not None:
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None

    def supprimer_element(self, event):
        """Supprime l'élément au clic droit"""
        if self.selection is not None and self.selection.est_dans_element(event.x, event.y):
            self.canvas.delete(self.selection.window)
            self.elements.remove(self.selection)
            print(f"Élément supprimé à ({self.selection.x}, {self.selection.y})")
            self.selection = None  # Annuler la sélection après suppression
            self.supprimer_rectangle_selection()
        else:
            print("Aucun élément à supprimer à cet endroit")

class Element:
    def __init__(self, canvas, x, y, app):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.app = app

        self.frame = ctk.CTkFrame(self.app, width=120, height=50, corner_radius=8)
        self.label = ctk.CTkLabel(self.frame, text="Élément")
        self.label.pack(expand=True)

        self.window = self.canvas.create_window(x, y, window=self.frame)

        self.frame.bind("<B1-Motion>", self.deplacer)  # Déplacer avec clic gauche

    def deplacer(self, event):
        """Déplace l'élément"""
        self.x = event.x_root - self.app.winfo_rootx()
        self.y = event.y_root - self.app.winfo_rooty()
        self.canvas.coords(self.window, self.x, self.y)
        print(f"Élément déplacé à ({self.x}, {self.y})")

    def est_dans_element(self, x, y):
        """Vérifie si le clic est dans cet élément"""
        return (self.x - 60 <= x <= self.x + 60) and (self.y - 25 <= y <= self.y + 25)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
