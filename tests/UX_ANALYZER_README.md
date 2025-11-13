# UX Image Analyzer for Cursor Testing Toolkit

A Python tool to analyze UI screenshots for UX design quality, accessibility, and best practices. Perfect for evaluating screenshots captured during E2E testing.

## Features

- **Technical Metrics**: Image size, aspect ratio, brightness, contrast, color analysis
- **Layout Analysis**: Whitespace ratio, text density, visual hierarchy scoring
- **Accessibility Checks**: Color contrast, text readability estimation
- **AI-Powered Semantic Analysis**: Uses Google Gemini Vision to detect UI components, accessibility issues, and provide design recommendations
- **Comprehensive Scoring**: Overall UX score (0-100) with strengths, weaknesses, and actionable recommendations

## Installation

```bash
# Install required dependencies
pip install -r tests/requirements-ux-analyzer.txt

# Optional: For semantic analysis, choose one (or install multiple):
# 1. Gemini CLI (recommended - official Google tool)
# Install from: https://github.com/google-gemini/gemini-cli
# Or: npm install -g @google/gemini-cli

# 2. Claude Code CLI (Anthropic's official tool)
# Install from: https://claude.ai/code

# 3. OpenAI Codex CLI
npm install -g @openai/codex

# 4. Ollama (local, free)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llava

# 5. Google Cloud SDK (for gcloud)
# Install from https://cloud.google.com/sdk/docs/install

# 6. Or use API directly (requires API key)
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Analyze a Single Screenshot

```bash
python tests/ux_image_analyzer.py path/to/screenshot.png
```

### Analyze All Screenshots in a Directory

```bash
# Analyze all PNG files in tests/e2e/screenshots/
python tests/ux_image_analyzer.py tests/e2e/screenshots/

# Save results to JSON file
python tests/ux_image_analyzer.py tests/e2e/screenshots/ --output ux-analysis.json

# Print summary statistics
python tests/ux_image_analyzer.py tests/e2e/screenshots/ --output ux-analysis.json --summary
```

### CLI Backend Options

The tool automatically detects available CLI tools and uses them in this priority:

1. **Gemini CLI** (Google) - Official, recommended
2. **Claude Code CLI** (Anthropic) - Official
3. **Codex CLI** (OpenAI) - Official
4. **Ollama** (local, free) - Community
5. **gcloud** (Google Cloud)
6. **API** (fallback if no CLI available)

```bash
# Use specific backend
python tests/ux_image_analyzer.py screenshot.png --backend gemini
python tests/ux_image_analyzer.py screenshot.png --backend claude
python tests/ux_image_analyzer.py screenshot.png --backend codex
python tests/ux_image_analyzer.py screenshot.png --backend ollama
python tests/ux_image_analyzer.py screenshot.png --backend gcloud
python tests/ux_image_analyzer.py screenshot.png --backend api --api-key YOUR_KEY

# Force API mode (skip CLI)
python tests/ux_image_analyzer.py screenshot.png --no-cli --api-key YOUR_KEY
```

## Output Format

### Console Output

```
📸 Analyzing dashboard.png...
  ✅ Score: 78.5/100

✅ Overall Score: 78.5/100

Strengths:
  ✓ Good visual hierarchy
  ✓ Good whitespace balance
  ✓ Good color contrast

Weaknesses:
  ✗ Text readability could be improved
  ✗ Brightness may be too high

Recommendations:
  → Adjust text color, size, or background for better readability
  → Increase contrast between text and background colors
```

### JSON Output

When using `--output`, results are saved as JSON:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_images": 5,
  "results": [
    {
      "image_path": "screenshot.png",
      "overall_score": 78.5,
      "strengths": ["Good visual hierarchy", "Good whitespace balance"],
      "weaknesses": ["Text readability could be improved"],
      "recommendations": ["Adjust text color for better readability"],
      "metrics": {
        "image_size": [1920, 1080],
        "aspect_ratio": 1.78,
        "brightness": 145.2,
        "contrast": 45.8,
        "whitespace_ratio": 0.42,
        "visual_hierarchy_score": 0.65,
        "color_contrast_score": 0.72,
        "text_readability_score": 0.68,
        "ui_components_detected": ["button", "form", "navigation"],
        "accessibility_issues": ["Low contrast on secondary text"],
        "design_recommendations": [
          "Increase button size",
          "Add more whitespace"
        ]
      }
    }
  ]
}
```

## Metrics Explained

### Technical Metrics

- **Image Size**: Width and height in pixels
- **Aspect Ratio**: Width/height ratio
- **Brightness**: Average pixel brightness (0-255)
- **Contrast**: Standard deviation of pixel values (higher = more contrast)
- **Color Count**: Number of unique colors (sampled)
- **Dominant Colors**: Top 5 most common colors (RGB)

