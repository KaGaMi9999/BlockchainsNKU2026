from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import P2PKH_scriptPubKey
from ex3a import ex3a_txout_scriptPubKey


######################################################################
# TODO: set these parameters correctly
# 花费 ex3a 锁仓交易的唯一输出（9000 sat），实发 8000 sat，
# 差额 1000 sat 作为手续费。
amount_to_send = 0.00008
txid_to_spend = '6dabaec94b8fadfcf13914e3db4da69c9bb3332a14b85cd987630ebf2f28409b'
utxo_index = 0
######################################################################

txin_scriptPubKey = ex3a_txout_scriptPubKey
######################################################################
# TODO: implement the scriptSig for redeeming the transaction created
# in  Exercise 3a.
#
# 方程组的解：x = 1362，y = -1121。
# scriptSig 只需把这两个整数压栈，其余运算全部由 scriptPubKey 完成，
# 这样解锁脚本就是最小的。
txin_scriptSig = [1362, -1121]
######################################################################
txout_scriptPubKey = P2PKH_scriptPubKey(faucet_address)

response = send_from_custom_transaction(
    amount_to_send, txid_to_spend, utxo_index,
    txin_scriptPubKey, txin_scriptSig, txout_scriptPubKey)
print(response.status_code, response.reason)
print(response.text)
