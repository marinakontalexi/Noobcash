import requests
from flask import Flask, jsonify, request
import threading
import block
import node
import blockchain
import transaction
import netifaces as ni
import jsonpickle

master_node = '192.168.2.1'
master_port = ":5000"
my_port = ":5000"
total = 2

ip = ni.ifaddresses("enp0s8")[ni.AF_INET][0]['addr']
# ip = socket.gethostbyname(socket.gethostname())
p = None
event = threading.Event()

app = Flask(__name__)
chain = blockchain.Blockchain()

def mine_function(event):
    # logging.info("Thread %s: starting", name)
    # time.sleep(2)
    # logging.info("Thread %s: finishing", name)
    while not me.mine_block():
        if event.is_set():
            return
    print("mine ok")
    for x in me.ring:
        if x == me.wallet.address: continue 
        requests.post("http://" + me.ring[x][1] + '/newblock/', data = jsonpickle.encode(me.broadcast_block()))


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
    # for x in ring:
    #     me.wallet.utxos[x] = []
    #     me.wallet.chain_utxos[x] = []
    me.ring = ring.copy()
    me.chain_ring = me.ring.copy()
    me.wallet.utxos = chain.init_utxos.copy()
    me.wallet.chain_utxos = chain.init_utxos.copy()
    me.get_initial_blockchain(chain)
    return "0"

@app.route('/register/', methods=['POST'])
def register():
    if me.current_id_count >= total:
        print("ERROR: All nodes are already registered!")
        return "1"
    dict = request.get_json()         
    pk = dict["public_key"]
    ip = dict["ip"]
    if pk in me.ring:
        if me.ring[pk][1] == ip:
            requests.post("http://" + ip + '/genesis/', data = jsonpickle.encode((me.chain_ring.copy(), me.chain)))
        else:
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
    if me.receive(t):
        p = threading.Thread(target = mine_function, args=(event,), daemon=True)
        p.start()
        return "block ok"
    else:
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
    event.set()
    d = request.data
    b = jsonpickle.decode(d)  
    if not me.receive_block(b):    # diakladwsi
        for x in me.ring:
            if x == me.wallet.address: continue
            requests.post("http://" + me.ring[x][1] + '/send_chain/', data = ip + my_port)
    else:
        event.clear()
    return "0"

@app.route('/send_chain/', methods=['POST'])
def send_chain():
    ip = request.data
    requests.post("http://" + ip.decode() + '/resolve/', 
                    data = jsonpickle.encode((me.chain, me.wallet.chain_utxos, me.chain_ring)))
    return "0"

@app.route('/resolve/', methods=['POST'])
def resolve():
    d = request.data
    (c, u, r) = jsonpickle.decode(d)
    me.choose_chain(c, u, r)
    event.clear()
    return "0"

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    me = node.Node(ip + my_port)
    app.run(host=ip, port=port)