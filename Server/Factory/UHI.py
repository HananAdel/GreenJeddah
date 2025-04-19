from EcoVariable import EcoVariable

# Hello Reema! put your analysis in this class please
# and integrate your ai analysis to each class :) and if you cant just tell us
class UHI(EcoVariable):
    
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