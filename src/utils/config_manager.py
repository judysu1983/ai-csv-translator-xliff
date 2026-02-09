"""
Configuration Manager

Loads and manages all YAML configuration files and environment variables.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class LanguageConfig:
    """Language configuration"""
    code: str
    name: str
    bcp47: str
    native_name: str


@dataclass
class DimensionConfig:
    """LQA dimension configuration"""
    weight: float
    description: str
    critical: bool


@dataclass
class LQACriteria:
    """LQA evaluation criteria"""
    dimensions: Dict[str, DimensionConfig]
    thresholds: Dict[str, int]


class ConfigManager:
    """Manages configuration from YAML files and environment variables"""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize config manager

        Args:
            config_dir: Directory containing config files (default: "config")
        """
        self.config_dir = Path(config_dir)

        # Load environment variables from .env file
        load_dotenv()

        # Cache for loaded configs
        self._languages_cache: Optional[Dict[str, LanguageConfig]] = None
        self._lqa_criteria_cache: Optional[LQACriteria] = None
        self._prompts_cache: Optional[Dict[str, str]] = None

    def load_languages(self) -> Dict[str, LanguageConfig]:
        """
        Load language configurations from languages.yaml

        Returns:
            Dictionary mapping language code to LanguageConfig
        """
        if self._languages_cache:
            return self._languages_cache

        languages_file = self.config_dir / "languages.yaml"

        with open(languages_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        languages = {}
        for lang_data in data['languages']:
            lang_config = LanguageConfig(
                code=lang_data['code'],
                name=lang_data['name'],
                bcp47=lang_data['bcp47'],
                native_name=lang_data['native_name']
            )
            languages[lang_config.code] = lang_config

        self._languages_cache = languages
        return languages

    def load_lqa_criteria(self) -> LQACriteria:
        """
        Load LQA criteria from lqa_criteria.yaml

        Returns:
            LQACriteria object with dimensions and thresholds
        """
        if self._lqa_criteria_cache:
            return self._lqa_criteria_cache

        criteria_file = self.config_dir / "lqa_criteria.yaml"

        with open(criteria_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Parse dimensions
        dimensions = {}
        for dim_name, dim_data in data['dimensions'].items():
            dimensions[dim_name] = DimensionConfig(
                weight=dim_data['weight'],
                description=dim_data['description'],
                critical=dim_data['critical']
            )

        # Parse thresholds
        thresholds = data['thresholds']

        lqa_criteria = LQACriteria(
            dimensions=dimensions,
            thresholds=thresholds
        )

        # Validate weights sum to 1.0
        total_weight = sum(dim.weight for dim in dimensions.values())
        if not (0.99 <= total_weight <= 1.01):  # Allow for floating point imprecision
            raise ValueError(f"LQA dimension weights must sum to 1.0, got {total_weight}")

        self._lqa_criteria_cache = lqa_criteria
        return lqa_criteria

    def load_translation_prompts(self) -> Dict[str, str]:
        """
        Load translation prompts from translation_prompts.yaml

        Returns:
            Dictionary mapping prompt name to prompt template
        """
        if self._prompts_cache:
            return self._prompts_cache

        prompts_file = self.config_dir / "translation_prompts.yaml"

        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self._prompts_cache = data
        return data

    def get_language(self, code: str) -> Optional[LanguageConfig]:
        """
        Get language configuration by code

        Args:
            code: Language code (e.g., 'zh-CN', 'ja-JP')

        Returns:
            LanguageConfig or None if not found
        """
        languages = self.load_languages()
        return languages.get(code)

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def validate_config(self) -> bool:
        """
        Validate all configuration files are loadable and valid

        Returns:
            True if all configs are valid

        Raises:
            Exception if any config is invalid
        """
        # Load all configs to trigger validation
        self.load_languages()
        self.load_lqa_criteria()
        self.load_translation_prompts()

        return True

    def get_prompt_template(self, category: Optional[str] = None) -> str:
        """
        Get appropriate translation prompt template based on category

        Args:
            category: Content category (ui, compliance, etc.)

        Returns:
            Prompt template string
        """
        prompts = self.load_translation_prompts()

        # Select prompt based on category
        if category in ['ui', 'form_label', 'button', 'section_header']:
            return prompts.get('ui_strings', prompts['default_prompt'])
        elif category in ['compliance', 'legal', 'safety']:
            return prompts.get('compliance', prompts['default_prompt'])
        else:
            return prompts['default_prompt']
