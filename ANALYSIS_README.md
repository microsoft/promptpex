# Analysis of PromptPex Evaluation Results

This directory contains comprehensive tools for analyzing evaluation results from PromptPex benchmark testing.

## Overview

The evaluation system generates results in CSV format from various benchmark tests. These tools provide detailed visualizations of performance metrics, compliance rates, baseline comparisons, and rule-by-rule analysis across different models and benchmarks.

## Quick Start

1. **Setup Environment:**
   ```bash
   ./setup.sh
   ```

2. **Activate Environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Run Analysis:**
   ```bash
   python samples/analyze_metrics.py --help
   ```

## Files

- **analyze_metrics.py**: Python script for generating comprehensive analysis charts and metrics with full plot-results integration
- **analyze-metrics-v3.ipynb**: Jupyter notebook for interactive metric analysis using all analyze_metrics.py functions
- **analyze-metrics-v2.ipynb**: Legacy interactive analysis notebook (no longer needed)
- **plot-results.ipynb**: Original compliance and performance visualization notebook (no longer needed)
- **requirements.txt**: Python dependencies for the analysis tools

## Features

### Comprehensive Analysis Types

1. **Individual Benchmark Analysis**: Detailed metrics for each benchmark with PromptPex inverse calculations
2. **Aggregated Cross-Benchmark Analysis**: Combined performance metrics across all benchmarks
3. **Baseline vs PromptPex Comparison**: Side-by-side comparison with baseline performance
4. **Single Model Analysis**: Focused analysis for specific models (e.g., gpt-oss)
5. **Plot-Results Style Analysis**: Compliance-focused analysis with 5 specialized chart types
6. **Relative Improvement Analysis**: Statistical analysis with Cohen's d effect sizes and neutral reporting

### Enhanced Visualization Features

- **Larger Fonts**: 20px font sizes for model labels in charts for better readability
- **Optimized Legends**: Smart legend placement to prevent chart widening
- **Title Control**: Optional `--no-titles` flag for clean chart presentation
- **Neutral Reporting**: Non-judgmental framing of compliance changes
- **Model-Specific PDFs**: Dedicated relative improvement charts for individual models

### Chart Types Generated

#### Standard Analysis Charts
- **Performance by Benchmark**: Shows main metrics and PromptPex inverse performance
- **Aggregated Metrics**: Overall performance across all benchmarks
- **Baseline Comparison**: PromptPex vs baseline performance with statistical significance
- **Relative Improvement Charts**: Statistical analysis with percentage changes and effect sizes
- **Model-Specific Analysis**: Individual model performance breakdowns

#### Plot-Results Style Charts
- **Non-Compliance by Benchmark**: Rule violation patterns across benchmarks
- **Rule vs Inverse Rule Performance**: Comparison of positive vs negative test outcomes
- **PromptPex vs Baseline Metrics**: Detailed baseline comparison analysis
- **Test Validity Analysis**: Assessment of test reliability and consistency
- **Rules Count Analysis**: Distribution and coverage of rule types

### CSV File Outputs

The analysis generates several CSV files for further processing:
- `pp-cpct.csv`: Compliance percentages by benchmark and model
- `pos-neg-cpct.csv`: Positive vs negative rule compliance comparison
- `pp-compare.csv`: PromptPex vs baseline comparison data
- `pp-test-validity.csv`: Test validity and reliability metrics
- `pp-grounded-rules.csv`: Rule count and grounding analysis

### PDF Outputs

Generated PDF files include:
- `pp-relative-improvement-{metric}.pdf`: Relative change analysis charts
- `pp-relative-improvement-{metric}---{model}-Model.pdf`: Model-specific relative improvement
- `pp-baseline-comparison-{metric}.pdf`: Baseline comparison charts
- `pp-baseline-comparison-{model}-{metric}.pdf`: Model-specific baseline comparison
- `pp-cpct.pdf`, `pos-neg-cpct.pdf`, `pp-compare.pdf`: Plot-results style charts

## Quick Start

### Python Script Analysis

#### Basic Analysis
```bash
# Analyze evaluation results with full analysis
python samples/analyze_metrics.py -d /path/to/eval/directory

# Analyze specific benchmarks only
python samples/analyze_metrics.py -d /path/to/eval/directory -b "benchmark1,benchmark2"

# Save plots to custom directory
python samples/analyze_metrics.py -d /path/to/eval/directory -o /path/to/output
```

#### Analysis Control Options
```bash
# Skip individual benchmark analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-individual

# Skip aggregated metrics analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-aggregated

# Skip baseline comparison analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-baseline

# Skip plot-results style analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-plotresults

# Generate charts without titles (for clean presentation)
python samples/analyze_metrics.py -d /path/to/eval/directory --no-titles
```

