from abc import ABC, abstractmethod

class BaseGame(ABC):

    @abstractmethod
    async def start(self, round_end_callback, wrong_answer_callback):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def submit(self, data):
        pass
