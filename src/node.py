import blockchain
import block
import wallet
import transaction
from datetime import datetime
import Crypto

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
		# print("CREATE:\n")
		# print(self.ring[self.wallet.address][0], self.ring[receiver_address][0], receiver)
		return transaction.Transaction(self.wallet.public_key, receiver_address, amount, self.wallet.private_key, transactionInputs)

	def receive(self, T):
		if self.validate_transaction(T):
			B = self.add_transaction_to_block(T)
			if B != None:
				print("transaction received\n")
				return True
		print("transaction not received\n")	
		return False

	def validate_transaction(self, T):
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
			for t in self.wallet.utxos[str(T.sender_address)]:
				if x.equal(t):
					found = True
					self.wallet.utxos[str(T.sender_address)].remove(t)
					if x.address in self.ring: 						# update ring dict
						self.ring[x.address][2] -= x.amount
					else: 
						print("Something went wrong with NBCs dict")
					break
			if not found: 
				print("Error: Wrong Transaction Inputs!\n")
				return False
			
		print("utxos after remove: ")
		for x in self.wallet.utxos:
			print("node: ", self.ring[x][0])
			for y in self.wallet.utxos[x]:
				y.print_trans()

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
			self.wallet.utxos[x.address].append(x)
			self.ring[x.address][2] += x.amount

		print("utxos after append: ")
		for x in self.wallet.utxos:
			print("node: ", self.ring[x][0])
			for y in self.wallet.utxos[x]:
				y.print_trans()
		
		return True

	# blockchain functions

	def create_new_block(self):
		self.currentBlock = block.Block(self.currentBlock.hash)
		return
	
	def add_transaction_to_block(self, T):
		self.currentBlock.add_transaction(T)
		if len(self.currentBlock.listOfTransactions) == block.capacity:
			return self.mine_block()
		return None

	def get_initial_blockchain(self, chain):
		self.chain = chain
		self.currentBlock = block.Block(chain.lasthash)
		tout = chain.listOfBlocks[0].listOfTransactions[0].transaction_outputs
		for x in tout:
			self.wallet.utxos[x.address].append(x)
		return

	def mine_block(self):
		while (not self.valid_proof(str(self.currentBlock.hash()), blockchain.MINING_DIFFICULTY)):
			nonce = Crypto.Random.random.getrandbits(32)
			setattr(self.currentBlock, 'nonce', nonce)
		return self.broadcast_block()

	def broadcast_block(self):
		self.chain.add_block(self.currentBlock)
		res = self.currentBlock
		self.chain.add_block(self.currentBlock)
		self.create_new_block()
		return res

	def valid_proof(self, hash, difficulty):
		return hash[0:difficulty] == "0"*difficulty

	def receive_block(self, B):
		# checks?
		self.chain.add_block(B)
		return
	#concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain