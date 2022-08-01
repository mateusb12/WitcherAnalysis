import networkx as nx
from pyvis.network import Network
from nlp.relationship_creator import get_network_df


class NodePlot:
    def __init__(self):
        self.network_df = get_network_df()
        self.G = nx.from_pandas_edgelist(self.network_df, source="source", target="target", edge_attr="value",
                                         create_using=nx.Graph())
        self.net = Network(notebook=True, width="1000px", height="700px", bgcolor="#222222", font_color="white")

    def __set_node_size(self):
        node_degree = dict(self.G.degree)
        nx.set_node_attributes(self.G, node_degree, 'size')

    def __set_centrality_measures(self):
        degree_dict = nx.degree_centrality(self.G)
        betweenness_dict = nx.betweenness_centrality(self.G)
        closeness_dict = nx.closeness_centrality(self.G)
        nx.set_node_attributes(self.G, degree_dict, 'degree_centrality')
        nx.set_node_attributes(self.G, betweenness_dict, 'betweenness_centrality')
        nx.set_node_attributes(self.G, closeness_dict, 'closeness_centrality')

    def plot(self):
        self.net.from_nx(self.G)
        self.net.show("witcher.html")

