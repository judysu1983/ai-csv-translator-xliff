# Architecture

See the main README for Mermaid workflow diagrams.

## System Components

1. **CSV Reader** - Validates and parses MongoDB CSV exports
2. **AI Translator** - GPT-4/5 translation engine with batch processing
3. **XLIFF Generator** - Creates TMS-compatible XLIFF files
4. **AI LQA Evaluator** - Multi-dimensional quality assessment
5. **Report Generator** - HTML/JSON/CSV quality reports
6. **TMS Integration** - Phrase/Crowdin API integration
7. **XLIFF Importer** - Round-trip import to CSV

## Data Flow

CSV → Translation → LQA → XLIFF → TMS → Human Review → Import → Final CSV
