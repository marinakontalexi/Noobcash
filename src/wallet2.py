from Crypto.PublicKey import RSA

class Wallet:

	def __init__(self):
		key_length = 1024
		rsaKeys = RSA.generate(key_length)
		self.private_key = rsaKeys.export_key()
		self.public_key = rsaKeys.publickey().export_key()
		self.address = str(self.public_key)
		self.utxos = {}

	def balance(self):
		return sum([x.amount for x in self.utxos[self.address]])
