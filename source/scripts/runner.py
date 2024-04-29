import pandas as pd

from nlp_processing.entity_extractor import EntityExtractor
from nlp_processing.entity_filter import EntityFilter
from nlp_processing.relationship_creator import RelationshipCreator
from witcher_network.node_plot import NodePlot


class Runner:
    def __init__(self, series: str = "witcher"):
        """This class is the heart of the project. This class
        → 1. Reads the books and creates the entity dataframe
        → 2. Filters the entity dataframe, only including character entities
        → 3. Creates the network dataframe, stating who is connected to who
        → 4. Creates the network plot, storing the network in a .html file"""
        self.book_analyser = EntityExtractor()
        self.book_analyser.set_series(series)
        self.entity_filter = EntityFilter(series=series)
        self.relationship_creator = RelationshipCreator()
        self.node_plot = NodePlot()
        self.book_number: int = 0
        self.book_name = ""

    def set_book(self, book_number: int):
        self.book_analyser.select_book(book_number)
        self.book_number = book_number
        self.book_name = self.book_analyser.book_names_dict[self.book_number]

    def book_pipeline(self) -> pd.DataFrame:
        print("Entity dataframe analysis")
        entity_df = self.book_analyser.get_book_entity_table()
        self.entity_filter.set_entity_df(entity_df)
        print("Creating filtered dataframe")
        filtered_df = self.entity_filter.export_filtered_dataframe()
        self.relationship_creator.set_entity_df(filtered_df)
        print("Creating network dataframe")
        relationship_df = self.relationship_creator.aggregate_network()
        self.node_plot.set_network_df(relationship_df)
        self.node_plot.pipeline()
        degree_centrality_dict = self.node_plot.degree_dict
        return pd.DataFrame.from_dict(degree_centrality_dict, orient='index')

    def get_centrality(self) -> dict:
        return self.node_plot.get_centrality()

    def plot(self) -> None:
        self.node_plot.plot(self.book_name)


def __main():
    r = Runner("witcher")
    r.set_book(4)
    r.book_pipeline()
    r.plot()
    print("wow")


if __name__ == "__main__":
    __main()
