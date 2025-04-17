#LES ELEMENTS AUTOMATIQUEMENT RELIES

import customtkinter as ctk
import tkinter as tk
import json

class MindMap(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mind Map")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.nodes = []  # Список усіх вузлів
        self.connections = []  # Список усіх з'єднань

        # Меню для збереження та завантаження
        self.menu = ctk.CTkFrame(self)
        self.menu.pack(fill="x")

        self.save_button = ctk.CTkButton(self.menu, text="Зберегти", command=self.save_to_json)
        self.save_button.pack(side="left", padx=10, pady=5)

        self.load_button = ctk.CTkButton(self.menu, text="Завантажити", command=self.load_from_json)
        self.load_button.pack(side="left", padx=10, pady=5)

        self.bind("<Button-1>", self.create_node)  # Клік мишею створює вузол

    def create_node(self, event):
        """Створює новий вузол у місці кліку"""
        node = Node(self.canvas, event.x, event.y, self)
        self.nodes.append(node)

        if len(self.nodes) > 1:
            self.connect_nodes(self.nodes[-2], node)

    def connect_nodes(self, node1, node2):
        """Створює лінію між двома вузлами"""
        line = self.canvas.create_line(
            node1.x, node1.y, node2.x, node2.y, width=2, fill="black"
        )
        self.connections.append((node1, node2, line))
        node1.add_connection(node2)
        node2.add_connection(node1)

    def save_to_json(self):
        """Зберігає Mind Map у JSON-файл"""
        data = {
            "nodes": [{"x": node.x, "y": node.y, "text": node.label.cget("text")} for node in self.nodes],
            "connections": [(self.nodes.index(n1), self.nodes.index(n2)) for n1, n2, _ in self.connections]
        }
        with open("mind_map.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("✅ Mind Map збережено!")

    def load_from_json(self):
        """Завантажує Mind Map з JSON-файлу"""
        try:
            with open("mind_map.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.canvas.delete("all")  # Очищаємо все
            self.nodes.clear()
            self.connections.clear()

            # Відновлення вузлів
            for node_data in data["nodes"]:
                node = Node(self.canvas, node_data["x"], node_data["y"], self, node_data["text"])
                self.nodes.append(node)

            # Відновлення з'єднань
            for n1_idx, n2_idx in data["connections"]:
                self.connect_nodes(self.nodes[n1_idx], self.nodes[n2_idx])

            print("✅ Mind Map завантажено!")

        except FileNotFoundError:
            print("⚠ Файл не знайдено!")
        except json.JSONDecodeError:
            print("⚠ Помилка при зчитуванні JSON!")

class Node:
    def __init__(self, canvas, x, y, mind_map, text="Вузол"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.mind_map = mind_map
        self.connections = []

        self.frame = ctk.CTkFrame(self.mind_map, width=100, height=50, corner_radius=8)
        self.label = ctk.CTkLabel(self.frame, text=text)
        self.label.pack(expand=True)

        self.window = self.canvas.create_window(x, y, window=self.frame)

        self.frame.bind("<B1-Motion>", self.drag)  # Переміщення вузла

    def drag(self, event):
        """Переміщує вузол та оновлює з'єднання"""
        self.x = event.x_root - self.mind_map.winfo_rootx()
        self.y = event.y_root - self.mind_map.winfo_rooty()
        self.canvas.coords(self.window, self.x, self.y)

        # Оновлення ліній
        for node in self.connections:
            index = self.mind_map.nodes.index(node)
            self.canvas.coords(
                self.mind_map.connections[index][2],
                self.x, self.y, node.x, node.y
            )

    def add_connection(self, node):
        """Додає зв'язок між вузлами"""
        if node not in self.connections:
            self.connections.append(node)

if __name__ == "__main__":
    app = MindMap()
    app.mainloop()
