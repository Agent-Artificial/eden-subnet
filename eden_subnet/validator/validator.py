import os
from eden_subnet.base.base import BaseValidator
from eden_subnet.base.config import SampleInput
from eden_subnet.validator.config import ValidatorSettings
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage
from cellium.client import CelliumClient


client = CelliumClient()
client.base_url = client.choose_base_url()
client.api_key = client.choose_api_key()


class Validator(BaseValidator):
    def __init__(self, config: ValidatorSettings) -> None:
        super().__init__(settings=config)
        self.tokenizer = TikTokenizer(
            kwargs=TokenUsage(prompt=0, total=0, request=0, response=0)
        )

    def get_testing_input(self):
        message = Message(
            content="Please generate a short poem based on a theme."
            role="usr"
                )
        responses = client.generate(
            messages=[message],
        )
        full_message += "\n".join([response["content"] for response in responses])
        for response in responses:
            "\n"
            
        self.generate_embeddings()
        
    def get_validate_input(self, input):
        self.get_miner_generation(miner_list=self.get_queryable_miners(), miner_input=)
