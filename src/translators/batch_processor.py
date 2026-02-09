"""
Batch Processor

Processes translation jobs in batches with progress tracking.
"""
from typing import List, Dict
from tqdm import tqdm

from src.converters.csv_reader import TranslationRecord
from src.translators.ai_translator import AITranslator, TranslationResult
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BatchProcessor:
    """Processes translations in batches"""

    def process_translation_job(
        self,
        records: List[TranslationRecord],
        target_langs: List[str],
        translator: AITranslator,
        batch_size: int = 50,
        source_lang: str = 'en'
    ) -> Dict[str, List[TranslationResult]]:
        """
        Process a full translation job for multiple languages

        Args:
            records: List of TranslationRecord objects
            target_langs: List of target language codes
            translator: AITranslator instance
            batch_size: Number of records per batch
            source_lang: Source language code

        Returns:
            Dictionary mapping language code to list of TranslationResult objects
        """
        all_results = {}

        for target_lang in target_langs:
            logger.info(f"Starting translation to {target_lang} ({len(records)} records)")

            results = self.process_batch(
                records=records,
                target_lang=target_lang,
                translator=translator,
                source_lang=source_lang
            )

            all_results[target_lang] = results
            logger.info(f"Completed translation to {target_lang}")

        return all_results

    def process_batch(
        self,
        records: List[TranslationRecord],
        target_lang: str,
        translator: AITranslator,
        source_lang: str = 'en'
    ) -> List[TranslationResult]:
        """
        Process a batch of translations for a single language

        Args:
            records: List of TranslationRecord objects
            target_lang: Target language code
            translator: AITranslator instance
            source_lang: Source language code

        Returns:
            List of TranslationResult objects
        """
        results = []

        # Process with progress bar
        for record in tqdm(records, desc=f"Translating to {target_lang}"):
            try:
                result = translator.translate(
                    text=record.source_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    context=record.category,
                    max_length=record.max_length,
                    category=record.category
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to translate record {record.id}: {str(e)}")
                # Create a fallback result
                results.append(TranslationResult(
                    original_text=record.source_text,
                    translated_text=f"[TRANSLATION FAILED: {str(e)}]",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    model="error",
                    prompt_tokens=0,
                    completion_tokens=0,
                    timestamp=None,
                    category=record.category
                ))

        return results
