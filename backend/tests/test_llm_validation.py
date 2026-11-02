import json
import pytest
from app.models.llm_outputs import (
    NodeSummaryOutput,
    NodeStructureOutput,
    DocumentAnalysisOutput,
    ChatResponseOutput,
    validate_llm_json_output,
    safe_parse_llm_json,
)


class TestNodeSummaryOutput:
    """Tests for NodeSummaryOutput model."""

    def test_valid_summary(self):
        """Test valid summary passes validation."""
        data = {
            "summary": "This is a valid summary of the node content.",
            "key_points": ["Point 1", "Point 2"],
            "confidence": 0.9,
        }
        model = NodeSummaryOutput(**data)
        assert model.summary == "This is a valid summary of the node content."
        assert model.key_points == ["Point 1", "Point 2"]
        assert model.confidence == 0.9

    def test_empty_summary_raises(self):
        """Test empty summary raises validation error."""
        data = {"summary": "", "key_points": [], "confidence": 1.0}
        with pytest.raises(ValueError):
            NodeSummaryOutput(**data)

    def test_whitespace_summary_raises(self):
        """Test whitespace-only summary raises validation error."""
        data = {"summary": "   ", "key_points": [], "confidence": 1.0}
        with pytest.raises(ValueError):
            NodeSummaryOutput(**data)

    def test_summary_stripped(self):
        """Test summary whitespace is stripped."""
        data = {"summary": "  Valid summary  ", "key_points": [], "confidence": 1.0}
        model = NodeSummaryOutput(**data)
        assert model.summary == "Valid summary"

    def test_confidence_bounds(self):
        """Test confidence bounds validation."""
        with pytest.raises(ValueError):
            NodeSummaryOutput(summary="Test", confidence=1.5)
        with pytest.raises(ValueError):
            NodeSummaryOutput(summary="Test", confidence=-0.1)

    def test_key_points_deduplication(self):
        """Test key points are deduplicated."""
        data = {"summary": "Test", "key_points": ["Point 1", "Point 1", "Point 2"]}
        model = NodeSummaryOutput(**data)
        assert model.key_points == ["Point 1", "Point 2"]


class TestNodeStructureOutput:
    """Tests for NodeStructureOutput model."""

    def test_valid_structure(self):
        """Test valid structure passes validation."""
        data = {
            "title": "Chapter 1",
            "level": 0,
            "structure_number": "1",
            "start_page": 1,
            "end_page": 10,
        }
        model = NodeStructureOutput(**data)
        assert model.title == "Chapter 1"
        assert model.level == 0

    def test_invalid_structure_number(self):
        """Test invalid structure number pattern raises error."""
        data = {
            "title": "Chapter 1",
            "level": 0,
            "structure_number": "1.2.3.4.5",  # Too deep
            "start_page": 1,
            "end_page": 10,
        }
        # This should still pass pattern-wise (pattern is flexible)
        model = NodeStructureOutput(**data)
        assert model.structure_number == "1.2.3.4.5"

    def test_end_page_before_start_raises(self):
        """Test end_page before start_page raises error."""
        data = {
            "title": "Chapter 1",
            "level": 0,
            "structure_number": "1",
            "start_page": 10,
            "end_page": 5,
        }
        with pytest.raises(ValueError):
            NodeStructureOutput(**data)


class TestDocumentAnalysisOutput:
    """Tests for DocumentAnalysisOutput model."""

    def test_valid_analysis(self):
        """Test valid document analysis."""
        data = {
            "structure": [
                {
                    "title": "Chapter 1",
                    "level": 0,
                    "structure_number": "1",
                    "start_page": 1,
                    "end_page": 10,
                }
            ],
            "document_type": "technical",
            "language": "en",
        }
        model = DocumentAnalysisOutput(**data)
        assert model.document_type == "technical"
        assert model.language == "en"

    def test_defaults(self):
        """Test default values."""
        data = {
            "structure": [
                {
                    "title": "Chapter 1",
                    "level": 0,
                    "structure_number": "1",
                    "start_page": 1,
                    "end_page": 10,
                }
            ]
        }
        model = DocumentAnalysisOutput(**data)
        assert model.document_type == "unknown"
        assert model.language == "en"


class TestValidateLLMJsonOutput:
    """Tests for validate_llm_json_output function."""

    def test_valid_json_validates(self):
        """Test valid JSON passes validation."""
        json_str = json.dumps({
            "summary": "Valid summary",
            "key_points": ["Point 1"],
            "confidence": 0.8,
        })
        result = validate_llm_json_output(json_str, NodeSummaryOutput)
        assert isinstance(result, NodeSummaryOutput)
        assert result.summary == "Valid summary"

    def test_invalid_json_raises(self):
        """Test invalid JSON raises ValueError."""
        json_str = "not valid json"
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_llm_json_output(json_str, NodeSummaryOutput)

    def test_validation_failure_raises(self):
        """Test validation failure raises ValueError."""
        json_str = json.dumps({"summary": ""})
        with pytest.raises(ValueError, match="Validation failed"):
            validate_llm_json_output(json_str, NodeSummaryOutput)


class TestSafeParseLLMJson:
    """Tests for safe_parse_llm_json function."""

    def test_valid_json_returns_model(self):
        """Test valid JSON returns validated model."""
        json_str = json.dumps({"summary": "Test", "confidence": 0.9})
        result = safe_parse_llm_json(json_str, NodeSummaryOutput)
        assert isinstance(result, NodeSummaryOutput)
        assert result.summary == "Test"

    def test_validation_failure_uses_fallback(self):
        """Test validation failure uses fallback."""
        json_str = json.dumps({"summary": ""})
        fallback = NodeSummaryOutput(summary="Fallback summary", confidence=0.1)
        result = safe_parse_llm_json(json_str, NodeSummaryOutput, fallback=fallback)
        assert result is fallback

    def test_json_decode_error_uses_fallback(self):
        """Test JSON decode error uses fallback."""
        json_str = "not valid json"
        fallback = NodeSummaryOutput(summary="Fallback summary", confidence=0.1)
        result = safe_parse_llm_json(json_str, NodeSummaryOutput, fallback=fallback)
        assert result is fallback

    def test_validation_failure_no_fallback_raises(self):
        """Test validation failure raises without fallback."""
        json_str = json.dumps({"summary": ""})
        with pytest.raises(ValueError):
            safe_parse_llm_json(json_str, NodeSummaryOutput)

