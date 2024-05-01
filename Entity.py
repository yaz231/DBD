from abc import ABC, abstractmethod
class Entity(ABC):
    def __init__(self, position):
        self.position = position
        self.reward = 0

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def update(self):
        pass