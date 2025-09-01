from abc import ABC, abstractmethod
from typing import Callable, Any

class MessageBroker(ABC):
    @abstractmethod
    async def connect(self): ...
    
    @abstractmethod
    async def publish(self, topic: str, message: dict): ...
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable[[dict], Any]): ...
    
    @abstractmethod
    async def close(self): ...
