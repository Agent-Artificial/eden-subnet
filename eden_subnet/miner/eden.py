"""This is an example of how you can write a script to launch miners. Inherit the miner class into a new miner and instantiate an instance of that class when you call the script modified by the minter settings to your specificiation. Make sure the file this code is in is the first part of the miner name. In this example it is eden which is the start of eden.Miner where Miner is the class name."""

from eden_subnet.miner.miner import Miner, MinerSettings
import argparse


def parseargs():
    """
    Parses command line arguments using argparse module.

    Returns:
        argparse.Namespace: Object containing the parsed arguments.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10001)
    parser.add_argument("--use_testnet", type=bool, default=False)
    return parser.parse_args()


args = parseargs()

# Apply settings

miner_settings = MinerSettings(
    key_name=args.key_name,
    module_path=args.key_name,
    host=args.host,
    port=args.port,
)

configuration = miner_settings


# Create new class names to let the miners have unique names.
class Miner_1(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_2(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_3(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_4(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_5(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_6(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_7(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_8(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


class Miner_9(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )

class Miner_10(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        """
        Initializes the MinerSettings with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60,
        )


# Map the classes to the their names so you can call them with a string.
miner_map = {
    "Miner_1": Miner_1,
    "Miner_2": Miner_2,
    "Miner_3": Miner_3,
    "Miner_4": Miner_4,
    "Miner_5": Miner_5,
    "Miner_6": Miner_6,
    "Miner_7": Miner_7,
    "Miner_8": Miner_8,
    "Miner_9": Miner_9,
}

# Instantiate the selected map miner and serve.
miner = miner_map[args.key_name.split(".")[-1]](configuration)

# (miner_settings)

miner.serve(configuration)
