import tiktoken
from typing import List
from eden_subnet.miner.config import TokenUsage


class TikTokenizer(TokenUsage):
    def __init__(self, **kwargs) -> None:
        """
        Initializes the TikTokenManager object with the provided keyword arguments.

        Parameters:
            **kwargs (dict): A dictionary of keyword arguments.
                - total (int): The total number of tokens.
                - response_tokens (int): The number of response tokens.
                - prompt_tokens (int): The number of prompt tokens.

        Returns:
            None
        """
        super().__init__(**kwargs)
        self.session_total = 0
        self.request_tokens = 0
        self.response_tokens = 0
        self.total_tokens = kwargs["total"]
        self.completion_tokens = kwargs["response_tokens"]
        self.prompt_tokens = kwargs["prompt_tokens"]
        self.historical_list: List[TokenUsage] = []

    def remove(self, index) -> TokenUsage:
        """
        Remove an element from the historical list at the specified index.

        Parameters:
            index (int): The index of the element to remove.

        Returns:
            str: A message indicating that the index has been removed.

        Raises:
            IndexError: If the index is out of range.

        Side Effects:
            - The element at the specified index is removed from the historical list.
            - If the index is 0, the session_total, prompt_tokens, request_tokens, response_tokens, and historical_list attributes are reset to 0 or an empty list.
        """
        self.historical_list.pop(index)
        if index == 0:
            self.session_total = 0
            self.prompt_tokens = 0
            self.request_tokens = 0
            self.response_tokens = 0
            self.historical_list = 0

        return TokenUsage(
            prompt=self.prompt_tokens,
            request=self.request_tokens,
            response=self.response_tokens,
            total=self.session_total,
        )

    def update(self, total: int, request: int, response: int) -> TokenUsage:
        """
        Updates the session total, prompt tokens, request tokens, and response tokens with the provided values.

        Parameters:
            total (int): The total number of tokens.
            request (int): The number of request tokens.
            response (int): The number of response tokens.

        Returns:
            str: A message indicating that the update was successful.
        """
        self.session_total += total
        self.prompt_tokens: int = total
        self.request_tokens: int = request
        self.response_tokens: int = response
        return TokenUsage(
            prompt=self.prompt_tokens,
            request=self.request_tokens,
            response=self.response_tokens,
            total=self.session_total,
        )

    def create_embedding(self, text: str, encoding_name: str = "cl100k_base") -> List[int]:
        """
        Creates an embedding for the given text using the specified encoding.

        Parameters:
            text (str): The input text to create an embedding for.
            encoding_name (str, optional): The name of the encoding to use. Defaults to "cl100k_base".

        Returns:
            List[int]: The encoded representation of the input text.
        """
        encoding = tiktoken.get_encoding(encoding_name)
        return encoding.encode(text)

    def count_tokens(self, string: str, encoding_name: str = "cl100k_base") -> int:
        """
        Counts the number of tokens in a given string using the specified encoding.

        Parameters:
            string (str): The input string to count the tokens of.
            encoding_name (str, optional): The name of the encoding to use. Defaults to "cl100k_base".

        Returns:
            int: The number of tokens in the input string.
        """
        encoding: tiktoken.Encoding = tiktoken.get_encoding(encoding_name=encoding_name)
        return len(encoding.encode(text=string))