#### Focused Analysis
```bash
# Only baseline comparison and relative improvement analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-individual --skip-aggregated --skip-plotresults

# Only plot-results style compliance analysis
python samples/analyze_metrics.py -d /path/to/eval/directory --skip-individual --skip-aggregated --skip-baseline
```

### Jupyter Notebook Analysis

#### Interactive Analysis
```bash
# Start Jupyter and open the comprehensive notebook
jupyter notebook samples/analyze-metrics-v3.ipynb
```

#### Notebook Usage
The notebook provides interactive access to all analyze_metrics.py functions:
- Individual benchmark analysis
- Aggregated metrics visualization  
- Baseline comparison charts
- Single model deep-dive analysis
- Plot-results style compliance analysis

### Environment Setup

1. **Setup Environment:**
   ```bash
   ./setup.sh
   ```

2. **Activate Environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Run Analysis:**
   ```bash
   python samples/analyze_metrics.py --help
   ```

## Expected Directory Structure

```
evals_directory/
├── benchmark1/
│   └── benchmark1/
│       └── overview.csv          # Main results file
├── benchmark2/
│   └── benchmark2/
│       ├── overview.csv          # Main results file
│       └── rules.txt             # Rule definitions (optional)
└── ...
```

### Required Files
- **overview.csv**: Main evaluation results with model performance data
- Must contain columns: model, tests compliant, baseline %, accuracy metrics

### Optional Files  
- **rules.txt**: Rule definitions for plot-results analysis
- Additional accuracy columns (e.g., "accuracy with azure:o4-mini_2025-04-16")

## Command Line Options

### Required Arguments
- `-d, --evals-dir PATH`: Directory containing evaluation results (default: ../evals/test-all-2025-09-29/eval)

### Optional Arguments
- `-b, --benchmarks LIST`: Comma-separated list of benchmark names to analyze
- `-o, --output-dir PATH`: Directory to save plots (default: same as evals-dir)
- `--skip-individual`: Skip individual benchmark analysis
- `--skip-aggregated`: Skip aggregated metrics analysis
- `--skip-baseline`: Skip baseline comparison analysis
- `--skip-plotresults`: Skip plot-results style analysis
- `--no-titles`: Remove titles from all generated charts for clean presentation

### Usage Examples
```bash
# Basic analysis with all components
python samples/analyze_metrics.py -d evals/test-all-2025-09-29-paper/eval

# Analysis for specific benchmarks without titles
python samples/analyze_metrics.py -d evals/my-eval -b "speech-tag,art-prompt" --no-titles

# Only baseline and relative improvement analysis
python samples/analyze_metrics.py -d evals/my-eval --skip-individual --skip-aggregated --skip-plotresults

# Full analysis with custom output directory
python samples/analyze_metrics.py -d evals/my-eval -o /path/to/output
```

## Output

### Individual Benchmark Analysis
PDFs are saved for each benchmark in the evaluation directory:
- `benchmark-{name}-metrics.pdf` - Individual benchmark performance analysis

### Aggregated Analysis
- `pp-model-averages.pdf` - Model performance comparison across benchmarks
- `pp-average-tests-per-model.pdf` - Average test metrics per model
- `benchmark-sums-{metric}.pdf` - Metric summations across benchmarks
- `pp-grouped-{metric}.pdf` - Grouped metric analysis

### Baseline Comparison & Relative Improvement
- `pp-baseline-comparison-{metric}.pdf` - Overall baseline vs PromptPex comparison
- `pp-baseline-comparison-{model}-{metric}.pdf` - Model-specific baseline comparison
- `pp-relative-improvement-{metric}.pdf` - Overall relative change analysis
- `pp-relative-improvement-{metric}---{model}-Model.pdf` - Model-specific relative improvement

### Plot-Results Style Analysis
- `pp-cpct.pdf` - Compliance percentages by benchmark
- `pos-neg-cpct.pdf` - Positive vs negative rule compliance
- `pp-compare.pdf` - PromptPex vs baseline comparison
- `pp-test-validity.pdf` - Test validity and reliability analysis
- `pp-grounded-rules.pdf` - Rule count and grounding analysis

### Statistical Features
- **Effect Sizes**: Cohen's d calculations for practical significance
- **Relative Changes**: Percentage changes with neutral reporting
- **Standard Deviations**: Statistical variability measurements
- **Confidence Metrics**: Error bars and statistical significance indicators

## Dependencies

- pandas >= 2.0
- matplotlib >= 3.0
- numpy >= 1.20

Install with: `pip install -r requirements.txt`