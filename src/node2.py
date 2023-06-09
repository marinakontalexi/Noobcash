import blockchain
import block
import wallet2
import transaction2
from Crypto.Random import random
import requests
from termcolor import colored
import rest2
import time
import json

class Node:

	def __init__(self, ip):
		self.NBC=rest2.total*100
		self.current_id_count = 0
		self.wallet = self.create_wallet()
		self.ring = {self.wallet.address : [0, ip, self.NBC]} # here we store information for every node, as its id, its address (ip:port) its public key and its balance
		self.currentBlock = None
		self.chain = None
		self.start_time = time.time()
		self.avg = []
		self.t = time.time()
		
	# node functions

	def create_wallet(self):
		return wallet2.Wallet()

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
		if receiver_address == -1: 
			print("Wrong receiver address")
			return None
		for t in self.wallet.utxos[self.wallet.address]:
			if not t.available: continue
			if s >= amount: break
			# setattr(t, 'available', False)
			transactionInputs.append(t.copy())
			s += t.amount
		if s < amount: 
			print("Not enough NBCs")
			return None
		return transaction2.Transaction(self.wallet.public_key, receiver_address, amount, self.wallet.private_key, transactionInputs)
		
	def receive(self, T):
		if self.validate_transaction(T):
			print("Transaction is valid")
			return True
		print(colored("Error: Transaction " + T.print_trans() + " is not valid.", "red"))	
		return False

	def validate_transaction(self, T):
		safeutxos = self.wallet.utxos.copy()
		safering = self.ring.copy()
		if not T.verify_signature(): 
			print("Error: Wrong signature!")
			return False
		if T.receiver_address not in self.ring:
			print("Error: Wrong receiver address!")
			return False
		
		for x in T.transaction_inputs:			# check for valid transaction inputs
			found = False
			for t in safeutxos[str(T.sender_address)]:
				if x.equal(t) and t.available:
					found = True
					setattr(t, 'available', False)
					safering[x.address][2] -= x.amount		# update ring dict
					break
				elif x.equal(t):
					print("Input UTXO is taken. Retry.")
					return False
			if not found: 
				print("Error: Wrong Transaction Inputs!")
				return False
		
		change = sum([x.amount for x in T.transaction_inputs]) -  T.amount
		if change > 0:
			correct_outputs = [transaction2.TransactionIO(T.hash().digest(), str(T.sender_address), change),
		     transaction2.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]
		elif change == 0:
			correct_outputs = [transaction2.TransactionIO(T.hash().digest(), T.receiver_address, T.amount)]
		else:
			print("Error: Transaction inputs do not contain enough NBCs!")
			return False

		if (len(T.transaction_outputs) != len(correct_outputs)):
			print("Error: Invalid Transaction Outputs!")
			return False
		for i in range(len(correct_outputs)):
			if not T.transaction_outputs[i].equal(correct_outputs[i]):     # check for valid transaction outputs
				print("Error: Wrong Transaction Outputs!")
				return False
		
		for x in correct_outputs:
			safeutxos[x.address].append(x)
			safering[x.address][2] += x.amount
		self.wallet.utxos = safeutxos.copy()
		self.ring = safering.copy()
		return True

	# blockchain functions

	def create_new_block(self):
		self.currentBlock = block.Block(self.currentBlock.myhash)
		return
	
	def add_transaction_to_block(self, T):
		self.currentBlock.add_transaction(T)

	def get_initial_blockchain(self, chain):
		if not self.validate_chain(chain):
			print("ERROR: Invalid chain!")
			return
		self.chain = chain.copy()
		self.currentBlock = block.Block(chain.lasthash)
		self.t = time.time()
		return
	
	def validate_chain(self, chain):
		genesis = chain.listOfBlocks[0]
		self.chain = blockchain.Blockchain()
		self.chain.add_block(genesis)
		self.wallet.utxos = chain.init_utxos
		for i in range(1, len(chain.listOfBlocks)):
			if not self.validate_block(chain.listOfBlocks[i]):
				return False
		return True

	def mine_block(self):
		nonce = random.getrandbits(32)
		setattr(self.currentBlock, 'nonce', nonce)
		myhash = self.currentBlock.hash()
		setattr(self.currentBlock, 'myhash', myhash)
		return self.valid_proof(myhash)

	def broadcast_block(self):								# add block to chain, update utxos for each transaction in block
		res = self.currentBlock
		if len(res.listOfTransactions) == 0: return res
		self.chain.add_block(self.currentBlock)

		self.avg.append(time.time() - self.t)
		self.t = time.time()

		for t in res.listOfTransactions:
			sender = str(t.sender_address)
			for t_in in t.transaction_inputs:
				for x in self.wallet.utxos[sender]:
					if x.equal(t_in): 
						self.wallet.utxos[sender].remove(x)
						break
		self.create_new_block()
		return res
	
	def valid_proof(self, hash):
		return hash[0:blockchain.MINING_DIFFICULTY] == "0"*blockchain.MINING_DIFFICULTY

	def receive_block(self, B):
		if len(B.listOfTransactions) == 0: return False
		if self.validate_block(B):
			print("Block is valid! :)")
			self.currentBlock = B.copy()
			b = self.broadcast_block()
			return True
		print("Warning: Block not valid!")
		return False
	
	def validate_block(self, B):
		safeutxos = self.wallet.utxos.copy()
		safering = self.ring.copy()
		if self.chain.lasthash != B.previousHash:
			print("Error: Block has wrong previous hash!")
			return False
		if B.myhash != B.hash():
			print("Error: Block has wrong hash!")
			return False
		
		for i in range(len(self.currentBlock.listOfTransactions)-1, -1, -1):		# undo my transactions
			t = self.currentBlock.listOfTransactions[i]
			sender = str(t.sender_address)
			receiver = t.receiver_address
			for t_in in t.transaction_inputs:
				for x in self.wallet.utxos[sender]:
					if x.equal(t_in): 
						setattr(x, 'available', True)
						break
			for t_out in t.transaction_outputs:
				for x in self.wallet.utxos[t_out.address]:
					if x.equal(t_out):
						self.wallet.utxos[t_out.address].remove(x)
			self.ring[sender][2] += t.amount
			self.ring[receiver][2] -= t.amount

		for i in range(len(B.listOfTransactions)):
			t = B.listOfTransactions[i]
			if not self.validate_transaction(t):		# attention: this function changes self.wallet.utxos
				self.wallet.utxos = safeutxos.copy()
				self.ring = safering.copy()
				print("Error: Transaction ", i, " was invalid!")
				return False
			# print("UTXOS AFTER REDO", i)
			# for x in self.wallet.utxos:
			# 	for y in self.wallet.utxos[x]:
			# 		print(y.print_trans())
		return True

	def choose_chain(self, chain, curr, utxos, ring):
		if chain.length > self.chain.length:
			self.chain = chain.copy()
			self.currentBlock = curr.copy()
			for x in ring:
				self.ring[x] = []
				for i in range(3):
					self.ring[x].append(ring[x][i])
				self.wallet.utxos[x] = []
				for t in utxos[x]:
					self.wallet.utxos[x].append(t.copy())
					
			for i in range(len(self.currentBlock.listOfTransactions)-1, -1, -1):		# undo my transactions
				t = self.currentBlock.listOfTransactions[i]
				sender = str(t.sender_address)
				receiver = t.receiver_address
				for t_in in t.transaction_inputs:
					for x in self.wallet.utxos[sender]:
						if x.equal(t_in): 
							setattr(x, 'available', True)
							break
				for t_out in t.transaction_outputs:
					for x in self.wallet.utxos[t_out.address]:
						if x.equal(t_out):
							self.wallet.utxos[t_out.address].remove(x)
				self.ring[sender][2] += t.amount
				self.ring[receiver][2] -= t.amount
			self.currentBlock = block.Block(chain.lasthash)
			self.avg.append(time.time() - self.t)
			self.t = time.time()
			return False
		return True
		
	def balance():
		url = 'http://' + rest2.ip + rest2.my_port + '/balance/'
		response = requests.get(url)
		print('Your balance is :', response.text)
		return response
	
	def view():
		url = 'http://' + rest2.ip + rest2.my_port + '/view/'
		response = requests.get(url)
		re = response.json()
		r = json.dumps(re).replace(',', ',\n')
		print('Last block added to blockchain')
		print(r)

	def sendTransCli(id, amount):
		url = 'http://' + rest2.ip + rest2.my_port + '/t?to='+ str(id) + '&amount=' + str(amount)
		# print(url)
		response = requests.get(url)
		if(response.status_code == 200):
			print('Transcation is sent!')
		else:
			print('Transaction was not sent please repeat!')