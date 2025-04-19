from EcoVariable import EcoVariable

# Hello Manar! put your analysis in this class please

class WaterQuality(EcoVariable):
    
    def __init__(self,name,location,startTime,endTime):
        self.name = name
        self.location = location
        self.startTime = startTime
        self.endTime= endTime

    # Yet to be implemented..
    # These are overided methods from the factory abstract class EcoVariable
    def retrieveData():
        pass

    def generateMap():
        pass

    def generateChart():
        pass

    def generateAiAnalysis():
        pass