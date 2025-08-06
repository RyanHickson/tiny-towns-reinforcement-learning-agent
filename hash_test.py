class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __hash__(self):
        return hash((self.first_name, self.last_name))
    

john = Person("John", "Doe")
hash_value = hash(john)
test_dict = {}
test_dict[hash_value] = john

hash_found = False

if hash(john) in test_dict:
    hash_found = True

print(hash_found)
print(f"The hash value of {john} is {hash_value}")



{'board': "[['empty' 'empty' 'empty' 'Cottage']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']]", 'parents': ["[['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']]", "[['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']\n ['empty' 'empty' 'empty' 'empty']]"], 'visits': 6, 'reward_sum': 0.12000000000000001, 'average_reward': 0.02, 'turn': 1, 'terminal': False}