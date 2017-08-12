class input:
    def __init__(self):
        self.OUT_PORT2 = 0
        self.OUT_PORT3 = 0
        self.OUT_PORT4LO = 0
        self.OUT_PORT4HI = 0
        self.OUT_PORT5 = 0
        self.IN_PORT1 = 0
        self.IN_PORT2 = 0

    def OutPutPort(self, port, value):  # TODO IO
        if port == 2:
            self.OUT_PORT2 = value
        elif port == 3:
            self.OUT_PORT3 = value
        elif port == 4:
            self.OUT_PORT4LO = self.OUT_PORT4HI
            self.OUT_PORT4HI = value
        elif port == 5:
            self.OUT_PORT5 = value

    def InPutPort(self, port):  # TODO IO
        result = 0
        if port == 1:
            result = self.IN_PORT1
        elif port == 2:
            result = self.IN_PORT2
        elif port == 3:
            result = (((self.OUT_PORT4HI << 8) | self.OUT_PORT4LO) << self.OUT_PORT2) >> 8
        return result
