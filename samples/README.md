# PromptPex Analysis Tools

This directory contains comprehensive analysis tools for evaluating PromptPex benchmark results. The tools provide detailed statistical analysis, visualization, and comparison capabilities for prompt evaluation data.

## Quick Start

```bash
# Basic analysis of evaluation results
python analyze_metrics.py -d /path/to/eval/directory

# Analysis with clean charts (no titles)
python analyze_metrics.py -d /path/to/eval/directory --no-titles

# Focused baseline comparison analysis
python analyze_metrics.py -d /path/to/eval/directory --skip-individual --skip-aggregated --skip-plotresults
```

## Main Analysis Script

### `analyze_metrics.py`

The primary analysis tool that generates comprehensive evaluation reports including:

#### Features
- **Statistical Analysis**: Relative improvement calculations with Cohen's d effect sizes
- **Baseline Comparison**: PromptPex vs baseline performance analysis
- **Model-Specific Analysis**: Individual model breakdowns (e.g., GPT-OSS)
- **Neutral Reporting**: Non-judgmental framing of compliance changes
- **Enhanced Visualization**: Large fonts, optimized legends, optional title removal

#### Analysis Types
1. **Individual Benchmark Analysis**: Detailed per-benchmark metrics
2. **Aggregated Analysis**: Cross-benchmark performance summaries  
3. **Baseline Comparison**: Statistical comparison with baseline results
4. **Plot-Results Style**: Compliance-focused charts and CSV exports

#### Command Line Options
```bash
# Required
-d, --evals-dir PATH     Directory containing evaluation results

# Optional  
-b, --benchmarks LIST   Comma-separated benchmark names to analyze
-o, --output-dir PATH   Custom output directory for plots
--skip-individual       Skip individual benchmark analysis
--skip-aggregated       Skip aggregated metrics analysis  
--skip-baseline         Skip baseline comparison analysis
--skip-plotresults      Skip plot-results style analysis
--no-titles             Remove titles from charts for clean presentation
```

#### Output Files

**Relative Improvement Analysis:**
- `pp-relative-improvement-{metric}.pdf` - Overall relative change analysis
- `pp-relative-improvement-{metric}---{model}-Model.pdf` - Model-specific analysis

**Baseline Comparison:**
- `pp-baseline-comparison-{metric}.pdf` - Overall baseline vs PromptPex
- `pp-baseline-comparison-{model}-{metric}.pdf` - Model-specific baseline comparison

**Plot-Results Style:**
- `pp-cpct.pdf` - Compliance percentages by benchmark
- `pos-neg-cpct.pdf` - Positive vs negative rule compliance
- `pp-compare.pdf` - PromptPex vs baseline comparison
- `pp-test-validity.pdf` - Test validity analysis
- `pp-grounded-rules.pdf` - Rule count analysis

**CSV Data:**
- `pp-cpct.csv`, `pos-neg-cpct.csv`, `pp-compare.csv`, etc.

## Interactive Analysis

### `analyze-metrics-v3.ipynb`

Jupyter notebook providing interactive access to all analysis functions:
- Real-time parameter adjustment
- Custom visualization options
- Exploratory data analysis
- Integration with all `analyze_metrics.py` capabilities

```bash
# Start interactive analysis
jupyter notebook analyze-metrics-v3.ipynb
```

## Legacy Files

### `analyze-metrics-v2.ipynb` 
Legacy interactive analysis notebook (superseded by v3)

### `plot-results.ipynb`
Original compliance visualization notebook (functionality integrated into `analyze_metrics.py`)

## Statistical Features

### Relative Improvement Analysis
- **Percentage Changes**: Neutral reporting of increases/decreases
- **Effect Sizes**: Cohen's d calculations for practical significance
- **Confidence Intervals**: Statistical uncertainty measurements
- **Model Comparisons**: Individual and aggregate performance analysis

### Enhanced Visualizations
- **Large Fonts**: 20px model labels for better readability
- **Smart Legends**: Optimized positioning to prevent chart expansion
- **Professional Styling**: Technical paper-ready formatting
- **Optional Titles**: `--no-titles` flag for clean presentation

### Neutral Reporting Framework
- **Non-Judgmental Language**: Reports changes without "better/worse" implications
- **Statistical Objectivity**: Facts-based analysis of compliance metrics
- **Contextual Interpretation**: Allows readers to draw their own conclusions

## Setup

```bash
# Setup environment
./setup.sh

# Activate environment  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Dependencies

- pandas >= 2.0
- matplotlib >= 3.0  
- numpy >= 1.20
- jupyter >= 1.0 (for notebooks)

## Usage Examples

```bash
# Full analysis with all components
python analyze_metrics.py -d evals/test-all-2025-09-29-paper/eval

# Specific benchmarks only
python analyze_metrics.py -d evals/my-eval -b "speech-tag,art-prompt,elements"

# Clean charts for presentation
python analyze_metrics.py -d evals/my-eval --no-titles

# Only compliance analysis
python analyze_metrics.py -d evals/my-eval --skip-individual --skip-aggregated --skip-baseline

# Only baseline and relative improvement analysis
python analyze_metrics.py -d evals/my-eval --skip-individual --skip-aggregated --skip-plotresults

# Custom output directory
python analyze_metrics.py -d evals/my-eval -o /path/to/output
```

For detailed information, see [ANALYSIS_README.md](../ANALYSIS_README.md) in the project root.