import random
import json
import time
import os

import requests.sessions
import requests
import asyncio
from requests.exceptions import ConnectionError
import numpy as np
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from scipy.spatial.distance import cosine
from communex.compat.key import Keypair, classic_load_key
from communex.client import CommuneClient
from communex._common import get_node_url
from pydantic import BaseModel
from typing import List, Any
import argparse

from eden_subnet.miner.tiktokenizer import TikTokenizer

load_dotenv()

def parseargs():
    """
    Parse command line arguments using argparse module.

    Returns:
        argparse.Namespace: Object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default=None, help="Name of the validator as it will appear on chain")
    parser.add_argument("--module_path", type=str, default=None, help="Filename with out the .json suffix in the ~/.commune/key directory")
    parser.add_argument("--host", type=str, default=None, help="Host address for the validator")
    parser.add_argument("--port", type=int, default=None, help="Port for the validator")
    parser.add_argument("--url", type=str, default=None, help="Base URL for inference request.")
    parser.add_argument("--api_key", type=str, default=None, help="OpenAI or Agent Artificial API Key")
    parser.add_argument("--model", type=str, default=None, help="OpenAI or Agent Artificial Model")
    return parser.parse_args()


ARGS = parseargs()


tokenizer = TikTokenizer()
comx = CommuneClient(get_node_url())


logger.level("INFO")


class Message(BaseModel):
    """
    A class representing a message.

    Explanation:
    This class defines a data model for a message with a single attribute 'text' of type str.
    """

    role: str
    content: str


class Ss58Address(BaseModel):
    """
    A class representing an SS58 address.

    Explanation:
    This class defines a data model for an SS58 address with a single attribute 'address' of type str.
    """

    address: str  # Example field, adjust as needed


class ConfigDict(BaseModel):
    """
    A class representing a configuration dictionary.

    Explanation:
    This class defines a data model for a configuration dictionary with a single attribute 'arbitrary_types_allowed' that specifies whether arbitrary types are allowed by default.
    """

    arbitrary_types_allowed: bool = True


class ValidatorSettings(BaseModel):
    """
    A class representing validator settings.

    Explanation:
    This class defines a data model for validator settings including attributes like key name, module path, host, and port. Additional settings can be added as needed.
    """

    key_name: str
    module_path: str
    host: str
    port: int


class GenerateRequest(BaseModel):
    messages: list
    model: str


TOPICS = [
    "The pursuit of knowledge",
    "The impact of technology on society",
    "The struggle between tradition and modernity",
    "The nature of good and evil",
    "The consequences of war",
    "The search for identity",
    "The journey of self-discovery",
    "The effects of greed",
    "The power of love",
    "The inevitability of change",
    "The quest for power",
    "The meaning of freedom",
    "The impact of colonization",
    "The illusion of choice",
    "The influence of media",
    "The role of education",
    "The effects of isolation",
    "The battle against inner demons",
    "The corruption of innocence",
    "The loss of culture",
    "The value of art",
    "The complexities of leadership",
    "The nature of sacrifice",
    "The deception of appearances",
    "The consequences of environmental degradation",
    "The cycle of life and death",
    "The impact of global capitalism",
    "The struggle for equality",
    "The influence of religion",
    "The exploration of space",
    "The effects of addiction",
    "The dangers of ambition",
    "The dynamics of family",
    "The nature of truth",
    "The consequences of scientific exploration",
    "The illusion of happiness",
    "The pursuit of beauty",
    "The impact of immigration",
    "The clash of civilizations",
    "The struggle against oppression",
    "The quest for eternal life",
    "The nature of time",
    "The role of fate and destiny",
    "The impact of climate change",
    "The dynamics of revolution",
    "The challenge of sustainability",
    "The concept of utopia and dystopia",
    "The nature of justice",
    "The role of mentorship",
    "The price of fame",
    "The impact of natural disasters",
    "The boundaries of human capability",
    "The mystery of the unknown",
    "The consequences of denial",
    "The impact of trauma",
    "The exploration of the subconscious",
    "The paradox of choice",
    "The limitations of language",
    "The influence of genetics",
    "The dynamics of power and control",
    "The nature of courage",
    "The erosion of privacy",
    "The impact of artificial intelligence",
    "The concept of the multiverse",
    "The struggle for resource control",
    "The effects of globalization",
    "The dynamics of social class",
    "The consequences of unbridled capitalism",
    "The illusion of security",
    "The role of memory",
    "The dynamics of forgiveness",
    "The challenges of democracy",
    "The mystery of creation",
    "The concept of infinity",
    "The meaning of home",
    "The impact of pandemics",
    "The role of mythology",
    "The fear of the unknown",
    "The challenge of ethical decisions",
    "The nature of inspiration",
    "The dynamics of exclusion and inclusion",
    "The consequences of prejudice",
    "The effects of fame and anonymity",
    "The nature of wisdom",
    "The dynamics of trust and betrayal",
    "The struggle for personal autonomy",
    "The concept of rebirth",
    "The meaning of sacrifice",
    "The impact of terrorism",
    "The challenge of mental health",
    "The exploration of alternate realities",
    "The illusion of control",
    "The consequences of technological singularity",
    "The role of intuition",
    "The dynamics of adaptation",
    "The challenge of moral dilemmas",
    "The concept of legacy",
    "The impact of genetic engineering",
    "The role of art in society",
    "The effects of cultural assimilation",
]


import aiohttp
import asyncio
from asyncio import Semaphore

class Validator:
    key_name: str
    module_path: str
    host: str
    port: int
    settings: ValidatorSettings
    keypair: Any
    """
    Represents a validator with key name, module path, host, port, and settings.

    Args:
        key_name: The name of the key.
        module_path: The path of the module.
        host: The host address.
        port: The port number.
        settings: ValidatorSettings object containing settings.

    Attributes:
        key_name (str): The name of the key.
        module_path (str): The path of the module.
        host (str): The host address.
        port (int): The port number.
        settings (ValidatorSettings): ValidatorSettings object containing settings.

    Methods:
        get_uid: Retrieves the UID based on key mapping.
        load_local_key: Loads the local key from a JSON file.
        make_request: Makes an asynchronous request with messages and input URL.
        get_sample_result: Gets a sample result by making a request.
        cosine_similarity: Calculates the cosine similarity between two embeddings.
        validate_input: Evaluates the sample similarity using cosine similarity.
        : Gets similarities from multiple addresses.
        validate_loop: Validates the loop by scoring modules and voting.
        get_querymap_addresses: Parses addresses from the network.
        get_querymaps_weights: Parses existing weights from the network.
        get_querymap_stake: Parses stake information from the network.
        set_default_weights: Checks for unranked weights and assigns default weight.
        get_querymap_keys: Parses keys from the network.
        scale_numbers: Scales a list of numbers.
        list_to_dict: Converts a list to a dictionary.
        scale_dict_values: Scales dictionary values.
        score_modules: Calculates scores based on weights, stake, and similarity.
    """

    def __init__(
        self,
        settings: ValidatorSettings,
    ) -> None:
        """
        Initializes a Validator object with key name, module path, host, port, and settings.

        Args:
            key_name: The name of the key.
            module_path: The path of the module.
            host: The host address.
            port: The port number.
            settings: ValidatorSettings object containing settings.
        """
        self.key_name = settings.key_name
        self.module_path = settings.module_path
        self.host = settings.host
        self.port = settings.port
        self.settings = settings
        self.keypair = self.load_local_key()

    def get_uid(self):
        """
        Retrieves the unique identifier associated with the validator.

        Parameters:
            None

        Returns:
            The unique identifier (uid) of the validator.

        Raises:
            ValueError: If the unique identifier (uid) is not found.
        """
        key_map = self.get_querymap_keys()
        
        
        ss58_address = self.keypair.ss58_address
        for uid, ss58 in key_map.items():
            if ss58 == ss58_address:
                return uid
        raise ValueError(
            f"\nUID not found, {ss58} please check your validator is registered with\n comx module info {self.key_name}"
        )

    def load_local_key(self):
        """
        Loads the local key from the specified keypath and returns a Keypair object.

        Parameters:
            self: The Validator object.

        Returns:
            Keypair: A Keypair object with the private key and SS58 address.
        """
        keypath = Path(f"/home/administrator/.commune/key/{self.key_name}.json")
        
        with open(keypath, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]
            private_key = json.loads(key)["private_key"]
            ss58address = json.loads(key)["ss58_address"]

        return Keypair(private_key=private_key, ss58_address=ss58address)  

    def get_sample_result(self):
        """
        Asynchronously retrieves a sample result by selecting a random topic from the predefined TOPICS list,
        creating a message based on the chosen topic, making a request using the message, and returning the sample result.

        Returns:
            The sample result obtained from the request.

        Raises:
            Any exceptions that occur during the request.
        """
        logger.info("\nGetting sample result")
        topic = random.choice(TOPICS)
        logger.debug(f"\nsample topic:\n{topic}")
        topic_message = Message(
            content=f"Please write a short alegory about this topic: {topic}",
            role="user",
        )
        input_url = os.getenv("AGENTARTIFICIAL_URL") or os.getenv("OPENAI_URL")
        sample_result = self.make_request(
            message=topic_message, input_url=input_url
        )
        logger.debug(f"\nSample Result:\n{sample_result}")
        return sample_result

    async def get_miner_responses(self, selfuid, encoding, prompt_message, addresses):
        """
        Retrieves similarities from different addresses by making concurrent requests and validating the responses.

        Parameters:
            selfuid: The unique identifier of the calling entity.
            encoding: The encoding type for the validation.
            prompt_message: The message used for generating the response.
            addresses: A dictionary containing UIDs and corresponding addresses.

        Returns:
            A dictionary containing the responses from different addresses after validation.
        """
        miner_responses = {}
        semaphore = Semaphore(50)  # Limit concurrent requests to 50

        async def process_address(uid, address):
            if uid == selfuid:
                return
            url = f"http://{address}/generate"
            if f"http://{self.host}:{self.port}/generate" == url:
                return
            
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        response = await self.make_request_async(session, prompt_message, url)
                    if response:
                        miner_responses[uid] = self.validate_input(encoding, response)
                except Exception as e:
                    logger.debug(f"\nError getting similarities for {uid}: {e}\n{e.args}\n")

        tasks = [process_address(uid, address) for uid, address in addresses.items()]
        await asyncio.gather(*tasks)
        
        return miner_responses
    def make_request(self, message: Message, input_url: str = ""):
        model = ARGS.model or os.getenv("AGENTARTIFICIAL_MODEL") or os.getenv("OPENAI_MODEL")
        api_key = ARGS.api_key or os.getenv("AGENTARTIFICIAL_API_KEY") or os.getenv("OPENAI_API_KEY")
        payload = {
            "messages": [message],
            "model": model or None,
            "api_key": api_key or None
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" or None
        }
        try:
            response = requests.post(input_url, data=payload, headers=headers)
        except Exception as e:
            logger.debug(f"\nError making request: {e}\n{e.args}\n")
            return
        return response.text
    
    async def make_request_async(self, session, message: Message, input_url: str = ""):
        """
        Makes an asynchronous request based on the provided messages and input URL.

        Parameters:
            session: The aiohttp ClientSession to use for the request.
            message (Message): A Message object to be used in the request.
            input_url (str): The URL to make the request to. Default is an empty string.

        Returns:
            str: The content of the response from the request, processed to extract specific content.

        Raises:
            Exception: If an error occurs during the request process.
        """
        
        
        url_to_use = input_url or ARGS.url or os.getenv("AGENTARTIFICIAL_URL") or os.getenv("OPENAI_URL")
        model = ARGS.model or os.getenv("AGENTARTIFICIAL_MODEL") or os.getenv("OPENAI_MODEL")
        api_key = ARGS.api_key or os.getenv("AGENTARTIFICIAL_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        logger.info(f"\nMaking async request to: {url_to_use}")
        
        payload = json.dumps({
          "model": model,
          "messages": [
            {
              "role": "user",
              "content": message.content
            }
          ],
          "api_key": api_key
        })
        headers = {
          'Authorization': f'Bearer {api_key}',
          'Content-Type': 'application/json'
        }
        
        try:
            async with session.post(url_to_use, headers=headers, data=payload, timeout=30) as response:
                if response.status == 200:
                    try:
                        response_json = await response.json()
                        logger.success(f"\nRequest successfull: {response_json[:150]}...")
                        return response_json
                    except json.JSONDecodeError:
                        logger.error(f"\nFailed to decode JSON from response. Status: {response.status}, Content-Type: {response.headers.get('Content-Type')}")
                        return None
                else:
                    logger.error(f"\nRequest failed with status {response.status}. URL: {url_to_use}")
                    response_text = await response.text()
                    logger.error(f"Response content: {response_text[:200]}...")  # Log first 200 characters of response
                    return None
        except ConnectionError as e:
            logger.error(f"\nNetwork error occurred: {e}\n{e.args}\n")
            return None
        except Exception as e:
            logger.error(f"\nUnexpected error occurred: {e}\n{e.args}\n")
            return None

    def cosine_similarity(self, embedding1, embedding2):
        """
        Calculates the cosine similarity between two embeddings.

        Parameters:
            embedding1: The first embedding.
            embedding2: The second embedding.

        Returns:
            The normalized similarity value multiplied by 99.
        """
        logger.info("\nCalculating cosine similarity")

        # Example vectors
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Normalizing vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)

        # Calculating cosine distance
        cosine_distance = 1 -cosine(vec1_norm, vec2_norm) * 99 + 99
        if cosine_distance < 0:
            cosine_distance = 1
        logger.success(f"\ncosine distance: {cosine_distance}")
        return round(cosine_distance - 30)

    def validate_input(self, embedding1, embedding2):
        """
        A function to validate input embeddings by evaluating sample similarity.

        Parameters:
            embedding1: The first embedding.
            embedding2: The second embedding.

        Returns:
            The result of the validation after evaluating the similarity.
        """
        result = None
        
        if not embedding1:
            logger.error("\nembedding1 is empty, cannot validate")
            return 1
        
        
        if not embedding2:
            logger.warning("\nembedding2 is empty, setting score to 1")
            return 1
        # logger.debug(f"\nembedding1: {embedding1}\nembedding2: {embedding2}")
        try:
            response = self.cosine_similarity(
                embedding1=embedding1, embedding2=embedding2
            )
            result = round(response, 2)
            logger.success(f"\nvalidation result: {result}")
        except Exception as e:
            logger.warning(f"\ncould not connect to miner, adjusting score.\n{e}")
            result = 1
        return result * 100
    
    async def validate_loop(self):
        """
        Executes a loop to validate weights and scoring based on sample results and similarities.

        Parameters:
            None

        Returns:
            None
        """
        selfuid = self.get_uid()

        # Query the chain for the addresses, weights, and keys
        address_dict = self.get_querymap_addresses()
        # Debugging: Limit the number of addresses to 10
        # address_dict = dict(list(address_dict.items())[:10])
        weights_dict = self.get_querymaps_weights()
        weights_dict = self.set_default_weights(selfuid, weights_dict, address_dict)

        keys_dict = self.get_querymap_keys()

        # Generate a sample result and convert it into an embedding
        sample_result = self.get_sample_result()
        prompt_message = Message(content=str(sample_result), role="user")
        encoding = tokenizer.embedding_function.encode(str(sample_result))
        
        

        # Get the responses from the miners
        responses_dict = await self.get_miner_responses(
            selfuid, encoding, prompt_message, address_dict
        )
        
        # Score the modules
        score_dict = self.score_modules(
            weights_dict, address_dict, keys_dict, responses_dict
        )
        logger.debug(f"score_dict: {score_dict}")
        
        # Convert the weights into a list of uids and weight values for voting.
        logger.info("\nLoading weights")
        uids = []
        weights = []
        
        for uid, weight in score_dict.items():
            if uid == selfuid:
                continue
            uids.append(uid)
            weights.append(weight)
        logger.debug(f"\nuids: {uids}\nweights: {weights}")
        subnet_weights = {"uids": uids, "weights": weights}
        
        # Save a copy for debugging
        with open("data/weights.json", "w") as f:
            f.write(json.dumps(subnet_weights, indent=4))

        # Vote on the modules   
        try:
            result = comx.vote(key=self.keypair, netuid=10, weights=weights, uids=uids)
            if result.is_success:
                logger.info("Voted successfully")
            else:
                logger.error(f"\n{result}")
        except Exception as e:
            logger.exception(f"Error voting: {e}")
        
        logger.warning("Voted")
        time.sleep(60)

    def run_voteloop(self):
        while True:
            asyncio.run(self.validate_loop())

    def get_querymap_addresses(self):
        """
        Parses addresses and returns the result from comx.query_map_address with netuid 10.
        """
        logger.info("\nParsing addresses")
        return comx.query_map_address(netuid=10)

    def get_querymaps_weights(self):
        """
        Parses existing weights and creates a dictionary mapping UID to weight.

        Parameters:
            None

        Returns:
            dict: A dictionary mapping UID to weight based on the existing weights.
        """
        logger.info("\nParsing existing weights")
        # sourcery skip: dict-comprehension, identity-comprehension, inline-immediately-returned-variable
        weights = comx.query_map_weights(netuid=10)[1]
        weight_dict = {}
        for uid, weight in weights:  # type: ignore
            if uid not in weight_dict:
                weight_dict[uid] = weight
        return weight_dict

    def get_querymap_stake(self):
        """
        A function that parses stake information and returns the result from comx.query_map_stake with netuid 10.
        """
        logger.info("\nParsing stake")
        return comx.query_map_stake(netuid=10)

    def set_default_weights(self, selfuid, weights, addresses):
        """
        Checks for unranked weights and assigns a default weight of 30 to the missing weights.

        Parameters:
            selfuid: The unique identifier of the validator.
            weights: A dictionary mapping UID to weight.
            addresses: A dictionary containing addresses of validators.

        Returns:
            dict: A dictionary with updated weights.
        """
        logger.info("\nChecking for unranked weights")
        for uid, _ in addresses.items():
            for id in  range(820):
                if id not in weights and uid != selfuid:
                    weights[uid] = 30

        return weights

    def get_querymap_keys(self):
        """
        A function that parses keys and returns the result from comx.query_map_key with netuid 10.
        """
        logger.info("\nParsing keys")
        return comx.query_map_key(netuid=10)

    def scale_numbers(self, numbers):
        """
        A function that scales a list of numbers between 0 and 1 based on their minimum and maximum
        Parameters:
            self: The instance of the class.
            numbers: A list of numbers to be scaled.

        Returns:
            list: A list of scaled numbers between 0 and 1.
        """
        logger.info("\nScaling numbers")
        min_value = 1
        max_value = max(numbers)
        return [(number - min_value) / (max_value - min_value) for number in numbers]

    def list_to_dict(self, list):
        """
        A function that converts a list into a dictionary where the index of each element is the key.

        Parameters:
            self: The instance of the class.
            list: A list to be converted into a dictionary.

        Returns:
            dict: A dictionary where the keys are the indices of the list elements and the values are the elements themselves.
        """
        return {i: list[i] for i in range(len(list))}

    def scale_dict_values(self, dictionary):
        """
        A function that scales the values of a dictionary between 0 and 1 based on their minimum and maximum values.

        Parameters:
            self: The instance of the class.
            dictionary: A dictionary with numeric values to be scaled.

        Returns:
            dict: A dictionary with the scaled values between 0 and 1.
        """
        logger.info("\nScaling dictionary values")
        min_value = 0.000000000000001
        logger.debug(f"\nmin_value: {min_value}")
        max_value = max(dictionary.values()) or 1
        logger.debug(f"\nmax_value: {max_value}")
        
        return {
            key: (value - min_value) / (max_value - min_value)
            for key, value in dictionary.items()
        }
    def get_staketo_values(self):
        staketo_map = comx.query_map_staketo()
        key_map = comx.query_map_key(netuid=10)
        staketo_dict = {}
        for uid, key in key_map.items():
            staketo_value = 0.00001
            if key not in staketo_map:
                continue
            staketo = staketo_map[key]
            for stakeitems in staketo:
                _, value = stakeitems
                staketo_value += value
            staketo_dict[uid] = staketo_value
        return staketo_dict

    def score_modules(self, weights_dict, staketos_dict, keys_dict, similairity_dict):
        """
        Calculates the scores for modules based on weights, staketos, keys, and similarity values.

        Parameters:
            self: The instance of the class.
            weights_dict (dict): A dictionary containing weights for each module.
            staketos_dict (dict): A dictionary containing staketos for each module.
            keys_dict (dict): A dictionary containing keys for each module.
            similarity_dict (dict): A dictionary containing similarity values for each module.

        Returns:
            dict: A dictionary containing the calculated scores for each module.
        """
        logger.info("\nCalculating scores")
        logger.debug(f"\nweights_dict: {weights_dict}\nsimilairity_dict: {similairity_dict}")
        scaled_weight_dict = self.scale_dict_values(weights_dict)
        scaled_similairity_dict = self.scale_dict_values(similairity_dict)
        staketo_dict = self.get_staketo_values()
        scaled_staketo_dict = self.scale_dict_values(staketo_dict)
        scaled_scores = {}
        for uid in keys_dict.keys():     
            if uid not in scaled_similairity_dict:
                continue       
            calculated_score = (
                (scaled_weight_dict[uid] * 0.4) + (scaled_similairity_dict[uid] * 0.2) + (scaled_staketo_dict[uid] * 0.2)
            ) 
            if calculated_score <= 0:
                calculated_score = 0.00001
            logger.debug(f"UID: {uid}\nScore: {calculated_score}")
            scaled_scores[uid] = calculated_score
            
        print(scaled_scores)
        
        return self.scale_dict_values(scaled_scores)
    

class Validator(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            settings=settings,
        )
        self.key_name = settings.key_name
        self.module_path = settings.module_path
        self.host = settings.host
        self.port = settings.port
        self.keypair = self.load_local_key()
        
# Apply settings

def main():
    validator_settings = ValidatorSettings(
        key_name=ARGS.key_name or os.getenv("KEY_NAME"),
        module_path=ARGS.module_path or os.getenv("MODULE_PATH"),
        host=ARGS.host or os.getenv("HOST"),
        port=ARGS.port or os.getenv("PORT"),
    )
    # Serve the validator
    logger.info("\nLaunching validator")
    validator = Validator(settings=validator_settings)
    validator.run_voteloop()


if __name__ == "__main__":
    main()

