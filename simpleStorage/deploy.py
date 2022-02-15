from solcx import compile_standard
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    # comple soldidity

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
    )

    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

# get bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# print(bytecode)

# get abi

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# print(abi)

# connecting to rinkeby

w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/03a662dc23934445be7ee4ec040d8d4e")
)
chain_id = 4
my_address = "0x8a55D95fFB23178eA227D5c2b2af32D4aa92041D"
private_key = os.getenv("PRIVATE_KEY")
# "0x315737c573a3bca950ecbb5e8e573bbc025cab228528ab33a3a43d36e97e19ca"

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# launching confirmation - <class 'web3._utils.datatypes.Contract'>
print(SimpleStorage)

# get latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce) - should return 0. since it's the first transaction

# 1. build a transaction
# 2. sign transaction
# 3. send transaction

transaction = SimpleStorage.constructor().buildTransaction(
    {
        ## gas price needed to be explicit in order to execute
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# print(signed_txn)
# shows transaction hash
print("Deploying contract....")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract deployed!")

# working with contract, we always need:
# Contract Address
# Contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> reading and getting return value, on state change
# Transact -> changing state adding to the block chain.

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Contract Updated!")
print(simple_storage.functions.retrieve().call())


# create transaction, signed transaction, send transaction, and wait for transaction to complete with receipt ^
