import block
import wallet
import transaction

class Node:
	capacity = 1
	def __init__(self, ip):
		self.NBC=200;
		#self.chain
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		# self.NBCs 
		self.ring = {self.wallet.address : [0, ip, self.NBC]} # here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def create_new_block():
		return

	def create_wallet(self):
		return wallet.Wallet()

	def register_node_to_ring(self, public_key, ip):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.current_id_count += 1
		self.ring[self.wallet.address][2] += 100
		self.ring[public_key] = [self.current_id_count, ip, 0]		
		return self.ring

	def create_transaction(self, receiver, amount):
		s = 0 
		receiver_address = -1
		transactionInputs = []
		for x in self.ring:
			if self.ring[x][0] == receiver: receiver_address = x
		for t in self.wallet.utxos[self.wallet.address]:
			if s >= amount: break
			transactionInputs.append(t)
			s += t.amount
		return transaction.Transaction(self.wallet.public_key, receiver_address, amount, self.wallet.private_key, transactionInputs)


	# def broadcast_transaction(self,T):
	# 	log.append(T)

	def receive(self, T):
		print("balance_receive: ", self.ring[T.sender_address][2])
		return self.validate_transaction(T)
		# for x in newT.transaction_inputs:
		# 	print("Input:\n")
		# 	x.print_trans()
		# for x in newT.transaction_outputs:
		# 	print("Output:\n")
		# 	x.print_trans()
		# for x in self.wallet.utxos:
		# 	print("Wallet:")
		# 	x.print_trans()

	def validate_transaction(self, T):
		if not T.verify_signature(): 
			print("Error: Wrong signature!\n")
			return False
		if T.receiver_address == -1:
			print("Error: Wrong receiver id!\n")
			return False
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



	# def add_transaction_to_block():
	# 	#if enough transactions  mine



	# def mine_block():



	# def broadcast_block():


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):




	# #concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes


	# def resolve_conflicts(self):
	# 	#resolve correct chain



