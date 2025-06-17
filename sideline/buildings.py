class Building:
    """
    A class to define buildings, including monuments
    """

    def __init__(self, name, layout, type, ability, isCottageLike=False):
        self.name = name
        self.layout = layout
        self.type = type
        self.ability = ability
        self.isCottageLike = isCottageLike