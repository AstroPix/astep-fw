class ComsInterpreter:
    """
    Member dict: (static const) Contains all commands with the corresponding codes
    Member args: (static const) Contains the number of arguments for all cmds
    Member cargs:(static const, automatically generated) number of arguments for all codes
    Member prog: Byte array, contains current compiled program
    Method setStr: Compiles str into a byte array
    Method getStr: Decompiles byte array into a str
    Method setBytes: set member prog
    Method getBytes: returns current program
    """
    def __init__(self):
        self.dict = {"NOP":0xc5, "DRO":0xca, "HKD":0xcc, 
                     "LRC":0xd1, "LOC":0xd4, 
                     "PIX":0xd7, "STH":0xdd, 
                     "SIP":0xe2, "SIV":0xe4, "INJ":0xe7, "JNI":0xe8}
        self.args = {"NOP":0, "DRO":1, "HKD":1, 
                     "LRC":2, "LOC":2, 
                     "PIX":5, "STH":3, 
                     "SIP":5, "SIV":3, "INJ":0, "JNI":0}
        self.cargs={}
        for k, v in self.dict.items():
            self.cargs[v] = self.args[k]
        self.prog = bytes([])

    def checkCodes(self):
        ok = self.dict.keys()==self.args.keys()# Same keys in both 
        ok &= len(self.dict)==len(set(self.dict.values()))# No two commands have the same code
        return ok
    def printCodes(self):
        print(self.dict.keys())

    def setStr(self, s):
        if not self.checkCodes():
            raise ValueError("Dictionaries for compilation are invalid.")
        prog = []
        i = 0
        data = s.split(" ")
        while i < len(data):
            c = data[i]
            if c in self.dict:
                if len(data) <= i + self.args[c]:
                    raise ValueError("Not enough arguments after {}: Needed {}".format(\
                                      c, self.args[c]))
                for j in range(i+1, i+1+self.args[c]):
                    if data[j] in self.dict:
                        raise ValueError("{} is a command, but {} needs {} arguments".format(\
                                          data[j], c, self.args[c]))
                    if not data[j].isdigit():
                        raise ValueError("{} is not a positive int.".format(data[j]))
                prog.append(self.dict[c])
                for j in range(i+1, i+1+self.args[c]):
                    prog.append(int(data[j]))
                i += self.args[c]+1
            else:
                raise ValueError("{} is not a command, but a command was expected".format(c))
        self.prog = bytes(prog)

    def getStr(self):
        clist = []
        for b in self.prog:
            if b in self.dict.values():
              for it in self.dict.items():
                  if b == it[1]:
                      clist.append(it[0])
            else: clist.append(str(int(b)))
        return " ".join(clist)

    def setBytes(self, b):
        self.prog = b

    def getBytes(self):
        return self.prog


if __name__ == "__main__":
    I = ComsInterpreter()
    while True:
        cmdstr = input("> ")
        I.setStr(cmdstr)
        with open("upcmds.bin", "wb") as f:
            f.write(I.getBytes())
            f.flush()

