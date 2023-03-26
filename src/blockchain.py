MINING_DIFFICULTY = 3

class Blockchain:
    def __init__(self):
        self.listOfBlocks = []
        self.length = 0
        self.lasthash = -1
        self.init_utxos = []

    def add_block(self, B):
        self.listOfBlocks.append(B)
        self.length += 1
        self.lasthash = B.myhash
    
    def copy(self):
        b = Blockchain()
        setattr(b, 'listOfBlocks', self.listOfBlocks.copy())
        setattr(b, 'length', self.length)
        setattr(b, 'lasthash', self.lasthash)
        setattr(b, 'init_utxos', self.init_utxos)
        return b

    def print(self):
        acc = ""
        for i in range(len(self.listOfBlocks)):
            acc = acc + "Block " + str(i) + '\n' + self.listOfBlocks[i].print() + '\n'
        return acc