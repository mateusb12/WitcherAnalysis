from book_processing.entity_extractor import BookAnalyser
from book_processing.entity_filter import EntityFilter
from book_processing.relationship_creator import RelationshipCreator
from witcher_network.node_plot import NodePlot


class Wrapper:
    def __init__(self):
        self.book_analyser = BookAnalyser()
        self.entity_filter = EntityFilter()
        self.relationship_creator = RelationshipCreator()
        self.node_plot = NodePlot()
        self.book_number: int = 0

    def set_book(self, book_number: int):
        self.book_analyser.select_book(book_number)
        self.book_number = book_number

    def book_pipeline(self) -> None:
        entity_df = self.book_analyser.get_book_entity_df()
        self.entity_filter.set_entity_df(entity_df)
        df = self.entity_filter.export_filtered_dataframe()
        self.relationship_creator.set_entity_df(df)
        relationship_df = self.relationship_creator.aggregate_network()
        self.node_plot.set_network_df(relationship_df)
        self.node_plot.pipeline()

    def get_centrality(self) -> dict:
        return self.node_plot.get_centrality()

    def plot(self) -> None:
        self.node_plot.plot()


def __main():
    w = Wrapper()
    w.set_book(3)
    w.book_pipeline()
    w.plot()
    print("wow")


if __name__ == "__main__":
    __main()
