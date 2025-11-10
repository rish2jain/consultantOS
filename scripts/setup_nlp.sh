#!/bin/bash

# Setup NLP dependencies for ConsultantOS
# This script installs spaCy and required language models

set -e  # Exit on error

echo "=========================================="
echo "ConsultantOS NLP Setup"
echo "=========================================="
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not running in a virtual environment"
    echo "   It's recommended to use a virtual environment"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install spacy>=3.7.0 textblob>=0.17.0

# Download spaCy language model
echo ""
echo "📚 Downloading spaCy language model..."
echo "   This may take a few minutes..."

# Check if model already installed
if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✅ Model 'en_core_web_sm' already installed"
else
    python -m spacy download en_core_web_sm
    echo "✅ Model 'en_core_web_sm' installed successfully"
fi

# Download TextBlob corpora
echo ""
echo "📚 Downloading TextBlob corpora..."
python -m textblob.download_corpora

# Verify installation
echo ""
echo "🔍 Verifying installation..."

python << EOF
import spacy
import textblob

try:
    # Test spaCy
    nlp = spacy.load('en_core_web_sm')
    doc = nlp("Tesla announced partnership with Samsung")
    entities = [ent.text for ent in doc.ents]
    print(f"✅ spaCy working - Found entities: {entities}")

    # Test TextBlob
    blob = textblob.TextBlob("This is an excellent product!")
    sentiment = blob.sentiment
    print(f"✅ TextBlob working - Sentiment polarity: {sentiment.polarity:.2f}")

    print("")
    print("✅ All NLP components installed and verified successfully!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    exit(1)
EOF

# Print usage instructions
echo ""
echo "=========================================="
echo "✅ NLP Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run tests: pytest tests/test_nlp_tool.py -v"
echo "2. Try the NLP tools in Python:"
echo ""
echo "   from consultantos.tools.nlp_tool import analyze_text"
echo "   results = analyze_text('Your text here')"
echo "   print(results['entities'])"
echo ""
echo "3. See docs/NLP_INTEGRATION.md for full documentation"
echo ""
