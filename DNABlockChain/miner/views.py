from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import hashlib
import json
from time import time
from uuid import uuid4


class Blockchain:
    def __init__(self):

        self.chain =[]
        self.current_transactions = []
        self.new_block(previous_hash = 1, proof = 100) # 創世區塊
        self.nodes = set()

    def new_block(self,proof,previous_hash=None):

        block ={
            'index':len(self.chain)+1,
            'timestamp': time(),
            'transactions':self.current_transactions,
            'proof':proof,
            'prevoius_hash':previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions =[]
        self.chain.append(block)
        return block


    def new_transaction(self,sender,recipient,amount):

        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount,
        })
        return self.last_block['index']+1


    @staticmethod
    def hash(block):
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property # call return xxx
    def last_block(self):
        return self.chain[-1]





    def proof_work(self,last_proof):
        proof =0
        while self.valid_proof(last_proof,proof) is False:
            proof = proof+1
        return proof


    @staticmethod
    def valid_proof(last_proof,proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[0:4] == '0000'



#########  #########




node_identifier = str(uuid4()).replace('-','')

# Instantiate the Blockchain

blockchain = Blockchain()


@csrf_exempt
def new_transaction(request):
    values = json.loads(request.body.decode('utf8'))
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing Values'

    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    print(index)

    response  ={'message': 'Transaction will be added to Block %s'%index}

    return HttpResponse(json.dumps(response))


@csrf_exempt
def mine(request):

    last_block = blockchain.last_block
    last_proof = last_block['proof']

    proof = blockchain.proof_work(last_proof)
    print(proof)

    blockchain.new_transaction(
        sender ='0',
        recipient= node_identifier,
        amount=1,
    )

    block = blockchain.new_block(proof)
    response = {
        'message':'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof':block['proof'],
        'previous_hash': block['prevoius_hash'],
    }
    print(response)

    return HttpResponse(json.dumps(response))


@csrf_exempt
def full_chain(request):
    response ={
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return HttpResponse(json.dumps(response))