# AI CSV Translator with XLIFF Generation & LQA

AI-powered translation pipeline that processes CSV files containing MongoDB translation data, generates AI translations, creates XLIFF files for human review in TMS platforms, and performs comprehensive AI-based Language Quality Assessment (LQA).

## Features

- 🤖 **AI Translation**: GPT-4/5 powered translation for 34+ languages
- 📄 **XLIFF Generation**: XLIFF 1.2/2.0 compatible with Phrase, Crowdin, and other TMS platforms
- 🎯 **AI LQA**: Multi-dimensional quality evaluation with detailed scoring
- 🔗 **TMS Integration**: Direct integration with Phrase TMS (comments & custom fields)
- 📊 **Quality Reports**: HTML, CSV, and JSON reporting formats
- 🔄 **Round-trip**: Import reviewed XLIFF back to CSV for MongoDB

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-csv-translator-xliff.git
cd ai-csv-translator-xliff

# Install dependencies
pip install -e .

# Or using pip
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
OPENAI_API_KEY=your_openai_api_key
PHRASE_API_TOKEN=your_phrase_token
PHRASE_PROJECT_ID=your_project_id
```

### Basic Usage

```bash
# Translate CSV to multiple languages
python -m src.main translate \
  --input data/translations.csv \
  --target-langs zh-CN,ja-JP,fr-FR \
  --output-dir output/xliff

# With AI LQA enabled
python -m src.main translate \
  --input data/translations.csv \
  --target-langs zh-CN \
  --enable-lqa \
  --lqa-threshold 85 \
  --output-dir output/xliff

# Upload to Phrase TMS with LQA comments
python -m src.main upload-to-phrase \
  --xliff-dir output/xliff \
  --lqa-reports output/lqa \
  --add-comments

# Import reviewed XLIFF back to CSV
python -m src.main import-xliff \
  --xliff-dir output/reviewed \
  --output translations_final.csv
```

## CSV Input Format

Your CSV must have the following structure:

```csv
_id,mongoid,avettaId,mongoObject,formdisplayID,en,max_length,category
1,507f1f77bcf86cd7,AV001,supplier_form,SF_001,"Welcome to Supplier Registration",100,ui
```

**Required columns:**
- `_id`: Database primary key
- `mongoid`: MongoDB ObjectId
- `avettaId`: Avetta system identifier
- `mongoObject`: Collection/object reference
- `formdisplayID`: Form display identifier
- `en`: English source text (to be translated)

**Optional columns:**
- `max_length`: Character limit for UI
- `category`: Content classification
- Any other metadata columns (preserved in round-trip)

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed workflow diagrams.

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete usage instructions
- [API Reference](docs/API_REFERENCE.md) - Python API documentation
- [TMS Integration](docs/TMS_INTEGRATION.md) - Phrase/Crowdin integration guide
- [Architecture](docs/ARCHITECTURE.md) - System design and workflows

## Examples

See the [examples/](examples/) directory for:
- Sample CSV input files
- Configuration examples
- Output XLIFF samples

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_lqa/test_ai_evaluator.py
```

## Project Structure

```
ai-csv-translator-xliff/
├── src/                    # Source code
│   ├── translators/       # AI translation engine
│   ├── converters/        # CSV and XLIFF processing
│   ├── lqa/              # Quality assessment
│   ├── tms/              # TMS integrations
│   └── utils/            # Utilities
├── config/               # Configuration files
├── tests/                # Test suite
├── examples/             # Sample files
└── docs/                 # Documentation
```

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please use the GitHub issue tracker.
