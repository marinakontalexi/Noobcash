import transaction
import node
import wallet

n1 = node.Node()
n2 = node.Node()
ring = n1.register_node_to_ring(n2.wallet.address, -2)
n2.ring = {}
for x in ring:
    n2.ring[x] = ring[x].copy()

n1.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 200))
n2.wallet.utxos.append(transaction.TransactionIO(5, n1.wallet.public_key, 200))

n1.create_transaction(n2.wallet.public_key, 100)
n1.receive()
n2.receive()
node.log.pop()

n1.create_transaction(n2.wallet.public_key, 30)
n1.receive()
n2.receive()
print(n1.wallet.balance())
print("\n")
print(n2.wallet.balance())

for x in n1.ring:
    print(n2.ring[x])