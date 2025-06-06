import os
from pathlib import Path

import django
import pandas as pd
from unittest.mock import patch
import tempfile

import pytest

from scripts.runner import Runner


@pytest.fixture(scope="module")
def test_dir():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.project_config')
    django.setup()
    return tempfile.mkdtemp()


def test_full_pipeline(test_dir):
    """Test book processing from load to plot generation"""
    with patch('path_reference.folder_reference.get_book_graphs_path', return_value=test_dir):
        print(f"Patched path: {test_dir}")

        runner = Runner(series="witcher")
        runner.load_book(book_number=4)

        assert runner.book_number == 4
        assert runner.book_name == "5 Baptism of Fire"

        centrality_df = runner.process_entities()

        assert isinstance(centrality_df, pd.DataFrame)
        assert len(centrality_df) > 0
        assert "Geralt" in centrality_df.index

        runner.plot()

        expected_file = Path(test_dir) / f"{runner.book_name}.html"
        print(f"Expected file path: {expected_file}")
        assert expected_file.exists(), "Plot file not created"


@patch('nlp_processing.entity_analysis.relationship_creator.RelationshipBuilder.aggregate_network')
@patch('nlp_processing.entity_analysis.book_manager.BookManager.get_book_entities')
def test_mocked_processing(mock_get_entities, mock_aggregate_network):
    """Test with mocked dependencies for faster execution"""
    mock_entity_data = pd.DataFrame({
        "entities": [["Geralt", "Yennefer"], ["Ciri"], ["Geralt", "Triss"]],
        "character_entities": [["Geralt", "Yennefer"], ["Ciri"], ["Geralt", "Triss"]]
    })
    mock_network_data = pd.DataFrame({
        "source": ["Geralt", "Yennefer"],
        "target": ["Yennefer", "Ciri"],
        "value": [5, 3]
    })

    mock_get_entities.return_value = mock_entity_data
    mock_aggregate_network.return_value = mock_network_data

    runner = Runner(series="witcher")
    runner.load_book(4)
    centrality_df = runner.process_entities()

    assert isinstance(centrality_df, pd.DataFrame)
    assert len(centrality_df) > 0
    assert "Geralt" in centrality_df.index
