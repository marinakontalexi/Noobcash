import blockchain
from Crypto.Hash import SHA256
import jsonpickle

capacity = 3

class Block:
    def __init__(self, previousHash):
        self.previousHash = previousHash
        self.listOfTransactions = []
        self.nonce = 0
        self.myhash = self.hash()
        
    def hash(self):
        block_to_byte = bytes(str(self.previousHash) + jsonpickle.encode(self.listOfTransactions) + str(self.nonce), 'utf-8')	    
        self.myhash = SHA256.new(block_to_byte).hexdigest()
        return self.myhash
	
    def add_transaction(self, T):
        self.listOfTransactions.append(T)
