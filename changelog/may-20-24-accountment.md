# Update

**📢** We’re pleased to announce some changes to operations on the server this week! **📢**

## 🗳 Change in voting mechanics

We are approaching our server cap of 820, so in order to give everyone a fair chance at mining on the subnet, we’ve implemented a modifier that reduces your score relative to the number of miners launched. This will step down your score by 1 point per miner, affecting miners 11 (-1), 12 (-2) and so on, with a floor of 27 (the range is currently between 33-27). Some users have launched upwards of 90 miners on the server, and while we respect their tenacity, we want to ensure everyone has an opportunity to mine. Since our subnet is still maturing, our inference is not so demanding that the hardware is a limitation. This artificial limitation will help provide a metric for churn, and will require users to consider if the burn cost for launching 100 miners is worth it for the return, as lower ranked miners will be at risk of being knocked off the subnet. We started with a limited drop down but will be monitoring the situation closely and adjusting as needed. We are particularly interested in the long-term effects when we hit the server cap, but will not be expecting any major effects until then.

## **🎛 A**djustment to subnet parameters

We have also increased the set weight limit to just over the server's capacity. This enables a single validator to score the entire network, which we have configured to be performed on a rotating basis to keep the scores maintained. Over the weekend we exceeded the set weight limit, which caused issues when setting weights. Rotating between two groups of miners only caused half the network to not be getting emissions at any given time, even when synchronizing validator voting block alternation. This is a simple and straightforward solution to the issue without reducing the miners currently allowed on the subnet. Our overall goal for miner emissions would be slightly below the burn costs, while inference requirements are low to further discourage spamming the server. Once we implement the front end inference (coming soon!) and distributed vector storage miner, we will look at reducing the server limit to reward users for the additional work. Until then, enjoy the ease of mining!

## 🎢 All miners immediately onboarded

Corrected the onboarding loop so that validators dynamically grab everyone at once. The cohort system of onboarding miners is gone. Now everyone gets pulled every iteration cycle. Please note that information source likes ComStats dot org may not update in real time and there may be a lag before your miners display emissions, but the wait times are much shorter. 

# 🔧 Hotfix

An update for the launch utility. Commex updated their library which was a breaking change for the utility; the script now updates the library for you, so just pull the repo and run it.

If you recently launched miners be sure to double check their host and port information. You can check it with 
`comx misc stats —netuid 10`

This pulls your active keys and displays the module information registered with the chain. If you have your address registered as **None:None**, **127.0.0.1** or or host set to **[0.0.0.0](https://0.0.0.0)** you will notice you don’t receive emissions. This is because the validators are not on your local network and cant hit the miner so ranks it at 0. You can update the registered information on the chain with the **launch utilitiy** under option **8.**

## **📆 F**uture Plans **⏳**

### **👷🏽‍♂️S**ome other things we are working on:

- **⛩** We are building a gateway to help synchronize the validators on the subnet. Doing this manually is time consuming at best, and harrowing the rest of the time. We need a secure way to average the weights of the validators and maintain a whitelist to prevent any possible bad actors from disrupting our services. This whitelist will be available for anyone to apply to; no requirements other than the **global minimum** stake *(5200 com for validators and 256 for miners)* and a quick chat and handshake to ensure you're someone known in the community. We’re not expecting a large volume of validator applications since they are difficult to configure. Plus **👷🏽‍♀️**miners earn more emissions with less work. If server coverage becomes an issue, we may look at adjusting the incentive ratio, but we'd prefer not to as our high miner cap has the emissions spread thin as it is.
- **📄**Front end consumer for the vector embeddings. We have completed a front end to consume the vector data that will ultimately make up the subnet's foundational offering. It will be up in development today, and we should be ready to release early next week. This is a chat interface that performs a semantic search of uploaded documents. The documents are pulled and displayed for reference and cross-checking information, and a **🤖**language model interprets the information for you as your personal archivist.

Thanks for your ongoing support and we look forward to continue building **🌱**Eden into something really cool. **🦾**