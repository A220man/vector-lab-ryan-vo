
"""
Tests for add_page_offset_to_toc_json function.
"""
import pytest
from app.services.indexing import add_page_offset_to_toc_json


class TestAddPageOffsetToTocJson:
    """Tests for add_page_offset_to_toc_json function."""

    def test_basic_offset(self):
        """Test basic page offset addition."""
        toc = [
            {"title": "Chapter 1", "page": 1},
            {"title": "Chapter 2", "page": 5},
            {"title": "Chapter 3", "page": 10},
        ]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] == 11
        assert result[1]["page"] == 15
        assert result[2]["page"] == 20
        # Original unchanged
        assert toc[0]["page"] == 1

    def test_none_page_values(self):
        """Test handling of None page values."""
        toc = [
            {"title": "Chapter 1", "page": 1},
            {"title": "Chapter 2", "page": None},
            {"title": "Chapter 3", "page": 5},
        ]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] == 11
        assert result[1]["page"] is None
        assert result[2]["page"] == 15

    def test_all_none_pages(self):
        """Test when all pages are None."""
        toc = [
            {"title": "Chapter 1", "page": None},
            {"title": "Chapter 2", "page": None},
        ]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] is None
        assert result[1]["page"] is None

    def test_nested_children(self):
        """Test recursive handling of nested children."""
        toc = [
            {
                "title": "Part 1",
                "page": 1,
                "children": [
                    {"title": "Chapter 1", "page": 2},
                    {"title": "Chapter 2", "page": None},
                ],
            },
            {"title": "Part 2", "page": 10},
        ]
        result = add_page_offset_to_toc_json(toc, 5)
        
        assert result[0]["page"] == 6
        assert result[0]["children"][0]["page"] == 7
        assert result[0]["children"][1]["page"] is None
        assert result[1]["page"] == 15

    def test_empty_list(self):
        """Test empty TOC list."""
        result = add_page_offset_to_toc_json([], 10)
        assert result == []

    def test_zero_offset(self):
        """Test zero offset returns copy."""
        toc = [{"title": "Chapter 1", "page": 5}]
        result = add_page_offset_to_toc_json(toc, 0)
        
        assert result[0]["page"] == 5
        assert result is not toc  # New list
        assert result[0] is not toc[0]  # New dict

    def test_negative_offset(self):
        """Test negative offset."""
        toc = [{"title": "Chapter 1", "page": 10}]
        result = add_page_offset_to_toc_json(toc, -5)
        
        assert result[0]["page"] == 5

    def test_non_integer_page_string(self):
        """Test string page that can be converted to int."""
        toc = [{"title": "Chapter 1", "page": "5"}]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] == 15

    def test_non_convertible_page(self):
        """Test non-convertible page value left unchanged."""
        toc = [{"title": "Chapter 1", "page": "invalid"}]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] == "invalid"

    def test_preserves_other_fields(self):
        """Test that other fields are preserved."""
        toc = [
            {
                "title": "Chapter 1",
                "page": 1,
                "level": 1,
                "id": "ch1",
                "metadata": {"author": "test"},
            }
        ]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["title"] == "Chapter 1"
        assert result[0]["level"] == 1
        assert result[0]["id"] == "ch1"
        assert result[0]["metadata"] == {"author": "test"}
        assert result[0]["page"] == 11

    def test_deeply_nested(self):
        """Test deeply nested children."""
        toc = [
            {
                "title": "Level 1",
                "page": 1,
                "children": [
                    {
                        "title": "Level 2",
                        "page": 2,
                        "children": [
                            {"title": "Level 3", "page": 3},
                        ],
                    },
                ],
            },
        ]
        result = add_page_offset_to_toc_json(toc, 10)
        
        assert result[0]["page"] == 11
        assert result[0]["children"][0]["page"] == 12
        assert result[0]["children"][0]["children"][0]["page"] == 13


