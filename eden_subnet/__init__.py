import re
from re import Match
from loguru import logger
from communex.client import CommuneClient


IP_REGEX: re.Pattern[str] = re.compile(
    pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
)


def extract_address(string: str) -> re.Match[str] | None:
    """
    Extracts an address from a string.
    """
    return re.search(pattern=IP_REGEX, string=string)


def get_netuid(client: CommuneClient, subnet_name: str = "mosaic") -> int:
    """
    Get the netuid associated with a given subnet name.

    Args:
        client (CommuneClient): The commune client object.
        subnet_name (str, optional): The name of the subnet. Defaults to "mosaic".

    Returns:
        int: The netuid associated with the subnet name.

    Raises:
        ValueError: If the subnet name is not found.
    """
    subnets: dict[int, str] = client.query_map_subnet_names()
    for netuid, name in subnets.items():
        if name == subnet_name:
            logger.info("use netuid:", netuid)
            return netuid
    raise ValueError(f"Subnet {subnet_name} not found")


def get_ip_port(modules_addresses: dict[int, str]) -> dict[int, list[str]]:
    """
    Get the IP addresses and ports from a dictionary of module addresses.

    Args:
        modules_addresses (dict[int, str]): A dictionary mapping module IDs to their addresses.

    Returns:
        dict[int, list[str]]: A dictionary mapping module IDs to a list of IP addresses and ports.

    Raises:
        None

    Examples:
        >>> modules_addresses = {1: "192.168.0.1:8080", 2: "10.0.0.1:9090"}
        >>> get_ip_port(modules_addresses)
        {1: ["192.168.0.1", "8080"], 2: ["10.0.0.1", "9090"]}
    """
    filtered_addr: dict[int, Match[str] | None] = {
        id: extract_address(string=addr) for id, addr in modules_addresses.items()
    }
    ip_port: dict[int, list[str]] = {
        id: x.group(0).split(":") for id, x in filtered_addr.items() if x is not None
    }
    return ip_port
