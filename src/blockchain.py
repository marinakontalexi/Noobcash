from Crypto.Hash import SHA256

MINING_DIFFICULTY = 1

class Blockchain:
    def __init__(self):
        self.listOfBlocks = []
        self.length = 0

    def add_block(self, B):
        self.listOfBlocks.append(B)
        self.length += 1
        self.lasthash = B.myhash
