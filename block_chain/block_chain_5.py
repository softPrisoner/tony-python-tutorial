#!/usr/bin/python
# -*- coding:utf-8 -*-
import hashlib as hasher
from time import time
import json
from flask import Flask, jsonify, render_template
from argparse import ArgumentParser
import requests
blockchain = []
nodes = []
# add node


def add_node(node):
    nodes.append(node)


# 返回自身区块链高度
# return the lenght of blockchain
def get_height():
    last_block = blockchain[len(blockchain)-1]
    last_block_index = last_block["index"]
    return last_block_index

# hash for next data code be better


def hash(index, data, timestamp, previous_hash):
    sha = hasher.sha256()
    sha.update("{0}{1}{2}{3}".format(
        index, data, timestamp, previous_hash).encode("utf8"))
    return sha.hexdigest()

# create a block to append the latest roar list


def make_a_block(index, timestamp, data, previous_hash):
    block = {}
    block["index"] = index
    block["timestamp"] = timestamp
    block["data"] = data
    block["previous_hash"] = previous_hash
    block["hash"] = hash(index, data, timestamp, previous_hash)
    return block


def add_a_block(data):

    last_block = blockchain[len(blockchain)-1]


# this is index for block
    index = last_block["index"]+1
    timestamp = int(round(time() * 1000))
    previous_hash = last_block["hash"]

# append  the block in the list roar
    blockchain.append(make_a_block(index, timestamp, data, previous_hash))


def make_a_genesis_block():
    index = 0
    timestamp = int(round(time() * 1000))
    data = "Genesis Block"
    previous_hash = 0

# with blockchain  append
    blockchain.append(make_a_block(index, timestamp, data, previous_hash))


# flask info
app = Flask(__name__)


@app.route('/')
def home():
    # this is the index of data
    return render_template('index.html')

# 信息上链
@app.route('/say/<string:msg>', methods=['GET'])
def add_block(msg):
    add_a_block(msg)
    #jsonify the data
    return jsonify(blockchain)


@app.route('/blocks/last', methods=['GET'])
def get_last_block():
    last_block = blockchain[len(blockchain)-1]
    return jsonify(last_block)


@app.route('/blocks/<int:index>', methods=['GET'])
def get_block(index):
    if(len(blockchain) >= index):
        block = blockchain[index]
        return jsonify(block)
    else:
        return jsonify({"error": "noindex"})


@app.route('/blocks/<int:from_index>/<int:to_index>', methods=['GET'])
def get_block_from_to(from_index, to_index):
    blocks = []
    if(len(blockchain) > from_index and len(blockchain) > to_index and to_index >= from_index):
        for i in range(from_index, to_index+1):
            block = blockchain[i]
            blocks.append(block)
        return jsonify(blocks)
    else:
        return jsonify({"error": "noindex"})


@app.route('/blocks/all', methods=['GET'])
def get_all_block():
    return jsonify(blockchain)

# 查看区块链高度
@app.route('/blocks/height', methods=['GET'])
def get_block_height():
    last_block = blockchain[len(blockchain)-1]
    return jsonify(last_block["index"])

# 查看节点
@app.route('/nodes', methods=['GET'])
def get_get_nodes():
    return jsonify(nodes)

# 添加节点
@app.route('/nodes/add/<string:ip>/<int:port>', methods=['GET'])
def add_nodes(ip, port):
    node = {"ip": ip, "port": port}
    # 确保不重复添加
    if node not in nodes:
        nodes.append(node)
    return jsonify(nodes)

# 同步区块
@app.route('/blocks/sync', methods=['GET'])
def blocks_sync():
    json = []
    for node in nodes:
        ip = node["ip"]
        port = node["port"]
        url_height = "http://{0}:{1}/blocks/height".format(ip, port)
        url_all = "http://{0}:{1}/blocks/all".format(ip, port)
        # 尝试去同步
        try:
            # 尝试获得对方高度
            r_height = requests.get(url_height)
            height = int(r_height.json())
            self_index = get_height()

            # 如果对方的比自己的大
            if height > self_index:
                r_blocks_all = requests.get(url_all)
                blocks = r_blocks_all.json()

                # 把对方的blockchain赋值自己的blokchain
                # 这里有个问题，即区块链没有进行验证，以后会补上。
                blockchain.clear()
                for block in blocks:
                    blockchain.append(block)
                return jsonify("synced")
            else:
                # 不同步
                return jsonify("no synced")

        except:
            return jsonify("error")
    return jsonify("no nodes")


if __name__ == '__main__':
    make_a_genesis_block()
    add_a_block("hello")
    add_a_block("hi~")
    add_a_block("~")

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(debug=True, host='0.0.0.0', port=port)
