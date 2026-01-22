import tkinter as tk

class AgileDateSim:
    def __init__(self, root):
        self.root = root
        root.title("💘 Agile Date Simulator 💘")
        root.geometry("700x400")
        root.resizable(False, False)

        self.affection = 0
        self.cringe = 0
        self.step = 0

        self.story = [
            {
                "text": (
                    "🍷 Tu es à un date.\n"
                    "Alex (Agile Coach certifié) te regarde intensément.\n\n"
                    "Alex : « Alors… tu te situes où sur le framework émotionnel ? »"
                ),
                "choices": [
                    ("Parler de mes feelings", 2, 0),
                    ("Demander ce qu'est un framework émotionnel", 0, 1),
                    ("Changer de sujet (le pain)", 0, 2)
                ]
            },
            {
                "text": (
                    "Alex sourit.\n\n"
                    "Alex : « J'adore l'alignement émotionnel. "
                    "Tu fais des rétros personnelles ? »"
                ),
                "choices": [
                    ("Oui, chaque dimanche", 2, 0),
                    ("Seulement après un burn-out", 1, 1),
                    ("C'est quoi une rétro ?", 0, 2)
                ]
            },
            {
                "text": (
                    "Le serveur arrive.\n"
                    "Alex : « Ce vin manque de valeur business. »"
                ),
                "choices": [
                    ("Proposer une amélioration continue", 2, 0),
                    ("Boire en silence", 0, 1),
                    ("Dire 'OK boomer'", 0, 3)
                ]
            }
        ]

        self.main = tk.Frame(root, bg="#1e1e1e")
        self.main.pack(expand=True, fill="both")

        self.label = tk.Label(
            self.main,
            text="",
            fg="white",
            bg="#1e1e1e",
            font=("Arial", 12),
            wraplength=650,
            justify="left"
        )
        self.label.pack(pady=20)

        self.buttons = tk.Frame(self.main, bg="#1e1e1e")
        self.buttons.pack()

        self.stats = tk.Label(
            self.main,
            text=self.get_stats(),
            fg="gray",
            bg="#1e1e1e"
        )
        self.stats.pack(pady=10)

        self.show_step()

    def get_stats(self):
        return f"❤️ Affection : {self.affection} | 🤡 Cringe : {self.cringe}"

    def show_step(self):
        self.clear_buttons()

        if self.step < len(self.story):
            data = self.story[self.step]
            self.label.config(text=data["text"])

            for text, a, c in data["choices"]:
                tk.Button(
                    self.buttons,
                    text=text,
                    width=50,
                    command=lambda a=a, c=c: self.choose(a, c)
                ).pack(pady=3)
        else:
            self.ending()

        self.stats.config(text=self.get_stats())

    def choose(self, affection, cringe):
        self.affection += affection
        self.cringe += cringe
        self.step += 1
        self.show_step()

    def clear_buttons(self):
        for w in self.buttons.winfo_children():
            w.destroy()

    def ending(self):
        if self.affection >= 5 and self.cringe < 4:
            ending = (
                "💍 FIN : SCALE L'AGILE À LA RELATION\n\n"
                "Alex : « On est alignés. Je propose un sprint 2 ce week-end. »"
            )
        elif self.cringe >= 5:
            ending = (
                "👻 FIN : GHOSTÉ·E APRÈS LA RÉTRO\n\n"
                "Alex : « Je pense qu'on n'a pas assez de valeur partagée. »"
            )
        else:
            ending = (
                "🤝 FIN : AMIS LINKEDIN\n\n"
                "Alex : « Restons connectés et itérons plus tard. »"
            )

        self.label.config(text=ending)

if __name__ == "__main__":
    root = tk.Tk()
    AgileDateSim(root)
    root.mainloop()
