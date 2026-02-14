class Opening:
    def __init__(self, opening: str) -> None:
        self.opening = opening

        self.days = [
            "Lundi",
            "Mardi",
            "Mercredi",
            "Jeudi",
            "Vendredi",
            "Samedi",
            "Dimanche",
        ]

    def get(self) -> dict:
        """
        Récupère les horaires d'ouverture.

        :return: Les horaires d'ouverture
        """
        data = []

        for i, day in enumerate(self.opening.split(",")):
            d = {"jour": self.days[i], "ouverture": {}}
            for h, opening in enumerate(day):
                if h == 0:
                    d["ouverture"]["matin"] = True if opening == "1" else False
                elif h == 1:
                    d["ouverture"]["midi"] = True if opening == "1" else False
                elif h == 2:
                    d["ouverture"]["soir"] = True if opening == "1" else False

            data.append(d)

        return data
