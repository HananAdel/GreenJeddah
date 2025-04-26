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

       #to generate the analysis you need to pass to this method self.gemini.generate(description,self.startTime, self.endTime)
        
       # description = the real valuse of your index  for example f"{self.name} mean: {self.lst_mean:.2f}, std dev: {std_val:.2f}"

        #check what I did in UHI and AirQuality classes to undrstand what I mean