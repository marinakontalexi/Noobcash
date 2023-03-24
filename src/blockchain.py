from Crypto.Hash import SHA256

MINING_DIFFICULTY = 3

class Blockchain:
    def __init__(self):
        self.listOfBlocks = []
        self.length = 0

    def add_block(self, B):
        self.listOfBlocks.append(B)
        self.length += 1
        self.lasthash = B.myhash
    
    def copy(self):
        b = Blockchain()
        setattr(b, 'listOfBlocks', self.listOfBlocks.copy())
        setattr(b, 'length', self.length)
        return b

    def print(self):
        for i in range(len(self.listOfBlocks)):
            print ("Block ", i)
            self.listOfBlocks[i].print()
