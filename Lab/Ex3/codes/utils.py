import json
import socket

import requests

from bitcoin.core import b2x, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import *
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH


def send_from_custom_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        txin_scriptPubKey, txin_scriptSig, txout_scriptPubKey):
    txout = create_txout(amount_to_send, txout_scriptPubKey)
    txin = create_txin(txid_to_spend, utxo_index)
    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)
    return broadcast_transaction(new_tx)


def create_txin(txid, utxo_index):
    return CMutableTxIn(COutPoint(lx(txid), utxo_index))


def create_txout(amount, scriptPubKey):
    return CMutableTxOut(amount*COIN, CScript(scriptPubKey))


def create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey, seckey):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx,
                            0, SIGHASH_ALL)
    sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
    return sig


def create_signed_transaction(txin, txout, txin_scriptPubKey,
                              txin_scriptSig):
    tx = CMutableTransaction([txin], [txout])
    txin.scriptSig = CScript(txin_scriptSig)
    VerifyScript(txin.scriptSig, CScript(txin_scriptPubKey),
                 tx, 0, (SCRIPT_VERIFY_P2SH,))
    return tx


class _BroadcastResponse(object):
    """把 ElectrumX 的广播结果包装成和 requests.Response 一样可打印的对象。"""

    def __init__(self, txid):
        self.status_code = 200
        self.reason = 'OK (ElectrumX)'
        self.text = txid


def broadcast_via_electrum(raw_transaction):
    # Ex3 的锁定脚本（OP_ADD/OP_SUB）属于非标准脚本，mempool.space、
    # blockstream.info 这类开启标准性检查(testmempoolpolicy)的节点会直接
    # 拒收并报 -26 scriptpubkey。testnet3 的默认策略允许非标准交易，
    # 因此改用一个运行默认策略节点的 ElectrumX 服务器来广播。
    with socket.create_connection(('testnet.qtornado.com', 51001),
                                  timeout=30) as sock:
        stream = sock.makefile('rwb')

        def call(payload):
            stream.write((json.dumps(payload) + '\n').encode())
            stream.flush()
            return json.loads(stream.readline().decode())

        call({'id': 1, 'method': 'server.version',
              'params': ['trae', ['1.4', '1.4.2']]})
        resp = call({'id': 2, 'method': 'blockchain.transaction.broadcast',
                     'params': [raw_transaction]})
        if 'result' in resp:
            return _BroadcastResponse(resp['result'])
        raise RuntimeError('ElectrumX 广播失败: %s' % resp.get('error'))


def broadcast_transaction(tx):
    raw_transaction = b2x(tx.serialize())
    # ------------------------------------------------------------------
    # 原代码使用的 BlockCypher test3 节点早已停止同步：它的链高度一直卡在
    # 2023-07-05 的 2440465（而真实 testnet3 现在已到 5151360），
    # 所以向它广播会返回 400 "orphaned, missing reference <父交易>"。
    # 这里改为把「原始交易十六进制」POST 给仍在正常同步的 testnet3 公共接口，
    # 按顺序尝试，第一个成功(200)的直接返回；全部失败则改走 ElectrumX。
    # 成功时接口返回该交易的 txid（纯文本）。
    # ------------------------------------------------------------------
    headers = {'content-type': 'text/plain'}
    endpoints = [
        'https://mempool.space/testnet/api/tx',
        'https://blockstream.info/testnet/api/tx',
    ]
    response = None
    for url in endpoints:
        response = requests.post(url, headers=headers, data=raw_transaction)
        if response.status_code == 200:
            return response
        print('[broadcast] %s 失败: %s %s' %
              (url, response.status_code, response.text[:200]))
    print('[broadcast] 改用 testnet.qtornado.com 的 ElectrumX 广播')
    return broadcast_via_electrum(raw_transaction)
