from abc import ABC, abstractmethod

class BaseGame(ABC):

    @abstractmethod
    def start(self, round_end_callback, wrong_answer_callback):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def submit(self, data):
        pass
