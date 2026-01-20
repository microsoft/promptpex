#!/usr/bin/env python3
"""
PromptPex Evaluation Results Analysis Tool

This script provides comprehensive analysis of PromptPex evaluation results including:
- Individual benchmark analysis with detailed metrics
- Aggregated cross-benchmark performance analysis  
- Baseline vs PromptPex comparison with statistical significance
- Single model deep-dive analysis (e.g., gpt-oss)
- Plot-results style compliance analysis
- Relative improvement analysis with Cohen's d effect sizes
- Neutral reporting framework for compliance changes

Features:
- Enhanced visualization with large fonts and optimized legends
- Statistical analysis with effect sizes and confidence intervals
- Model-specific PDFs for detailed analysis
- Optional title removal for clean presentation
- CSV exports for further analysis

Usage:
    python analyze_metrics.py -d PATH_TO_EVAL_DIR [OPTIONS]

Options:
    -d, --evals-dir PATH    Directory containing evaluation results 
                           (default: ../evals/test-all-2025-09-29/eval)
    -b, --benchmarks LIST  Comma-separated list of benchmark names to analyze
                           (default: all available benchmarks)
    -o, --output-dir PATH   Directory to save plots (default: same as evals-dir)
    --skip-individual      Skip individual benchmark analysis
    --skip-aggregated      Skip aggregated metrics analysis 
    --skip-baseline        Skip baseline comparison analysis
    --skip-plotresults     Skip plot-results style analysis
    --no-titles            Remove titles from all generated charts
    --help                 Show this help message

Examples:
    # Full analysis with all components
    python analyze_metrics.py -d evals/test-all-2025-09-29-paper/eval
    
    # Clean charts without titles for presentation
    python analyze_metrics.py -d evals/my-eval --no-titles
    
    # Only baseline comparison and relative improvement
    python analyze_metrics.py -d evals/my-eval --skip-individual --skip-aggregated --skip-plotresults
    
    # Specific benchmarks with custom output
    python analyze_metrics.py -d evals/my-eval -b "speech-tag,art-prompt" -o /path/to/output
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set global matplotlib style for technical papers - apply to all plots
plt.rcParams.update({'font.size': 16})  # Increased from 14 to 16
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.labelsize'] = 18  # Increased from 16 to 18
plt.rcParams['xtick.labelsize'] = 15  # Increased from 13 to 15
plt.rcParams['ytick.labelsize'] = 15  # Increased from 13 to 15
plt.rcParams['legend.fontsize'] = 15  # Increased from 13 to 15
plt.rcParams['axes.titlesize'] = 20   # Increased from 18 to 20
plt.rcParams['figure.titlesize'] = 22 # Increased from 20 to 22


def parse_metric(val):
    """Parse a metric value, handling various formats including percentages."""
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.endswith('%'):
                return float(val[:-1])
            elif val.lower() in ['nan', '', 'none', 'null']:
                return 0.0
            else:
                return float(val)
        elif pd.isna(val):
            return 0.0
        else:
            return float(val)
    except (ValueError, TypeError):
        return 0.0


def calculate_relative_improvement(baseline_val, promptpex_val, is_compliance_metric=True):
    """Calculate relative change percentage between baseline and promptpex.
    
    Args:
        baseline_val: Baseline metric value
        promptpex_val: PromptPex metric value  
        is_compliance_metric: If True, reports changes in non-compliance
                             If False, reports changes in accuracy
    
    Returns:
        relative_change: Percentage change from baseline
        interpretation: String describing the result
    """
    if baseline_val == 0:
        return 0.0, "No baseline value"
    
    # Calculate relative change: (promptpex - baseline) / baseline * 100
    change = (promptpex_val - baseline_val) / baseline_val * 100
    
    if is_compliance_metric:
        # For compliance metrics, report change in non-compliance
        if change > 0:
            interpretation = f"{change:.1f}% increase in non-compliance"
        elif change < 0:
            interpretation = f"{abs(change):.1f}% decrease in non-compliance"
        else:
            interpretation = "No change in non-compliance"
    else:
        # For accuracy metrics, report change in accuracy
        if change > 0:
            interpretation = f"{change:.1f}% increase in accuracy"
        elif change < 0:
            interpretation = f"{abs(change):.1f}% decrease in accuracy"
        else:
            interpretation = "No change in accuracy"
    
    return change, interpretation


def calculate_cohens_d(baseline_vals, promptpex_vals):
    """Calculate Cohen's d effect size between two groups.
    
    Args:
        baseline_vals: List of baseline values
        promptpex_vals: List of promptpex values
    
    Returns:
        cohens_d: Effect size
        interpretation: String describing effect size magnitude
    """
    if len(baseline_vals) < 2 or len(promptpex_vals) < 2:
        return 0.0, "Insufficient data"
    
    mean1, mean2 = np.mean(baseline_vals), np.mean(promptpex_vals)
    var1, var2 = np.var(baseline_vals, ddof=1), np.var(promptpex_vals, ddof=1)
    pooled_std = np.sqrt((var1 + var2) / 2)
    
    if pooled_std == 0:
        return 0.0, "No variance"
    
    cohens_d = (mean2 - mean1) / pooled_std
    
    # Interpret effect size
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        magnitude = "negligible"
    elif abs_d < 0.5:
        magnitude = "small"
    elif abs_d < 0.8:
        magnitude = "medium"
    else:
        magnitude = "large"
    
    direction = "positive" if cohens_d > 0 else "negative"
    interpretation = f"{magnitude} {direction} effect"
    
    return cohens_d, interpretation


def plot_relative_improvement_chart(benchmark_data, benchmark_names, metric_column, is_compliance_metric=True, outputDir=None, no_titles=False):
    """Create a chart showing relative improvement percentages across benchmarks."""
    if outputDir is None:
        outputDir = "."
    
    # Calculate relative improvements for each benchmark
    rel_improvements = []
    benchmark_labels = []
    
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        baseline_val = data['baseline_avg']
        promptpex_val = data['main_avg']
        
        rel_imp, _ = calculate_relative_improvement(baseline_val, promptpex_val, is_compliance_metric)
        rel_improvements.append(rel_imp)
        benchmark_labels.append(benchmark)
    
    # Calculate overall improvement
    overall_baseline = np.mean([benchmark_data[b]['baseline_avg'] for b in benchmark_names])
    overall_promptpex = np.mean([benchmark_data[b]['main_avg'] for b in benchmark_names])
    overall_rel_imp, _ = calculate_relative_improvement(overall_baseline, overall_promptpex, is_compliance_metric)
    
    # Add overall to the data
    rel_improvements.append(overall_rel_imp)
    benchmark_labels.append("Overall")
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Color bars based on positive/negative improvement
    colors = ['green' if imp > 0 else 'red' if imp < 0 else 'gray' for imp in rel_improvements]
    
    bars = ax.bar(range(len(rel_improvements)), rel_improvements, color=colors, alpha=0.7, edgecolor='black', linewidth=0.8)
    
    # Highlight the overall bar
    if len(benchmark_labels) > len(benchmark_names):
        bars[-1].set_alpha(1.0)
        bars[-1].set_linewidth(2)
        # Add separator line
        separator_x = len(benchmark_names) - 0.5
        ax.axvline(x=separator_x, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
    
    # Add value labels on bars
    for bar, improvement in zip(bars, rel_improvements):
        height = bar.get_height()
        label_y = height + (1 if height >= 0 else -3)
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
               f'{improvement:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top', 
               fontsize=11, weight='bold')
    
    # Customize the plot
    metric_type = "Non-Compliance" if is_compliance_metric else "Accuracy"
    ax.set_xlabel('Benchmark', fontsize=18)
    ax.set_ylabel('Relative Change (%)', fontsize=18)
    if not no_titles:
        # Handle model-specific titles
        if " - " in metric_column and " Model" in metric_column:
            ax.set_title(f'Relative Change in {metric_type} - {project_name} vs Baseline for {metric_column}', fontsize=20, pad=20)
        else:
            ax.set_title(f'Relative Change in {metric_type} - {project_name} vs Baseline', fontsize=20, pad=20)
    ax.set_xticks(range(len(benchmark_labels)))
    ax.set_xticklabels(benchmark_labels, rotation=45, ha='right', fontsize=15)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelsize=15)
    
    # Add text annotation for positive vs negative
    change_text = "↑ Positive = Increase in {metric_type}\n↓ Negative = Decrease in {metric_type}".format(metric_type=metric_type.split('-')[0].strip())
    ax.text(0.02, 0.98, change_text, transform=ax.transAxes, fontsize=12,
            va='top', ha='left', bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-relative-improvement-{metric_column.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    print(f"Saved: {outputDir}/pp-relative-improvement-{metric_column.replace(' ', '-').replace('/', '-')}.pdf")


def print_improvement_summary_table(benchmark_data, benchmark_names, metric_column, is_compliance_metric=True, project_name='PromptPex'):
    """Print a comprehensive table showing absolute values, relative improvements, and effect sizes."""
    print(f"\n{'='*100}")
    # Handle special case for tests compliant to avoid "TESTS COMPLIANT Non-Compliance"
    if metric_column.lower().startswith("tests compliant"):
        analysis_title = metric_column.upper().replace("TESTS COMPLIANT", "TEST NON-COMPLIANCE")
    else:
        analysis_title = metric_column.upper()
    print(f"COMPREHENSIVE IMPROVEMENT ANALYSIS - {analysis_title}")
    print(f"{'='*100}")
    
    # Calculate overall statistics
    all_baseline = [benchmark_data[b]['baseline_avg'] for b in benchmark_names]
    all_promptpex = [benchmark_data[b]['main_avg'] for b in benchmark_names]
    
    overall_baseline = np.mean(all_baseline)
    overall_promptpex = np.mean(all_promptpex)
    overall_rel_imp, overall_interpretation = calculate_relative_improvement(
        overall_baseline, overall_promptpex, is_compliance_metric)
    overall_cohens_d, overall_effect_interpretation = calculate_cohens_d(
        all_baseline, all_promptpex)
    
    # Print header
    header_cols = [
        "Benchmark",
        "Baseline %", 
        f"{project_name} %",
        "Abs. Diff",
        "Rel. Change %",
        "Effect Size",
        "Interpretation"
    ]
    print("\t".join([col.ljust(15)[:15] for col in header_cols]))
    print("-" * 115)
    
    # Print per-benchmark data
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        baseline_val = data['baseline_avg']
        promptpex_val = data['main_avg']
        abs_diff = promptpex_val - baseline_val
        
        rel_imp, rel_interpretation = calculate_relative_improvement(
            baseline_val, promptpex_val, is_compliance_metric)
        
        # Calculate effect size for this benchmark (using individual data if available)
        baseline_vals = [baseline_val]  # Could be expanded to include all individual values
        promptpex_vals = [promptpex_val]
        cohens_d, effect_interpretation = calculate_cohens_d(
            [baseline_val] * 5, [promptpex_val] * 5)  # Approximate with repeated values
        
        row_data = [
            benchmark[:15],
            f"{baseline_val:.1f}%",
            f"{promptpex_val:.1f}%",
            f"{abs_diff:+.1f}%",
            f"{rel_imp:+.1f}%",
            f"{cohens_d:.2f}",
            rel_interpretation[:15]
        ]
        print("\t".join([str(item).ljust(15)[:15] for item in row_data]))
    
    # Print overall summary
    print("-" * 115)
    overall_row = [
        "OVERALL",
        f"{overall_baseline:.1f}%",
        f"{overall_promptpex:.1f}%",
        f"{overall_promptpex - overall_baseline:+.1f}%",
        f"{overall_rel_imp:+.1f}%",
        f"{overall_cohens_d:.2f}",
        overall_interpretation[:15]
    ]
    print("\t".join([str(item).ljust(15)[:15] for item in overall_row]))
    
    # Add detailed interpretation
    print(f"\n{'='*100}")
    print("SUMMARY INTERPRETATION:")
    print(f"{'='*100}")
    
    metric_type = "non-compliance" if is_compliance_metric else "accuracy"
    
    print(f"• Metric Type: {metric_type}")
    print(f"• Overall Baseline: {overall_baseline:.1f}%")
    print(f"• Overall {project_name}: {overall_promptpex:.1f}%")
    print(f"• Absolute Difference: {overall_promptpex - overall_baseline:+.1f} percentage points")
    print(f"• Relative Change: {overall_interpretation}")
    print(f"• Effect Size: {overall_effect_interpretation} (Cohen's d = {overall_cohens_d:.3f})")
    
    if is_compliance_metric:
        if overall_rel_imp > 0:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   representing a {overall_rel_imp:.1f}% relative increase in {metric_type}.")
        elif overall_rel_imp < 0:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   representing a {abs(overall_rel_imp):.1f}% relative decrease in {metric_type}.")
        else:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   showing no change in {metric_type}.")
    else:
        if overall_rel_imp > 0:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   representing a {overall_rel_imp:.1f}% relative increase in {metric_type}.")
        elif overall_rel_imp < 0:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   representing a {abs(overall_rel_imp):.1f}% relative decrease in {metric_type}.")
        else:
            print(f"\n📊 {project_name} achieved {overall_promptpex:.1f}% {metric_type} vs. baseline's {overall_baseline:.1f}%, ")
            print(f"   showing no change in {metric_type}.")


def parse_metric(val):
    """Parse a metric value, handling various formats including percentages."""
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.endswith('%'):
                return float(val[:-1])
            elif val.lower() in ['nan', '', 'none', 'null']:
                return 0.0
            else:
                return float(val)
        elif pd.isna(val):
            return 0.0
        else:
            return float(val)
    except (ValueError, TypeError):
        return 0.0


def get_metrics_start_col(df):
    """Get the column index where metrics start (after 'model' and basic info)."""
    try:
        return df.columns.get_loc('tests') 
    except KeyError:
        # If 'tests' column doesn't exist, start from the second column
        return 1


def analyze_benchmark_metrics(benchmark, evalsDir, prettyBenchmarkNames, outputDir=None, no_titles=False):
    """Analyze and plot metrics for a single benchmark."""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    if outputDir is None:
        outputDir = evalsDir
        
    csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
    if not os.path.isfile(csv_path):
        print(f"Warning: {csv_path} not found, skipping.")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    start_col = get_metrics_start_col(df)
    metrics = df.columns[start_col:]
    models = df['model'].tolist()
    
    if len(metrics) == 0 or len(models) == 0:
        print(f"No metrics or models found for {benchmark}")
        return

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    width = 0.8 / len(models)
    x = np.arange(len(metrics))
    
    for i, model in enumerate(models):
        values = []
        for metric in metrics:
            val = parse_metric(df[df['model'] == model].iloc[0][metric])
            values.append(val)
        offset = (i - (len(models) - 1) / 2) * width
        ax.bar(x + offset, values, width, label=model, alpha=0.8)
    
    ax.set_xlabel('Metrics', fontsize=18)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=45, ha='right', fontsize=15)
    ax.set_ylabel('Metric Value', fontsize=18)
    if not no_titles:
        ax.set_title(f"Model Metrics for {prettyBenchmarkNames.get(benchmark, benchmark)}", fontsize=20)
    ax.legend(loc='best', fontsize=15, ncol=2)
    ax.tick_params(axis='y', labelsize=15)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/benchmark-{benchmark}-metrics.pdf', bbox_inches='tight')
    plt.show()


def collect_metrics(benchmarks, evalsDir):
    """Collect metrics from all benchmarks."""
    all_data = {}
    all_models = set()
    all_metrics = set()
    
    for benchmark in benchmarks:
        csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        if not os.path.isfile(csv_path):
            print(f"Warning: {csv_path} not found, skipping.")
            continue
            
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        start_col = get_metrics_start_col(df)
        
        benchmark_data = {}
        for _, row in df.iterrows():
            model = row['model']
            all_models.add(model)
            model_data = {}
            for col in df.columns[start_col:]:
                all_metrics.add(col)
                model_data[col] = parse_metric(row[col])
            benchmark_data[model] = model_data
        all_data[benchmark] = benchmark_data
    
    return all_data, list(all_models), list(all_metrics)


def compute_model_metric_averages(all_data, all_models, all_metrics):
    """Compute average metrics for each model across all benchmarks."""
    model_metric_avg = {model: {} for model in all_models}
    for metric in all_metrics:
        for model in all_models:
            values = []
            for benchmark in all_data:
                if model in all_data[benchmark] and metric in all_data[benchmark][model]:
                    values.append(all_data[benchmark][model][metric])
            if values:
                model_metric_avg[model][metric] = sum(values) / len(values)
            else:
                model_metric_avg[model][metric] = 0.0
    return model_metric_avg


def print_metric_table(model_metric_avg, prettyMetrics=None):
    """Print a table of average metrics by model."""
    if not model_metric_avg:
        print("No metric data available.")
        return
    
    models = list(model_metric_avg.keys())
    if not models:
        print("No models found.")
        return
    
    first_model_metrics = model_metric_avg[models[0]]
    if not first_model_metrics:
        print("No metrics found for any model.")
        return
    
    metrics = list(first_model_metrics.keys())
    print("Average Metrics by Model:")
    if prettyMetrics:
        header = ["Model"] + [prettyMetrics.get(m, m) for m in metrics]
    else:
        header = ["Model"] + metrics
    
    print("\t".join(header))
    for model in models:
        row = [model] + [f"{model_metric_avg[model][metric]:.2f}" for metric in metrics]
        print("\t".join(row))


def plot_grouped_bar_chart(model_metric_avg, outputDir, evalsDir, no_titles=False):
    """Plot grouped bar chart of model metrics."""
    if not model_metric_avg:
        print("No metric data available for plotting.")
        return
    
    models = list(model_metric_avg.keys())
    if not models:
        print("No models found for plotting.")
        return
    
    first_model_metrics = model_metric_avg[models[0]]
    if not first_model_metrics:
        print("No metrics found for plotting.")
        return
    
    metrics = list(first_model_metrics.keys())
    if len(metrics) == 0:
        print("No metrics available for plotting.")
        return
    
    x = np.arange(len(models))
    width = 0.8 / len(metrics)
    fig, ax = plt.subplots(figsize=(14, 6))
    for i, metric in enumerate(metrics):
        values = [model_metric_avg[model][metric] for model in models]
        ax.bar(x + i*width, values, width, label=metric)
    ax.set_xticks(x + width*(len(metrics)-1)/2)
    ax.set_xticklabels(models, rotation=20, fontsize=20)
    ax.set_ylabel('Average Metric Value', fontsize=18)
    if not no_titles:
        ax.set_title('Average Model Metrics Across Benchmarks', fontsize=20)
    ax.legend(loc='best', fontsize=15, ncol=2)
    ax.tick_params(axis='y', labelsize=15)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-model-averages.pdf', bbox_inches='tight')
    plt.show()


def collect_and_sum_benchmark_metrics(benchmarks, evalsDir, columns_of_interest):
    """Collect and sum metrics across benchmarks."""
    data = {}
    sums = {bench: {col: 0.0 for col in columns_of_interest} for bench in benchmarks}
    for benchmark in benchmarks:
        csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        if not os.path.isfile(csv_path):
            print(f"Warning: {csv_path} not found, skipping.")
            continue
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        data[benchmark] = {}
        for _, row in df.iterrows():
            model = row['model']
            data[benchmark][model] = {}
            for col in columns_of_interest:
                val = parse_metric(row.get(col, 0))
                data[benchmark][model][col] = val
                sums[benchmark][col] += val
    return data, sums


def print_sums_table(sums, columns_of_interest):
    """Print table of summed metrics by benchmark."""
    print("Benchmark\t" + "\t".join(columns_of_interest))
    for bench, colvals in sums.items():
        row = [bench] + [f"{colvals[col]:.2f}" for col in columns_of_interest]
        print("\t".join(row))


def plot_sums_bar(sums, columns_of_interest, outputDir, evalsDir, no_titles=False):
    """Plot bar charts of summed metrics."""
    benchmarks = list(sums.keys())
    for col in columns_of_interest:
        values = [sums[bench][col] for bench in benchmarks]
        plt.figure(figsize=(10, 5))
        plt.bar(benchmarks, values)
        plt.ylabel(col, fontsize=18)
        if not no_titles:
            plt.title(f"Sum of {col} by Benchmark", fontsize=20)
        plt.xticks(rotation=20, fontsize=15)
        plt.yticks(fontsize=15)
        plt.tight_layout()
        plt.savefig(f'{outputDir}/benchmark-sums-{col.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
        plt.show()


def average_tests_per_model(benchmarks, evalsDir):
    """Calculate average tests per model for each benchmark."""
    averages = {}
    for benchmark in benchmarks:
        csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        if not os.path.isfile(csv_path):
            print(f"Warning: {csv_path} not found, skipping.")
            continue
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        tests = df['tests'].apply(parse_metric)
        if len(tests) > 0:
            avg = np.mean(tests)
        else:
            avg = 0.0
        averages[benchmark] = avg
    return averages


def print_avg_table(averages):
    """Print average tests per model table."""
    print("Benchmark\tAverage Tests per Model")
    for bench, avg in averages.items():
        print(f"{bench}\t{avg:.2f}")


def plot_avg_bar(averages, outputDir, evalsDir, no_titles=False):
    """Plot bar chart of average tests per model."""
    benchmarks = list(averages.keys())
    values = list(averages.values())
    plt.figure(figsize=(10, 5))
    plt.bar(benchmarks, values)
    plt.ylabel("Average Tests per Model", fontsize=18)
    if not no_titles:
        plt.title("Average Tests per Model by Benchmark", fontsize=20)
    plt.xticks(rotation=20, fontsize=15)
    plt.yticks(fontsize=15)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-average-tests-per-model.pdf', bbox_inches='tight')
    plt.show()


def get_default_benchmarks(evalsDir):
    """Get all available benchmarks from the evaluation directory."""
    benchmarks = []
    if os.path.isdir(evalsDir):
        for item in os.listdir(evalsDir):
            item_path = os.path.join(evalsDir, item)
            if os.path.isdir(item_path):
                overview_path = os.path.join(item_path, item, "overview.csv")
                if os.path.isfile(overview_path):
                    benchmarks.append(item)
    return sorted(benchmarks)


def plot_grouped_barplot_by_benchmark_and_model(benchmarks, evalsDir, column_of_interest, outputDir=None, show_error_bars=False, no_titles=False):
    """Create a grouped barplot showing a specific column as a function of benchmark and model."""
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    if outputDir is None:
        outputDir = evalsDir
    
    # Data structure: {benchmark: {model: value}}
    data = {}
    all_models = set()
    
    for benchmark in benchmarks:
        csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        if not os.path.isfile(csv_path):
            print(f"Warning: {csv_path} not found, skipping.")
            continue
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        if "model" not in df.columns or column_of_interest not in df.columns:
            print(f"Warning: Required columns not found in {csv_path}, skipping.")
            continue
            
        data[benchmark] = {}
        for _, row in df.iterrows():
            model = row["model"]
            val = parse_metric(row[column_of_interest])
            data[benchmark][model] = val
            all_models.add(model)
    
    all_models = sorted(all_models)
    benchmarks_with_data = [b for b in benchmarks if b in data]
    
    if not benchmarks_with_data or not all_models:
        print("No data found for plotting.")
        return
    
    # Build data matrix: rows=benchmarks, columns=models
    values = []
    for benchmark in benchmarks_with_data:
        row = []
        for model in all_models:
            row.append(data.get(benchmark, {}).get(model, 0.0))
        values.append(row)
    values = np.array(values)  # shape: (num_benchmarks, num_models)
    
    # Calculate averages and standard deviations across benchmarks for each model
    model_averages = []
    model_std_devs = []
    for i, model in enumerate(all_models):
        # Get values for this model across all benchmarks
        model_values = values[:, i]
        # Only consider non-zero values for statistics
        non_zero_values = model_values[model_values > 0]
        if len(non_zero_values) > 0:
            avg = np.mean(non_zero_values)
            std = np.std(non_zero_values, ddof=1) if len(non_zero_values) > 1 else 0.0
        else:
            avg = 0.0
            std = 0.0
        model_averages.append(avg)
        model_std_devs.append(std)
    
    # Add the average row to the data
    all_values = np.vstack([values, model_averages])
    all_labels = benchmarks_with_data + ["Average"]
    
    # Create the grouped bar plot
    x = np.arange(len(all_labels))  # positions for all groups including average
    width = 0.8 / len(all_models)  # width of individual bars
    
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Create bars for each model
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_models)))
    for i, model in enumerate(all_models):
        offset = (i - (len(all_models) - 1) / 2) * width
        bars = ax.bar(x + offset, all_values[:, i], width, label=model, alpha=0.8, color=colors[i])
        
        # Style the average (last) bar differently and optionally add error bars
        if len(bars) > len(benchmarks_with_data):
            # Highlight the average bars with different styling
            bars[-1].set_alpha(1.0)  # Make average bar more opaque
            bars[-1].set_edgecolor('black')  # Add black border to average bar
            bars[-1].set_linewidth(2)
            
            # Add error bar to the average bar only if show_error_bars is True
            if show_error_bars:
                avg_x_pos = x[-1] + offset
                avg_height = model_averages[i]
                error_bar = model_std_devs[i]
                
                if error_bar > 0:  # Only add error bar if we have variation
                    ax.errorbar(avg_x_pos, avg_height, yerr=error_bar, 
                               fmt='none', color='black', capsize=5, capthick=2, alpha=0.8)
    
    # Add a vertical separator line before the average group
    if len(all_labels) > 1:
        separator_x = len(benchmarks_with_data) - 0.5
        ax.axvline(x=separator_x, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=18)
    ax.set_ylabel(column_of_interest, fontsize=18)
    title_suffix = ' (with Cross-Benchmark Averages ± SD)' if show_error_bars else ' (with Cross-Benchmark Averages)'
    if not no_titles:
        ax.set_title(f'{column_of_interest} by Benchmark and Model{title_suffix}', fontsize=20)
    ax.set_xticks(x)
    ax.set_xticklabels(all_labels, rotation=45, ha='right', fontsize=15)
    ax.legend(loc='upper left', fontsize=15, ncol=2)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelsize=15)
    
    # Add text annotation for the average section
    if len(all_labels) > 1:
        annotation_suffix = ' ± SD' if show_error_bars else ''
        ax.text(len(benchmarks_with_data), ax.get_ylim()[1] * 0.95, f'Cross-Benchmark\nAverages{annotation_suffix}', 
                ha='center', va='top', fontsize=14, style='italic', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-grouped-{column_of_interest.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print statistics including standard deviations
    print(f"\nModel Statistics for {column_of_interest} (including zeros):")
    print("=" * 60)
    for i, model in enumerate(all_models):
        print(f"{model}: {model_averages[i]:.2f} ± {model_std_devs[i]:.2f}")


def plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, metric_column="tests compliant", outputDir=None, show_error_bars=False, no_titles=False, project_name='PromptPex'):
    """
    Create a grouped bar plot showing baseline vs main metrics across benchmarks.
    Automatically detects whether to show compliance/non-compliance or raw values based on metric name.
    
    Args:
        benchmarks: List of benchmark names
        evalsDir: Directory containing evaluation results
        metric_column: Column name to plot (default: "tests compliant")
        outputDir: Directory to save plots (default: evalsDir)
        show_error_bars: Whether to show error bars (default: False)
    """
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    if outputDir is None:
        outputDir = evalsDir
    
    # Determine if this is a compliance metric (should be converted to non-compliance)
    # or an accuracy/other metric (should be shown as-is)
    is_compliance_metric = "compliant" in metric_column.lower()
    is_accuracy_metric = "accuracy" in metric_column.lower()
    
    # Set appropriate labels and conversion logic
    if is_compliance_metric:
        y_label = "Tests Non-compliance %"
        convert_values = lambda x: [100.0 - v for v in x]  # Convert to non-compliance
        title_suffix = "Non-Compliance"
    elif is_accuracy_metric:
        y_label = "Accuracy %"
        convert_values = lambda x: x  # Keep as-is for accuracy
        title_suffix = "Accuracy"
    else:
        y_label = metric_column
        convert_values = lambda x: x  # Keep as-is for other metrics
        title_suffix = metric_column
    
    # Collect data for each benchmark
    benchmark_data = {}
    all_main_values = []  # For calculating overall statistics
    all_baseline_values = []
    all_inverse_values = []
    
    for benchmark in benchmarks:
        main_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        baseline_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview-baseline.csv")
        
        # Skip if either file doesn't exist
        if not (os.path.isfile(main_csv_path) and os.path.isfile(baseline_csv_path)):
            continue
            
        try:
            # Read both CSV files
            main_df = pd.read_csv(main_csv_path)
            baseline_df = pd.read_csv(baseline_csv_path)
            
            # Strip whitespace from column names
            main_df.columns = main_df.columns.str.strip()
            baseline_df.columns = baseline_df.columns.str.strip()
            
            # Check if the metric column exists in both files
            if metric_column not in main_df.columns or metric_column not in baseline_df.columns:
                print(f"Warning: '{metric_column}' not found in {benchmark}, skipping.")
                continue
            
            # Get raw values for each dataset
            main_values = [parse_metric(val) for val in main_df[metric_column]]
            baseline_values = [parse_metric(val) for val in baseline_df[metric_column]]
            
            # Get inverse values (tests negative compliant) if available and this is a compliance metric
            inverse_values = []
            if is_compliance_metric and "tests negative compliant" in main_df.columns and "tests negative" in main_df.columns:
                for _, row in main_df.iterrows():
                    neg_compliant = parse_metric(row["tests negative compliant"])
                    neg_total = parse_metric(row["tests negative"])
                    if neg_total > 0:
                        compliance_pct = (neg_compliant / neg_total) * 100.0
                    else:
                        compliance_pct = 0.0
                    inverse_values.append(compliance_pct)
            
            # Apply appropriate conversion (non-compliance conversion or keep as-is)
            main_converted = convert_values(main_values)
            baseline_converted = convert_values(baseline_values)
            inverse_converted = convert_values(inverse_values) if inverse_values else []
            
            # Calculate averages and standard deviations  
            main_valid = [v for v in main_converted]  # Include all values
            baseline_valid = [v for v in baseline_converted]
            inverse_valid = [v for v in inverse_converted] if inverse_converted else []
            
            if main_valid and baseline_valid:
                main_avg = np.mean(main_valid)
                baseline_avg = np.mean(baseline_valid)
                main_std = np.std(main_valid, ddof=1) if len(main_valid) > 1 else 0.0
                baseline_std = np.std(baseline_valid, ddof=1) if len(baseline_valid) > 1 else 0.0
                
                # Calculate inverse stats if available
                inverse_avg = np.mean(inverse_valid) if inverse_valid else 0.0
                inverse_std = np.std(inverse_valid, ddof=1) if len(inverse_valid) > 1 else 0.0
                
                benchmark_data[benchmark] = {
                    'main_avg': main_avg,
                    'baseline_avg': baseline_avg,
                    'inverse_avg': inverse_avg,
                    'main_std': main_std,
                    'baseline_std': baseline_std,
                    'inverse_std': inverse_std,
                    'main_count': len(main_valid),
                    'baseline_count': len(baseline_valid),
                    'inverse_count': len(inverse_valid),
                    'main_values': main_valid,
                    'baseline_values': baseline_valid
                }
                
                # Store individual values for overall statistics
                all_main_values.extend(main_valid)
                all_baseline_values.extend(baseline_valid)
                if inverse_valid:
                    all_inverse_values.extend(inverse_valid)
                
        except Exception as e:
            print(f"Error processing {benchmark}: {e}")
            continue
    
    if not benchmark_data:
        print(f"No valid data found for {metric_column}")
        return
    
    # Prepare data for plotting
    benchmark_names = list(benchmark_data.keys())
    main_averages = [benchmark_data[b]['main_avg'] for b in benchmark_names]
    baseline_averages = [benchmark_data[b]['baseline_avg'] for b in benchmark_names]
    inverse_averages = [benchmark_data[b]['inverse_avg'] for b in benchmark_names]
    main_stds = [benchmark_data[b]['main_std'] for b in benchmark_names]
    baseline_stds = [benchmark_data[b]['baseline_std'] for b in benchmark_names]
    inverse_stds = [benchmark_data[b]['inverse_std'] for b in benchmark_names]
    
    # Calculate overall averages and standard deviations
    overall_main_avg = np.mean(all_main_values) if all_main_values else 0
    overall_baseline_avg = np.mean(all_baseline_values) if all_baseline_values else 0
    overall_inverse_avg = np.mean(all_inverse_values) if all_inverse_values else 0.0
    overall_main_std = np.std(all_main_values, ddof=1) if len(all_main_values) > 1 else 0.0
    overall_baseline_std = np.std(all_baseline_values, ddof=1) if len(all_baseline_values) > 1 else 0.0
    overall_inverse_std = np.std(all_inverse_values, ddof=1) if len(all_inverse_values) > 1 else 0.0
    
    # Extend data with overall averages
    extended_benchmark_names = benchmark_names + ["Overall Average"]
    extended_main_averages = main_averages + [overall_main_avg]
    extended_baseline_averages = baseline_averages + [overall_baseline_avg]
    extended_inverse_averages = inverse_averages + [overall_inverse_avg]
    extended_main_stds = main_stds + [overall_main_std]
    extended_baseline_stds = baseline_stds + [overall_baseline_std]
    extended_inverse_stds = inverse_stds + [overall_inverse_std]
    
    # Create the grouped bar plot with optional third bar
    x = np.arange(len(extended_benchmark_names))
    has_inverse = any(v > 0 for v in extended_inverse_averages)
    width = 0.25 if has_inverse else 0.35  # Adjust width based on number of bars
    
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Create bars with optional error bars
    error_kw = {'capsize': 4, 'capthick': 2, 'alpha': 0.8} if show_error_bars else None
    
    bars1 = ax.bar(x - width, extended_baseline_averages, width, label='Baseline', 
                   color='lightblue', alpha=0.8, edgecolor='navy', linewidth=0.5,
                   yerr=extended_baseline_stds if show_error_bars else None, 
                   error_kw=error_kw)
    bars2 = ax.bar(x, extended_main_averages, width, label=project_name, 
                   color='lightcoral', alpha=0.8, edgecolor='darkred', linewidth=0.5,
                   yerr=extended_main_stds if show_error_bars else None, 
                   error_kw=error_kw)
    
    # Add third bar only if we have inverse data and this is a compliance metric
    bars3 = None
    if has_inverse and is_compliance_metric:
        bars3 = ax.bar(x + width, extended_inverse_averages, width, label=f'{project_name} Inverse', 
                       color='lightgreen', alpha=0.8, edgecolor='darkgreen', linewidth=0.5,
                       yerr=extended_inverse_stds if show_error_bars else None, 
                       error_kw=error_kw)
    
    # Highlight the average bars with different styling
    if len(extended_benchmark_names) > len(benchmark_names):
        # Make average bars more prominent
        bars1[-1].set_alpha(1.0)
        bars1[-1].set_edgecolor('black')
        bars1[-1].set_linewidth(2)
        bars2[-1].set_alpha(1.0)
        bars2[-1].set_edgecolor('black')
        bars2[-1].set_linewidth(2)
        if bars3:
            bars3[-1].set_alpha(1.0)
            bars3[-1].set_edgecolor('black')
            bars3[-1].set_linewidth(2)
        
        # Add separator line
        separator_x = len(benchmark_names) - 0.5
        ax.axvline(x=separator_x, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
    # Add value labels on bars
    def add_value_labels(bars, values, errors):
        for bar, value, error in zip(bars, values, errors):
            height = bar.get_height()
            # Position label above error bar if shown, otherwise just above bar
            label_height = height + (error + 1.0 if show_error_bars else 1.0)
            ax.text(bar.get_x() + bar.get_width()/2., label_height,
                   f'{value:.0f}%', ha='center', va='bottom', fontsize=13)
    
    add_value_labels(bars1, extended_baseline_averages, extended_baseline_stds)
    add_value_labels(bars2, extended_main_averages, extended_main_stds)
    if bars3:
        add_value_labels(bars3, extended_inverse_averages, extended_inverse_stds)
    
    ax.set_xlabel('Benchmark', fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    title_suffix_error = " (with Overall Average ± SD)" if show_error_bars else " (with Overall Average)"
    inverse_title_part = f" vs {project_name} Inverse" if (has_inverse and is_compliance_metric) else ""
    if not no_titles:
        # Handle special case for tests compliant to avoid "Tests Compliant Non-Compliance"
        if metric_column.lower() == "tests compliant" and title_suffix == "Non-Compliance":
            chart_title = f'Test {title_suffix} - Baseline vs {project_name}{inverse_title_part} by Benchmark{title_suffix_error}'
        else:
            chart_title = f'{metric_column.title()} {title_suffix} - Baseline vs {project_name}{inverse_title_part} by Benchmark{title_suffix_error}'
        ax.set_title(chart_title, fontsize=20, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(extended_benchmark_names, rotation=45, ha='right', fontsize=15)
    ax.legend(fontsize=15)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelsize=15)
    
    # Set y-axis to accommodate error bars if shown
    all_values_for_scaling = extended_baseline_averages + extended_main_averages
    if bars3:
        all_values_for_scaling += extended_inverse_averages
        
    if show_error_bars:
        all_errors_for_scaling = extended_baseline_stds + extended_main_stds
        if bars3:
            all_errors_for_scaling += extended_inverse_stds
        max_val = max(np.array(all_values_for_scaling) + np.array(all_errors_for_scaling))
        ax.set_ylim(0, max_val * 1.15)
    else:
        max_val = max(all_values_for_scaling)
        ax.set_ylim(0, max_val * 1.1)
    
    # Add text annotation for overall average section
    if len(extended_benchmark_names) > len(benchmark_names):
        annotation_suffix = " ± SD" if show_error_bars else ""
        ax.text(len(benchmark_names), ax.get_ylim()[1] * 0.95, f'Overall\nAverage{annotation_suffix}', 
                ha='center', va='top', fontsize=14, style='italic', alpha=0.7)
    
    # Print comprehensive improvement summary
    print_improvement_summary_table(benchmark_data, benchmark_names, metric_column, is_compliance_metric, project_name)
    
    # Generate relative improvement chart
    plot_relative_improvement_chart(benchmark_data, benchmark_names, metric_column, is_compliance_metric, outputDir, no_titles)
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-baseline-comparison-{metric_column.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print summary statistics with standard deviations
    # Handle special case for tests compliant to avoid "tests compliant Non-Compliance"
    if metric_column.lower() == "tests compliant" and title_suffix == "Non-Compliance":
        summary_title = f"test {title_suffix}"
    else:
        summary_title = f"{metric_column} {title_suffix}"
    print(f"\nSummary Statistics for {summary_title}:")
    print("=" * 70)
    
    # Calculate improvements based on metric type
    if is_compliance_metric:
        # For non-compliance, lower is better
        improvement_main = overall_baseline_avg - overall_main_avg
        improvement_inverse = overall_baseline_avg - overall_inverse_avg
        improvement_word = "improvement" if improvement_main > 0 else "decline"
        improvement_word_inverse = "improvement" if improvement_inverse > 0 else "decline"
    else:
        # For accuracy and other metrics, higher is usually better
        improvement_main = overall_main_avg - overall_baseline_avg
        improvement_inverse = overall_inverse_avg - overall_baseline_avg
        improvement_word = "improvement" if improvement_main > 0 else "decline"
        improvement_word_inverse = "improvement" if improvement_inverse > 0 else "decline"
    
    print(f"Overall Average (Baseline): {overall_baseline_avg:.2f}% ± {overall_baseline_std:.2f}%")
    print(f"Overall Average ({project_name}): {overall_main_avg:.2f}% ± {overall_main_std:.2f}%")
    if has_inverse and is_compliance_metric:
        print(f"Overall Average ({project_name} Inverse): {overall_inverse_avg:.2f}% ± {overall_inverse_std:.2f}%")
    print(f"Overall Improvement ({project_name}): {improvement_main:+.2f}% ({improvement_word})")
    if has_inverse and is_compliance_metric:
        print(f"Overall Improvement ({project_name} Inverse): {improvement_inverse:+.2f}% ({improvement_word_inverse})")
    print(f"Number of benchmarks: {len(benchmark_names)}")
    print(f"Total data points: {len(all_baseline_values)} baseline, {len(all_main_values)} {project_name.lower()}" + 
          (f", {len(all_inverse_values)} inverse" if all_inverse_values else ""))
    
    # Handle special case for tests compliant to avoid "tests compliant Non-Compliance"
    if metric_column.lower() == "tests compliant" and title_suffix == "Non-Compliance":
        breakdown_title = f"test {title_suffix}"
    else:
        breakdown_title = f"{title_suffix}"
    print(f"\nPer-benchmark breakdown ({breakdown_title}):")
    print("-" * 70)
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        if is_compliance_metric:
            diff_main = data['baseline_avg'] - data['main_avg']  # For non-compliance, lower is better
            diff_inverse = data['baseline_avg'] - data['inverse_avg']
        else:
            diff_main = data['main_avg'] - data['baseline_avg']  # For accuracy, higher is better
            diff_inverse = data['inverse_avg'] - data['baseline_avg']
            
        print(f"{benchmark}:")
        print(f"  Baseline: {data['baseline_avg']:.1f}% ± {data['baseline_std']:.1f}% (n={data['baseline_count']})")
        print(f"  {project_name}: {data['main_avg']:.1f}% ± {data['main_std']:.1f}% (n={data['main_count']})")
        if has_inverse and is_compliance_metric:
            print(f"  {project_name} Inverse: {data['inverse_avg']:.1f}% ± {data['inverse_std']:.1f}% (n={data['inverse_count']})")
        print(f"  Improvement ({project_name}): {diff_main:+.1f}%")
        if has_inverse and is_compliance_metric:
            print(f"  Improvement ({project_name} Inverse): {diff_inverse:+.1f}%")
        print()


def parse_percentage(val):
    """Parse a percentage value, handling various formats."""
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.endswith('%'):
                return float(val[:-1])
            else:
                return float(val)
        elif pd.isna(val):
            return 0.0
        else:
            return float(val)
    except (ValueError, TypeError):
        return 0.0


def generate_plot_results_style_analysis(benchmarks, evalsDir, outputDir, project_name='PromptPex'):
    """
    Generate plot-results.ipynb style analysis and charts.
    Creates comprehensive compliance analysis with multiple chart types.
    """
    print("\n" + "="*60)
    print("PLOT-RESULTS STYLE ANALYSIS")
    print("="*60)
    
    # Set consistent matplotlib style for technical papers
    # (Global settings already applied at script start)
    
    # Define pretty names for benchmarks
    prettyNames = {
        "speech-tag": "speech-tag", 
        "text-to-p": "text-to-p",  
        "shakespearean-writing-assistant": "shakespeare", 
        "sentence-rewrite": "sentence", 
        "extract-names": "extract-names", 
        "elements": "elements", 
        "art-prompt": "art-prompt", 
        "classify-input-text": "classify"
    }
    
    # Data collection
    data = {}
    comp_val = {}
    base_comp_val = {}
    pos_comp_val = {}
    neg_comp_val = {}
    
    # Track benchmarks with negative tests for filtering
    benchmarks_with_neg_tests = []
    benchmarks_without_neg_tests = []
    
    print("Loading benchmark data...")
    
    for benchmark in benchmarks:
        csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        if not os.path.isfile(csv_path):
            print(f"Warning: {csv_path} not found, skipping benchmark {benchmark}")
            continue
            
        print(f"Processing benchmark: {benchmark}")
        data[benchmark] = pd.read_csv(csv_path)
        db = data[benchmark]
        
        # Check for negative tests
        if "tests negative" in db.columns:
            if db["tests negative"].iloc[0] == 0:
                print(f"  No negative tests for: {benchmark}")
                benchmarks_without_neg_tests.append(benchmark)
            else:
                benchmarks_with_neg_tests.append(benchmark)
        else:
            db["tests negative"] = 0
            benchmarks_without_neg_tests.append(benchmark)
        
        # Calculate compliance percentages
        db["compliant %"] = [parse_percentage(p) / 100 for p in db["tests compliant"]]
        
        # Check if baseline data exists
        baseline_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview-baseline.csv")
        if os.path.isfile(baseline_csv_path):
            baseline_df = pd.read_csv(baseline_csv_path)
            baseline_df.columns = baseline_df.columns.str.strip()
            if "tests compliant" in baseline_df.columns:
                db["baseline %"] = [parse_percentage(p) / 100 for p in baseline_df["tests compliant"]]
            else:
                db["baseline %"] = 0
        else:
            db["baseline %"] = 0
            
        db["pos rule %"] = db["tests positive compliant"] / db["tests positive"]
        
        # Handle division by zero for negative rules
        if db["tests negative"].iloc[0] > 0:
            db["neg rule %"] = db["tests negative compliant"] / db["tests negative"]
        else:
            db["neg rule %"] = np.nan
            
        db["valid test %"] = db["tests valid"] / db["tests"]
        
        # Store values
        comp_val[benchmark] = db["compliant %"]
        base_comp_val[benchmark] = db["baseline %"]
        pos_comp_val[benchmark] = db["pos rule %"]
        neg_comp_val[benchmark] = db["neg rule %"]
    
    # Filter out benchmarks that failed to load
    valid_benchmarks = [b for b in benchmarks if b in data]
    benchmarks = valid_benchmarks
    
    if not benchmarks:
        print("No valid benchmarks found for plot-results analysis")
        return
    
    # Calculate sums and means
    n_models = len(data[benchmarks[0]]["model"])
    comp_val["sum"] = pd.Series([0.0 for i in range(n_models)])
    base_comp_val["sum"] = pd.Series([0.0 for i in range(n_models)])
    pos_comp_val["sum"] = pd.Series([0.0 for i in range(n_models)])
    neg_comp_val["sum"] = pd.Series([0.0 for i in range(n_models)])
    
    # Sum up values across benchmarks
    for key in comp_val:
        if key != "sum":
            comp_val["sum"] = comp_val["sum"] + comp_val[key]
            base_comp_val["sum"] = base_comp_val["sum"] + base_comp_val[key]
            pos_comp_val["sum"] = pos_comp_val["sum"] + pos_comp_val[key]
            if key in benchmarks_with_neg_tests:
                neg_comp_val["sum"] = neg_comp_val["sum"] + neg_comp_val[key]
    
    # Calculate means
    comp_val["mean"] = comp_val["sum"] / len(benchmarks)
    base_comp_val["mean"] = base_comp_val["sum"] / len(benchmarks)
    pos_comp_val["mean"] = pos_comp_val["sum"] / len(benchmarks)
    if len(benchmarks_with_neg_tests) > 0:
        neg_comp_val["mean"] = neg_comp_val["sum"] / len(benchmarks_with_neg_tests)
    else:
        neg_comp_val["mean"] = pd.Series([np.nan for i in range(n_models)])
    
    # Generate CSV files
    print("Generating CSV files...")
    
    # 1. Non-compliance percentage per benchmark
    with open(f'{outputDir}/pp-cpct.csv', 'w') as cfile:
        print("Benchmark,", end="", file=cfile)
        db = data[benchmarks[0]]
        print(', '.join(map(str, db["model"])), file=cfile)
        
        for benchmark in benchmarks:
            name = prettyNames.get(benchmark, benchmark)
            print(name, ",", end="", file=cfile)
            db = data[benchmark]
            print(', '.join(map(str, (1 - db["compliant %"]))), file=cfile)
        
        print("average", ",", end="", file=cfile)
        print(', '.join(map(str, (1 - comp_val["mean"]))), file=cfile)
    
    # 2. Test validity per benchmark
    with open(f'{outputDir}/pp-test-validity.csv', 'w') as cfile:
        print("Benchmark, tests, valid tests", file=cfile)
        for benchmark in benchmarks:
            name = prettyNames.get(benchmark, benchmark)
            db = data[benchmark]
            print(f'{name},{db["tests"].iloc[0]}, {db["tests valid"].iloc[0]}', file=cfile)
    
    # 3. Positive vs negative compliance (only for benchmarks with negative tests)
    with open(f'{outputDir}/pos-neg-cpct.csv', 'w') as cfile:
        models = data[benchmarks[0]]["model"]
        pos_sum = pd.Series([0.0 for i in range(len(models))])
        neg_sum = pd.Series([0.0 for i in range(len(models))])
        
        print("Model, Rule % Non-Compliance, Inv Rule % Non-Compliance", file=cfile)
        
        for b in benchmarks_with_neg_tests:
            db = data[b]
            pos_sum += db["pos rule %"]
            neg_sum += db["neg rule %"]
        
        if len(benchmarks_with_neg_tests) > 0:
            for m, psum, nsum in zip(models, pos_sum, neg_sum):
                print(m, ",", (1 - psum/len(benchmarks_with_neg_tests)), ",", (1 - nsum/len(benchmarks_with_neg_tests)), file=cfile)
    
    # 4. Project vs baseline comparison
    with open(f'{outputDir}/pp-compare.csv', 'w') as cfile:
        models = data[benchmarks[0]]["model"]
        pp_sum = pd.Series([0.0 for i in range(len(models))])
        bl_sum = pd.Series([0.0 for i in range(len(models))])
        
        print(f"Model, {project_name} % Non-Compliance, Baseline % Non-Compliance", file=cfile)
        
        for b in benchmarks:
            db = data[b]
            pp_sum += db["compliant %"]
            bl_sum += db["baseline %"]
        
        for m, psum, bsum in zip(models, pp_sum, bl_sum):
            print(m, ",", (1 - psum/len(benchmarks)), ",", (1 - bsum/len(benchmarks)), file=cfile)
    
    # 5. Rules count per benchmark
    with open(f'{outputDir}/pp-grounded-rules.csv', 'w') as cfile:
        print("benchmark, rules, grounded rules", file=cfile)
        for benchmark in benchmarks:
            rules_file_path = os.path.join(evalsDir, benchmark, benchmark, 'rules.txt')
            if os.path.exists(rules_file_path):
                with open(rules_file_path, 'r') as file:
                    lines = file.readlines()
                    rule_count = len([line for line in lines if line.strip()])
            else:
                rule_count = 0
                print(f"Warning: {rules_file_path} not found")
            
            name = prettyNames.get(benchmark, benchmark)
            print(f"{name}, {rule_count}, {rule_count}", file=cfile)
    
    print("Generating charts...")
    
    # Generate Chart 1: Non-compliance by benchmark and model
    _plot_non_compliance_by_benchmark(outputDir, project_name)
    
    # Generate Chart 2: Rule vs Inverse Rule comparison
    _plot_rule_vs_inverse_rule(outputDir, project_name)
    
    # Generate Chart 3: Project vs Baseline comparison
    _plot_promptpex_vs_baseline(outputDir, project_name)
    
    # Generate Chart 4: Test validity chart
    _plot_test_validity(outputDir, project_name)
    
    # Generate Chart 5: Rules count chart
    _plot_rules_count(outputDir, project_name)
    
    print(f"Plot-results style analysis complete! Files saved to {outputDir}")


def _plot_non_compliance_by_benchmark(outputDir, project_name='PromptPex'):
    """Generate clustered bar chart of non-compliance by benchmark and model."""
    try:
        df = pd.read_csv(f'{outputDir}/pp-cpct.csv')
        df = df[df['Benchmark'] != 'average']
        df.set_index('Benchmark', inplace=True)
        
        fig, ax = plt.subplots(figsize=(18, 8))
        
        n_benchmarks = len(df.index)
        n_models = len(df.columns)
        bar_width = 0.8 / n_models
        indices = np.arange(n_benchmarks)
        
        # Use consistent colors
        colors = plt.cm.Set3(np.linspace(0, 1, n_models))
        
        for i, model in enumerate(df.columns):
            ax.bar(indices + i * bar_width, df[model] * 100, bar_width, 
                   label=model, alpha=0.8, color=colors[i], edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(indices + bar_width * (n_models - 1) / 2)
        ax.set_xticklabels(df.index, rotation=45, ha='right', fontsize=15)
        ax.set_xlabel('Benchmark', fontsize=18)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=18)
        ax.set_title('Non-Compliance by Benchmark and Model', fontsize=20, pad=20)
        ax.legend(loc='upper right', fontsize=15, ncol=2)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='y', labelsize=15)
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-cpct.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-cpct.pdf")
        
    except Exception as e:
        print(f"Error generating non-compliance chart: {e}")


def _plot_rule_vs_inverse_rule(outputDir, project_name='PromptPex'):
    """Generate rule vs inverse rule comparison chart."""
    try:
        df = pd.read_csv(f'{outputDir}/pos-neg-cpct.csv')
        df_filtered = df.dropna(subset=[' Inv Rule % Non-Compliance'])
        df_filtered = df_filtered[df_filtered[' Inv Rule % Non-Compliance'] != 1.0]
        
        if len(df_filtered) == 0:
            print("No data available for rule vs inverse rule chart")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bar_width = 0.35
        indices = range(len(df_filtered))
        
        ax.bar(indices, df_filtered[' Rule % Non-Compliance'] * 100, bar_width, 
               label='Rule', alpha=0.8, color='lightcoral', edgecolor='darkred', linewidth=0.8)
        ax.bar([i + bar_width for i in indices], df_filtered[' Inv Rule % Non-Compliance'] * 100, bar_width, 
               label='Inverse Rule', alpha=0.8, color='lightgreen', edgecolor='darkgreen', linewidth=0.8)
        
        ax.set_xticks([i + bar_width / 2 for i in indices])
        ax.set_xticklabels(df_filtered['Model'], rotation=0, ha='center', fontsize=20)
        ax.set_xlabel('Model', fontsize=18)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=18)
        ax.set_title('Rule vs Inverse Rule Non-Compliance', fontsize=20, pad=20)
        ax.legend(fontsize=15)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='y', labelsize=15)
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pos-neg-cpct.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pos-neg-cpct.pdf")
        
    except Exception as e:
        print(f"Error generating rule vs inverse rule chart: {e}")


def _plot_promptpex_vs_baseline(outputDir, project_name='PromptPex'):
    """Generate project vs Baseline comparison chart."""
    try:
        df = pd.read_csv(f'{outputDir}/pp-compare.csv')
        
        # Replace PromptPex with project_name in column headers
        df.columns = df.columns.str.replace('PromptPex', project_name)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bar_width = 0.35
        indices = range(len(df))
        
        ax.bar(indices, df[f' {project_name} % Non-Compliance'] * 100, bar_width, 
               label=project_name, alpha=0.8, color='lightcoral', edgecolor='darkred', linewidth=0.8)
        ax.bar([i + bar_width for i in indices], df[' Baseline % Non-Compliance'] * 100, bar_width, 
               label='Baseline', alpha=0.8, color='lightsteelblue', edgecolor='darkblue', linewidth=0.8)
        
        ax.set_xticks([i + bar_width / 2 for i in indices])
        ax.set_xticklabels(df['Model'], rotation=0, ha='center', fontsize=20)
        ax.set_xlabel('Model', fontsize=18)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=18)
        ax.set_title(f'{project_name} vs Baseline Non-Compliance', fontsize=20, pad=20)
        ax.legend(fontsize=15)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='y', labelsize=15)
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-compare.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-compare.pdf")
        
    except Exception as e:
        print(f"Error generating {project_name} vs Baseline chart: {e}")


def _plot_test_validity(outputDir, project_name='PromptPex'):
    """Generate test validity chart."""
    try:
        df = pd.read_csv(f'{outputDir}/pp-test-validity.csv')
        
        fig, ax = plt.subplots(figsize=(18, 8))
        
        plot_columns = [col for col in df.columns if col != 'Benchmark']
        n_benchmarks = len(df)
        n_columns = len(plot_columns)
        bar_width = 0.8 / n_columns
        x_positions = range(n_benchmarks)
        
        colors = ['lightblue', 'lightgreen']
        
        for i, col in enumerate(plot_columns):
            x_offset = [x + (i - (n_columns-1)/2) * bar_width for x in x_positions]
            ax.bar(x_offset, df[col], width=bar_width, 
                   label=col, alpha=0.8, color=colors[i % len(colors)], 
                   edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x_positions)
        ax.set_xticklabels(df['Benchmark'], rotation=45, ha='right', fontsize=15)
        ax.set_xlabel('Benchmark', fontsize=18)
        ax.set_ylabel('Number of Tests', fontsize=18)
        ax.set_title('Test Validity by Benchmark', fontsize=20, pad=20)
        ax.legend(fontsize=15)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='y', labelsize=15)
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-test-validity.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-test-validity.pdf")
        
    except Exception as e:
        print(f"Error generating test validity chart: {e}")


def _plot_rules_count(outputDir, project_name='PromptPex'):
    """Generate rules count chart."""
    try:
        df = pd.read_csv(f'{outputDir}/pp-grounded-rules.csv')
        
        fig, ax = plt.subplots(figsize=(18, 8))
        
        plot_columns = [col for col in df.columns if col != 'benchmark']
        n_benchmarks = len(df)
        n_columns = len(plot_columns)
        bar_width = 0.8 / n_columns
        x_positions = range(n_benchmarks)
        
        colors = ['lightcoral', 'lightblue']
        
        for i, col in enumerate(plot_columns):
            x_offset = [x + (i - (n_columns-1)/2) * bar_width for x in x_positions]
            ax.bar(x_offset, df[col], width=bar_width, 
                   label=col, alpha=0.8, color=colors[i % len(colors)], 
                   edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x_positions)
        ax.set_xticklabels(df['benchmark'], rotation=45, ha='right', fontsize=15)
        ax.set_xlabel('Benchmark', fontsize=18)
        ax.set_ylabel('Number of Rules', fontsize=18)
        ax.set_title('Rules Count by Benchmark', fontsize=20, pad=20)
        ax.legend(fontsize=15)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='y', labelsize=15)
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-grounded-rules.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-grounded-rules.pdf")
        
    except Exception as e:
        print(f"Error generating rules count chart: {e}")


def plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, model_filter, metric_column="tests compliant", outputDir=None, show_error_bars=False, no_titles=False, project_name='PromptPex'):
    """
    Create a grouped bar plot showing baseline vs main metrics across benchmarks for a specific model only.
    Automatically detects whether to show compliance/non-compliance or raw values based on metric name.
    
    Args:
        benchmarks: List of benchmark names
        evalsDir: Directory containing evaluation results
        model_filter: Specific model name to filter for (e.g., "gpt-oss")
        metric_column: Column name to plot (default: "tests compliant")
        outputDir: Directory to save plots (default: evalsDir)
        show_error_bars: Whether to show error bars (default: False)
    """
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    if outputDir is None:
        outputDir = evalsDir
    
    # Determine if this is a compliance metric (should be converted to non-compliance)
    # or an accuracy/other metric (should be shown as-is)
    is_compliance_metric = "compliant" in metric_column.lower()
    is_accuracy_metric = "accuracy" in metric_column.lower()
    
    # Set appropriate labels and conversion logic
    if is_compliance_metric:
        y_label = "Tests Non-compliance %"
        convert_values = lambda x: [100.0 - v for v in x]  # Convert to non-compliance
        title_suffix = "Non-Compliance"
    elif is_accuracy_metric:
        y_label = "Accuracy %"
        convert_values = lambda x: x  # Keep as-is for accuracy
        title_suffix = "Accuracy"
    else:
        y_label = metric_column
        convert_values = lambda x: x  # Keep as-is for other metrics
        title_suffix = metric_column
    
    # Collect data for each benchmark
    benchmark_data = {}
    all_main_values = []  # For calculating overall statistics
    all_baseline_values = []
    all_inverse_values = []
    
    for benchmark in benchmarks:
        main_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview.csv")
        baseline_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview-baseline.csv")
        
        # Skip if either file doesn't exist
        if not (os.path.isfile(main_csv_path) and os.path.isfile(baseline_csv_path)):
            continue
            
        try:
            # Read both CSV files
            main_df = pd.read_csv(main_csv_path)
            baseline_df = pd.read_csv(baseline_csv_path)
            
            # Strip whitespace from column names
            main_df.columns = main_df.columns.str.strip()
            baseline_df.columns = baseline_df.columns.str.strip()
            
            # Filter for specific model
            main_df_filtered = main_df[main_df['model'] == model_filter]
            baseline_df_filtered = baseline_df[baseline_df['model'] == model_filter]
            
            # Check if the model exists in both datasets and metric column exists
            if (len(main_df_filtered) == 0 or len(baseline_df_filtered) == 0 or 
                metric_column not in main_df.columns or metric_column not in baseline_df.columns):
                print(f"Warning: Model '{model_filter}' or column '{metric_column}' not found in {benchmark}, skipping.")
                continue
            
            # Get values for the specific model
            main_values = [parse_metric(val) for val in main_df_filtered[metric_column]]
            baseline_values = [parse_metric(val) for val in baseline_df_filtered[metric_column]]
            
            # Get inverse values (tests negative compliant) if available and this is a compliance metric
            inverse_values = []
            if is_compliance_metric and "tests negative compliant" in main_df.columns and "tests negative" in main_df.columns:
                for _, row in main_df_filtered.iterrows():
                    neg_compliant = parse_metric(row["tests negative compliant"])
                    neg_total = parse_metric(row["tests negative"])
                    if neg_total > 0:
                        compliance_pct = (neg_compliant / neg_total) * 100.0
                    else:
                        compliance_pct = 0.0
                    inverse_values.append(compliance_pct)
            
            # Apply appropriate conversion (non-compliance conversion or keep as-is)
            main_converted = convert_values(main_values)
            baseline_converted = convert_values(baseline_values)
            inverse_converted = convert_values(inverse_values) if inverse_values else []
            
            # Remove zero/invalid values for average calculation (but keep them for completeness)
            main_valid = [v for v in main_converted]
            baseline_valid = [v for v in baseline_converted]
            inverse_valid = [v for v in inverse_converted] if inverse_converted else []
            
            if main_valid and baseline_valid:
                main_avg = np.mean(main_valid)
                baseline_avg = np.mean(baseline_valid)
                main_std = np.std(main_valid, ddof=1) if len(main_valid) > 1 else 0.0
                baseline_std = np.std(baseline_valid, ddof=1) if len(baseline_valid) > 1 else 0.0
                
                # Calculate inverse stats if available
                inverse_avg = np.mean(inverse_valid) if inverse_valid else 0.0
                inverse_std = np.std(inverse_valid, ddof=1) if len(inverse_valid) > 1 else 0.0
                
                benchmark_data[benchmark] = {
                    'main_avg': main_avg,
                    'baseline_avg': baseline_avg,
                    'inverse_avg': inverse_avg,
                    'main_std': main_std,
                    'baseline_std': baseline_std,
                    'inverse_std': inverse_std,
                    'main_count': len(main_valid),
                    'baseline_count': len(baseline_valid),
                    'inverse_count': len(inverse_valid),
                    'main_values': main_valid,
                    'baseline_values': baseline_valid
                }
                
                # Store individual values for overall statistics
                all_main_values.extend(main_valid)
                all_baseline_values.extend(baseline_valid)
                if inverse_valid:
                    all_inverse_values.extend(inverse_valid)
            
        except Exception as e:
            print(f"Error processing {benchmark}: {str(e)}")
            continue
    
    if not benchmark_data:
        print(f"No benchmark data found for model '{model_filter}'.")
        return
    
    # Prepare data for plotting
    benchmark_names = list(benchmark_data.keys())
    main_values = [benchmark_data[b]['main_avg'] for b in benchmark_names]
    baseline_values = [benchmark_data[b]['baseline_avg'] for b in benchmark_names]
    inverse_values = [benchmark_data[b]['inverse_avg'] for b in benchmark_names]
    main_errors = [benchmark_data[b]['main_std'] for b in benchmark_names]
    baseline_errors = [benchmark_data[b]['baseline_std'] for b in benchmark_names]
    inverse_errors = [benchmark_data[b]['inverse_std'] for b in benchmark_names]
    
    # Calculate overall averages and standard deviations
    overall_main_avg = np.mean(all_main_values)
    overall_baseline_avg = np.mean(all_baseline_values)
    overall_inverse_avg = np.mean(all_inverse_values) if all_inverse_values else 0.0
    overall_main_std = np.std(all_main_values, ddof=1) if len(all_main_values) > 1 else 0.0
    overall_baseline_std = np.std(all_baseline_values, ddof=1) if len(all_baseline_values) > 1 else 0.0
    overall_inverse_std = np.std(all_inverse_values, ddof=1) if len(all_inverse_values) > 1 else 0.0
    
    # Add averages to the data
    all_benchmark_names = benchmark_names + ["Average"]
    all_main_values_plot = main_values + [overall_main_avg]
    all_baseline_values_plot = baseline_values + [overall_baseline_avg]
    all_inverse_values_plot = inverse_values + [overall_inverse_avg]
    all_main_errors_plot = main_errors + [overall_main_std]
    all_baseline_errors_plot = baseline_errors + [overall_baseline_std]
    all_inverse_errors_plot = inverse_errors + [overall_inverse_std]
    
    # Create the grouped bar plot with bars (inverse only for compliance metrics)
    x = np.arange(len(all_benchmark_names))
    has_inverse = any(v > 0 for v in all_inverse_values_plot) and is_compliance_metric
    width = 0.25 if has_inverse else 0.35  # Adjust width based on number of bars
    
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Create bars with optional error bars - use different colors for single model view
    error_kw = {'capsize': 4, 'capthick': 2, 'alpha': 0.8} if show_error_bars else None
    
    bars1 = ax.bar(x - width, all_baseline_values_plot, width, label='Baseline', 
                   color='lightsteelblue', alpha=0.8, edgecolor='darkblue', linewidth=0.8,
                   yerr=all_baseline_errors_plot if show_error_bars else None, 
                   error_kw=error_kw)
    bars2 = ax.bar(x, all_main_values_plot, width, label=project_name, 
                   color='orange', alpha=0.8, edgecolor='darkorange', linewidth=0.8,
                   yerr=all_main_errors_plot if show_error_bars else None, 
                   error_kw=error_kw)
    
    # Add third bar only if we have inverse data and this is a compliance metric
    bars3 = None
    if has_inverse:
        bars3 = ax.bar(x + width, all_inverse_values_plot, width, label=f'{project_name} Inverse', 
                       color='lightgreen', alpha=0.8, edgecolor='darkgreen', linewidth=0.8,
                       yerr=all_inverse_errors_plot if show_error_bars else None, 
                       error_kw=error_kw)
    
    # Highlight the average bars with different styling
    if len(all_benchmark_names) > len(benchmark_names):
        # Make average bars more prominent
        bars1[-1].set_alpha(1.0)
        bars1[-1].set_edgecolor('black')
        bars1[-1].set_linewidth(2)
        bars2[-1].set_alpha(1.0)
        bars2[-1].set_edgecolor('black')
        bars2[-1].set_linewidth(2)
        if bars3:
            bars3[-1].set_alpha(1.0)
            bars3[-1].set_edgecolor('black')
            bars3[-1].set_linewidth(2)
    
    # Add a vertical separator line before the average group
    if len(all_benchmark_names) > 1:
        separator_x = len(benchmark_names) - 0.5
        ax.axvline(x=separator_x, color='gray', linestyle='--', alpha=0.7, linewidth=1)
    
    # Add value labels on bars
    def add_value_labels(bars, values, errors):
        for bar, value, error in zip(bars, values, errors):
            height = bar.get_height()
            # Position label above error bar if shown, otherwise just above bar
            label_height = height + (error + 1.0 if show_error_bars else 1.0)
            ax.text(bar.get_x() + bar.get_width()/2., label_height,
                   f'{value:.0f}%', ha='center', va='bottom', fontsize=13, weight='bold')
    
    add_value_labels(bars1, all_baseline_values_plot, all_baseline_errors_plot)
    add_value_labels(bars2, all_main_values_plot, all_main_errors_plot)
    if bars3:
        add_value_labels(bars3, all_inverse_values_plot, all_inverse_errors_plot)
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    title_suffix_error = " (with Overall Average ± SD)" if show_error_bars else " (with Overall Average)"
    inverse_title_part = f" vs {project_name} Inverse" if has_inverse else ""
    if not no_titles:
        # Handle special case for tests compliant to avoid "Tests Compliant Non-Compliance"
        if metric_column.lower() == "tests compliant" and title_suffix == "Non-Compliance":
            chart_title = f'Test {title_suffix} - Baseline vs {project_name}{inverse_title_part} for {model_filter} Model{title_suffix_error}'
        else:
            chart_title = f'{metric_column.title()} {title_suffix} - Baseline vs {project_name}{inverse_title_part} for {model_filter} Model{title_suffix_error}'
        ax.set_title(chart_title, fontsize=20, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(all_benchmark_names, rotation=45, ha='right', fontsize=15)
    ax.legend(fontsize=15)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelsize=15)
    
    # Set y-axis to accommodate error bars if shown
    all_values_for_scaling = all_baseline_values_plot + all_main_values_plot
    if bars3:
        all_values_for_scaling += all_inverse_values_plot
        
    if show_error_bars:
        all_errors_for_scaling = all_baseline_errors_plot + all_main_errors_plot
        if bars3:
            all_errors_for_scaling += all_inverse_errors_plot
        max_val = max(np.array(all_values_for_scaling) + np.array(all_errors_for_scaling))
        ax.set_ylim(0, max_val * 1.15)
    else:
        max_val = max(all_values_for_scaling)
        ax.set_ylim(0, max_val * 1.1)
    
    # Add text annotation for the average section
    if len(all_benchmark_names) > 1:
        annotation_suffix = " ± SD" if show_error_bars else ""
        ax.text(len(benchmark_names), ax.get_ylim()[1] * 0.95, f'Overall\nAverage{annotation_suffix}', 
                ha='center', va='top', fontsize=14, style='italic', alpha=0.7)
    
    # Add model name annotation
    ax.text(0.02, 0.98, f'Model: {model_filter}', transform=ax.transAxes, fontsize=16, 
            color='darkblue', alpha=0.8, weight='bold', va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-baseline-comparison-{model_filter}-{metric_column.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print comprehensive improvement summary for single model
    print_improvement_summary_table(benchmark_data, benchmark_names, f"{metric_column} - {model_filter} Model", is_compliance_metric, project_name)

    # Generate relative improvement chart for single model
    plot_relative_improvement_chart(benchmark_data, benchmark_names, f"{metric_column} - {model_filter} Model", is_compliance_metric, outputDir, no_titles)
    if is_compliance_metric:
        # For non-compliance, lower is better
        improvement_main = overall_baseline_avg - overall_main_avg
        improvement_inverse = overall_baseline_avg - overall_inverse_avg
        improvement_word = "improvement" if improvement_main > 0 else "decline"
        improvement_word_inverse = "improvement" if improvement_inverse > 0 else "decline"
    else:
        # For accuracy and other metrics, higher is usually better
        improvement_main = overall_main_avg - overall_baseline_avg
        improvement_inverse = overall_inverse_avg - overall_baseline_avg
        improvement_word = "improvement" if improvement_main > 0 else "decline"
        improvement_word_inverse = "improvement" if improvement_inverse > 0 else "decline"
    
    print(f"Overall Average (Baseline): {overall_baseline_avg:.2f}% ± {overall_baseline_std:.2f}%")
    print(f"Overall Average ({project_name}): {overall_main_avg:.2f}% ± {overall_main_std:.2f}%")
    if has_inverse:
        print(f"Overall Average ({project_name} Inverse): {overall_inverse_avg:.2f}% ± {overall_inverse_std:.2f}%")
    print(f"Overall Improvement ({project_name}): {improvement_main:+.2f}% ({improvement_word})")
    if has_inverse:
        print(f"Overall Improvement ({project_name} Inverse): {improvement_inverse:+.2f}% ({improvement_word_inverse})")
    print(f"Number of benchmarks: {len(benchmark_names)}")
    print(f"Total data points: {len(all_baseline_values)} baseline, {len(all_main_values)} {project_name.lower()}" + 
          (f", {len(all_inverse_values)} inverse" if all_inverse_values else ""))
    
    # Handle special case for tests compliant to avoid "tests compliant Non-Compliance"
    if metric_column.lower().startswith("tests compliant") and title_suffix == "Non-Compliance":
        breakdown_title = f"test {title_suffix}"
    else:
        breakdown_title = f"{title_suffix}"
    print(f"\nPer-benchmark breakdown for {model_filter} ({breakdown_title}):")
    print("-" * 80)
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        if is_compliance_metric:
            diff_main = data['baseline_avg'] - data['main_avg']  # For non-compliance, lower is better
            diff_inverse = data['baseline_avg'] - data['inverse_avg']
        else:
            diff_main = data['main_avg'] - data['baseline_avg']  # For accuracy, higher is better
            diff_inverse = data['inverse_avg'] - data['baseline_avg']
            
        print(f"{benchmark}:")
        print(f"  Baseline: {data['baseline_avg']:.1f}% ± {data['baseline_std']:.1f}% (n={data['baseline_count']})")
        print(f"  {project_name}: {data['main_avg']:.1f}% ± {data['main_std']:.1f}% (n={data['main_count']})")
        if has_inverse:
            print(f"  {project_name} Inverse: {data['inverse_avg']:.1f}% ± {data['inverse_std']:.1f}% (n={data['inverse_count']})")
        print(f"  Improvement ({project_name}): {diff_main:+.1f}%")
        if has_inverse:
            print(f"  Improvement ({project_name} Inverse): {diff_inverse:+.1f}%")
        print()


def run_full_analysis(evalsDir, benchmarks=None, outputDir=None, 
                     skip_individual=False, skip_aggregated=False, skip_baseline=False, skip_plotresults=False, no_titles=False, project_name='PromptPex'):
    """Run the complete analysis pipeline."""
    
    if outputDir is None:
        outputDir = evalsDir
    
    if benchmarks is None:
        benchmarks = get_default_benchmarks(evalsDir)
        
    if not benchmarks:
        print(f"No benchmarks found in {evalsDir}")
        return
        
    print(f"Analyzing {len(benchmarks)} benchmarks from {evalsDir}")
    print(f"Saving plots to {outputDir}")
    print(f"Benchmarks: {', '.join(benchmarks)}")
    
    # Create output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)
    
    prettyBenchmarkNames = {
        "speech-tag": "speech-tag", 
        "text-to-p": "text-to-p",  
        "shakespearean-writing-assistant": "shakespeare", 
        "sentence-rewrite": "sentence", 
        "extract-names": "extract-names", 
        "elements": "elements", 
        "art-prompt": "art-prompt", 
        "classify-input-text": "classify"
    }
    
    # Individual benchmark analysis
    if not skip_individual:
        print("\n" + "="*60)
        print("INDIVIDUAL BENCHMARK ANALYSIS")
        print("="*60)
        for benchmark in benchmarks:
            print(f"\nAnalyzing benchmark: {benchmark}")
            analyze_benchmark_metrics(benchmark, evalsDir, prettyBenchmarkNames, outputDir, no_titles)
    
    # Aggregated analysis
    if not skip_aggregated:
        print("\n" + "="*60)
        print("AGGREGATED METRICS ANALYSIS")
        print("="*60)
        
        # Collect all data
        all_data, all_models, all_metrics = collect_metrics(benchmarks, evalsDir)
        
        if not all_metrics:
            print("No metrics found across all benchmarks. Cannot proceed with aggregated analysis.")
        elif not all_models:
            print("No models found across all benchmarks. Cannot proceed with aggregated analysis.")
        else:
            # Model averages
            print("\nComputing model metric averages...")
            model_metric_avg = compute_model_metric_averages(all_data, all_models, all_metrics)
            print_metric_table(model_metric_avg)
            plot_grouped_bar_chart(model_metric_avg, outputDir, evalsDir, no_titles)
            
            # Get sample data to determine available columns
            if benchmarks:
                csv_path = os.path.join(evalsDir, benchmarks[0], benchmarks[0], "overview.csv")
                if os.path.isfile(csv_path):
                    df = pd.read_csv(csv_path)
                    df.columns = df.columns.str.strip()
                    start_col = get_metrics_start_col(df)
                    columns_of_interest = list(df.columns[start_col:])
                    
                    # Sum metrics analysis
                    print("\nComputing benchmark sums...")
                    data, sums = collect_and_sum_benchmark_metrics(benchmarks, evalsDir, columns_of_interest)
                    #print_sums_table(sums, columns_of_interest)
                    #plot_sums_bar(sums, columns_of_interest, outputDir, evalsDir)
            
            # Average tests per model
            print("\nComputing average tests per model...")
            averages = average_tests_per_model(benchmarks, evalsDir)
            print_avg_table(averages)
            plot_avg_bar(averages, outputDir, evalsDir, no_titles)
            
            # Grouped analysis
            print("\nRunning grouped analysis...")
            if 'tests compliant' in all_metrics:
                plot_grouped_barplot_by_benchmark_and_model(benchmarks, evalsDir, "tests compliant", outputDir, no_titles=no_titles)
    
    # Baseline analysis
    if not skip_baseline:
        print("\n" + "="*60)
        print("BASELINE COMPARISON ANALYSIS")
        print("="*60)
        
        # Check if any benchmark has baseline data
        has_baseline = False
        for benchmark in benchmarks[:3]:  # Check first few benchmarks
            baseline_csv_path = os.path.join(evalsDir, benchmark, benchmark, "overview-baseline.csv")
            if os.path.isfile(baseline_csv_path):
                has_baseline = True
                break
        
        if has_baseline:
            print("\nRunning baseline vs main analysis...")
            plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, "tests compliant", outputDir, no_titles=no_titles, project_name=project_name)
            
            # Try accuracy comparison if available
            csv_path = os.path.join(evalsDir, benchmarks[0], benchmarks[0], "overview.csv")
            if os.path.isfile(csv_path):
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                accuracy_cols = [col for col in df.columns if 'accuracy' in col.lower()]
                if accuracy_cols:
                    print(f"\nRunning accuracy baseline comparison for: {accuracy_cols[0]}")
                    plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, accuracy_cols[0], outputDir, no_titles=no_titles, project_name=project_name)
            
            # Run single model analysis for gpt-oss if available
            print("\nRunning single model analysis for gpt-oss...")
            plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, "gpt-oss", "tests compliant", outputDir, no_titles=no_titles, project_name=project_name)
            if 'accuracy_cols' in locals() and accuracy_cols:
                plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, "gpt-oss", accuracy_cols[0], outputDir, no_titles=no_titles, project_name=project_name)
        else:
            print("No baseline data found. Skipping baseline comparison.")
    
    # Plot-results style analysis
    if not skip_plotresults:
        print("\n" + "="*60)
        print("PLOT-RESULTS STYLE ANALYSIS")
        print("="*60)
        generate_plot_results_style_analysis(benchmarks, evalsDir, outputDir, project_name)
    
    print(f"\nAnalysis complete! Plots saved to {outputDir}")
    

def main():
    """Main command line interface."""
    parser = argparse.ArgumentParser(
        description='Analyze evaluation results and generate plots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_metrics.py
  python analyze_metrics.py -d /path/to/evals -o /path/to/output
  python analyze_metrics.py -b "speech-tag,art-prompt,elements"
  python analyze_metrics.py --skip-baseline --skip-individual
  python analyze_metrics.py --skip-plotresults
        """
    )
    
    parser.add_argument('-d', '--evals-dir', 
                       default='../evals/test-all-2025-09-29/eval',
                       help='Directory containing evaluation results')
    
    parser.add_argument('-b', '--benchmarks',
                       help='Comma-separated list of benchmark names to analyze')
    
    parser.add_argument('-o', '--output-dir',
                       help='Directory to save plots (default: same as evals-dir)')
    
    parser.add_argument('--skip-individual', action='store_true',
                       help='Skip individual benchmark analysis')
    
    parser.add_argument('--skip-aggregated', action='store_true', 
                       help='Skip aggregated metrics analysis')
    
    parser.add_argument('--skip-baseline', action='store_true',
                       help='Skip baseline comparison analysis')
    
    parser.add_argument('--skip-plotresults', action='store_true',
                       help='Skip plot-results style analysis')
    
    parser.add_argument('--no-titles', action='store_true',
                       help='Remove titles from all generated charts')
    parser.add_argument('--project-name', default='PromptPex',
                        help='Name of the project to use in charts and tables (default: PromptPex)')
    
    args = parser.parse_args()
    
    # Validate paths
    evalsDir = os.path.abspath(args.evals_dir)
    if not os.path.isdir(evalsDir):
        print(f"Error: Evaluation directory not found: {evalsDir}")
        sys.exit(1)
    
    # Parse benchmark list
    benchmarks = None
    if args.benchmarks:
        benchmarks = [b.strip() for b in args.benchmarks.split(',')]
        # Validate benchmarks exist
        for benchmark in benchmarks:
            benchmark_path = os.path.join(evalsDir, benchmark)
            if not os.path.isdir(benchmark_path):
                print(f"Warning: Benchmark directory not found: {benchmark_path}")
    
    # Set output directory
    outputDir = args.output_dir if args.output_dir else evalsDir
    
    # Run analysis
    run_full_analysis(
        evalsDir=evalsDir,
        benchmarks=benchmarks,
        outputDir=outputDir,
        skip_individual=args.skip_individual,
        skip_aggregated=args.skip_aggregated,
        skip_baseline=args.skip_baseline,
        skip_plotresults=args.skip_plotresults,
        no_titles=args.no_titles,
        project_name=args.project_name
    )


if __name__ == "__main__":
    main()