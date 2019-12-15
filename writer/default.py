from abc import ABC, abstractmethod


class AMetaWriter(ABC):
    """
    Abstract class for implementing specific meta writers
    Each meta writer could expand che's abilities to write multiple meta file formats
    """
    def __init__(self):
        pass

    @abstractmethod
    def write(self, file):
        pass


class APageWriter(ABC):
    """
    Abstract class for implementing specific page writers
    Each page writer could expand che's abilities to write multiple page file formats
    """
    def __init__(self):
        pass

    @abstractmethod
    def write(self, file):
        pass
