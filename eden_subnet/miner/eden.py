from eden_subnet.miner.miner import Miner, MinerSettings
import argparse


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10001)
    parser.add_argument("--use_testnet", type=bool, default=False)
    return parser.parse_args()


args = parseargs()

miner_settings = MinerSettings(
    key_name=args.key_name,
    module_path=args.key_name,
    host=args.host,
    port=args.port,
    ss58_address: Ss58Address=None,
    use_testnet=args.use_testnet,
    call_timeout: int
)

configuration = miner_settings


class Miner_1(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_2(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_3(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_4(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_5(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_6(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_7(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_8(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


class Miner_9(Miner):
    def __init__(self, settings: MinerSettings) -> None:
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            ss58_address=settings.get_ss58_address(settings.key_name),
            use_testnet=False,
            call_timeout=60
        )


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

miner = miner_map[configuration.key_name.split(".")[1]]()

miner.serve(MinerSettings)
