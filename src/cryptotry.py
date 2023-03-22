from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA


# Generate a new RSA key pair with the specified key length
key_length = 1024
key = RSA.generate(key_length)

# Get the RSA keys
private_key = key.export_key()
public_key = key.publickey().export_key()

msg = b"The aliens are coming!"
hash = SHA256.new(msg)

# Generate the signature
signer = pkcs1_15.new(RSA.import_key(private_key))
signature = signer.sign(hash)

verifier = pkcs1_15.new(RSA.import_key(public_key))

#Exception will be thrown if verification fails
verifier.verify(hash, signature)