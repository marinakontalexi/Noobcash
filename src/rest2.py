import requests
from flask import Flask, request
import threading
import block
import node2
import blockchain
import transaction2
import netifaces as ni
import socket
import jsonpickle
import time
from random import randint
from termcolor import colored
from numpy import average

master_node = '10.0.0.1'
master_port = ":5000"
my_port = ":5000"
total = 5
project_path = "../"
color_cli = "green"
color_buffer = "yellow"
color_miner = "light_blue"
color_time = "dark_grey"

ip = ni.ifaddresses("eth1")[ni.AF_INET][0]['addr']
# ip = socket.gethostbyname(socket.gethostname())

app = Flask(__name__)
chain = blockchain.Blockchain()

def queue_function(stop_event, die_event):
    # print(colored("Buffer is active",color_buffer))
    l = s = time.time()
    while True:
        if die_event.is_set():
            # print(colored("Buffer exits",color_buffer))
            return
        if time.time() - s > 5:
            print(colored("Length of queue " + str(len(q)), color_time))
            s = time.time()
        if len(q) == 0: continue
        if len(me.currentBlock.listOfTransactions) < block.capacity:                
            print(colored("Block is not full", color_buffer))   
            if len(q) != 0: 
                t = q.pop(0)  
                if me.receive(t):         
                    me.add_transaction_to_block(t)
                    print(colored("T was added to block. Block size is " + str(len(me.currentBlock.listOfTransactions)), color_buffer))
                if len(me.currentBlock.listOfTransactions) == block.capacity:                
                    print(colored("Block is full!", color_buffer))
                    print(colored("Mining starts...", color_miner))
                    while not me.mine_block():
                        if time.time() - l > 10:
                            print(colored("mining...", color_time))
                            l = time.time()
                        if stop_event.is_set(): print(colored("I stop mining", color_miner))
                        while stop_event.is_set():
                            if die_event.is_set(): 
                                print(colored("Buffer exits",color_buffer))
                                return
                    print(colored("Mining succeeded", color_miner))
                    newblock = me.broadcast_block()
                    for x in me.ring:
                        if x == me.wallet.address: continue 
                        requests.post("http://" + me.ring[x][1] + '/newblock/', data = jsonpickle.encode(newblock))  

