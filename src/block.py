import blockchain
from Crypto.Hash import SHA256

capacity = 1

class Block:
    def __init__(self, previousHash):
        self.previousHash = previousHash
        self.listOfTransactions = []
		#self.hash
		#self.nonce
        
    def hash(self):
        block_to_byte = bytes(str(self.sender_address) + str(self.receiver_address) + str(self.amount), 'utf-8')	    
        return SHA256.new(block_to_byte)
	
    def add_transaction(self, T):
        self.listOfTransactions.append(T)
