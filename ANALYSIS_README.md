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

### Chart Types Generated

#### Standard Analysis Charts
- **Performance by Benchmark**: Shows main metrics and PromptPex inverse performance
- **Aggregated Metrics**: Overall performance across all benchmarks
- **Baseline Comparison**: PromptPex vs baseline performance with statistical significance

#### Plot-Results Style Charts
- **Non-Compliance by Benchmark**: Rule violation patterns across benchmarks
- **Rule vs Inverse Rule Performance**: Comparison of positive vs negative test outcomes
- **PromptPex vs Baseline Metrics**: Detailed baseline comparison analysis
- **Test Validity Analysis**: Assessment of test reliability and consistency
- **Rules Count Analysis**: Distribution and coverage of rule types

### CSV File Outputs

The analysis generates several CSV files for further processing:
- `overview.csv`: Main benchmark performance metrics
- `overview-baseline.csv`: Baseline comparison data
- `aggregated_results.csv`: Cross-benchmark aggregated metrics
- `single_model_results.csv`: Model-specific performance data
- `plot_results_*.csv`: Compliance and rule analysis data

## Quick Start

### Python Script Analysis

#### Basic Analysis
```bash
# Analyze a single benchmark directory
python samples/analyze_metrics.py /path/to/benchmark/directory

# Analyze with custom output directory
python samples/analyze_metrics.py /path/to/benchmark/directory --output-dir /path/to/output
```

#### Baseline Comparison Analysis
```bash
# Compare PromptPex results with baseline
python samples/analyze_metrics.py /path/to/promptpex/results --baseline /path/to/baseline/results

# Include single model analysis for gpt-oss
python samples/analyze_metrics.py /path/to/promptpex/results --baseline /path/to/baseline/results --single-model gpt-oss
```

#### Comprehensive Analysis
```bash
# Generate all analysis types including plot-results style
python samples/analyze_metrics.py /path/to/benchmark/directory --all

# Skip plot-results analysis if not needed
python samples/analyze_metrics.py /path/to/benchmark/directory --all --skip-plotresults

# Generate only plot-results style analysis
python samples/analyze_metrics.py /path/to/benchmark/directory --plot-results-only
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
benchmark_directory/
├── overview.csv              # Main results file
├── overview-baseline.csv     # Baseline comparison data (optional)
└── rules.txt                # Rule definitions file (for plot-results analysis)
```

## Command Line Options

- `--baseline`: Path to baseline results directory for comparison
- `--output-dir`: Custom output directory for generated charts and CSVs
- `--single-model`: Generate analysis for specific model (e.g., gpt-oss)
- `--all`: Generate all analysis types (individual + aggregated + baseline + single model + plot-results)
- `--plot-results-only`: Generate only plot-results style analysis
- `--skip-plotresults`: Skip plot-results analysis when using --all flag
- `-b, --benchmarks`: Analyze specific benchmarks (comma-separated)
- `-o, --output`: Custom output directory

## Output

Plots are saved as PDF files in the evaluation directory:
- `benchmark-{name}-metrics.pdf` - Individual benchmark analysis
- `pp-model-averages.pdf` - Model performance comparison  
- `pp-average-tests-per-model.pdf` - Test averages
- `benchmark-sums-{metric}.pdf` - Metric summations
- `pp-baseline-*.pdf` - Baseline comparison plots

## Dependencies

- pandas >= 2.0
- matplotlib >= 3.0
- numpy >= 1.20

Install with: `pip install -r requirements.txt`