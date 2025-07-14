class Agent:
    def __init__(self, name, actions, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.99):
        self.name = name
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
    
    def __str__(self):
        return "{}".format(self.name)
    
    def get_state(self, player, game):
        pass
        # STATE LOGIC
    
    def choose_action(self, state):
        pass
        # GREEDY CHOICES

    # REMEMBER TO ACTUALLY WRITE SOME AGENT LOGIC IN HERE