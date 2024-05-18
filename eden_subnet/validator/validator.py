import random
import json
import time
import os
import requests
import asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from communex.compat.key import Keypair, classic_load_key
from communex.client import CommuneClient
from communex._common import get_node_url
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from eden_subnet.miner.tiktokenizer import TikTokenizer

load_dotenv()

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


class Validator:
    key_name: str
    module_path: str
    host: str
    port: int
    settings: ValidatorSettings
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
        get_similairities: Gets similarities from multiple addresses.
        validate_loop: Validates the loop by scoring modules and voting.
        parse_addresses: Parses addresses from the network.
        parse_weights: Parses existing weights from the network.
        parse_stake: Parses stake information from the network.
        check_weights: Checks for unranked weights and assigns default weight.
        parse_keys: Parses keys from the network.
        scale_numbers: Scales a list of numbers.
        list_to_dict: Converts a list to a dictionary.
        scale_dict_values: Scales dictionary values.
        score_modules: Calculates scores based on weights, stake, and similarity.
    """

    def __init__(
        self,
        key_name: str,
        module_path: str,
        host: str,
        port: int,
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
        self.key_name = key_name or settings.key_name
        self.module_path = module_path or settings.module_path
        self.host = host or settings.host
        self.port = port or settings.port
        self.settings = settings

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
        key_map = comx.query_map_key(netuid=10)
        keypair = classic_load_key(self.key_name)
        ss58_address = keypair.ss58_address
        ss58 = ""
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
        keypath = (
            Path(f"$HOME/.commune/key/{self.key_name}.json").expanduser().resolve()
        )
        with open(keypath, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]
            private_key = json.loads(key)["private_key"]
            ss58address = json.loads(key)["ss58_address"]
            return Keypair(private_key=private_key, ss58_address=ss58address)

    async def make_request(self, message: Message, input_url: str = ""):
        """
        A function that makes a request based on the provided messages and input URL.

        Parameters:
            messages (List[Message]): A list of Message objects to be used in the request.
            input_url (str): The URL to make the request to. Default is an empty string.

        Returns:
            str: The content of the response from the request, processed to extract specific content.

        Raises:
            Exception: If an error occurs during the request process.
        """
        # input_url = "http://localhost:10001/generate"
        logger.info("\nMaking request")

        payload = json.dumps(
            {
                "messages": [{"content": message.content, "role": "user"}],
                "model": "llama-3-8b-instruct",
            }
        )
        headers = {"Content-Type": "application/json"}
        if api_key := os.getenv("AGENTARTIFICIAL_API_KEY") or os.getenv(
            "OPENAI_API_KEY"
        ):
            headers["Authorization"] = f"Bearer {api_key}"

        result = ""
        try:
            response = requests.request(
                method="POST",
                url=input_url,
                headers=headers,
                data=payload,
                timeout=30,
            )
            logger.debug(f"\nResponse:\n{response.content}")
            result = response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.debug(f"\nError making request:\n{e}")
            if input_url != str(os.getenv("AGENTARTIFICIAL_URL")):
                result = []

        return result

    async def get_sample_result(self):
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
        sample_result = await self.make_request(
            message=topic_message, input_url=str(os.getenv("AGENTARTIFICIAL_URL"))
        )
        logger.debug(f"\nSample Result:\n{sample_result}")
        return sample_result

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
        import numpy as np
        from scipy.spatial.distance import cosine

        # Example vectors
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Normalizing vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)

        # Calculating cosine distance
        cosine_distance = cosine(vec1_norm, vec2_norm)
        logger.debug(f"\ncosine distance: {cosine_distance}")

        normalized_similiarity = cosine_distance + 1
        logger.debug(f"\nnormalized similarity: {normalized_similiarity}")
        return normalized_similiarity * 99

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
        
        logger.info("\nEvaluating sample similarity")
        if not embedding2 and len(embedding1) != 0:
            zero_score = [0 for _ in range(len(embedding1))]
            embedding2=zero_score
        
        try:
            response = self.cosine_similarity(
                embedding1=embedding1, embedding2=embedding2
            )
            logger.debug(f"\nsimilarity result: {response}...")
            result = round(response, 2)
        except Exception as e:
            logger.error(f"\ncould not connect to miner, adjusting score.\n{e}")
            result = 0.001
        return result

    async def get_similairities(self, selfuid, encoding, prompt_message, addresses):
        """
        Retrieves similarities from different addresses by making requests and validating the responses.

        Parameters:
            selfuid: The unique identifier of the calling entity.
            encoding: The encoding type for the validation.
            prompt_message: The message used for generating the response.
            addresses: A dictionary containing UIDs and corresponding addresses.

        Returns:
            A dictionary containing the responses from different addresses after validation.
        """
        miner_responses = {}
        for uid, address in addresses.items():
            logger.info(f"\nGetting similairities - {uid}")
            if uid == selfuid:
                continue
            url = f"http://{address}/generate"
            if f"http://{self.host}:{self.port}/generate" == url:
                continue
            try:
                response = await self.make_request(
                    message=prompt_message, input_url=url
                )

                miner_responses[uid] = self.validate_input(encoding, response)
            except Exception as e:
                logger.debug(f"\nError getting similairities: {e}\n{e.args}\n")
            time.sleep(10)
        return miner_responses

    async def validate_loop(self):
        """
        Executes a loop to validate weights and scoring based on sample results and similarities.

        Parameters:
            None

        Returns:
            None
        """
        selfuid = self.get_uid()

        address_dict = self.parse_addresses()
        weights_dict = self.parse_weights()
        weights_dict = self.check_weights(selfuid, weights_dict, address_dict)

        keys_dict = self.parse_keys()

        sample_result = await self.get_sample_result()
        prompt_message = Message(content=str(sample_result), role="user")
        encoding = tokenizer.embedding_function.encode(str(sample_result))

        similiarity_dict = await self.get_similairities(
            selfuid, encoding, prompt_message, address_dict
        )
        score_dict = self.score_modules(
            weights_dict, address_dict, keys_dict, similiarity_dict
        )

        logger.info("\nLoading key")
        uids = []
        weights = []
        
        for uid, weight in score_dict.items():
            if uid == selfuid:
                continue
            uids.append(uid)
            weights.append(weight)
        logger.debug(f"\nuids: {uids}\nweights: {weights}")
        comx.vote(key=Keypair(self.key_name), netuid=10, weights=weights, uids=uids)
        logger.warning("Voted")
        time.sleep(60)

    def run_voteloop(self):
        while True:
            asyncio.run(self.validate_loop())

    def parse_addresses(self):
        """
        Parses addresses and returns the result from comx.query_map_address with netuid 10.
        """
        logger.info("\nParsing addresses")
        return comx.query_map_address(netuid=10)

    def parse_weights(self):
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

    def parse_stake(self):
        """
        A function that parses stake information and returns the result from comx.query_map_stake with netuid 10.
        """
        logger.info("\nParsing stake")
        return comx.query_map_stake(netuid=10)

    def check_weights(self, selfuid, weights, addresses):
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
            if uid not in weights and uid != selfuid:
                weights[uid] = 30

        return weights

    def parse_keys(self):
        """
        A function that parses keys and returns the result from comx.query_map_key with netuid 10.
        """
        logger.info("\nParsing keys")
        return comx.query_map_key(netuid=10)

    def scale_numbers(self, numbers):
        """
        A function that scales a list of numbers between 0 and 1 based on their minimum and maximum values.

        Parameters:
            self: The instance of the class.
            numbers: A list of numbers to be scaled.

        Returns:
            list: A list of scaled numbers between 0 and 1.
        """
        logger.info("\nScaling numbers")
        min_value = min(numbers)
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
        return {
            key: (value - min(dictionary.values()))
            / (max(dictionary.values()) - min(dictionary.values()))
            for key, value in dictionary.items()
        }

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
        staketos = {}
        for uid, key in keys_dict.items():
            if key in staketos_dict:
                staketo = staketos_dict[key]
                staketos[uid] = staketo
        scaled_staketos_dict = self.scale_dict_values(staketos)
        scaled_weight_dict = self.scale_dict_values(weights_dict)
        scaled_similairity_dict = self.scale_dict_values(similairity_dict)
        scaled_scores = {}
        for uid in keys_dict.keys():
            if uid in scaled_staketos_dict:
                stake = scaled_staketos_dict[uid]
            calculated_score = (
                scaled_weight_dict[uid] * 0.4
                + stake * 0.2
                + scaled_similairity_dict[uid] * 0.2
            ) 
            scaled_scores[uid] = calculated_score
        scaled_score = self.scale_dict_values(scaled_scores)
        print(scaled_score)
        return scaled_score
