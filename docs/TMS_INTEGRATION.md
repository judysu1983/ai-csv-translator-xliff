# TMS Integration Guide

## Phrase TMS Setup

1. Get API token from Phrase account settings
2. Create or identify project ID
3. Add to .env file
4. Run upload command

```bash
python -m src.main upload-to-phrase \
  --xliff-dir output/xliff \
  --lqa-reports output/lqa \
  --add-comments
```

## Crowdin Setup

Similar process - see Crowdin API documentation.

## Custom TMS

Extend `src/tms/base_tms.py` for custom integrations.
