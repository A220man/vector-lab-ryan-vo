"""Tests for index routes validation endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestValidateSummaryEndpoint:
    """Tests for POST /validate-summary endpoint."""

    def test_valid_json_validates(self):
        """Test valid JSON passes validation."""
        request_data = {
            "node_content": "Test content",
            "llm_json": '{"summary": "Valid summary", "key_points": ["Point 1", "Point 2"], "confidence": 0.9}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["fallback_used"] is False
        assert data["summary"]["summary"] == "Valid summary"
        assert data["summary"]["key_points"] == ["Point 1", "Point 2"]
        assert data["summary"]["confidence"] == 0.9

    def test_whitespace_summary_stripped(self):
        """Test whitespace in summary is stripped."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "  Trimmed summary  ", "key_points": [], "confidence": 0.8}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["fallback_used"] is False
        assert data["summary"]["summary"] == "Trimmed summary"

    def test_empty_summary_uses_fallback(self):
        """Test empty summary field returns fallback."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "", "key_points": ["Point 1"]}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["fallback_used"] is True

    def test_whitespace_only_summary_uses_fallback(self):
        """Test whitespace-only summary returns fallback."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "   ", "key_points": ["Point 1"]}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["fallback_used"] is True

    def test_missing_summary_uses_fallback(self):
        """Test missing summary field returns fallback."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"key_points": ["Point 1"]}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["fallback_used"] is True

    def test_invalid_json_returns_error(self):
        """Test invalid JSON returns error."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "Valid", "key_points": }'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["fallback_used"] is True

    def test_invalid_confidence_bounds_uses_fallback(self):
        """Test confidence out of bounds returns fallback."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "Valid summary", "confidence": 1.5}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["fallback_used"] is True

    def test_minimal_valid_json(self):
        """Test minimal valid JSON with only summary."""
        request_data = {
            "node_content": "Content",
            "llm_json": '{"summary": "Minimal valid"}'
        }
        response = client.post("/api/v1/index/validate-summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["fallback_used"] is False
        assert data["summary"]["summary"] == "Minimal valid"
        assert data["summary"]["key_points"] == []
        assert data["summary"]["confidence"] == 1.0
