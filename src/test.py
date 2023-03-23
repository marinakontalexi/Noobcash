import jsonpickle
import requests
from flask import Flask, jsonify, request, render_template
import socket  
import json 
# from flask_cors import CORS
# import block
import node
# import blockchain
import transaction

n1 = node.Node("")
n2 = node.Node("")
ring = n1.register_node_to_ring(n2.wallet.address, -2)
t1 = transaction.TransactionIO(bytes(5), n1.wallet.address, 200)
n1.wallet.utxos["0"]=t1
n2.wallet.utxos["0"]=t1

t = transaction.Transaction(n1.wallet.public_key, n2.wallet.address, 100, n1.wallet.private_key, [t1])
print(type(t.sender_address))
frozen = jsonpickle.encode(t)

t2 = jsonpickle.decode(frozen)
print(type(t2.sender_address))
