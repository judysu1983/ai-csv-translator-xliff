"""
Validators

Data validation functions for CSV, XLIFF, and language codes.
"""
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass


# Required CSV columns
REQUIRED_CSV_COLUMNS = ['_id', 'mongoid', 'avettaId', 'mongoObject', 'formdisplayID', 'en']


@dataclass
class ValidationResult:
    """Validation result"""
    valid: bool
    errors: List[str]
    warnings: List[str]


def validate_csv_schema(df: pd.DataFrame) -> ValidationResult:
    """
    Validate CSV schema has all required columns

    Args:
        df: pandas DataFrame to validate

    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []

    # Check for required columns
    missing_columns = set(REQUIRED_CSV_COLUMNS) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")

    # Check for empty DataFrame
    if df.empty:
        errors.append("CSV file is empty")

    # Check for duplicate IDs
    if '_id' in df.columns and df['_id'].duplicated().any():
        warnings.append("Duplicate _id values found")

    # Check for empty source text
    if 'en' in df.columns:
        empty_count = df['en'].isna().sum() + (df['en'] == '').sum()
        if empty_count > 0:
            warnings.append(f"{empty_count} records have empty source text")

    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors, warnings=warnings)


def validate_translation_record(record: dict) -> bool:
    """
    Validate a single translation record has required fields

    Args:
        record: Dictionary containing translation record

    Returns:
        True if valid
    """
    required_fields = ['_id', 'mongoid', 'avettaId', 'mongoObject', 'formdisplayID', 'en']

    for field in required_fields:
        if field not in record:
            return False
        if record[field] is None or (isinstance(record[field], str) and not record[field].strip()):
            if field == 'en':  # Source text must not be empty
                return False

    return True


def validate_language_code(code: str, valid_codes: List[str]) -> bool:
    """
    Validate language code against list of valid codes

    Args:
        code: Language code to validate (e.g., 'zh-CN')
        valid_codes: List of valid language codes

    Returns:
        True if valid
    """
    return code in valid_codes


def validate_max_length(text: str, max_len: Optional[int]) -> bool:
    """
    Validate text length against maximum

    Args:
        text: Text to validate
        max_len: Maximum length (None means no limit)

    Returns:
        True if valid (within length)
    """
    if max_len is None:
        return True

    return len(text) <= max_len


def validate_xliff(xml_content: str, version: str = "1.2") -> ValidationResult:
    """
    Basic XLIFF validation

    Args:
        xml_content: XLIFF XML content
        version: XLIFF version ('1.2' or '2.0')

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []

    # Basic checks
    if not xml_content or not xml_content.strip():
        errors.append("XLIFF content is empty")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    # Check for XLIFF tag
    if '<xliff' not in xml_content:
        errors.append("Missing <xliff> root element")

    # Check version
    if version == "1.2":
        if 'version="1.2"' not in xml_content:
            warnings.append("XLIFF version 1.2 not specified in document")
    elif version == "2.0":
        if 'version="2.0"' not in xml_content:
            warnings.append("XLIFF version 2.0 not specified in document")

    # Check for translation units
    if '<trans-unit' not in xml_content and '<unit' not in xml_content:
        errors.append("No translation units found")

    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors, warnings=warnings)
