from abc import ABC, abstractmethod
from GeminiAnalysis import GeminiAnalysis  # Add this line!

# Global Gemini Client
GEMINI_API_KEY = "AIzaSyCRyZU8gZKTGK9x3cLtjPfWQ975LhH0L5c"  # Only here!
gemini_client = GeminiAnalysis(api_key=GEMINI_API_KEY)  # Only once!

# This is the factory interface/abstract
class EcoVariable(ABC):
    # Intializing the eco variable object
    def __init__(self,name,location,startTime,endTime):
        self.name = name
        self.location = location
        self.startTime = startTime
        self.endTime= endTime
        self.gemini = gemini_client 


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

