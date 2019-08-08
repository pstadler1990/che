from abc import ABC, abstractmethod


class AMetaLoader(ABC):
    """
    Abstract class for implementing specific meta loaders
    Each meta loader could expand che's abilities to load multiple meta file formats
    """
    def __init__(self):
        pass

    @abstractmethod
    def read(self, file):
        pass
