import requests
from flask import Flask, jsonify, request, render_template
import socket  
import json 
# from flask_cors import CORS
import block
import node
import blockchain
import transaction
import wallet
import netifaces as ni
import jsonpickle

master_node = '192.168.2.1'
master_port = ":5000"
my_port = ":5000"
total = 2

ip = ni.ifaddresses("enp0s8")[ni.AF_INET][0]['addr']
# ip = socket.gethostbyname(socket.gethostname())
NBCs = 200

app = Flask(__name__)
chain = blockchain.Blockchain()


#.......................................................................................


@app.route('/', methods=['GET'])
def get_transactions():
    return "Hello World!"
#     transactions = blockchain.transactions

#     response = {'transactions': transactions}
#     return jsonify(response), 200

@app.route('/login/', methods=['GET'])
def login(): 
    requests.post("http://" + master_node + master_port + '/register/', json = {"public_key" : me.wallet.address,
                                                                                "ip" : ip + my_port})
    return "Login Submitted"

@app.route('/login/', methods=['POST'])
def relogin():
    me.wallet = me.create_wallet()
    requests.post("http://" + master_node + master_port + '/register/', json = {"public_key" : me.wallet.address,
                                                                                "ip" : ip + my_port})
    return "Relogin Submitted"

@app.route('/genesis/', methods=['POST'])
def get_genesis():
    chain = jsonpickle.decode(request.data)
    print("GENESIS:")
    for x in me.wallet.utxos:
        print(x)
    me.get_initial_blockchain(chain)
    return "0"


@app.route('/register/', methods=['POST'])
def register():
    dict = request.get_json()
    pk = dict["public_key"]
    ip = dict["ip"]
    print(pk, ip)
    if pk in me.ring:
        print("ERROR: Public key already registered")
        requests.post("http://" + ip + '/login/')
        return "1"
    me.register_node_to_ring(pk, ip)

    if me.current_id_count == total - 1:
        init_t = transaction.Transaction(b'0', me.wallet.address, 100*total, b'0', [])
        init_B = block.Block("1")
        init_B.add_transaction(init_t)
        init_B.myhash = init_B.hash()
        chain.add_block(init_B)
        for x in me.ring:
            if me.ring[x][0] == 0: continue
            requests.post("http://" + me.ring[x][1] + '/newnode/', data = jsonpickle.encode(me.ring)) 
            requests.post("http://" + me.ring[x][1] + '/genesis/', data = jsonpickle.encode(chain))     
    return "0"

@app.route('/newnode/', methods=['POST'])
def get_new_node():
    d = request.data
    ring = jsonpickle.decode(d)
    for x in ring:
        me.wallet.utxos[x] = []
    me.ring = ring.copy()
    print("NEWNODE:")
    for x in me.wallet.utxos:
        print(x)
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
    app.run(host=ip, port=port)