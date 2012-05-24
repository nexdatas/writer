class TangoDataWriter:
    def __init__(self,name):
        self.name=name
        self.xml=""
        self.json=""

    def open(self):
        print 'open'

    def setXML(self,xml):
        self.xml=xml
        print 'setXML'

    def getXML(self):
        print 'getXML'
        return self.xml

    def setJSON(self,json):
        self.json=json
        print 'setXML'

    def getJSON(self):
        print 'getXML'
        return self.json

    def record(self):
        print 'record'


    def close(self):
        print 'close'



if __name__ == "__main__":


    # Create a TDW object
    tdw = TangoDataWriter("TDW")
    
