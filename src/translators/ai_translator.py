"""
AI Translator

OpenAI GPT-4/5 powered translation with context-aware prompts.
"""
from openai import OpenAI
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import re

from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class TranslationResult:
    """Result of a translation"""
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    timestamp: datetime
    category: Optional[str] = None


class AITranslator:
    """AI-powered translator using OpenAI API"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize AI translator

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4-turbo-preview)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.config = ConfigManager()

        logger.info(f"Initialized AI Translator with model: {model}")

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: Optional[str] = None,
        max_length: Optional[int] = None,
        category: Optional[str] = None
    ) -> TranslationResult:
        """
        Translate text from source to target language

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'zh-CN')
            context: Optional context for translation
            max_length: Optional maximum length constraint
            category: Content category for prompt selection

        Returns:
            TranslationResult object
        """
        # Get language configs
        target_lang_config = self.config.get_language(target_lang)
        if not target_lang_config:
            raise ValueError(f"Unknown target language: {target_lang}")

        # Get appropriate prompt template
        prompt_template = self.config.get_prompt_template(category)

        # Build prompt
        prompt = self._build_prompt(
            template=prompt_template,
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            target_lang_name=target_lang_config.name,
            context=context,
            max_length=max_length
        )

        logger.info(f"Translating text to {target_lang} (length: {len(text)} chars)")

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            translated_text = response.choices[0].message.content.strip()

            # Remove quotes if the model added them
            translated_text = translated_text.strip('"').strip("'")

            # Validate length if constraint exists
            if max_length and len(translated_text) > max_length:
                logger.warning(f"Translation exceeds max_length ({len(translated_text)} > {max_length})")
                # Truncate but warn
                translated_text = translated_text[:max_length]

            result = TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_lang=source_lang,
                target_lang=target_lang,
                model=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                timestamp=datetime.now(),
                category=category
            )

            logger.info(f"Translation successful (tokens: {result.prompt_tokens + result.completion_tokens})")
            return result

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise

    def _build_prompt(
        self,
        template: str,
        text: str,
        source_lang: str,
        target_lang: str,
        target_lang_name: str,
        context: Optional[str] = None,
        max_length: Optional[int] = None
    ) -> str:
        """
        Build translation prompt from template

        Args:
            template: Prompt template string
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            target_lang_name: Target language display name
            context: Optional context
            max_length: Optional max length

        Returns:
            Formatted prompt string
        """
        # Replace placeholders in template
        prompt = template.format(
            source_lang=source_lang,
            target_lang=target_lang,
            target_lang_name=target_lang_name,
            text=text,
            context=context or "None",
            max_length=max_length or "No limit"
        )

        return prompt

    def translate_batch(
        self,
        texts: list,
        source_lang: str,
        target_lang: str,
        contexts: Optional[list] = None,
        max_lengths: Optional[list] = None,
        categories: Optional[list] = None
    ) -> list:
        """
        Translate multiple texts (calls translate for each)

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            contexts: Optional list of contexts
            max_lengths: Optional list of max lengths
            categories: Optional list of categories

        Returns:
            List of TranslationResult objects
        """
        results = []

        for i, text in enumerate(texts):
            context = contexts[i] if contexts and i < len(contexts) else None
            max_length = max_lengths[i] if max_lengths and i < len(max_lengths) else None
            category = categories[i] if categories and i < len(categories) else None

            result = self.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                context=context,
                max_length=max_length,
                category=category
            )
            results.append(result)

        return results
