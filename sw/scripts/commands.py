import logging

#from drivers.boards.board_driver import BoardDriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def getNumber(s):
    return True, int(s)


class CmdsInterpreter:
    """
    Member args: (static const) Contains the number of arguments for all cmds
    Member limits: (static const) dict of list of couples (min, max) for allowed values in cmd arguments
    """
    def __init__(self):
        self.args = {"nop":0,
                     "loc":2,
                     "pix":5, "row":4, "col":4, "sth":3,
                     "ccm":3}
        self.limits = {"nop":[],
                     "loc":[(0, 2), (0, 3)],
                     "pix":[(0,2), (0,3), (0, 34), (0,34)], "row":[(0,2), (0,3), (0, 34)], "col":[(0,2), (0,3), (0, 34)], "sth":[(0,2), (0,3), (0, 1800)],
                     "ccm":[(0, 2), (0, 3)]}

    def checkArg(self, cmd, arg, i):
        """
        Checks if an argument is within bounds
        :param arg: number
        :param i: argument number
        :returns: bool
        """
        if i >= len(self.limits[cmd]): return True
        mini, maxi = self.limits[cmd][i]
        return arg >= mini and arg <= maxi

    def checkStr(self, s):
        """
        Compiles str into a program
        :param s: str, list of commands
        :returns: list of str and int, a valid sequence of instructions to update AstroPix configuration
        """
        prog = []
        i = 0
        s.replace(" "," ") # Replace non-breaking space with normal space
        s.replace("\t"," ") # Replace tabs with normal space
        s.replace("\n"," ") # Replace newlines with normal space
        data = s.split(" ")
        data = [e for e in data if e != ""] # Remove empty strings
        logger.info(f"Obtained {len(data)} non-empty tokens.")
        while i < len(data):
            token = data[i]
            if token in self.args:
                if len(data) <= i + self.args[token]:
                    logger.error(f"Not enough tokens after {token}: Needed {self.args[token]} but got {len(data)-i-1}")
                    i += 1; continue
                cmd = [token]; cmdok = True
                for j in range(i+1, i+1+self.args[token]):
                    if data[j] in self.args:
                        logger.error(f"{data[j]} is a command, but {token} needs {self.args[token]} arguments")
                        cmdok = False; i=j; break
                    status, number = getNumber(data[j])
                    if not status:
                        logger.error(f"{data[j]} could not be converted to a number")
                        cmdok = False; i = j+1; break
                    if not self.checkArg(token, number, j-i-1):
                        logger.error(f"{number} is out of bounds {self.limits[token][j-i-1]} (cmd={token})")
                        cmdok = False; i = j+1; break
                    cmd.append(number)
                if cmdok:
                    logger.info(f"Accepted command {cmd}")
                    prog.append(cmd)
                    i += self.args[token]+1
            else:
                logger.error(f"{token} is not a command, but a command was expected")
                i += 1
        logger.info(f"Decoded {len(prog)} valid commands.")
        return prog

    def execute(self, prog, boardDriver):
        for cmd in prog:
            if cmd[0] == "nop":
                logger.info("Found nop")
            elif cmd[0] == "loc" and len(cmd) == self.args[cmd[0]]+1:
                boardDriver.getAsic(cmd[1]).reset_recconfig(cmd[2])
                logger.info(f"Layer {cmd[1]} chip {cmd[2]} OFF")
            elif cmd[0] == "pix" and len(cmd) == self.args[cmd[0]]+1:
                if cmd[5]:
                    boardDriver.getAsic(cmd[1]).enable_pixel(chip=cmd[2], row=cmd[3], col=cmd[4])
                    logger.info(f"Pixel of layer {cmd[1]} chip {cmd[2]} row {cmd[3]} col {cmd[4]} Acivated")
                else:
                    boardDriver.getAsic(cmd[1]).disable_pixel(chip=cmd[2], row=cmd[3], col=cmd[4])
                    logger.info(f"Pixel of layer {cmd[1]} chip {cmd[2]} row {cmd[3]} col {cmd[4]} Deactivated")
            elif cmd[0] == "row" and len(cmd) == self.args[cmd[0]]+1:
                if cmd[4]:
                    for i in range(boardDriver.getAsic(cmd[1])._num_cols):
                        boardDriver.getAsic(cmd[1]).enable_pixel(chip=cmd[2], row=cmd[3], col=i)
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} row {cmd[3]} Activated")
                else:
                    for i in range(boardDriver.getAsic(cmd[1])._num_cols):
                        boardDriver.getAsic(cmd[1]).disable_pixel(chip=cmd[2], row=cmd[3], col=i)
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} row {cmd[3]} Deactivated")
            elif cmd[0] == "col" and len(cmd) == self.args[cmd[0]]+1:
                if cmd[4]:
                    for i in range(boardDriver.getAsic(cmd[1])._num_cols):
                        boardDriver.getAsic(cmd[1]).enable_pixel(chip=cmd[2], col=cmd[3], row=i)
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} col {cmd[3]} Activated")
                else:
                    for i in range(boardDriver.getAsic(cmd[1])._num_cols):
                        boardDriver.getAsic(cmd[1]).disable_pixel(chip=cmd[2], col=cmd[3], row=i)
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} col {cmd[3]} Deactivated")
            elif cmd[0] == "sth" and len(cmd) == self.args[cmd[0]]+1:
                dacBL = boardDriver.asics[cmd[1]].asic_config[f"config_{cmd[2]}"]["vdacs"]["blpix"][1]
                boardDriver.asics[cmd[1]].asic_config[f"config_{cmd[2]}"]["vdacs"]["thpix"][1] = dacBL + cmd[3]
                logger.info(f"Layer {cmd[1]} chip {cmd[2]}")
            elif cmd[0] == "ccm" and len(cmd) == self.args[cmd[0]]+1:
                checksum = boardDriver.getAsic(cmd[1]).computeChecksum(cmd[2])
                if checksum == cmd[3]:
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} checksum {checksum} Valid")
                else:
                    logger.info(f"Layer {cmd[1]} chip {cmd[2]} checksum {checksum} Invalid (expected {cmd[3]})")
            else:
                logger.error(f"Command not found: {cmd}")




if __name__ == "__main__":
    formatter = logging.Formatter("%(levelname)s:%(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh)
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")
    I = CmdsInterpreter()
    while True:
        cmdstr = input("> ")
        if cmdstr == "exit": break
        prog = I.checkStr(cmdstr)
        print(prog)

