import requests
from flask import Flask, request
import threading
import block
import node
import blockchain
import transaction
import netifaces as ni
import socket
import jsonpickle
import time

master_node = '10.0.0.1'
master_port = ":5000"
my_port = ":5000"
total = 2
project_path = "../"

ip = ni.ifaddresses("eth1")[ni.AF_INET][0]['addr']
# ip = socket.gethostbyname(socket.gethostname())

app = Flask(__name__)
chain = blockchain.Blockchain()

def queue_function(qevent):
    p = None
    while True:
        if qevent.is_set():
            return
        if len(me.currentBlock.listOfTransactions) == 2:
            print("block size is 2!")
        if len(q) == 0: continue
        if p == None: 
            if len(me.currentBlock.listOfTransactions) == block.capacity:                
                print("p is None and block is full")
                p = threading.Thread(target = mine_function, args=(blc_rcv,), daemon=True)
                p.start()
            if len(me.currentBlock.listOfTransactions) < block.capacity:                
                print("p is None and block is not full")
                t = q.pop(0)
                if me.receive(t):                
                    print("t was received") 
                    me.add_transaction_to_block(t)
                    print("t was added to block. Block size is ", len(me.currentBlock.listOfTransactions))  
        elif p.is_alive(): continue
        else:
            if len(me.currentBlock.listOfTransactions) == block.capacity:                
                print("p is not alive and block is full")
                p = threading.Thread(target = mine_function, args=(blc_rcv,), daemon=True)
                p.start()
            if len(me.currentBlock.listOfTransactions) < block.capacity:                
                print("p is not alive and block is not full")
                t = q.pop(0)
                if me.receive(t):                
                    print("t was received") 
                    me.add_transaction_to_block(t)
                    print("t was added to block") 

def mine_function(event):
    print("I start mining")
    while not me.mine_block():
        if event.is_set():
            print("I stop mining")
            event.clear()
            return
    print("mine ok")
    for x in me.ring:
        if x == me.wallet.address: continue 
        requests.post("http://" + me.ring[x][1] + '/newblock/', data = jsonpickle.encode(me.broadcast_block()))

def cli_function():
    time.sleep(10)
    if ip != master_node: requests.get("http://" + ip  + my_port + "/login/")
    time.sleep(10)    
    queue = threading.Thread(target = queue_function, args=(qevent,), daemon=True)
    queue.start()
    time.sleep(10)
    f = open(project_path + "5nodes/transactions{}.txt".format(me.ring[me.wallet.address][0]), "r")
    s = s = f.readline()
    t = time.time()
    while s != "":
        [r, amount] = s.split()
        rcv = r[2:]
        if int(rcv) >= total: continue
        requests.get("http://" + ip  + my_port + "/t?to=" + rcv + '&amount=' + amount)
        time.sleep(10)
        s = f.readline()
    print("Time", time.time() - t)
    # kill queue
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
    (ring, chain) = jsonpickle.decode(request.data)
    for x in ring:
        me.ring[x] = []
        me.chain_ring[x] = []
        for i in range(3):
            me.ring[x].append(ring[x][i])
            me.chain_ring[x].append(ring[x][i])
        me.wallet.utxos[x] = []
        me.wallet.chain_utxos[x] = []
        for t in chain.init_utxos[x]:
            me.wallet.utxos[x].append(t)
            me.wallet.chain_utxos[x].append(t)
    me.get_initial_blockchain(chain)
    return "0"

