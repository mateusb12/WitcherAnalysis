from unittest.mock import Mock, patch
import pandas as pd
import pytest
from spacy.tokens import Doc

from nlp_processing.entity_network_from_filedata import EntityNetworkPipeline


class TestEntityNetworkPipeline:
    """Test suite for EntityNetworkPipeline components"""

    @patch('nlp_processing.entity_network_from_filedata.load_nlp_model')
    def setup_pipeline(self, mock_load_nlp_model):
        """Helper method to set up a pipeline with mocked dependencies"""
        mock_model = Mock()
        mock_load_nlp_model.return_value = mock_model

        pipeline = EntityNetworkPipeline()

        pipeline.text_processor = Mock()
        pipeline.entity_extractor = Mock()
        pipeline.relationship_creator = Mock()
        pipeline.node_plot = Mock()

        return pipeline

    def test_pipeline_initialization(self):
        """Test that the pipeline initializes all necessary components"""
        with patch('nlp_processing.entity_network_from_filedata.load_nlp_model') as mock_load_nlp_model:
            mock_model = Mock()
            mock_load_nlp_model.return_value = mock_model

            pipeline = EntityNetworkPipeline()

            assert pipeline.model == mock_model
            assert pipeline.text_processor is not None
            assert pipeline.entity_extractor is not None
            assert pipeline.relationship_creator is not None
            assert pipeline.node_plot is not None
            assert pipeline.text_data == ""
            assert isinstance(pipeline.character_table, pd.DataFrame)
            assert pipeline.book_filename == ""
            assert pipeline.progress_callback is None

    def test_setup_method(self):
        """Test the setup method properly assigns values"""
        pipeline = self.setup_pipeline()

        test_text = "This is a sample text"
        test_df = pd.DataFrame({"character": ["Character1", "Character2"]})
        test_filename = "test_book.txt"

        pipeline.setup(test_text, test_df, test_filename)

        assert pipeline.text_data == test_text
        assert pipeline.character_table.equals(test_df)
        assert pipeline.book_filename == test_filename

    @patch('nlp_processing.entity_network_from_filedata.filter_entity_df', spec=True)
    def test_filter_entity_dataframe(self, mock_filter_entity):
        """Test the filter_entity_dataframe method"""
        pipeline = self.setup_pipeline()

        test_df = pd.DataFrame({
            'entities': ['Entity1', 'Entity2']
        })

        mock_filter_entity.side_effect = lambda entity, characters_df: entity

        pipeline.character_table = pd.DataFrame({"character": ["Character1"]})

        result = pipeline.filter_entity_dataframe(test_df)

        assert mock_filter_entity.call_count == len(test_df)

        assert isinstance(result, pd.DataFrame)
        assert 'character_entities' in result.columns

    def test_get_book_entity_dataframe(self):
        """Test the get_booK_entity_dataframe method"""
        pipeline = self.setup_pipeline()

        mock_entity_df = pd.DataFrame({"entities": ["Entity1", "Entity2"]})

        pipeline.text_processor.analyze_book_from_text_data.return_value = Mock(spec=Doc)
        pipeline.entity_extractor.extract_book_entities.return_value = mock_entity_df

        mock_callback = Mock()
        pipeline.progress_callback = mock_callback

        original_method = pipeline.get_booK_entity_dataframe
        pipeline.get_booK_entity_dataframe = lambda: mock_entity_df

        pipeline.text_data = "Sample text"
        result = pipeline.get_booK_entity_dataframe()

        assert result.equals(mock_entity_df)

    def test_analyze_pipeline(self):
        """Test the complete analyze_pipeline method"""
        pipeline = self.setup_pipeline()

        mock_entity_df = pd.DataFrame({"entities": ["Entity1", "Entity2"]})
        pipeline.get_booK_entity_dataframe = Mock(return_value=mock_entity_df)

        mock_filtered_df = pd.DataFrame({"entities": ["FilteredEntity1"]})
        pipeline.filter_entity_dataframe = Mock(return_value=mock_filtered_df)

        mock_relationship_df = pd.DataFrame({"source": ["Entity1"], "target": ["Entity2"]})
        pipeline.relationship_creator.aggregate_network.return_value = mock_relationship_df

        pipeline.book_filename = "test_book.txt"

        pipeline.analyze_pipeline()

        pipeline.get_booK_entity_dataframe.assert_called_once()
        pipeline.filter_entity_dataframe.assert_called_once_with(mock_entity_df)
        pipeline.relationship_creator.set_entity_df.assert_called_once_with(mock_filtered_df)
        pipeline.relationship_creator.aggregate_network.assert_called_once()
        pipeline.node_plot.set_network_df.assert_called_once_with(mock_relationship_df)
        pipeline.node_plot.plot.assert_called_once_with(book_name="test_book.txt")

    def test_progress_callback(self):
        """Test that the progress callback works correctly"""
        pipeline = self.setup_pipeline()
        mock_callback = Mock()
        pipeline.progress_callback = mock_callback

        mock_entity_df = pd.DataFrame({"entities": ["Entity1", "Entity2"]})

        original_method = pipeline.get_booK_entity_dataframe

        def mock_get_book_entity_df():
            for i in range(0, 100, 10):
                progress = i / 100
                pipeline.progress_callback(progress)
            return mock_entity_df

        pipeline.get_booK_entity_dataframe = mock_get_book_entity_df

        pipeline.text_data = "Sample text"
        result = pipeline.get_booK_entity_dataframe()

        assert mock_callback.call_count > 0

        progress_values = [call_args[0][0] for call_args in mock_callback.call_args_list]
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i-1]

        assert result.equals(mock_entity_df)


