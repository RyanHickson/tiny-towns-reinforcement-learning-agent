from gymnasium.spaces import MultiDiscrete

class Agent:
    def __init__(self, name):
        self.name = name
        self.action_space = MultiDiscrete([
        5,  # RESOURCE INDEX
        16, # TILE ID INDEX
        2,  # NO/ YES
        8,  # BUILDING TYPE
        7,  # BUILDING TYPE WITHOUT MONUMENT
        ])
    
    def __str__(self):
        return "{}".format(self.name)

    # def dynamic_to_fixed_action_state(self):

    
    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE