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
import netifaces as ni

master_node = '192.168.2.1'
master_port = ":5000"
my_port = ":5000"
registered = False

ip = ni.ifaddresses("enp0s8")[ni.AF_INET][0]['addr']
# ip = socket.gethostbyname(socket.gethostname())
NBCs = 200

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
    print("-1")
    requests.post("http://" + master_node + master_port + '/register/', json = {"public_key" : me.wallet.public_key.decode(),
                                                                                "ip" : ip + my_port})
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
    print("2")
    registered = True
    for x in me.ring:
        requests.post("http://" + me.ring[x][1] + '/newnode/', json = {"pk" : pk.decode(),
                                                                            "id" : me.ring[pk][0],
                                                                            "ip" : me.ring[pk][1],
                                                                            "NBC" : me.ring[pk][2]})
    return "0"

@app.route('/newnode/', methods=['POST'])
def get_new_node():
    print("3")
    dict = request.get_json()
    pk = dict["pk"].encode()
    id = dict["id"]
    ip = dict["ip"]
    NBC = dict["NBC"]
    me.ring[pk] = [id, ip, NBC]
    print("4")
    return "0"

@app.route('/ring/', methods=['GET'])
def show_ring():
    acc = "id   address \t balance\n"
    for x in me.ring:
        acc = acc + str(me.ring[x][0]) + " " + str(me.ring[x][1]) + " " + str(me.ring[x][2]) + "\n"
    return acc

@app.route('/t', methods=['GET'])
def make_transaction():
    args = request.args
    receiver = int(args.get('to'))
    amount = int(args.get('amount'))
    t = me.create_transaction(receiver, amount)
    for x in me.ring:
        requests.post("http://" + me.ring[x][1] + '/broadcast/', data = jsonpickle.encode(t))
    return "0"

@app.route('/broadcast/', methods=['POST'])
def get_transaction():
    d = request.data
    t = jsonpickle.decode(d)
    if me.receive(t):
        return "transaction ok"
    else:
        return "invalid transaction"

@app.route('/balance/', methods=['GET'])
def get_balance():
    return str(me.wallet.balance())

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    me = node.Node(ip + my_port)
    me.wallet.utxos[me.wallet.public_key] = [transaction.TransactionIO(0, me.wallet.public_key, NBCs)] # initial transaction
    app.run(host=ip, port=port)