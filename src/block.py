from Crypto.Hash import SHA256
import jsonpickle

capacity = 2

class Block:
    def __init__(self, previousHash):
        self.previousHash = previousHash
        self.listOfTransactions = []
        self.nonce = 0
        self.myhash = self.hash()
        
    def hash(self):
        block_to_byte = bytes(str(self.previousHash) + jsonpickle.encode(self.listOfTransactions) + str(self.nonce), 'utf-8')	    
        return SHA256.new(block_to_byte).hexdigest()
	
    def add_transaction(self, T):
        self.listOfTransactions.append(T)

    def copy(self):
        b = Block(self.previousHash)
        setattr(b, 'listOfTransactions', self.listOfTransactions.copy())
        setattr(b, 'nonce', self.nonce)
        setattr(b, 'myhash', self.myhash)
        return b

    def print(self):
        acc = "Previous Hash: " + self.previousHash + '\n' + "My Hash: " +  self.myhash + '\n' +  "Nonce: ", str(self.nonce) + '\n'
        for x in self.listOfTransactions:
            acc = acc + x.print_trans()
        return acc
