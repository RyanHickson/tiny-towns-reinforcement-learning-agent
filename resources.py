# RESOURCES

class Resource:
    """
    A class to define the resources used in the game to construct buildings within the town boards
    """

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        return False

class EmptyResource(Resource):
    def __init__(self, name, id):
        super().__init__(name, id)
    
    def __str__(self):
        return self.name

wood = Resource("wood", 1)
wheat = Resource("wheat", 2)
glass = Resource("glass", 3)
brick = Resource("brick", 4)
stone = Resource("stone", 5)

empty = EmptyResource(name="empty", id=0)
wild = Resource("wild", 1000)

