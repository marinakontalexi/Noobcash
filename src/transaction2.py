from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
import jsonpickle
import rest2

class TransactionIO:

    def __init__(self, transaction_id, address, amount):
        self.transaction_id = transaction_id
        self.address = address
        self.amount = amount
        self.available = True
        # self.id = self.hash().hexdigest()
    
    def print_trans(self):
        print("TransactionIO ", rest2.addresses[self.address], ": ", self.amount)
    
    def equal(self, T):
        return self.hash().digest() == T.hash().digest()
    
    def hash(self):
        #calculate self.hash
        block_to_byte = bytes(str(self.transaction_id) + str(self.address) + str(self.amount), 'utf-8')
        return SHA256.new(block_to_byte)
        

class Transaction:

    def __init__(self, sender_address, receiver_address, amount, sender_private_key, transactionInputs):
    
        self.sender_address = sender_address # To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = receiver_address # To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = amount # το ποσό που θα μεταφερθεί
        self.transaction_inputs = transactionInputs # λίστα από Transaction Input
        transaction_id = self.hash() # το hash του transaction
        change = sum([x.amount for x in transactionInputs]) -  amount
        if change > 0:
            self.transaction_outputs = [TransactionIO(transaction_id.digest(), str(sender_address), change), 
                                        TransactionIO(transaction_id.digest(), receiver_address, amount)] 
        else:
            self.transaction_outputs = [TransactionIO(transaction_id.digest(), receiver_address, amount)]
        if sender_address != b'0':
            self.signature = self.sign_transaction(sender_private_key)

    def to_dict(self):
        return 
        
    def hash(self):
        block_to_byte = bytes(str(self.sender_address) + str(self.receiver_address) + str(jsonpickle.encode(self.transaction_inputs)) + str(self.amount), 'utf-8')
        return SHA256.new(block_to_byte)

    def sign_transaction(self, sender_private_key):
        """
        Sign transaction with private key
        """
        signer = pkcs1_15.new(RSA.import_key(sender_private_key))
        return signer.sign(self.hash())
    
    def print_trans(self):
        print("TRANSACTION ", rest2.addresses[str(self.sender_address)], " -> ", rest2.addresses[self.receiver_address], self.amount)
    
    def verify_signature(self):
        pk = RSA.import_key(self.sender_address)
        verifier = PKCS1_v1_5.new(pk)
        return verifier.verify(self.hash(), self.signature)