@app.route('/register/', methods=['POST'])
def register():
    if me.current_id_count >= total:
        print("ERROR: All nodes are already registered!")
        return "1"
    dict = request.get_json()         
    pk = dict["public_key"]
    IP = dict["ip"]
    if pk in me.ring:
        if me.ring[pk][1] == ip:
            requests.post("http://" + IP + '/genesis/', data = jsonpickle.encode((me.chain_ring.copy(), me.chain)))
        else:
            print("ERROR: Public key already registered")
            requests.post("http://" + IP + '/login/')
        return "1"
        
    me.register_node_to_ring(pk, IP)

    if me.current_id_count == total - 1:
        init_t = transaction.Transaction(b'0', me.wallet.address, 100*total, b'0', [])
        init_B = block.Block("1")
        init_B.add_transaction(init_t)
        init_B.myhash = init_B.hash()
        chain.add_block(init_B)
        for x in init_t.transaction_outputs:
            me.wallet.utxos[x.address] = [x]
            me.wallet.chain_utxos[x.address] = [x]
        me.currentBlock = block.Block(chain.lasthash)
        me.chain = chain.copy()
        me.chain.init_utxos = me.wallet.utxos.copy()
        for x in me.ring:
            if me.ring[x][0] == 0: continue
            requests.post("http://" + me.ring[x][1] + '/genesis/', data = jsonpickle.encode((me.chain_ring, me.chain)))
        for x in me.ring:
            if me.ring[x][0] == 0: continue
            t = me.create_transaction(me.ring[x][0], 100)
            for y in me.ring:
                requests.post("http://" + me.ring[y][1] + '/broadcast/', data = jsonpickle.encode(t))
    return "0"

@app.route('/ring/', methods=['GET'])
def show_ring():
    acc = {-1 : ["address", "balance"]}
    for x in me.ring:
        acc[me.ring[x][0]] = [me.ring[x][1], me.ring[x][2]]
    return jsonpickle.encode(acc)

@app.route('/chain_ring/', methods=['GET'])
def show_chain_ring():
    acc = {-1 : ["address", "balance"]}
    for x in me.chain_ring:
        acc[me.chain_ring[x][0]] = [me.chain_ring[x][1], me.chain_ring[x][2]]
    return jsonpickle.encode(acc)

@app.route('/t', methods=['GET'])
def make_transaction():
    args = request.args
    receiver = int(args.get('to'))
    amount = int(args.get('amount'))
    t = me.create_transaction(receiver, amount)
    for x in me.ring:
        if x == me.wallet.address: continue
        requests.post("http://" + me.ring[x][1] + '/broadcast/', data = jsonpickle.encode(t))
    requests.post("http://" + me.ring[me.wallet.address][1] + '/broadcast/', data = jsonpickle.encode(t))
    return "0"

@app.route('/broadcast/', methods=['POST'])
def get_transaction():
    print("TRANSACTION RECEIVED\n")
    d = request.data
    t = jsonpickle.decode(d) 
    q.append(t)
    print("I pushed a transaction")
    return "0"
            

@app.route('/balance/', methods=['GET'])
def get_balance():
    return str(me.wallet.balance())

@app.route('/blockchain/', methods=['GET'])
def print_blockchain():
    me.chain.print()
    return "Check stdout"

@app.route('/utxos/', methods=['GET'])
def print_utxos():
    for x in me.wallet.utxos:
        for y in me.wallet.utxos[x]:
            y.print_trans()
    return "Check stdout"

@app.route('/newblock/', methods=['POST'])
def get_block():
    print("BLOCK RECEIVED\n")
    qevent.set()
    blc_rcv.set()
    d = request.data
    b = jsonpickle.decode(d)  
    if not me.receive_block(b):    # diakladwsi
        for x in me.ring:
            if x == me.wallet.address: continue
            requests.post("http://" + me.ring[x][1] + '/send_chain/', data = ip + my_port)
    else:
        qevent.clear()
        queue = threading.Thread(target = queue_function, args=(p,qevent), daemon=True)
        queue.start()
    return "0"

@app.route('/send_chain/', methods=['POST'])
def send_chain():
    IP = request.data
    requests.post("http://" + IP.decode() + '/resolve/', 
                    data = jsonpickle.encode((me.chain, me.wallet.chain_utxos, me.chain_ring)))
    return "0"

@app.route('/resolve/', methods=['POST'])
def resolve():
    d = request.data
    (c, u, r) = jsonpickle.decode(d)
    me.choose_chain(c, u, r)
    qevent.clear()
    queue = threading.Thread(target = queue_function, args=(p,qevent), daemon=True)
    queue.start()
    return "0"

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    me = node.Node(ip + my_port)

    blc_rcv = threading.Event()
    qevent = threading.Event()
    q = []
    cli = threading.Thread(target = cli_function, args=(), daemon=True)
    cli.start()

    app.run(host=ip, port=port)