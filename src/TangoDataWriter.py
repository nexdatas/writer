class TangoDataWriter:
    def __init__(self,name):
        self.name=name
        self.xml=""
        self.json=""

    def open(self):
        pass

    def setXML(self,xml):
        self.xml=xml

    def getXML(self):
        return self.xml

    def record(self):
        pass


    def close(self):
        pass



if __name__ == "__main__":


    # Create a TDW object
    tdw = TangoDataWriter("TDW")
    
