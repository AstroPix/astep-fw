
def isbyte(s):
    """
    Check if str s can be converted into a byte (int between 0-255)
    Supports decimal, hex and binary
    """
    return (s.isdigit() and int(s)>=0 and int(s)<=255) \
        or (s.startswith("0x") and int(s, 16)>=0 and int(s, 16)<=255) \
        or (s.startswith("0b") and int(s, 2)>=0 and int(s, 2)<=255)

def tonum(s):
    if not isbyte(s):
        raise ValueError("{} is not a positive int.".format(data[j]))
    if s.isdigit(): return int(s)
    elif s.startswith("0x"): return int(s, 16)
    elif s.startswith("0b"): return int(s, 2)
    else: raise ValueError("{} is not a positive int.".format(data[j]))

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
        self.dict = {"nop":0xc5, "rod":0xca, "hkd":0xcc, "shv":0xcf, "saf":0xd1, 
                     "lrc":0xd7, "lfc":0xd8, "loc":0xdb, 
                     "pix":0xdd, "row":0xde, "col":0xe1, "sth":0xe2, 
                     "icm":0xe8, 
                     "sip":0xf3, "siv":0xf5, "inj":0xf6, "jni":0xf9}
        self.args = {"nop":0, "rod":1, "hkd":1, "shv":1, "saf":1, 
                     "lrc":1, "lfc":1, "loc":1, 
                     "pix":4, "row":3, "col":3, "sth":2, 
                     "icm":2, 
                     "sip":4, "siv":2, "inj":0, "jni":0}
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
                    raise ValueError("Not enough arguments after {}: Needed {} but got {}".format(\
                                      c, self.args[c], len(data)))
                for j in range(i+1, i+1+self.args[c]):
                    if data[j] in self.dict:
                        raise ValueError("{} is a command, but {} needs {} arguments".format(\
                                          data[j], c, self.args[c]))
                    if not isbyte(data[j]):
                        raise ValueError("{} is not a positive int.".format(data[j]))
                prog.append(self.dict[c])
                for j in range(i+1, i+1+self.args[c]):
                    prog.append( tonum(data[j]) )
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

