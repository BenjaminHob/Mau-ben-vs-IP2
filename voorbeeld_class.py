class voertuig:
    snelheid: float = 0.0
    acceleratie: float = 0.0
    aantal_wielen: int = 0
    massa: float = 0.0
    wielen: list

    def __init__(self, merk, model, bouwjaar=None):
        self.merk = merk
        self.model = model
        self.wielen = []
        if not bouwjaar:
            print("Bouwjaar niet opgegeven, standaardwaarde 'Onbekend' wordt gebruikt.")
            self.bouwjaar = "Onbekend"
        else:
            self.bouwjaar = bouwjaar

    @property
    def merk(self):
        return self._merk

    @merk.setter
    def merk(self, value):
        if value == "Tesla":
            print("Waarschuwing: Tesla is een slecht merk!")
        self._merk = value

    def start(self):
        print(f"{self.merk} {self.model} is gestart.")

    def stop(self):
        print(f"{self.merk} {self.model} is gestopt.")

    def versnellen(self, versnelling):
        self.acceleratie = versnelling
        self.snelheid += self.acceleratie
        print(
            f"{self.merk} {self.model} versnelt met {self.acceleratie} m/s². Nieuwe snelheid: {self.snelheid} m/s."
        )

    def __str__(self):
        return f"{self.merk} {self.model} ({self.bouwjaar})"


class fiets(voertuig):
    def __init__(self, merk, model, bouwjaar, versnellingen):
        super().__init__(merk, model, bouwjaar)
        self.versnellingen = versnellingen
        self.wielen = []
        for i in range(2):  # Assuming a bicycle has 2 wheels
            self.wielen.append(wiel(28, "racefiets"))

    def start(self):
        print(f"{self.merk} {self.model} (fiets) is gestart.")

    def stop(self):
        print(f"{self.merk} {self.model} (fiets) is gestopt.")

    def __str__(self):
        return f"{self.merk} {self.model} ({self.bouwjaar}), {self.versnellingen} versnellingen"


class auto(voertuig):
    def __init__(self, merk, model, bouwjaar, brandstof):
        super().__init__(merk, model, bouwjaar)
        self.brandstof = brandstof
        self.wielen = []
        for i in range(4):  # Assuming a car has 4 wheels
            self.wielen.append(wiel(24, "passenger"))

    def start(self):
        print(f"{self.merk} {self.model} (auto) is gestart.")

    def stop(self):
        print(f"{self.merk} {self.model} (auto) is gestopt.")

    def __str__(self):
        return (
            f"{self.merk} {self.model} ({self.bouwjaar}), brandstof: {self.brandstof}"
        )


class wiel:
    def __init__(self, diameter, type):
        self.diameter = diameter
        self.type = type

    # def __str__(self):
    #     return f"Wiel: {self.diameter} inch, type: {self.type}"


class leeg:
    def __init__(self):
        pass


if __name__ == "__main__":
    mijn_voertuig = voertuig("Toyota", "Corolla")
    # mijn_voertuig_2 = voertuig("Ford", "Focus", 2019)
    mijn_fiets = fiets("Gazelle", "Orange", 2021, 7)
    print(mijn_fiets)
    mijn_auto = auto("Volvo", "XC40", 2024, "elektrisch")
    print(mijn_auto)
    # mijn_voertuig.start()
    # mijn_voertuig.stop()
    wiel1 = wiel(28, "racefiets")

    mijn_leeg = leeg()

    print(mijn_fiets.acceleratie)
    mijn_fiets.kapot = 10.0
