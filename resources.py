# RESOURCES

class Resource:
    """
    A class to define the resources used in the game to construct buildings within the town boards
    """
    def __init__(self, name):
        self.name = name
        
    def get_name(self):
        return self.name

wood = Resource("wood")
wheat = Resource("wheat")
glass = Resource("glass")
brick = Resource("brick")
stone = Resource("stone")

emptyTile = Resource("     ")
wild = Resource("wild")


resource_types = [wood, wheat, glass, brick, stone]
#                 1      2      3      4      5