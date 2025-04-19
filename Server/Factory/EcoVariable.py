from abc import ABC, abstractmethod
# This is the factory interface/abstract
class EcoVariable(ABC):
    # Intializing the eco variable object
    def __init__(self,name,location,startTime,endTime):
        self.name = name
        self.location = location
        self.startTime = startTime
        self.endTime= endTime


    # Hnn notes: here are the abstract functions to use in your analysis
    @abstractmethod
    def retrieveData():
        pass

    @abstractmethod
    def generateMap():
        pass

    @abstractmethod
    def generateChart():
        pass

    @abstractmethod
    def generateAiAnalysis():
        pass

