# API Reference

## AITranslator

```python
from src.translators.ai_translator import AITranslator

translator = AITranslator(api_key="...", model="gpt-4-turbo-preview")
result = translator.translate(text="Hello", source_lang="en", target_lang="zh-CN")
```

## AIQualityEvaluator

```python
from src.lqa.ai_evaluator import AIQualityEvaluator

evaluator = AIQualityEvaluator(api_key="...", threshold=85)
lqa = evaluator.evaluate_translation(source="Hello", translation="你好", target_lang="zh-CN")
```

## XLIFFGenerator

```python
from src.converters.xliff_generator import XLIFFGenerator

generator = XLIFFGenerator(version="1.2")
generator.create_xliff(translations, "en", "zh-CN", "output.xlf", lqa_results)
```

See source code for full API documentation.