def cli_function(me):
    if ip != master_node:   
        time.sleep(10)      # wait untill master_node is up
        requests.get("http://" + ip  + my_port + "/login/")
    queue = threading.Thread(target = queue_function, args=(stop, die,), daemon=True)
    queue.start()
    time.sleep(100)          # wait until you start making t from file
    while(me.ring[me.wallet.address][2] < 100): continue
    if (args.auto):
        id = (args.n // 5 + 1)  * me.ring[me.wallet.address][0] + (args.p)%2
        f = open(project_path + "5nodes/transactions{}.txt".format(id), "r")
        s = f.readline()
        t = time.time()
        log = 0
        while s != "":
            if log == 20: break            
            [r, amount] = s.split()
            rcv = r[2:]
            if int(rcv) >= total: 
                s = f.readline()
                continue
            print(colored("Posting transaction: " + s, color_cli))
            requests.get("http://" + ip  + my_port + "/t?to=" + rcv + '&amount=' + amount)
            log += 1
            sleep = randint(sleep, sleep+5)
            time.sleep(sleep)
            s = f.readline()
        print(colored("I posted " + str(log) + " transactions", color_cli))
        requests.post("http://" + ip  + my_port + "/throughput/", data = jsonpickle.encode(t))
    if queue.is_alive(): queue.join()
    
#.......................................................................................


@app.route('/', methods=['GET'])
def get_transactions():
    return "Hello World!"

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
        transaction2.addresses[x] = str(ring[x][0])
        me.ring[x] = []
        for i in range(3):
            me.ring[x].append(ring[x][i])
        me.wallet.utxos[x] = []
        for t in chain.init_utxos[x]:
            me.wallet.utxos[x].append(t)
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
            requests.post("http://" + IP + '/genesis/', data = jsonpickle.encode((me.ring.copy(), me.chain)))
        else:
            print("ERROR: Public key already registered")
            requests.post("http://" + IP + '/login/')
        return "1"
        
    me.register_node_to_ring(pk, IP)

    if me.current_id_count == total - 1:
        init_t = transaction2.Transaction(b'0', me.wallet.address, 100*total, b'0', [])
        init_B = block.Block("1")
        init_B.add_transaction(init_t)
        init_B.myhash = init_B.hash()
        chain.add_block(init_B)
        for x in init_t.transaction_outputs:
            me.wallet.utxos[x.address] = [x]
        me.currentBlock = block.Block(chain.lasthash)
        me.chain = chain.copy()
        me.chain.init_utxos = me.wallet.utxos.copy()
        for x in me.ring:
            transaction2.addresses[x] = str(me.ring[x][0])
            if me.ring[x][0] == 0: continue
            requests.post("http://" + me.ring[x][1] + '/genesis/', data = jsonpickle.encode((me.ring, me.chain)))
        time.sleep(20)      # wait until all nodes are initialized
        for x in me.ring:
            if me.ring[x][0] == 0: continue
            t = me.create_transaction(me.ring[x][0], 100)
            for y in me.ring:
                requests.post("http://" + me.ring[y][1] + '/broadcast/', data = jsonpickle.encode(t))
            time.sleep(10)
    return "0"

@app.route('/ring/', methods=['GET'])
def show_ring():
    acc = {}
    for x in me.ring:
        d = {}
        d["IP Address"] = me.ring[x][1]
        d["Balance"] = me.ring[x][2]
        acc[me.ring[x][0]] = d
    return acc

@app.route('/current/', methods=['GET'])
def show_current_block():
    return me.currentBlock.print()

@app.route('/t', methods=['GET'])
def make_transaction():
    if request.remote_addr != ip: 
        print("You cannot make a transaction for someone else!")
        return "1" 
    args = request.args
    receiver = int(args.get('to'))
    amount = int(args.get('amount'))
    for i in range(3):
        t = me.create_transaction(receiver, amount)
        if t != None: break
    if t == None: 
        return "Invalid transaction"
    for x in me.ring:
        requests.post("http://" + me.ring[x][1] + '/broadcast/', data = jsonpickle.encode(t))
    return t.print_trans()

@app.route('/broadcast/', methods=['POST'])
def get_transaction():
    print("TRANSACTION RECEIVED")
    d = request.data
    t = jsonpickle.decode(d)
    q.append(t)
    print("I pushed a transaction")
    return "0"
            

@app.route('/balance/', methods=['GET'])
def get_balance():
    return str(me.wallet.balance())

@app.route('/view/', methods=['GET'])
def get_view():
    s = len(me.chain.listOfBlocks)
    return me.chain.listOfBlocks[s-1].print()

@app.route('/blockchain/', methods=['GET'])
def print_blockchain():
    return me.chain.print()

@app.route('/utxos/', methods=['GET'])
def print_utxos():
    acc = {}
    for x in me.wallet.utxos:
        acc2 = {}
        for i in range(len(me.wallet.utxos[x])):
            acc2["UTXO" + str(i)] = me.wallet.utxos[x][i].print_trans()
        acc[transaction2.addresses[x]] = acc2
    return acc

@app.route('/newblock/', methods=['POST'])
def get_block():
    print("BLOCK RECEIVED")
    stop.set()
    d = request.data
    b = jsonpickle.decode(d)  
    if not me.receive_block(b):    # diakladwsi
        for x in me.ring:
            if x == me.wallet.address: continue
            requests.post("http://" + me.ring[x][1] + '/send_chain/', data = ip + my_port)
    else:
        die.set()
        time.sleep(3) 
        die.clear()
        stop.clear() 
        queue = threading.Thread(target = queue_function, args=(stop, die,), daemon=True)
        queue.start()
    return "0"

@app.route('/send_chain/', methods=['POST'])
def send_chain():
    IP = request.data
    requests.post("http://" + IP.decode() + '/resolve/', 
                    data = jsonpickle.encode((me.chain, me.currentBlock, me.wallet.utxos, me.ring)))     
    return "0"

@app.route('/resolve/', methods=['POST'])
def resolve():
    d = request.data
    (c, b, u, r) = jsonpickle.decode(d)
    if me.choose_chain(c, b, u, r): 
        stop.clear()
        return "1"
    die.set()
    time.sleep(3)
    die.clear()
    stop.clear()
    queue = threading.Thread(target = queue_function, args=(stop, die,), daemon=True)
    queue.start()
    return "0"

@app.route('/throughput/', methods=['POST'])
def get_time():
    me.start_time = jsonpickle.decode(request.data)
    return "0"

@app.route('/throughput/', methods=['GET'])
def find_throughput():
    if me.start_time == 0: print("Something went wrong")
    t = time.time()
    numOfTrans = (len(me.chain.listOfBlocks)-1)*block.capacity - total + 1
    res = {}
    res["Valid Transactions"] = numOfTrans
    res["Total Transactions"] = total*20
    res["Total Time"] = t - me.start_time
    res["Throughput"] = numOfTrans / (t - me.start_time)
    return res

@app.route('/avg/', methods=['GET'])
def show_average():
    me.avg.pop(0)       # first blocks take much longer due to synchronization
    return {"Average Block Time" : average(me.avg)}

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', default=5000, type=int, help='port to listen on')
    parser.add_argument("-ip", default=ip, help="IP of the host")
    parser.add_argument("-diff", default=3, type=int, help="Mining difficulty")
    parser.add_argument("-cap", default=3, type=int, help="Block capacity")
    parser.add_argument("-n", default=5, type=int, help="Number of nodes")
    parser.add_argument("-w", default=1, help="Wait time")
    parser.add_argument("--auto", default=False, action="store_true", help="Automatic transaction making")

    args = parser.parse_args()
    ip = args.ip
    port = args.p
    blockchain.MINING_DIFFICULTY = args.diff
    block.capacity = args.cap
    total = args.n
    sleep = args.w

    my_port = ":" + str(port)
    me = node2.Node(ip + my_port)
    
    queue = None
    stop = threading.Event()
    die = threading.Event()
    q = []
    cli = threading.Thread(target = cli_function, args=(me,), daemon=True)
    cli.start()
    
    app.run(host=ip, port=port)

    cli.join()