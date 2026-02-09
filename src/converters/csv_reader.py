"""
CSV Reader

Reads and validates MongoDB CSV exports for translation.
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

from ..utils.validators import validate_csv_schema, REQUIRED_CSV_COLUMNS
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class TranslationRecord:
    """Translation record from CSV"""
    id: int
    mongoid: str
    avetta_id: str
    mongo_object: str
    form_display_id: str
    source_text: str
    max_length: int = None
    category: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CSVReader:
    """Reads and validates CSV files"""

    REQUIRED_COLUMNS = REQUIRED_CSV_COLUMNS

    def read(self, file_path: str) -> List[TranslationRecord]:
        """
        Read CSV file and return translation records

        Args:
            file_path: Path to CSV file

        Returns:
            List of TranslationRecord objects

        Raises:
            ValueError: If CSV is invalid
        """
        logger.info(f"Reading CSV file: {file_path}")

        # Read CSV
        df = pd.read_csv(file_path, encoding='utf-8')

        # Validate schema
        validation = validate_csv_schema(df)
        if not validation.valid:
            error_msg = f"CSV validation failed: {', '.join(validation.errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if validation.warnings:
            for warning in validation.warnings:
                logger.warning(warning)

        # Convert to TranslationRecord objects
        records = []
        for idx, row in df.iterrows():
            # Extract required fields
            record = TranslationRecord(
                id=int(row['_id']),
                mongoid=str(row['mongoid']),
                avetta_id=str(row['avettaId']),
                mongo_object=str(row['mongoObject']),
                form_display_id=str(row['formdisplayID']),
                source_text=str(row['en']),
                max_length=int(row['max_length']) if pd.notna(row.get('max_length')) else None,
                category=str(row['category']) if pd.notna(row.get('category')) else None,
                metadata={}
            )

            # Store all other columns as metadata
            for col in df.columns:
                if col not in ['_id', 'mongoid', 'avettaId', 'mongoObject', 'formdisplayID', 'en', 'max_length', 'category']:
                    if pd.notna(row[col]):
                        record.metadata[col] = row[col]

            records.append(record)

        logger.info(f"Successfully loaded {len(records)} translation records")
        return records

    def write(self, records: List[Dict[str, Any]], output_path: str):
        """
        Write translation records to CSV

        Args:
            records: List of dictionaries containing translation data
            output_path: Path to output CSV file
        """
        logger.info(f"Writing {len(records)} records to CSV: {output_path}")

        df = pd.DataFrame(records)

        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Write to CSV
        df.to_csv(output_path, index=False, encoding='utf-8')

        logger.info(f"Successfully wrote CSV file: {output_path}")
