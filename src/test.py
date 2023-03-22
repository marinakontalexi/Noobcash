import jsonpickle
import requests
from flask import Flask, jsonify, request, render_template
import socket  
import json 
# from flask_cors import CORS
# import block
import ncopy as nod
# import blockchain
import tcopy as trans
import wallet
import myclass
import my

n1 = nod.Node()
n2 = nod.Node()
ring = n1.register_node_to_ring(n2.wallet.address, -2)
n1.wallet.utxos.append(trans.TransactionIO(bytes(5), n1.wallet.public_key, 200))
n2.wallet.utxos.append(trans.TransactionIO(bytes(5), n1.wallet.public_key, 200))

t = n1.create_transaction(n2.wallet.public_key, 100)

temp = myclass.c(t.transaction_id)
frozen = jsonpickle.encode(temp)

t2 = jsonpickle.decode(frozen)
print(t2.id)