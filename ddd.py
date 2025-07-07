from mesa import Agent, Model
from mesa.time import RandomActivation

class MyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def step(self):
        # Define agent behavior here
        pass

class MyModel(Model):
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        for i in range(self.num_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)
    
    def step(self):
        self.schedule.step()

if __name__ == "__main__":
    model = MyModel(N=10)
    for t in range(5):
        model.step()
