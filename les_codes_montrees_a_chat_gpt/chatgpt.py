#CONTENU DE L'ELEMENT

import json
import customtkinter as ctk
import os


class Noeud:
    def __init__(self, id, titre, contenu, parent_id=None):
        self.id = id
        self.titre = titre
        self.contenu = contenu
        self.parent_id = parent_id

    def to_dict(self):
        return {"id": self.id, "titre": self.titre, "contenu": self.contenu, "parent_id": self.parent_id}
    
class MindMap:
    def __init__(self, fichier="mindmap.json"):
        self.noeuds = []
        self.fichier = fichier
        self.charger()

    def ajouter_noeud(self, titre, contenu, parent_id=None):
        id = len(self.noeuds) + 1
        noeud = Noeud(id, titre, contenu, parent_id)
        self.noeuds.append(noeud)

    def sauvegarder(self):
        with open(self.fichier, "w") as f:
            json.dump([noeud.to_dict() for noeud in self.noeuds], f, indent=4)

    def charger(self):
        if os.path.exists(self.fichier):
            with open(self.fichier, "r") as f:
                try:
                    data = json.load(f)
                    self.noeuds = [Noeud(**noeud) for noeud in data]
                except json.JSONDecodeError:
                    self.noeuds = []
        else:
            with open(self.fichier, "w") as f:
                json.dump([], f)

class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mind Map App")
        self.geometry("600x400")
        self.mindmap = MindMap()
        self.creer_widgets()

    def creer_widgets(self):
        self.label_titre = ctk.CTkLabel(self, text="Titre:")
        self.label_titre.pack()
        
        self.entree_titre = ctk.CTkEntry(self)
        self.entree_titre.pack()
        
        self.label_contenu = ctk.CTkLabel(self, text="Contenu:")
        self.label_contenu.pack()
        
        self.entree_contenu = ctk.CTkEntry(self)
        self.entree_contenu.pack()
        
        self.bouton_ajouter = ctk.CTkButton(self, text="Ajouter Noeud", command=self.ajouter_noeud)
        self.bouton_ajouter.pack()
        
        self.bouton_sauvegarder = ctk.CTkButton(self, text="Sauvegarder", command=self.sauvegarder)
        self.bouton_sauvegarder.pack()
        
        self.bouton_charger = ctk.CTkButton(self, text="Charger", command=self.charger)
        self.bouton_charger.pack()
        
        # Ajout d'un Textbox pour afficher les nœuds
        self.textbox_noeuds = ctk.CTkTextbox(self, wrap="word")
        self.textbox_noeuds.pack(fill="both", expand=True)
        
    def ajouter_noeud(self):
        titre = self.entree_titre.get()
        contenu = self.entree_contenu.get()
        self.mindmap.ajouter_noeud(titre, contenu)

    def sauvegarder(self):
        self.mindmap.sauvegarder()

    def charger(self):
        self.mindmap.charger()
        self.mettre_a_jour_interface()

    def mettre_a_jour_interface(self):
        # Met à jour le Textbox avec les nœuds chargés
        self.textbox_noeuds.delete(1.0, ctk.END)  # Efface les anciens éléments
        for noeud in self.mindmap.noeuds:
            self.textbox_noeuds.insert(ctk.END, f"{noeud.titre}: {noeud.contenu}\n\n")

if __name__ == "__main__":
    app = Interface()
    app.mainloop()
