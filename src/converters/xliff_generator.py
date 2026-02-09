"""
XLIFF Generator

Generates XLIFF 1.2/2.0 files for TMS platforms.
"""
from lxml import etree
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.converters.csv_reader import TranslationRecord
from src.translators.ai_translator import TranslationResult
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class XLIFFGenerator:
    """Generates XLIFF files from translations"""

    def __init__(self, version: str = "1.2"):
        """
        Initialize XLIFF generator

        Args:
            version: XLIFF version ('1.2' or '2.0')
        """
        self.version = version
        logger.info(f"Initialized XLIFF Generator (version {version})")

    def create_xliff(
        self,
        records: List[TranslationRecord],
        translations: List[TranslationResult],
        source_lang: str,
        target_lang: str,
        output_path: str,
        lqa_results: Optional[List] = None
    ) -> Path:
        """
        Create XLIFF file from translations

        Args:
            records: Original translation records
            translations: Translation results
            source_lang: Source language code
            target_lang: Target language code
            output_path: Path to output XLIFF file
            lqa_results: Optional LQA results to embed

        Returns:
            Path to created XLIFF file
        """
        logger.info(f"Generating XLIFF {self.version} file: {output_path}")

        if self.version == "1.2":
            xliff_root = self._create_xliff_12(
                records, translations, source_lang, target_lang, lqa_results
            )
        else:
            xliff_root = self._create_xliff_20(
                records, translations, source_lang, target_lang, lqa_results
            )

        # Create output directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write XLIFF to file
        tree = etree.ElementTree(xliff_root)
        tree.write(
            str(output_file),
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        )

        logger.info(f"XLIFF file created successfully: {output_path}")
        return output_file

    def _create_xliff_12(
        self,
        records: List[TranslationRecord],
        translations: List[TranslationResult],
        source_lang: str,
        target_lang: str,
        lqa_results: Optional[List] = None
    ) -> etree.Element:
        """Create XLIFF 1.2 structure"""

        # Create root element
        xliff = etree.Element('xliff', version='1.2')

        # Create file element
        file_elem = etree.SubElement(
            xliff,
            'file',
            attrib={
                'source-language': source_lang,
                'target-language': target_lang,
                'datatype': 'plaintext',
                'original': 'mongodb_export'
            }
        )

        # Add body
        body = etree.SubElement(file_elem, 'body')

        # Add translation units
        for i, (record, translation) in enumerate(zip(records, translations)):
            trans_unit = etree.SubElement(
                body,
                'trans-unit',
                id=str(record.id),
                resname=record.form_display_id
            )

            # Source text
            source = etree.SubElement(trans_unit, 'source')
            source.text = record.source_text

            # Target text
            target = etree.SubElement(trans_unit, 'target')
            target.text = translation.translated_text

            # Add metadata as notes
            note = etree.SubElement(trans_unit, 'note')
            note.text = f"mongoid: {record.mongoid}"

            if record.category:
                note = etree.SubElement(trans_unit, 'note')
                note.text = f"category: {record.category}"

            if record.max_length:
                note = etree.SubElement(trans_unit, 'note')
                note.text = f"max_length: {record.max_length}"

            # Add LQA score if available
            if lqa_results and i < len(lqa_results):
                lqa = lqa_results[i]
                if hasattr(lqa, 'weighted_score'):
                    note = etree.SubElement(trans_unit, 'note')
                    note.text = f"lqa_score: {lqa.weighted_score:.1f}"

                    note = etree.SubElement(trans_unit, 'note')
                    note.text = f"lqa_status: {lqa.status}"

        return xliff

    def _create_xliff_20(
        self,
        records: List[TranslationRecord],
        translations: List[TranslationResult],
        source_lang: str,
        target_lang: str,
        lqa_results: Optional[List] = None
    ) -> etree.Element:
        """Create XLIFF 2.0 structure"""

        # Create root element
        xliff = etree.Element(
            'xliff',
            version='2.0',
            srcLang=source_lang,
            trgLang=target_lang
        )

        # Create file element
        file_elem = etree.SubElement(xliff, 'file', id='f1')

        # Add units
        for i, (record, translation) in enumerate(zip(records, translations)):
            unit = etree.SubElement(
                file_elem,
                'unit',
                id=str(record.id),
                name=record.form_display_id
            )

            # Add segment
            segment = etree.SubElement(unit, 'segment')

            # Source
            source = etree.SubElement(segment, 'source')
            source.text = record.source_text

            # Target
            target = etree.SubElement(segment, 'target')
            target.text = translation.translated_text

            # Add metadata as notes
            notes = etree.SubElement(unit, 'notes')

            note = etree.SubElement(notes, 'note')
            note.text = f"mongoid: {record.mongoid}"

            if record.category:
                note = etree.SubElement(notes, 'note')
                note.text = f"category: {record.category}"

            if record.max_length:
                note = etree.SubElement(notes, 'note')
                note.text = f"max_length: {record.max_length}"

            # Add LQA score if available
            if lqa_results and i < len(lqa_results):
                lqa = lqa_results[i]
                if hasattr(lqa, 'weighted_score'):
                    note = etree.SubElement(notes, 'note')
                    note.text = f"lqa_score: {lqa.weighted_score:.1f}"

                    note = etree.SubElement(notes, 'note')
                    note.text = f"lqa_status: {lqa.status}"

        return xliff
