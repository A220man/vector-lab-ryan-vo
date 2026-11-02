"""
Pydantic models for validating LLM JSON outputs.
These models define the expected structure of LLM responses
used in the indexing pipeline and other AI features.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import json


class NodeSummaryOutput(BaseModel):
    """Expected output structure for node summary generation."""
    summary: str = Field(..., min_length=1, max_length=5000, description="Concise summary of the node content")
    key_points: List[str] = Field(default_factory=list, max_length=10, description="Key points extracted from the content")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for the summary quality")

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    @field_validator("key_points")
    @classmethod
    def key_points_unique(cls, v: List[str]) -> List[str]:
        seen = set()
        result = []
        for point in v:
            point = point.strip()
            if point and point not in seen:
                seen.add(point)
                result.append(point)
        return result


class NodeStructureOutput(BaseModel):
    """Expected output structure for document structure analysis."""
    title: str = Field(..., min_length=1, max_length=512)
    level: int = Field(..., ge=0, le=6, description="Heading level (0=chapter, 1=section, etc.)")
    structure_number: str = Field(..., pattern=r"^\d+(\.\d+)*$", description="Hierarchical structure number like '1.2.3'")
    start_page: int = Field(..., ge=1)
    end_page: int = Field(..., ge=1)
    children: List["NodeStructureOutput"] = Field(default_factory=list)

    @field_validator("end_page")
    @classmethod
    def end_page_after_start(cls, v: int, info) -> int:
        if "start_page" in info.data and v < info.data["start_page"]:
            raise ValueError("end_page must be >= start_page")
        return v


class DocumentAnalysisOutput(BaseModel):
    """Expected output for full document analysis."""
    structure: List[NodeStructureOutput] = Field(..., min_length=1)
    document_type: str = Field(default="unknown", description="Type of document: technical, legal, academic, etc.")
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")


class ChatResponseOutput(BaseModel):
    """Expected output structure for chat responses with citations."""
    response: str = Field(..., min_length=1)
    citations: List[dict] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


def validate_llm_json_output(
    raw_output: str,
    model_class: type[BaseModel],
    context: str = "LLM output"
) -> BaseModel:
    """
    Validate raw LLM JSON output against a Pydantic model.

    Args:
        raw_output: Raw string output from LLM (should be valid JSON)
        model_class: Pydantic model class to validate against
        context: Description for error messages

    Returns:
        Validated model instance

    Raises:
        ValueError: If output is not valid JSON or fails validation
    """
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"{context}: Invalid JSON - {e}")

    try:
        return model_class.model_validate(data)
    except Exception as e:
        raise ValueError(f"{context}: Validation failed - {e}")


def safe_parse_llm_json(
    raw_output: str,
    model_class: type[BaseModel],
    fallback: Optional[BaseModel] = None,
    context: str = "LLM output"
) -> BaseModel:
    """
    Safely parse LLM JSON output with optional fallback.

    Args:
        raw_output: Raw string output from LLM
        model_class: Pydantic model class to validate against
        fallback: Optional fallback model instance if validation fails
        context: Description for error messages

    Returns:
        Validated model instance or fallback

    Raises:
        ValueError: If validation fails and no fallback provided
    """
    try:
        return validate_llm_json_output(raw_output, model_class, context)
    except ValueError as e:
        if fallback is not None:
            return fallback
        raise


# Resolve forward references
NodeStructureOutput.model_rebuild()

