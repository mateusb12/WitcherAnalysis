import enum
from pathlib import Path

import networkx as nx
import pandas as pd
from pyvis.network import Network
import community as community_louvain

from nlp_processing.entity_analysis.relationship_creator import get_network_df
from path_reference.folder_reference import get_book_graphs_path


class Centrality(enum.Enum):
    degree = 1
    betweenness = 2
    closeness = 3


class NodePlot:
    """This class is used to plot the networkx graph using pyvis library."""
    def __init__(self):
        self.network_df = None
        self.net = None
        self.G = None
        self.degree_dict = {}
        self.betweenness_dict = {}
        self.closeness_dict = {}

    def set_network_df(self, input_df: pd.DataFrame):
        self.network_df = input_df
        if 'value' not in self.network_df.columns:
            raise ValueError("The input dataframe must contain a 'value' column")
        self.G = nx.from_pandas_edgelist(self.network_df, source="source", target="target", edge_attr="value",
                                         create_using=nx.Graph())

    def __set_node_size(self):
        node_degree = dict(self.G.degree)
        nx.set_node_attributes(self.G, node_degree, 'size')

    def __set_centrality_measures(self):
        self.degree_dict = nx.degree_centrality(self.G)
        self.betweenness_dict = nx.betweenness_centrality(self.G)
        self.closeness_dict = nx.closeness_centrality(self.G)
        nx.set_node_attributes(self.G, self.degree_dict, 'degree_centrality')
        nx.set_node_attributes(self.G, self.betweenness_dict, 'betweenness_centrality')
        nx.set_node_attributes(self.G, self.closeness_dict, 'closeness_centrality')

    def __set_communities(self):
        communities = community_louvain.best_partition(self.G)
        nx.set_node_attributes(self.G, communities, 'group')

    def pipeline(self):
        self.__set_node_size()
        self.__set_centrality_measures()
        self.__set_communities()

    def plot(self, book_name: str = "2 The Sword of Destiny"):
        self.pipeline()
        self.net = Network(notebook=False, width="2000px", height="1400px", bgcolor="#222222", font_color="white")
        self.net.from_nx(self.G)
        book_path = Path(get_book_graphs_path(), f"{book_name}.html")
        self.net.show(str(book_path), notebook=False)

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
    df = get_network_df()
    npl.set_network_df(df)
    npl.plot()


if __name__ == "__main__":
    __main()
