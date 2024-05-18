# Eden Subnet 10

## Introduction

The Eden Subnet simplifies the way machines learn and manage data through its Commune Subnet, which centers around a Vector Store. Think of it as creating memories for AI: it takes textual content—such as PDFs, markdown, and text files—transforms them into embeddings, and stores them for AI retrieval. This is part of a process known as Retrieval-Augmented Generation (RAG), crucial for enhancing AI interactions.

Beyond this fundamental operation, the Vector Store serves as a crucial repository for embeddings—dense numerical representations of text tokens produced by machine learning algorithms. As a key component of a broader AI ecosystem, it significantly improves the accessibility and utility of data for large language models (LLMs) and other AI systems. The store is populated and maintained by dedicated nodes called "embedding miners," who are instrumental in ensuring the availability of high-quality, semantically rich embeddings. These miners, along with validators, play a vital role in generating and refining these embeddings to power a variety of AI-driven applications and innovations.

The strength of this subnet lies in its ability to enhance AI capabilities through Retrieval-Augmented Generation (RAG). By integrating this mechanism, AI agents, chatbots, and tools can expand their understanding and discuss topics outside their inherent knowledge base, simply by referencing materials like PDFs. This approach is computationally efficient compared to the alternatives of training new models or manually incorporating extensive documents into a model’s context window.

Vector stores play a crucial role in augmenting the abilities and knowledge base of existing AI models. We incentivize miners to deliver high-quality embedding services, rewarding them based on the excellence of their contributions. This not only enhances the overall quality of AI interactions but also creates a win-win situation for both miners and AI developers.

## Future Work

We are initiating our subnet by deploying simple embedding miners. These miners utilize embedding functions to generate token embeddings, which are then stored in vectorstores. The second phase of our project involves leveraging these embedding miners to establish a distributed vector store. Our strategy includes creating domain-specific knowledge stores, which will be indexed on the blockchain. These stores will provide data as a service to large language models (LLMs). Additionally, we are exploring the integration of knowledge graphs and the storage of synthetic data. Potential collaborations are being considered, including one with the Synthia subnet, to enhance our capabilities in synthetic data handling.

## Setup Instructions

Once you clone the repo you need to copy the `eden.py` file from `eden_subnet/miner/eden.py` to whatever the first part of your name is going to be.

Example: 
`cp eden_subnet/miner/eden.py eden_subnet/miner/my_miner.py`

Inside of that file you need to change the class name from  `Miner_1` to whatever you want the second part of the name to be.

Example:
```class Miner_1(Miner):    >    class BobTheMiner(Miner): ...
    ...                           ...
```

that determines the key name and module path so in the example it would be 
my_miner.BobTheMiner
then you need to make a key
comx key create my_miner.BobTheMiner
then you need to register the miner 
comx module register my_miner.BobTheMiner my_miner.BobTheMiner 66.235.35.363 8000 --netuid 10
after that you need to serve it with
python -m eden_subnet.cli --key_name my_miner.BobTheMiner my_miner.BobTheMiner --host 0.0.0.0 --port 8000
or you can call the file directly 
python -m eden_subnet/miner/my_miner --key_name my_miner.BobTheMiner --host 0.0.0.0 --port 8000

## Embedding Miner

Base miner is in the [miner](eden_subnet/miner/miner.py) folder. Copy the class `Miner` and pass it the `MinerSettings` class to deploy your own version. The repo references the position of the miner class and the file it resides in through a naming convention of the miner. Use <FILE_NAME>.<CLASS_NAME> for both the name of the key you are staking with and the file/class name of the code to your miner. 
To launch your miner run 
`python -m eden_subnet.cli serve-miner miner.Miner miner.Miner 0.0.0.0 10001`

That command will serve a miner listening on all ip addresses(use 0.0.0.0 for serving and your machines actual ip for registering) on port 10001. The miner code is located in `eden_subnet.miner.miner` and inside of that script there is a class called `Miner` that is being served.

Ensure the key has the same name and the file in the miner directory has the first word of your miner name and the class inside of that file is the second. Open the port and you should be good to go. 

There is also a docker compose that will deploy validators and miners. You will have to adjust the key_names on the docker files along with the port to your specific specifications to use it. 

## Validator

The Validator generates a random allegory based on some topics that change regularly and produces embeddings locally before making a request to a miner. It then compares the two using a semantic similarity of the vectors and provides a score. Then it takes the scores of the whole subnet and calculates your position based on how well your embedder did and how that stands up against the rest of the subnet adjusting the weights accordingly.

The validator is served similarly to the miner with 
`python -m eden_subnet.cli server-validator validator.Validator validator.Validator 0.0.0.0 10010`

Like the miner the validator will serve the class `Validator` which lives in a folder `eden_subnet.validator.validator` and provide that on port 10010 listening on all ip's

## Registering

Once you confirm that you can run the validator and/or miner you need to register the module with the subnet. use the command

`comx module register KEY_NAME MODULE_PATH HOST_IP PORT --netuid 10 --stake AMOUNT`

So for our example with the miner we would provide our actual ip address and copy the information accordingly

`comx module register miner.Miner miner.Miner 66.224.58.25 10010 --netuid 10 --stake 256`


## Notes

There is a global burn fee for registering modules(miners and validators are both modules) based on demand. Currently the base rate is 10com and it doubles every threshold amount reached per epoch. You'll want to ensure you have enough to cover that cost for miners. 

If you would like to run validator we would appreciate the assistance in subnet coverage. The staking amount for voting with a validator is 5000 so you will need to have the burn fee which varies based on demand and along with the minimum vote requirement or you will not be able to run your validator. Any anomalous or strange behavior of validators will be investigated and any self voting or gaming the system will result in being added to the black list. 

Everyone should start off on pretty even footing as there is not a wild difference in embedding model. So the tie breaker is how much stake you have on the miner. Pulling all your stake off a miner will not be wise if you do not want to get bumped off the subnet. That will be replaced with how much storage you are providing to the network as the features roll out. 

If you have any questions or concerns please contact coolrazor or bakobiibizo on discord or send an email to info@agentartificial.com

## Contributions

This was built by [Eden](https://twitter.com/project_eden_ai) in partnernship with [Agent Artificial](https://agentartificial.com)

It is a subnet of [Commune](https://github.com/commune-ai/commune), an open source decentralized blockchain. The repo is based on the [Communex Synthia repo](https://github.com/agicommies/synthia). Special thanks to the team over at [Communex](https://github.com/agicommies) for their on going assistance in puzzling all this out. 

If you'd like to contribute please make a pull request detailing any changes you've made or open an issue so we can hash out how to make a larger change. 


