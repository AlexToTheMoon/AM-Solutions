import argparse
from urllib.request import urlopen, Request
import json

PRUNING = 50000

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

POST_HEADERS = {
    'Content-Type': 'application/json'
}
POST_HEADERS.update(HEADERS)

MAINNET = {
    'chain-id': "axelar-dojo-1",
    'tx-indexing': 'on',
}

TESTNET = {
    'chain-id': "axelar-testnet-lisbon-3",
    'tx-indexing': 'on',
}


def test_rest_earliest_block(base_url, test_values):
    rest_url = f'{base_url}/cosmos/base/tendermint/v1beta1/blocks/latest'
    httprequest = Request(rest_url, headers=HEADERS)
    try:
        with urlopen(httprequest) as response:
            if response.status != 200:
                print('ERROR: Pruning verification: failed getting latest block from rest api')
                return
            info = response.read().decode()
            latest_block = json.loads(info)
    except Exception as ex:
        print(f'ERROR: failed getting /cosmos/base/tendermint/v1beta1/blocks/latest from rest api: {ex}')
        return

    height = int(latest_block['block']['header']['height'])
    earliest = height - PRUNING
    rest_url = f'{base_url}/cosmos/base/tendermint/v1beta1/blocks/{earliest}'
    httprequest = Request(rest_url, headers=HEADERS)
    try:
        with urlopen(httprequest) as response:
            if response.status != 200:
                print('ERROR: Pruning verification: failed getting earliest block from rest api')
                return
            result = response.read().decode()
            result = json.loads(result)
            if ('block' not in result
                    or 'header' not in result['block']
                    or 'height' not in result['block']['header']
                    or int(result['block']['header']['height']) != earliest):
                print(f"ERROR: Pruning verification failed: expected to have default pruning of 50k blocks")
                return
        print("PASSED Pruning verification")
    except Exception as ex:
        print(f'ERROR: failed getting /cosmos/base/tendermint/v1beta1/blocks/{earliest} from rest api: {ex}')
        return


def test_rest_general_info(base_url, test_values):
    rest_url = f"{base_url}/cosmos/base/tendermint/v1beta1/node_info"
    httprequest = Request(rest_url, headers=HEADERS)
    try:
        with urlopen(httprequest) as response:
            if response.status != 200:
                print('ERROR: failed getting node_info from rest api')
                return
            info = response.read().decode()
            info = json.loads(info)
            if info['default_node_info']['network'] != test_values['chain-id']:
                print(
                    f"ERROR: Chain ID verification failed: expected: {test_values['chain-id'].lower()}, got: {info['default_node_info']['network'].lower()}")
            else:
                print("PASSED Chain ID verification")
            if info["default_node_info"]['other']['tx_index'].lower() != test_values['tx-indexing'].lower():
                print(
                    f"ERROR: TX indexing verification failed: expected: {test_values['tx-indexing']}, got: {info['default_node_info']['other']['tx_index']}")
            else:
                print("PASSED TX indexing verification")
    except Exception as ex:
        print(f'ERROR: failed getting /cosmos/base/tendermint/v1beta1/node_info from rest api: {ex}')
        return


def test_tendermint_rpc_info(base_url, test_values):
    url = f"{base_url}/status"
    httprequest = Request(url, headers=HEADERS)
    try:
        with urlopen(httprequest) as response:
            if response.status != 200:
                print('ERROR: failed getting node_info from rest api')
                return
            status = response.read().decode()
            status = json.loads(status)['result']
            node_info = status['node_info']

            if node_info['network'] != test_values['chain-id']:
                print(
                    f"ERROR: Chain ID verification failed: expected: {test_values['chain-id'].lower()}, got: {status['node_info']['network'].lower()}")
            else:
                print("PASSED Chain ID verification")
            if node_info['other']['tx_index'].lower() != test_values['tx-indexing'].lower():
                print(
                    f"ERROR: TX indexing verification failed: expected: {test_values['tx-indexing']}, got: {status['node_info']['other']['tx_index']}")
            else:
                print("PASSED TX indexing verification")

            earliest = int(status['sync_info']['earliest_block_height'])
            latest = int(status['sync_info']['latest_block_height'])
            if status['sync_info']['catching_up']:
                print("ERROR: Your node is still catching up")
                return

            if latest - earliest >= PRUNING:
                print("PASSED Pruning verification")
            else:
                print(
                    f"ERROR: Pruning verification failed: expected to have default pruning of 50k blocks, got: {latest - earliest}, latest {latest}, earliest {earliest}")
    except Exception as ex:
        print(f'ERROR: failed getting /status from tendermint-rpc api: {ex}')
        return



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('rest', help="axelar node rest endpoint")
    parser.add_argument('tendermintrpc', help="evmos node tendermint-rpc endpoint")
    parser.add_argument('--network', help="mainnet or testnet, default mainnet", default='mainnet')

    args = parser.parse_args()

    test_values = MAINNET if args.network == 'mainnet' else TESTNET
    print("Testing REST endpoint:")
    test_rest_general_info(args.rest, test_values)
    test_rest_earliest_block(args.rest, test_values)
    print("*" * 20)
    print("\nTesting Tendermint-RPC endpoint:")
    test_tendermint_rpc_info(args.tendermintrpc, test_values)
    print("*" * 20)


if "__main__" == __name__:
    main()
