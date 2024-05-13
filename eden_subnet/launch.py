from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair, resolve_key_ss58, classic_load_key
import argparse

comx = CommuneClient(get_node_url())
SUBNET_UID = 10


def launch_loop(
    module_name: str,
    number_modules: int,
    stake: int,
    port: int,
    delegation_fee: int,
    host: str,
):
    """
    A function to launch multiple modules with specified parameters.

    Parameters:
        module_name (str): The base name of the modules.
        number_modules (int): The number of modules to launch.
        stake (int): The amount of stake for each module.
        port (int): The base port number for the modules.
        delegation_fee (int): The delegation fee for each module.
        host (str): The host address where the modules will be launched.

    Returns:
        None
    """
    for i in range(number_modules):
        name = f"{module_name}{i}"
        address = f"{host}:{port+i}"
        key = resolve_key_ss58(f"{module_name}{i}")
        private_key = classic_load_key(key).private_key
        keypair = Keypair(ss58_address=key, private_key=private_key)
        comx.register_module(keypair, name, min_stake=stake, subnet=str(SUBNET_UID))
        comx.update_module(
            key=keypair,
            address=address,
            delegation_fee=delegation_fee,
            metadata=None,
            name=name,
            netuid=SUBNET_UID,
        )


def main(
    module_name: str,
    number_modules: int,
    stake: int,
    port: int,
    delegation_fee: int,
    host: str,
):
    """
    Executes a loop to launch modules.

    Args:
        module_name (str): The name of the module to launch.
        number_modules (int): The number of modules to launch.
        stake (int): The stake amount for each module.
        port (int): The port number for each module.
        delegation_fee (int): The delegation fee for each module.
        host (str): The host address for each module.

    Returns:
        None
    """
    launch_loop(module_name, number_modules, stake, port, delegation_fee, host)


def parse_arguments():
    """
    Parses the command line arguments and returns the parsed arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.

    """
    parser = argparse.ArgumentParser(description="Launch a number of modules.")
    parser.add_argument("--module_name", type=str, default="miner.Miner")
    parser.add_argument("--number_modules", type=int, default="3")
    parser.add_argument("--stake", type=int, default=10)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--delegation_fee", type=float, default=0.01)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    module_name = args.module_name
    number_modules = args.number_modules
    stake = args.stake
    port = args.port
    delegation_fee = args.delegation_fee
    host = args.host

    launch_loop(module_name, number_modules, stake, port, delegation_fee, host)
