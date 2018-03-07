from flask import Flask, jsonify, request
import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests


class Blockchain:
    def __init__(self):
        # 交易列表
        self.current_transactions = []
        # 区块链
        self.chain = []
        # 网络节点
        self.nodes = set()
        # 创世区块
        self.new_block(previous_hash='1', proof=100)


    def register_node(self, address):
        '''
        添加新的节点进入区块链网络，分布式的目的是去中心化
        :param address: 新节点网络地址，如：192.168.5.20:1314
        '''
        # urlparse解析url <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        parsed_url = urlparse(address)
        # 将新节点的url地址添加到节点中
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        '''
        检验区块链是否是合法的
        1.检查区块链是否连续
        2.检查工作量证明是否正常
        :param chain: 一份区块链
        :return: True 区块链合法，False 区块链非法
        '''
        last_block = chain[0] #创世区块
        current_index = 1

        # 循环检查每个区块
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n-----------\n')
            # 本区块存储的hash是否等于上一个区块通过hash函数计算出的hash，判断区块链是否连续
            if block['previous_hash'] != self.hash(last_block):
                return False
            # 验证工作量证明是否计算正确
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        '''
        共识算法，确保区块链网络中每个网络节点存储的区块链都是一致的，通过长区块链替换短区块链实现
        :return: True 替换 False不替换
        '''
        neighbours = self.nodes # 邻居节点
        new_chain = None
        # 我拥有区块链的长度
        max_length = len(self.chain)

        for node in neighbours:
            # 访问节点的一个接口，拿到该接口的区块链长度和区块链本身
            try:
                response = requests.get(f'http://{node}/chain')

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # 判断邻居节点发送过来的区块链长度是否最长且是否合法
                    if length > max_length and self.valid_chain(chain):
                        # 使用邻居节点的区块链
                        max_length = length
                        new_chain = chain
            except:
                # 节点没开机
                pass
        if new_chain:
            self.chain = new_chain
            return True
        return False


    def new_block(self, proof, previous_hash):
        '''
        创建一个新区块加入到区块链中
        :param proof: 工作量证明
        :param previous_hash: 上一个区块的hash
        :return: 一个新区块
        '''

        # 区块
        block = {
            # 索引
            'index':len(self.chain) + 1,
            # 时间戳
            'timestamp': time(),
            # 交易账本
            'transactions':self.current_transactions,
            # 工作量证明
            'proof':proof,
            # 上一块区块的hash
            'previous_hash':previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        # 将区块添加到区块链中，此时交易账本是空，工作量证明是空
        self.chain.append(block)
        return block


    def new_transaction(self, sender, recipient, amount):
        '''
        创建一个新的交易，添加到我创建的下一个区块中
        :param sender: 发送者地址，发送数字币的地址
        :param recipient: 接受者地址，接受数字币的地址
        :param amount: 数字币数量
        :return: 记录本次交易的区块索引
        '''
        # 交易账本，可包含多个交易
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        # 交易账本添加到最新的区块中
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        '''
        :return: 区块链中最后一个区块
        '''
        return self.chain[-1]

    @staticmethod
    def hash(block):
        '''
        使用SHA256哈希算法计算区块的哈希
        :param block: 区块
        :return: 区块hash
        '''
        # sort_keys()：json解析后获得的字典将通过key排序，encode()进行utf-8编码，不然hashlib加密会报错
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        '''
        简单的工作量证明算法
        找到一个数，使得区块的hash前4位为0
        :param last_proof 上一个区块的工作量证明
        :return: 特殊的数
        '''

        # 工作量证明--->穷举法计算出特殊的数
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        '''
        验证工作量证明，计算出的hash是否正确
        对上一个区块的proof和hash与当期区块的proof最sha256运算
        :param last_proof: 上一个区块的工作量
        :param proof: 当前区块的工作量
        :param last_hash: 上一个区块的hash
        :return: True 工作量是正确的 False 错误
        '''
        # f-string pyton3.6新的格式化字符串函数
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)

# 通过uuid4()基于伪随机数生成区块链网络唯一的ID
node_identifier = str(uuid4()).replace('-','')
# 实例化区块链
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    '''
    建立新区块
    :return:
    '''
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    # 挖矿获得一个数字货币奖励，将奖励的交易记录添加到账本中，其他的交易记录通过new_transaction接口添加
    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message':'新区块建立',
        'index':block['index'],
        'transactions':block['transactions'],
        'proof':block['proof'],
        'previous_hash':block['previous_hash'],
    }

    return jsonify(response),200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    '''
    将新的交易添加到最新的区块中
    :return:
    '''
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return '缺失必要字段',400

    index = blockchain.new_transaction(values['sender'], values['recipient'],values['amount'])
    response = {'message':f'交易账本被添加到新的区块中{index}'}
    return jsonify(response),201

@app.route('/chain', methods=['GET'])
def full_chain():
    '''
    获得完整的区块链
    :return: 整份区块链
    '''
    response = {
        'chain':blockchain.chain,
        'length':len(blockchain.chain),
    }
    return jsonify(response),200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error:提供有效节点列表',400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': '新节点加入区块链网络',
        'total_nodes':list(blockchain.nodes),
    }
    return jsonify(response),201

@app.route('/node/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message':'本节点区块链被替换',
            'new_chain':blockchain.chain
        }
    else:
        response={
            'message':'本节点区块链是权威的(区块链网络中最长的)',
            'chain':blockchain.chain
        }
    return  jsonify(response),200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p','--port', default=5000, type=int, help='服务启动时对应的端口')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
