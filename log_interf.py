from abc import ABC, abstractmethod


class LoggerInterface(ABC):
    @abstractmethod
    def print(self, txt: str):
        pass
