import json
from hashlib import sha256
from time import time, sleep
from datetime import datetime


file = "blockchain.json"


def readChain():
    with open(file, encoding="utf-8") as read:
        return json.loads(read.read())
        

def insertChain(new):
    chain = readChain()
    chain["blocks"].append(new)
    with open(file, "w") as write:
        json.dump(chain, write, indent=4)
        
        
def readTransection():
    with open(file, encoding="utf-8") as read:
        return json.loads(read.read())
        

def insertTransection(new):
    tx = readChain()
    tx["transections"].append(new)
    with open(file, "w") as write:
        json.dump(tx, write, indent=4)



class Blockchain:
    
    Index, Nonce, Difficulty, Hash, PrevHash, Timestamp = 1, None, 4, None, None, int(time())
    
    def __init__(self):
        if len(readChain()["blocks"]) == 0:
            first = {
                "index": self.Index,
                "nonce": self.Nonce,
                "difficulty": self.Difficulty,
                "timestamp": self.Timestamp,
                "prev_hash": self.PrevHash
            }
            first["data"] = [ { "message": "Hello World!"} ]
            first["hash"] = self.SHA256(first)
            self.newBlock(first)
     
    def lastBlock(self):
        return readChain()["blocks"][-1]
        
    def newBlock(self, new):
        insertChain(new)

    def SHA256(self, data):
        return sha256(json.dumps(data, sort_keys=True).encode('ascii')).hexdigest()
    
    

class Transections(Blockchain):
    
    def _lastTx(self):
        return readTransection()["transections"][-1]


    def confirmations(self, tx):
        alltx = readTransection()["transections"]
        for i in range(len(alltx)):
            if alltx[i]["txid"] == tx["txid"]:
                alltx[i]["confirmations"] += 1
                alltx[i]["data"]["index"] = tx["data"]["index"]
                alltx[i]["data"]["nonce"] = tx["data"]["nonce"]
                alltx[i]["data"]["difficulty"] = tx["data"]["difficulty"]
                break
        rtx = readChain()
        rtx["transections"] = alltx
        with open(file, "w") as write:
            json.dump(rtx, write, indent=4)
                
        
    
    def createTransection(self, **kwargs):
        if len(readTransection()["transections"]) == 0:
            data = {
                "txid": 1,
                "confirmations": 0,
                "data": {
                    "index": None,
                    "nonce": None,
                    "difficulty": None,
                    "timestamp": int(time()),
                    "prev_hash": self.lastBlock()["hash"],
                    "data": "First transection"
                }
            }
            insertTransection(data)
            return
        data = {
            "txid": self._lastTx()["txid"]+1,
            "confirmations": 0,
            "data": {
                "index": None,
                "nonce": None,
                "difficulty": None,
                "timestamp": int(time()),
                "prev_hash": self.lastBlock()["hash"],
                "data": kwargs
            }
        }
        insertTransection(data)
        return

# tx = Transections()
# for i in range(19):
#     tx.createTransection(sender = "man", reciver="phumin", detail={ "total": 500 })



class Miner(Blockchain):
    
    COMFIRMATIONS = 1

    
    def _validateHash(self, hashs):
        for i in range(self.Difficulty):
            if hashs[i] != "0":
                return False
        return True
    
    def _poof(self, tx):
        tx["data"]["index"] = self.lastBlock()["index"]+1
        tx["data"]["difficulty"] = self.Difficulty
        tx["data"]["nonce"] = 0
        block = tx["data"]
        while True:
            hashs = self.SHA256(block)
            if self._validateHash(hashs):
                block["hash"] = hashs
                self.newBlock(block)
                Transections().confirmations(tx)
                print("[{}] Approved [ Hash: {} ]".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), hashs))
                break
            else:
                # print("[{}]: Rejected '{}'".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), hashs))
                pass
            block["nonce"] += 1
    
    def job(self):
        tx = readTransection()["transections"]
        for i in tx:
            if i["confirmations"] < self.COMFIRMATIONS:
                print("[{}] New Job [ TXID: {} ]".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), i["txid"]))
                self._poof(i)
                break # test

                    
    
    def run(self):
        self.job()
        
while True:
    Miner().run()
    sleep(10)