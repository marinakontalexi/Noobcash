import blockchain
import block
import wallet
import transaction
from datetime import datetime

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

	def create_new_block(self):
		return

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, address, ip):
		if self.ring[self.wallet.address][0] != 0:
			print("Sorry you cannot register a node!\n")
			return
		self.current_id_count += 1
		self.ring[address] = [self.current_id_count, ip, 0]
		for x in self.ring:
			print("node:", x)
			for y in self.ring[x]:
				print(y)

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
		# print("balance_receive: ", self.ring[T.sender_address][2])
		if self.validate_transaction(T):
			self.add_transaction_to_block(T)

	def validate_transaction(self, T):
		if not T.verify_signature(): 
			print("Error: Wrong signature!\n")
			return False
		if T.receiver_address == -1:
			print("Error: Wrong receiver id!\n")
			return False
		if T.sender_address in self.ring: print("valid key")
		for x in self.ring:
			print("x", x, type(x))
			print("sender_address: ", T.sender_address, type(T.sender_address))
			print(x == T.sender_address)
		
		if self.ring[T.sender_address][2] < T.amount:
			# print("balance_validate: ", self.ring[T.sender_address][2], T.amount)
			print("Error: Not enough NBCs for transaction!\n")
			return False
		
		for x in T.transaction_inputs:			# check for valid transaction inputs
			found = False
			for t in self.wallet.utxos[T.sender_address]:
				if x.equal(t):
					found = True
					self.wallet.utxos[T.sender_address].remove(t)
					if x.address in self.ring: 						# update ring dict
						self.ring[x.address][2] -= x.amount
					else: 
						print("Something went wrong with NBCs dict")
					break
			if not found: 
				print("Error: Wrong Transaction Inputs!\n")
				return False
			
		change = sum([x.amount for x in T.transaction_inputs]) -  T.amount
		if change > 0:
			correct_outputs = [transaction.TransactionIO(T.hash().digest(), T.sender_address, change),
		     transaction.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]
		else:
			correct_outputs = [transaction.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]

		# print("given outputs:")
		# for x in T.transaction_outputs:
		# 	x.print_trans()
		# print("correct outputs:")
		# output1.print_trans()
		# output2.print_trans()
		if (len(T.transaction_outputs) != len(correct_outputs)):
			print("Error: Invalid Transaction Outputs!\n")
			return False
		for i in range(len(correct_outputs)):
			if not T.transaction_outputs[i].equal(correct_outputs[i]):     # check for valid transaction outputs
				print("Error: Wrong Transaction Outputs!\n")
				return False
		
		for x in T.transaction_outputs:
			self.wallet.utxos[T.receiver_address].append(x)
			self.ring[x.address][2] += x.amount
			print("x.address: ", self.ring[x.address][0])
			print("amount: ", self.ring[x.address][2])
		return True

	# blockchain functions

	def add_transaction_to_block(self, T):
		self.currentBlock.add_transaction(T)
		if len(self.currentBlock.listOfTransactions) == block.capacity:
			self.mine_block()
			return True
		return False

	def get_initial_blockchain(self, chain):
		self.chain = chain

	def mine_block(self):
		nonce = self.valid_proof()
		setattr(self.currentBlock, 'nonce', nonce)
		return

	def broadcast_block(self):
		self.chain.add_block(self.currentBlock)
		res = self.currentBlock
		setattr(res, 'timestamp', datetime.now())
		print(res.timestamp)
		self.create_new_block()
		return res

	def valid_proof(slef, difficulty = blockchain.MINING_DIFFICULTY):
		return 0


	#concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain
