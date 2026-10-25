from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction


######################################################################
# TODO: Complete the scriptPubKey implementation for Exercise 3
#
# 学号 2412483：前 3 位 S = 241，后 4 位 D = 2483。
# 两者奇偶性相同（都是奇数），线性方程组
#     x + y = 241
#     x - y = 2483
# 存在整数解：x = (241+2483)/2 = 1362，y = (241-2483)/2 = -1121。
#
# scriptSig 只需要压入 x、y 两个整数，因此 scriptPubKey 必须先用
# OP_2DUP 复制一份，才能同时完成「加法」和「减法」两次校验：
#   <x> <y> OP_2DUP OP_ADD <241> OP_EQUALVERIFY OP_SUB <2483> OP_EQUAL
ex3a_txout_scriptPubKey = [
    OP_2DUP,          # 复制栈顶两个数：[x, y] -> [x, y, x, y]
    OP_ADD,           # 弹出两个 y、x 相加：[x, y, x+y]
    241,              # 压入 241
    OP_EQUALVERIFY,   # 校验 x+y == 241
    OP_SUB,           # 弹出 y、x 相减：[x-y]
    2483,             # 压入 2483
    OP_EQUAL          # 校验 x-y == 2483
]
######################################################################

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    # 花费 Ex1 分币交易的 2 号输出（0、1 号已分别在 Ex1、Ex2a 用过），
    # 该输出为 10000 sat；这里实发 9000 sat，差额 1000 sat 作为手续费。
    amount_to_send = 0.00009
    txid_to_spend = (
        'a94c1641cd0311ed2b6e33599829a128f597774e71dedb71bfe2e1699878ccb9')
    utxo_index = 2
    ######################################################################

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex3a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
