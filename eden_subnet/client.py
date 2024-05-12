from communex.client import CommuneClient
from communex._common import get_node_url

client = CommuneClient(get_node_url())

emissions = client.query_map_emission()
print(emissions[10])
miners = client.query_map_address()
print(miners[10])
