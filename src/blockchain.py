import blockchain
from Crypto.Hash import SHA256

MINING_DIFFICULTY = 1

class Blockchain:
    def __init__(self):
        self.listOfBlocks = []
        self.length = 0
        self.currenthash = -1

    def add_block(self, B):
        self.listOfBlocks.append(B)
        self.currenthash = B.hash