### Layout Metrics

- **Whitespace Ratio**: Percentage of light/white pixels (ideal: 30-60%)
- **Text Density**: Estimated percentage of dark pixels (text areas)
- **Visual Hierarchy Score**: Variation in brightness across regions (0-1, higher = better hierarchy)

### Accessibility Metrics

- **Color Contrast Score**: Brightness variation score (0-1, higher = better contrast)
- **Text Readability Score**: Combined contrast and brightness score (0-1)

### Semantic Analysis (CLI or API)

- **UI Components Detected**: List of components found (buttons, forms, etc.)
- **Accessibility Issues**: Specific accessibility problems identified
- **Design Recommendations**: Actionable UX improvement suggestions

**Backend Options:**

- **Gemini CLI** (recommended): Official Google CLI. Fast and reliable.
- **Claude Code CLI**: Official Anthropic CLI. Great for detailed analysis.
- **Codex CLI**: OpenAI's CLI tool. Install: `npm install -g @openai/codex`
- **Ollama**: Local, free, privacy-friendly. Install: `ollama pull llava`
- **gcloud**: Google Cloud Vision/Gemini via CLI
- **API**: Direct API calls (requires API keys)

## Integration with Testing

### In Playwright/Puppeteer Tests

```javascript
// After taking a screenshot
await page.screenshot({ path: "screenshot.png" });

// Analyze it
const { execSync } = require("child_process");
const result = execSync(
  `python tests/ux_image_analyzer.py screenshot.png --output analysis.json`,
  { encoding: "utf-8" }
);
```

### Batch Analysis After Test Run

```bash
# After running E2E tests that generate screenshots
python tests/ux_image_analyzer.py tests/e2e/screenshots/ \
  --output tests/e2e/ux-analysis-$(date +%Y%m%d).json \
  --summary
```

## Scoring System

The overall UX score (0-100) is calculated from:

- **Visual Hierarchy** (20 points): Size/importance variation
- **Whitespace** (15 points): Balance between content and space
- **Color Contrast** (20 points): Readability and accessibility
- **Text Readability** (15 points): Text visibility and clarity
- **Brightness** (10 points): Overall visual comfort
- **Aspect Ratio** (10 points): Standard screen compatibility
- **Semantic Analysis** (10 points): AI-detected issues and recommendations

## Limitations

- **Text Detection**: Uses heuristics, not actual OCR. For precise text analysis, consider adding `pytesseract` or `easyocr`.
- **Component Detection**: Semantic analysis requires Gemini API. Falls back to technical metrics only if unavailable.
- **Accessibility**: Simplified contrast checking. For WCAG compliance, use dedicated tools like `axe-core` or `pa11y`.
- **Performance**: Large images are sampled for color analysis to improve speed.

## Future Enhancements

Potential additions:

- OCR integration for actual text extraction and analysis
- WCAG 2.1 compliance checking
- Component-specific analysis (button sizes, form field spacing)
- Comparison between screenshots (visual regression)
- Integration with CI/CD pipelines
- Dashboard visualization of UX metrics over time

## Example Workflow

1. **Run E2E tests** that capture screenshots:

   ```bash
   npm run test:e2e
   ```

2. **Analyze all screenshots**:

   ```bash
   python tests/ux_image_analyzer.py tests/e2e/screenshots/ \
     --output ux-report.json \
     --summary
   ```

3. **Review results** and address recommendations

4. **Re-test** and compare scores to track UX improvements

## Troubleshooting

**"Pillow not installed"**

```bash
pip install Pillow
```

**"OpenCV not installed"** (optional, for better color analysis)

```bash
pip install opencv-python
```

**"No CLI backends found"**

- Install Gemini CLI: `npm install -g @google/gemini-cli` or see https://github.com/google-gemini/gemini-cli
- Or install Claude Code: See https://claude.ai/code
- Or install Codex: `npm install -g @openai/codex`
- Or install Ollama: `curl -fsSL https://ollama.com/install.sh | sh && ollama pull llava`
- Or use API mode: `--no-cli --api-key YOUR_KEY`

**"Ollama service not running"**

- Start Ollama: `ollama serve` (or it may auto-start)
- Check: `curl http://localhost:11434/api/tags`

**"No vision model found" (Ollama)**

- Install a vision model: `ollama pull llava`
- Or use a different backend: `--backend codex` or `--backend api`

**"Gemini API errors"**

- Check your API key: `echo $GEMINI_API_KEY`
- Semantic analysis is optional - tool works without it
- Check API quota/limits

**"No images found"**

- Ensure path is correct
- Check file extensions (.png, .jpg, .jpeg, .webp are supported)
