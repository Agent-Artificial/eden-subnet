import uvicorn
import tiktoken

from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field

from communex.module.module import Module, endpoint
from communex.client import Ss58Address
from eden_subnet.miner.tiktokenizer import TikTokenizer
from eden_subnet.miner.data_models import MinerSettings, EmbeddingRequest

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


class GenerateRequest(BaseModel):
    messages: list
    model: str


class Miner(BaseModel, Module):
    """
    A class representing a miner.

    Explanation:
    This class combines functionality from BaseModel and Module to define a miner with attributes such as key name, module path, host, port, SS58 address, and settings for using the testnet. It provides methods for getting the model, serving the miner, and generating responses.
    """

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
        """
        Initializes the Miner with the provided parameters.

        Args:
            key_name (str): The unique identifier for the miner.
            module_path (str): The path to the module.
            host (str): The host address for the miner.
            port (int): The port number for communication.
            ss58_address (Ss58Address): The SS58 address associated with the miner.
            use_testnet (bool): Flag indicating whether to use the testnet.
            call_timeout (int): The timeout duration for calls.

        Returns:
            None
        """
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

    @endpoint
    def get_model(self):
        """
        Retrieves the model associated with this instance.

        Returns:
            dict: A dictionary containing the model, with the key "model" and the value being the tokenizer object.
        """
        self.tokenizer.embedding_function = tiktoken.get_encoding("cl100k_base")
        return {"model": self.tokenizer.embedding_function}

    @endpoint
    def serve(self, settings: MinerSettings):
        """
        Serves the miner with the provided settings.

        Args:
            settings (MinerSettings): The settings object containing key_name, module_path, host, port, and ss58_address.

        Returns:
            None
        """
        uvicorn.run(app, host=settings.host, port=settings.port)

    def __call__(self):
        """
        Executes the instance when called, running the FastAPI app with the specified host and port.
        """
        uvicorn.run(app, host=self.host, port=self.port)

    @endpoint
    def generate(self, request: EmbeddingRequest):
        """
        A function that generates something based on the provided request.

        Args:
            request (GenerateRequest): The request object containing information for generation.

        Returns:
            dict: A dictionary containing the generated choices.

        Raises:
            HTTPException: If an HTTP exception occurs during the generation process.
        """
        dict_request = request.messages[0].content
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": self.tokenizer.embedding_function.encode(dict_request)
                    }
                }
        ]}


@app.post("/generate")
def generate(request: GenerateRequest):
    """
    A function that generates something based on the provided request.

    Args:
        request (GenerateRequest): The request object containing information for generation.

    Returns:
        dict: A dictionary containing the generated choices.

    Raises:
        HTTPException: If an HTTP exception occurs during the generation process.
    """
    try:
        miner = Miner(
            key_name="miner.Miner",
            module_path="miner.Miner",
            host="0.0.0.0",
            port=10001,
            ss58_address=Ss58Address("miner.Miner"),
            use_testnet=False,
            call_timeout=60,
        )
        result = miner.generate(request)
        logger.debug(f"result: {result}")
        if result:
            return result

    except HTTPException as e:
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
