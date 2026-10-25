from bitcoin.core.script import *

from utils import *
from config import (my_private_key, my_public_key, my_address,
                    faucet_address)


def P2PKH_scriptPubKey(address):
    ######################################################################
    # TODO: Complete the standard scriptPubKey implementation for a
    # PayToPublicKeyHash transaction
    ######################################################################
    # script_address 基于给定的 bitcoin 地址生成一段脚本，
    # 原始字节为：76 a9 14 <20 字节公钥哈希> 88 ac
    script_address = address.to_scriptPubKey()

    # 掐头去尾（去掉开头的 76 a9 14 和结尾的 88 ac），
    # 提取出中间那 20 字节的公钥哈希
    temp_hash_value = script_address[3:-2]

    Script_PubKey = [
        OP_DUP,            # 复制堆栈顶端数据
        OP_HASH160,        # 计算 hash 函数两次，第一次用 SHA-256，第二次用 RIPEMD-160
        temp_hash_value,   # 前面计算出来的公钥哈希值
        OP_EQUALVERIFY,    # 检查栈顶两个元素是否相等（公钥哈希是否匹配）
        OP_CHECKSIG        # 检查栈顶元素是否是有效签名
    ]
    return Script_PubKey
    ######################################################################


def P2PKH_scriptSig(txin, txout, txin_scriptPubKey):
    # 用私钥对「这笔交易 + 该输入所引用的 scriptPubKey」签名，
    # 得到 <签名>（末尾已附带 SIGHASH_ALL 标志字节）
    signature = create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey,
                                             my_private_key)
    ######################################################################
    # TODO: Complete this script to unlock the BTC that was sent to you
    # in the PayToPublicKeyHash transaction. You may need to use variables
    # that are globally defined.
    ######################################################################
    Script_Sig = [
        signature,       # 用私钥签出来的签名
        my_public_key    # 自己的公钥（其哈希要与 scriptPubKey 里的哈希一致）
    ]
    return Script_Sig
    ######################################################################


def send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index,
                                txout_scriptPubKey):
    txout = create_txout(amount_to_send, txout_scriptPubKey)

    txin_scriptPubKey = P2PKH_scriptPubKey(my_address)
    txin = create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey)

    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)

    return broadcast_transaction(new_tx)


if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    #
    # 需要你根据自己的链上数据填写的三个参数：
    #   txid_to_spend : 你要花费的那笔交易的哈希(txid)
    #   utxo_index    : 该交易里属于「你的地址」的那个输出下标（从 0 开始）
    #   amount_to_send: 发回给 faucet 的金额(BTC)，必须小于该输出金额，
    #                   差额留给矿工作为手续费
    #
    # 你已经用 split_test_coins.py 把 faucet 的 0.00113807 BTC 拆成了：
    #   txid = a94c1641cd0311ed2b6e33599829a128f597774e71dedb71bfe2e1699878ccb9
    #   10 个输出，每个 10000 sat(0.0001 BTC)，输出的下标是 0~9
    # 练习1 就花其中 0 号输出：留 1000 sat 手续费，实发 9000 sat。
    # （以后做 Ex2/Ex3 时把 utxo_index 依次改成 1、2 即可，每个输出用一次）
    ######################################################################
    txid_to_spend = (
        'a94c1641cd0311ed2b6e33599829a128f597774e71dedb71bfe2e1699878ccb9')
    utxo_index = 0
    amount_to_send = 0.00009  # 实发 9000 sat，手续费 1000 sat
    ######################################################################

    txout_scriptPubKey = P2PKH_scriptPubKey(faucet_address)
    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index, txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
