import requests
from flask import Flask, jsonify, request, render_template
import socket  
import json 
# from flask_cors import CORS
# import block
import node
# import blockchain
import transaction
import wallet
import jsonpickle

master_node = '192.168.1.11'
master_port = ":5000"
registered = False
ip = socket.gethostbyname(socket.gethostname())

app = Flask(__name__)
# CORS(app)
# blockchain = Blockchain()


#.......................................................................................



# get all transactions in the blockchain

@app.route('/', methods=['GET'])
def get_transactions():
    return "Hello World!"
#     transactions = blockchain.transactions

#     response = {'transactions': transactions}
#     return jsonify(response), 200

@app.route('/login/', methods=['GET'])
def login(): 
    requests.post("http://" + master_node + master_port + '/register/', json = {"public_key" : me.wallet.public_key.decode(),
                                                                                "ip" : ip}) == "0"
    if not registered:
        return "Login FAIL: Public key already registered"
    return "Login OK"

@app.route('/register/', methods=['POST'])
def register():
    dict = request.get_json()
    pk = dict["public_key"].encode()
    ip = dict["ip"]
    if pk in me.ring:
        return "ERROR: Public key already registered"
    me.register_node_to_ring(pk, ip)
    registered = True
    for x in me.ring:
        requests.post("http://" + x[1] + master_port + '/newnode/', json = {"pk" : pk.decode(),
                                                                            "id" : me.ring[pk][0],
                                                                            "ip" : me.ring[pk][1],
                                                                            "NBC" : me.ring[pk][2]})
    return "1"

@app.route('/newnode/', methods=['POST'])
def get_new_node():
    dict = request.get_json()
    pk = dict["pk"].encode()
    id = dict["id"]
    ip = dict["ip"]
    NBC = dict["NBC"]
    me.ring[pk] = [id, ip, NBC]

@app.route('/ring/', methods=['GET'])
def show_ring():
    acc = ""
    for x in me.ring:
        acc = acc + str(me.ring[x][0]) + " " + str(me.ring[x][1]) + " " + str(me.ring[x][2]) + "\n"
    return acc

@app.route('/t/', methods=['GET'])
def make_transaction():
    args = request.args
    receiver = args.get('to')
    amount = args.get('amount')
    receiver_address = -1
    inputs = []
    sum = 0
    for x in me.wallet.utxos:
        if x.address == me.wallet.address:
            if sum < amount:
                inputs.append(x)
                sum += x.amount 
            else: break
    for x in me.ring:
        if me.ring[x][0] == receiver: receiver_address = x
    t = transaction.Transaction(me.wallet.address, receiver_address, amount, me.wallet.private_key)
    for x in me.ring:
        requests.post("http://" + x[1] + master_port + '/broadcast/', data = jsonpickle.encode(t))

@app.route('/broadcast/', methods=['POST'])
def get_transaction():
    d = request.data
    t = jsonpickle.decode(d)
    me.receive(t)

@app.route('/balance/', methods=['GET'])
def get_balance():
    return str(me.wallet.balance())

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    me = node.Node()
    me.wallet.utxos.append(transaction.TransactionIO(5, me.wallet.public_key, 200))
    app.run(host=ip, port=port)