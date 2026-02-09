# User Guide

## Installation

```bash
pip install -e .
cp .env.example .env
# Edit .env with your API keys
```

## Basic Workflow

1. **Prepare CSV** - Ensure required columns exist
2. **Translate** - Run translation command
3. **Review LQA** - Check quality reports
4. **Upload to TMS** - Push to Phrase/Crowdin
5. **Human Review** - Linguists review in TMS
6. **Download** - Get reviewed XLIFF
7. **Import** - Convert back to CSV

See README.md for detailed command examples.
