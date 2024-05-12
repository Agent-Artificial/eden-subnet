from communex.module.module import Module, endpoint
from communex.module.server import ModuleServer
from communex.compat.key import Keypair, classic_load_key
from communex.client import CommuneClient, Ss58Address
from communex._common import get_node_url
from eden_subnet.miner.config import MinerSettings, Message
from pydantic import BaseModel, Field
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage
from loguru import logger
import uvicorn
import tiktoken
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tokenizer = TikTokenizer()
tokenizer.embedding_function = tiktoken.get_encoding("cl100k_base")


class Miner(BaseModel, Module):  # Make sure BaseModel is correctly integrated
    tokenizer: TikTokenizer = TikTokenizer()
    ss58_address: Ss58Address = Field(default_factory=None)
    key_name: str
    module_path: str
    host: str
    port: int
    use_testnet: bool
    call_timeout: int = 60

    def __init__(
        self,
        key_name: str,
        module_path: str,
        host: str,
        port: int,
        ss58_address: Ss58Address,
        use_testnet: bool,
        call_timeout: int,
    ) -> None:
        super().__init__(
            key_name=key_name,
            module_path=module_path,
            host=host,
            port=port,
            ss58_address=ss58_address,
            use_testnet=use_testnet,
            call_timeout=call_timeout,
        )
        self.ss58_address = Ss58Address(key_name)

    @app.post("/generate")
    def generate(self, message: Message):
        try:
            if not message.content:
                return {"error": "No message provided"}
            if not self.ss58_address:
                return {"error": "No ss58_address provided"}
            return tokenizer.embedding_function.encode(message.content)
        except HTTPException as e:
            raise HTTPException(status_code=500, detail={"error": str(e)}) from e

    @endpoint
    def get_model(self):
        return {"model": self.tokenizer}

    @endpoint
    def serve(self, settings: MinerSettings):
        settings.ss58_address = settings.get_ss58_address(key_name=settings.key_name)
        uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    uvicorn.run("miner.Miner", host="0.0.0.0", port=10001)
