import enum

import networkx as nx
from pyvis.network import Network
from nlp.relationship_creator import get_network_df
import community as community_louvain


class Centrality(enum.Enum):
    degree = 1
    betweenness = 2
    closeness = 3


class NodePlot:
    def __init__(self):
        self.network_df = get_network_df()
        self.G = nx.from_pandas_edgelist(self.network_df, source="source", target="target", edge_attr="value",
                                         create_using=nx.Graph())
        self.net = None

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

    def __set_communities(self):
        communities = community_louvain.best_partition(self.G)
        nx.set_node_attributes(self.G, communities, 'group')

    def __pipeline(self):
        self.__set_node_size()
        self.__set_centrality_measures()
        self.__set_communities()

    def plot(self):
        self.__pipeline()
        self.net = Network(notebook=False, width="2000px", height="1400px", bgcolor="#222222", font_color="white")
        self.net.from_nx(self.G)
        self.net.show("witcher.html")

    def get_centrality(self, input_type: Centrality = Centrality.degree) -> dict or None:
        if input_type == Centrality.degree:
            return nx.get_node_attributes(self.G, 'degree_centrality')
        elif input_type == Centrality.betweenness:
            return nx.get_node_attributes(self.G, 'betweenness_centrality')
        elif input_type == Centrality.closeness:
            return nx.get_node_attributes(self.G, 'closeness_centrality')
        else:
            return None


def __main():
    npl = NodePlot()
    npl.plot()


if __name__ == "__main__":
    __main()
