from eden_subnet.miner.miner import Miner, MinerSettings
from communex.compat.key import Ss58Address

MinerSettings = MinerSettings(
    key_name="eden.Miner_1",
    module_path="eden.Miner_1",
    host="0.0.0.0",
    port=10001,
    use_testnet=True,
)

Miner_1 = Miner(**MinerSettings.model_dump())

Miner_1.serve(MinerSettings)