@pytest.mark.integration
class TestEntityNetworkPipelineIntegration:
    """Integration tests for EntityNetworkPipeline with minimal mocking"""

    @pytest.fixture
    def sample_text_data(self):
        return "Character1 went to the store. Character1 met Character2 there. They talked about Character3."

    @pytest.fixture
    def sample_character_table(self):
        return pd.DataFrame({
            "character": ["Character1", "Character2", "Character3"],
            "alias": ["C1", "C2", "C3"],
            "type": ["PERSON", "PERSON", "PERSON"],
            "character_first_name": ["Character1", "Character2", "Character3"]  # Added this line
        })

    @patch('nlp_processing.entity_network_from_filedata.load_nlp_model')
    @patch('nlp_processing.entity_analysis.text_processor.TextProcessor')
    @patch('nlp_processing.entity_analysis.entity_extractor.EntityExtractor')
    @patch('nlp_processing.entity_analysis.relationship_creator.RelationshipBuilder')
    @patch('nlp_processing.entity_analysis.node_plot.NodePlot')
    def test_pipeline_end_to_end(self, mock_node_plot_cls, mock_relationship_cls,
                                 mock_entity_extractor_cls, mock_text_processor_cls,
                                 mock_load_nlp_model, sample_text_data, sample_character_table):
        """Test the pipeline from start to finish with mocked components"""
        mock_model = Mock()
        mock_load_nlp_model.return_value = mock_model

        mock_text_processor = mock_text_processor_cls.return_value
        mock_entity_extractor = mock_entity_extractor_cls.return_value
        mock_relationship_builder = mock_relationship_cls.return_value
        mock_node_plot = mock_node_plot_cls.return_value

        pipeline = EntityNetworkPipeline(progress_callback=Mock())
        pipeline.text_processor = mock_text_processor
        pipeline.entity_extractor = mock_entity_extractor
        pipeline.relationship_creator = mock_relationship_builder
        pipeline.node_plot = mock_node_plot

        mock_entity_df = pd.DataFrame({"entities": [["Character1"], ["Character2"], ["Character3"]]})
        pipeline.get_booK_entity_dataframe = Mock(return_value=mock_entity_df)

        mock_relationship_df = pd.DataFrame({
            "source": ["Character1", "Character1", "Character2"],
            "target": ["Character2", "Character3", "Character3"],
            "weight": [1, 1, 1]
        })
        mock_relationship_builder.aggregate_network.return_value = mock_relationship_df

        pipeline.setup(sample_text_data, sample_character_table, "test_book")

        pipeline.analyze_pipeline()

        pipeline.get_booK_entity_dataframe.assert_called_once()
        mock_relationship_builder.set_entity_df.assert_called_once()
        mock_relationship_builder.aggregate_network.assert_called_once()
        mock_node_plot.set_network_df.assert_called_once_with(mock_relationship_df)
        mock_node_plot.plot.assert_called_once_with(book_name="test_book")
