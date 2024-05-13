# Eden Subnet 10

## Ebbeddings

We are starting off our subnet with embedding miners. They quite simply use embedding functions to produce embeddings of tokens for storage in vectorstores. Phase two of our subnet will be to use those embedding miners to begin a distributed vecotor store. Our plan is to have knowledge stores in different domains referenced on chain to miners providing the data as a service to LLMs. 

## Miner

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

This was built by [Eden](https://twitter.com/project_eden_ai) in parternship with [Agent Artificial](https://agentartificial.com)

It is a subnet of [Commune](https://github.com/commune-ai/commune), an open source decentralized blockchain. The repo is based on the [Communex Synthia repo](https://github.com/agicommies/synthia). Special thanks to the team over at [Communex](https://github.com/agicommies) for their on going assistance in puzzling all this out. 

If you'd like to contribute please make a pull request detailing any changes you've made or open an issue so we can hash out how to make a larger change. 


