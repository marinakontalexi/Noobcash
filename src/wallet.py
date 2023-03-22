import binascii

import Crypto
import Crypto.Random
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from Crypto import RSA

class Wallet:

	def __init__(self):
		key_length = 1024
		rsaKeys = RSA.generate(key_length)
		self.private_key = rsaKeys.export_key()
		self.public_key = rsaKeys.publickey().export_key()
		self.address = self.public_key
		self.utxos = []

	def balance(self):
		return sum([x.amount for x in self.utxos if x.address == self.address])
