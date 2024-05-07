from fastapi import FastAPI
import uvicorn
from communex.cli.module import ModuleServer
from communex.key import Keypair
from eden_subnet.miner.config import MinerSettings, Message
from eden_subnet.base.base import BaseModule
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage


class Miner(BaseModule):
    """Basic miner that generates images using the Huggingface Diffusers library."""

    def __init__(self, config: MinerSettings) -> None:
        """
        Initializes the Miner object with the provided key and configuration settings.

        Parameters:
            key (Keypair): The keypair used for the Miner.
            config (Optional[MinerSettings], optional): Configuration settings for the Miner. Defaults to None.

        Returns:
            None
        """
        super().__init__(settings=config)
        self.tokenizer = TikTokenizer(
            kwargs=TokenUsage(prompt=0, total=0, request=0, response=0)
        )

    def generate_embeddings(self, message: Message) -> None:
        self.tokenizer.create_embedding(
            text=message.content, encoding_name="cl100k_base"
        )

    def serve(self) -> None:
        """
        Starts the server and runs the FastAPI app.

        This function initializes a `ModuleServer` object with the current module, key, and a subnets whitelist
        containing the `netuid` attribute. It then retrieves the FastAPI app from the server and runs it using
        `uvicorn.run()`.

        Parameters:
            None

        Returns:
            None
        """
        server = ModuleServer(
            module=self.dynamic_import(),  # type: ignore
            key=Keypair(
                ss58_address=self.settings.ss58_address,
                public_key=self.settings.key_name,
            ),
            subnets_whitelist=[self.netuid],
        )
        app: FastAPI = server.get_fastapi_app()
        uvicorn.run(
            app=app, host=str(object=self.settings.host), port=int(self.settings.port)
        )


if __name__ == "__main__":
    configuration = MinerSettings(
        key_name="miner.Miner",
        module_path="miner.Miner",
        host="0.0.0.0",
        port=7777,
        use_testnet=False,
    )
    Miner(config=configuration).serve()
