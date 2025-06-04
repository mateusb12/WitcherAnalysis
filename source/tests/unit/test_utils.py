import unittest
from pathlib import Path
import pandas as pd
import tempfile

from utils.csv_utils import load_csv_text_example, convert_string_to_dataframe
from utils.time_utils import convert_time_format
from utils.folder_utils import handle_new_folder
from utils.relationship_utils import (
    bidirectional_sort,
    get_source_target_relationship_list,
    remove_string_duplicates
)
from utils.entity_utils import (
    convert_to_list,
    cast_to_str,
    filter_entity_df
)


class TestCsvUtils(unittest.TestCase):
    """Tests for csv_utils.py functions."""

    def test_load_csv_text_example(self):
        """Test that the load_csv_text_example function returns a non-empty string."""
        csv_text = load_csv_text_example()
        self.assertIsInstance(csv_text, str)
        self.assertGreater(len(csv_text), 0)
        self.assertIn('book,character,character_first_name', csv_text)

    def test_convert_string_to_dataframe(self):
        """Test conversion of CSV string to pandas DataFrame."""
        test_csv = "col1,col2\nval1,val2\nval3,val4"
        df = convert_string_to_dataframe(test_csv)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertEqual(list(df.columns), ['col1', 'col2'])
        self.assertEqual(df.iloc[0, 0], 'val1')
        self.assertEqual(df.iloc[1, 1], 'val4')


class TestTimeUtils(unittest.TestCase):
    """Tests for time_utils.py functions"""

    def test_convert_time_format_seconds_only(self):
        """Test conversion when there are only seconds"""
        result = convert_time_format("00:00:45")
        self.assertEqual(result, "45s")

    def test_convert_time_format_minutes_and_seconds(self):
        """Test conversion when there are minutes and seconds"""
        result = convert_time_format("00:05:30")
        self.assertEqual(result, "5min30s")

    def test_convert_time_format_hours_minutes_seconds(self):
        """Test conversion with hours, minutes and seconds"""
        result = convert_time_format("02:15:10")
        self.assertEqual(result, "2h15min10s")

    def test_convert_time_format_invalid_input(self):
        """Test handling of invalid input"""
        result = convert_time_format("invalid")
        self.assertEqual(result, "Invalid time format")

        result = convert_time_format("01:02")
        self.assertEqual(result, "Invalid time format")


class TestFolderUtils(unittest.TestCase):
    """Tests for folder_utils.py functions"""

    def test_handle_new_folder(self):
        """Test creating a new folder with __init__.py file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            new_folder = test_dir / "new_folder"
            test_file = new_folder / "test_file.txt"

            # Ensure the folder doesn't exist
            self.assertFalse(new_folder.exists())

            # Call the function to create the folder
            handle_new_folder(test_file)

            # Check that the folder and __init__.py were created
            self.assertTrue(new_folder.exists())
            self.assertTrue((new_folder / "__init__.py").exists())


class TestRelationshipUtils(unittest.TestCase):
    """Tests for relationship_utils.py functions."""

    def test_bidirectional_sort(self):
        """Test sorting of bidirectional relationships in a DataFrame"""
        input_df = pd.DataFrame({
            'source': ['A', 'B', 'C'],
            'target': ['B', 'A', 'D']
        })

        sorted_df = bidirectional_sort(input_df)

        # Check the first row with A and B should have them alphabetically sorted
        self.assertEqual(sorted_df.iloc[0, 0], 'A')
        self.assertEqual(sorted_df.iloc[0, 1], 'B')

        # Check the second row with B and A should be sorted to A and B
        self.assertEqual(sorted_df.iloc[1, 0], 'A')
        self.assertEqual(sorted_df.iloc[1, 1], 'B')

        # The third row should remain as is since C and D are already in order
        self.assertEqual(sorted_df.iloc[2, 0], 'C')
        self.assertEqual(sorted_df.iloc[2, 1], 'D')

    def test_get_source_target_relationship_list_empty(self):
        """Test getting relationships from an empty list."""
        result = get_source_target_relationship_list([])
        self.assertEqual(result, [])

    def test_get_source_target_relationship_list_single_item(self):
        """Test getting relationships from a list with one item."""
        result = get_source_target_relationship_list(['A'])
        self.assertEqual(result, [])

    def test_get_source_target_relationship_list_multiple_items(self):
        """Test getting relationships from a list with multiple items."""
        result = get_source_target_relationship_list(['A', 'B', 'C'])
        expected = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'C'}
        ]
        self.assertEqual(result, expected)

    def test_remove_string_duplicates(self):
        """Test removing duplicate strings from a list."""
        input_list = ['A', 'A', 'B', 'C', 'C', 'D']
        result = remove_string_duplicates(input_list)
        expected = ['A', 'B', 'C']
        self.assertEqual(result, expected)

    def test_remove_string_duplicates_empty(self):
        """Test removing duplicates from an empty list."""
        result = remove_string_duplicates([])
        self.assertEqual(result, [])

    def test_remove_string_duplicates_no_duplicates(self):
        """Test removing duplicates when there are none."""
        input_list = ['A', 'B', 'C']
        result = remove_string_duplicates(input_list)
        expected = ['A', 'B']
        self.assertEqual(result, expected)


class TestEntityUtils(unittest.TestCase):
    """Tests for entity_utils.py functions."""

    def test_cast_to_str(self):
        """Test casting a list to string."""
        result = cast_to_str(['A', 'B', 'C'])
        self.assertEqual(result, "['A', 'B', 'C']")

    def test_convert_to_list_from_string(self):
        """Test converting a string representation to a list."""
        result = convert_to_list("['A', 'B', 'C']")
        self.assertEqual(result, ['A', 'B', 'C'])

    def test_convert_to_list_already_list(self):
        """Test converting when already a list."""
        result = convert_to_list(['A', 'B', 'C'])
        self.assertEqual(result, ['A', 'B', 'C'])

    def test_filter_entity_df(self):
        """Test filtering entities based on DataFrame"""
        # Create a test character DataFrame
        characters_df = pd.DataFrame({
            'character': ['John Smith', 'Jane Doe', 'Robert Johnson'],
            'character_first_name': ['John', 'Jane', 'Robert']
        })

        # Test filtering with full names
        entity_list = "['John Smith', 'Unknown Person', 'Jane Doe']"
        result = filter_entity_df(entity_list, characters_df)
        self.assertEqual(result, ['John Smith', 'Jane Doe'])

        # Test filtering with first names
        entity_list = "['John', 'Unknown', 'Robert']"
        result = filter_entity_df(entity_list, characters_df)
        self.assertEqual(result, ['John', 'Robert'])


if __name__ == '__main__':
    unittest.main()
