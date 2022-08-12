class tempsensor:
    sensordir = "/sys/devices/w1_bus_master1/"

    def __init__(self, name):
        self.name = name
        self.path = tempsensor.sensordir+name+"/w1_slave"
        self.temperature = None
    
    def getTemp(self):
        try:
            raw = open(self.path, 'r').read()
            temp = float(raw.split("t=")[-1]) / 1000
            if temp>1:
                if self.temperature == None:
                    if temp == 85.0:
                        raise ValueError
                    print("Sensor " + self.name + " is now readable")
                self.temperature = temp
            else:
                raise ValueError
        except (FileNotFoundError, ValueError):
            if not self.temperature == None:
                print("Sensor " + self.name + " is not readable, skipping")
            self.temperature=None
        return self.temperature
