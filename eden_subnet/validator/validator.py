from typing import List
import random
from eden_subnet.base.base import BaseValidator
from eden_subnet.miner.config import Message
from eden_subnet.validator.config import ValidatorSettings, TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage
from communex.module.client import ModuleClient
from cellium.client import CelliumClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


client = CelliumClient()
client.base_url = client.choose_base_url()
client.api_key = client.choose_api_key()


class Validator(BaseValidator):
    def __init__(self, config: ValidatorSettings) -> None:
        super().__init__(settings=config)
        self.tokenizer = TikTokenizer(
            kwargs=TokenUsage(prompt=0, total=0, request=0, response=0)
        )
        self.cellium = CelliumClient()

    def get_message(self, topic) -> Message:
        test_prompt = f"please write a short alegory about the following topic: {topic}"
        return Message(content=test_prompt, role="user")

    def make_request(self, message: Message):
        responses = self.cellium.generate(messages=[message.model_dump()])

        full_message = ""
        for response in responses:
            full_message += "\n".join(response["choices"][0]["content"])

        return full_message

    def get_miner_by_netuid(self, miner_id: int):
        miners = self.get_queryable_miners()
        if not miners:
            return
        return miners[miner_id]

    def get_random_miner(self):
        miners = self.get_queryable_miners()
        if not miners:
            return
        return random.choice(miners)

    def get_embedding(self, text_input: str):
        return self.tokenizer.create_embedding(text=text_input)

    def evalutate_similarity(self, embedding1, embedding2):
        return self.tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )

    def serve(self) -> None:
        server = ModuleClient(
            host=self.settings.host,
            port=self.settings.port,
            key=Keypair(
                ss58_address=self.settings.ss58_address,
                public_key=self.settings.key_name,
            ),
        )
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[self.get_queryable_miners()],
            allow_credentials=True,
            allow_methods=["GET, POST, OPTIONS"],
            allow_headers = [{"Content-Type", "application/json"}],
        )
        uvicorn.run(
            app=app, host=str(object=self.settings.host), port=int(self.settings.port)
        )
        return

    def serve():
        