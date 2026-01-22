import tkinter as tk
import random

class AgileDateInsanity:
    def __init__(self, root):
        self.root = root
        root.title("💘 AGILE DATE SIMULATOR – SAFe EDITION™ 💘")
        root.geometry("800x500")
        root.resizable(False, False)

        self.affection = 0
        self.cringe = 0
        self.buzzwords = 0
        self.sanity = 100
        self.step = 0

        self.events = [
            {
                "text": (
                    "🍷 Premier date.\n"
                    "Alex arrive avec un tote bag 'Scrum is life'.\n\n"
                    "Alex : « Avant de commander, faisons un icebreaker. "
                    "Quel est ton animal totem agile ? »"
                ),
                "choices": [
                    ("Le loup collaboratif", 2, 0, 2, 0),
                    ("Le backlog non priorisé", 1, 1, 1, -5),
                    ("Partir aux toilettes et ne jamais revenir", 0, 3, 0, -20)
                ]
            },
            {
                "text": (
                    "Alex hoche la tête avec gravité.\n\n"
                    "Alex : « Intéressant. Et sur une échelle de SAFe à SAFe, "
                    "comment tu gères le conflit émotionnel ? »"
                ),
                "choices": [
                    ("Par une rétro sincère", 2, 0, 2, 0),
                    ("Je refactor mes sentiments", 1, 1, 2, -5),
                    ("Je ressens des émotions normales", 0, 3, 0, -10)
                ]
            },
            {
                "text": (
                    "📊 Alex sort un tableau.\n"
                    "Alex : « J'ai modélisé notre compatibilité en PI Planning. »"
                ),
                "choices": [
                    ("Demander la vélocité du couple", 2, 0, 2, 0),
                    ("Demander si l'amour est un KPI", 1, 1, 2, -5),
                    ("Renverser le tableau", 0, 4, 0, -15)
                ]
            },
            {
                "text": (
                    "🚨 ÉVÉNEMENT ALÉATOIRE 🚨\n"
                    "Un Scrum Master apparaît et commence une rétro impromptue."
                ),
                "choices": [
                    ("Participer activement", 2, 0, 1, -5),
                    ("Dire 'let's take this offline'", 1, 1, 2, 0),
                    ("Crier 'STOP AU CULTE'", 0, 4, 0, -20)
                ]
            }
        ]

        self.main = tk.Frame(root, bg="#111")
        self.main.pack(expand=True, fill="both")

        self.text = tk.Label(
            self.main,
            fg="white",
            bg="#111",
            font=("Arial", 13),
            wraplength=760,
            justify="left"
        )
        self.text.pack(pady=20)

        self.buttons = tk.Frame(self.main, bg="#111")
        self.buttons.pack()

        self.stats = tk.Label(
            self.main,
            fg="gray",
            bg="#111",
            font=("Arial", 10)
        )
        self.stats.pack(pady=10)

        self.show_event()

    def show_event(self):
        self.clear_buttons()

        if self.step < len(self.events):
            event = self.events[self.step]
            self.text.config(text=event["text"])

            for label, a, c, b, s in event["choices"]:
                tk.Button(
                    self.buttons,
                    text=label,
                    width=60,
                    command=lambda a=a, c=c, b=b, s=s: self.choose(a, c, b, s)
                ).pack(pady=4)
        else:
            self.boss_fight()

        self.update_stats()

    def choose(self, affection, cringe, buzz, sanity):
        self.affection += affection
        self.cringe += cringe
        self.buzzwords += buzz
        self.sanity += sanity
        self.step += 1
        self.show_event()

    def update_stats(self):
        self.stats.config(
            text=(
                f"❤️ Affection: {self.affection} | "
                f"🤡 Cringe: {self.cringe} | "
                f"📊 Buzzwords: {self.buzzwords} | "
                f"🧠 Santé mentale: {self.sanity}"
            )
        )

    def clear_buttons(self):
        for w in self.buttons.winfo_children():
            w.destroy()

    def boss_fight(self):
        self.clear_buttons()
        self.text.config(
            text=(
                "👹 BOSS FINAL : PI PLANNING DU COUPLE 👹\n\n"
                "Alex : « Engageons-nous sur 6 mois avec des objectifs mesurables. »"
            )
        )

        tk.Button(
            self.buttons,
            text="💍 Accepter et scaler l'amour",
            width=60,
            command=self.good_ending
        ).pack(pady=5)

        tk.Button(
            self.buttons,
            text="💀 Dire 'je préfère ressentir des choses'",
            width=60,
            command=self.bad_ending
        ).pack(pady=5)

    def good_ending(self):
        if self.affection >= 6 and self.buzzwords >= 6 and self.sanity > 0:
            ending = (
                "💍 FIN ULTIME : AMOUR AGILE À L'ÉCHELLE\n\n"
                "Vous êtes désormais un couple certifié SAFe.\n"
                "Votre relation a une roadmap et zéro émotion imprévue."
            )
        else:
            ending = (
                "🤝 FIN MITIGÉE : PARTENAIRES DE PI\n\n"
                "Vous vous voyez uniquement en comité de pilotage."
            )
        self.text.config(text=ending)
        self.clear_buttons()

    def bad_ending(self):
        ending = (
            "🔥 FIN APOCALYPSE 🔥\n\n"
            "Alex : « Ton mindset n'est pas mature. »\n"
            "Tu repars libre, vivant, et toujours humain."
        )
        self.text.config(text=ending)
        self.clear_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    AgileDateInsanity(root)
    root.mainloop()
