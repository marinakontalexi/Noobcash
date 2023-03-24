import blockchain
import block
import wallet
import transaction
from Crypto.Random import random

class Node:

	def __init__(self, ip):
		self.NBC=200
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		# self.NBCs 
		self.ring = {self.wallet.address : [0, ip, self.NBC]} # here we store information for every node, as its id, its address (ip:port) its public key and its balance 
		self.currentBlock = None
		self.chain = None

	# node functions

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, address, ip):
		if self.ring[self.wallet.address][0] != 0:
			print("Sorry you cannot register a node!\n")
			return
		self.current_id_count += 1
		self.ring[address] = [self.current_id_count, ip, 0]
		self.wallet.utxos[address] = []

	# transaction functions

	def create_transaction(self, receiver, amount):
		s = 0 
		receiver_address = -1
		transactionInputs = []
		for x in self.ring:
			if self.ring[x][0] == receiver: 
				receiver_address = x
				break
		for t in self.wallet.utxos[self.wallet.address]:
			if s >= amount: break
			transactionInputs.append(t)
			s += t.amount
		return transaction.Transaction(self.wallet.public_key, receiver_address, amount, self.wallet.private_key, transactionInputs)
		
	def receive(self, T):
		if self.validate_transaction(T, True):
			print("Transaction is valid\n")
			return self.add_transaction_to_block(T)
		print("Error: Transaction not valid\n")	
		return False

	def validate_transaction(self, T, u):
		if u:
			utxos = self.wallet.utxos
		else: 
			utxos = self.chain.utxos

		if not T.verify_signature(): 
			print("Error: Wrong signature!\n")
			return False
		if T.receiver_address == -1:
			print("Error: Wrong receiver id!\n")
			return False
		
		if self.ring[str(T.sender_address)][2] < T.amount:
			print("Error: Not enough NBCs for transaction!\n")
			return False
		
		for x in T.transaction_inputs:			# check for valid transaction inputs
			found = False
			for t in utxos[str(T.sender_address)]:
				if x.equal(t):
					found = True
					utxos[str(T.sender_address)].remove(t)
					if x.address in self.ring: 						# update ring dict
						self.ring[x.address][2] -= x.amount
					else: 
						print("Something went wrong with ring")
					break
			if not found: 
				print("Error: Wrong Transaction Inputs!\n")
				return False
		
		change = sum([x.amount for x in T.transaction_inputs]) -  T.amount
		if change > 0:
			correct_outputs = [transaction.TransactionIO(T.hash().digest(), str(T.sender_address), change),
		     transaction.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]
		else:
			correct_outputs = [transaction.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]

		if (len(T.transaction_outputs) != len(correct_outputs)):
			print("Error: Invalid Transaction Outputs!\n")
			return False
		for i in range(len(correct_outputs)):
			if not T.transaction_outputs[i].equal(correct_outputs[i]):     # check for valid transaction outputs
				print("Error: Wrong Transaction Outputs!\n")
				return False
		
		for x in T.transaction_outputs:
			utxos[x.address].append(x)
			self.ring[x.address][2] += x.amount
		return True

	# blockchain functions

	def create_new_block(self):
		self.currentBlock = block.Block(self.currentBlock.myhash)
		return
	
	def add_transaction_to_block(self, T):
		self.currentBlock.add_transaction(T)
		if len(self.currentBlock.listOfTransactions) == block.capacity:
			return True
		return False

	def get_initial_blockchain(self, chain, utxos):
		# safecurrent = self.currentBlock.copy()
		if not self.validate_chain(chain):
			print("ERROR: Invalid chain!")
			# self.currentBlock = safecurrent
			return
		self.chain = chain.copy()
		self.currentBlock = block.Block(chain.lasthash)
		self.wallet.utxos = utxos.copy()
		self.chain.utxos = utxos.copy()
		return

	def mine_block(self):
		nonce = random.getrandbits(32)
		setattr(self.currentBlock, 'nonce', nonce)
		myhash = self.currentBlock.hash()
		setattr(self.currentBlock, 'myhash', myhash)
		return self.valid_proof(myhash, blockchain.MINING_DIFFICULTY)

	def broadcast_block(self):
		res = self.currentBlock
		self.chain.add_block(self.currentBlock)
		self.create_new_block()
		return res
	
	def valid_proof(self, hash, difficulty):
		return hash[0:difficulty] == "0"*difficulty

	def receive_block(self, B):
		if self.validate_block(B):
			print("Block is valid\n")
			self.chain.add_block(B.copy())
			return True
		print("Warning: Block not valid!\n")
		return False
	
	def validate_block(self, B):
		safeutxos = self.chain.utxos.copy()
		if self.chain.lasthash != B.previousHash:
			print("Error: Block has wrong previous hash!\n")
			return False
		if B.myhash != B.hash():
			print("Error: Block has wrong hash!\n")
			return False
		for i in range(len(B.listOfTransactions)):
			t = B.listOfTransactions[i]
			if not self.validate_transaction(t, False):
				print("Error: Transaction ", i, " was invalid!\n")
				self.chain.utxos = safeutxos
				return False
		return True
	
	def validate_chain(self, chain):
		# for b in chain.listOfBlocks:
		return True

	def choose_chain(self, chain, utxos):
		if chain.length > self.chain.length:
			self.chain = chain.copy()
			self.currentBlock = block.Block(chain.lasthash)
			self.wallet.utxos = utxos.copy()
			self.chain.utxos = utxos.copy()
		return
		

	# def resolve_conflicts(self, B):
	# 	return self.currentBlock.previousHash == B.previousHash