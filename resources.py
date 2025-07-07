# RESOURCES


class Resource:
    """
    A class to define the resources used in the game to construct buildings within the town boards
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


wood = Resource("wood")
wheat = Resource("wheat")
glass = Resource("glass")
brick = Resource("brick")
stone = Resource("stone")

empty = Resource("empty")
wild = Resource("wild")
