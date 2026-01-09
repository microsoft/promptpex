#!/usr/bin/env python3
"""
Analyze Metrics Script - Command line version of analyze-metrics notebook

This script analyzes evaluation results from the PromptPex evaluation framework
and generates various plots and statistics about benchmark performance.

Usage:
    python analyze_metrics.py [OPTIONS]

Options:
    -d, --evals-dir PATH    Directory containing evaluation results 
                           (default: ../evals/test-all-2025-09-29/eval)
    -b, --benchmarks LIST   Comma-separated list of benchmark names to analyze
                           (default: all available benchmarks)
    -o, --output-dir PATH   Directory to save plots (default: same as evals-dir)
    --skip-individual      Skip individual benchmark analysis
    --skip-aggregated      Skip aggregated metrics analysis 
    --skip-baseline        Skip baseline comparison analysis
    --help                 Show this help message
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


def analyze_benchmark_metrics(benchmark, evalsDir, prettyBenchmarkNames, outputDir=None):
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
    
    ax.set_xlabel('Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.set_ylabel('Metric Value')
    ax.set_title(f"Model Metrics for {prettyBenchmarkNames.get(benchmark, benchmark)}")
    ax.legend(loc='best', fontsize='small', ncol=2)
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


def plot_grouped_bar_chart(model_metric_avg, outputDir, evalsDir):
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
    ax.set_xticklabels(models, rotation=20)
    ax.set_ylabel('Average Metric Value')
    ax.set_title('Average Model Metrics Across Benchmarks')
    ax.legend(loc='best', fontsize='small', ncol=2)
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


def plot_sums_bar(sums, columns_of_interest, outputDir, evalsDir):
    """Plot bar charts of summed metrics."""
    benchmarks = list(sums.keys())
    for col in columns_of_interest:
        values = [sums[bench][col] for bench in benchmarks]
        plt.figure(figsize=(10, 5))
        plt.bar(benchmarks, values)
        plt.ylabel(col)
        plt.title(f"Sum of {col} by Benchmark")
        plt.xticks(rotation=20)
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


def plot_avg_bar(averages, outputDir, evalsDir):
    """Plot bar chart of average tests per model."""
    benchmarks = list(averages.keys())
    values = list(averages.values())
    plt.figure(figsize=(10, 5))
    plt.bar(benchmarks, values)
    plt.ylabel("Average Tests per Model")
    plt.title("Average Tests per Model by Benchmark")
    plt.xticks(rotation=20)
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


def plot_grouped_barplot_by_benchmark_and_model(benchmarks, evalsDir, column_of_interest, outputDir=None, show_error_bars=False):
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
    ax.set_xlabel('Benchmark')
    ax.set_ylabel(column_of_interest)
    title_suffix = ' (with Cross-Benchmark Averages ± SD)' if show_error_bars else ' (with Cross-Benchmark Averages)'
    ax.set_title(f'{column_of_interest} by Benchmark and Model{title_suffix}')
    ax.set_xticks(x)
    ax.set_xticklabels(all_labels, rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add text annotation for the average section
    if len(all_labels) > 1:
        annotation_suffix = ' ± SD' if show_error_bars else ''
        ax.text(len(benchmarks_with_data), ax.get_ylim()[1] * 0.95, f'Cross-Benchmark\nAverages{annotation_suffix}', 
                ha='center', va='top', fontsize=10, style='italic', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-grouped-{column_of_interest.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print statistics including standard deviations
    print(f"\nModel Statistics for {column_of_interest} (including zeros):")
    print("=" * 60)
    for i, model in enumerate(all_models):
        print(f"{model}: {model_averages[i]:.2f} ± {model_std_devs[i]:.2f}")


def plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, metric_column="tests compliant", outputDir=None, show_error_bars=False):
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
                    'main': main_avg,
                    'baseline': baseline_avg,
                    'inverse': inverse_avg,
                    'main_std': main_std,
                    'baseline_std': baseline_std,
                    'inverse_std': inverse_std,
                    'main_count': len(main_valid),
                    'baseline_count': len(baseline_valid),
                    'inverse_count': len(inverse_valid)
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
    main_averages = [benchmark_data[b]['main'] for b in benchmark_names]
    baseline_averages = [benchmark_data[b]['baseline'] for b in benchmark_names]
    inverse_averages = [benchmark_data[b]['inverse'] for b in benchmark_names]
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
    bars2 = ax.bar(x, extended_main_averages, width, label='Promptpex', 
                   color='lightcoral', alpha=0.8, edgecolor='darkred', linewidth=0.5,
                   yerr=extended_main_stds if show_error_bars else None, 
                   error_kw=error_kw)
    
    # Add third bar only if we have inverse data and this is a compliance metric
    bars3 = None
    if has_inverse and is_compliance_metric:
        bars3 = ax.bar(x + width, extended_inverse_averages, width, label='Promptpex Inverse', 
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
                   f'{value:.1f}%', ha='center', va='bottom', fontsize=8)
    
    add_value_labels(bars1, extended_baseline_averages, extended_baseline_stds)
    add_value_labels(bars2, extended_main_averages, extended_main_stds)
    if bars3:
        add_value_labels(bars3, extended_inverse_averages, extended_inverse_stds)
    
    ax.set_xlabel('Benchmark', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    title_suffix_error = " (with Overall Average ± SD)" if show_error_bars else " (with Overall Average)"
    inverse_title_part = " vs Promptpex Inverse" if (has_inverse and is_compliance_metric) else ""
    ax.set_title(f'{metric_column.title()} {title_suffix} - Baseline vs Promptpex{inverse_title_part} by Benchmark{title_suffix_error}', 
                 fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(extended_benchmark_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
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
                ha='center', va='top', fontsize=10, style='italic', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-baseline-comparison-{metric_column.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print summary statistics with standard deviations
    print(f"\nSummary Statistics for {metric_column} {title_suffix}:")
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
    print(f"Overall Average (Promptpex): {overall_main_avg:.2f}% ± {overall_main_std:.2f}%")
    if has_inverse and is_compliance_metric:
        print(f"Overall Average (Promptpex Inverse): {overall_inverse_avg:.2f}% ± {overall_inverse_std:.2f}%")
    print(f"Overall Improvement (Promptpex): {improvement_main:+.2f}% ({improvement_word})")
    if has_inverse and is_compliance_metric:
        print(f"Overall Improvement (Promptpex Inverse): {improvement_inverse:+.2f}% ({improvement_word_inverse})")
    print(f"Number of benchmarks: {len(benchmark_names)}")
    print(f"Total data points: {len(all_baseline_values)} baseline, {len(all_main_values)} promptpex" + 
          (f", {len(all_inverse_values)} inverse" if all_inverse_values else ""))
    
    print(f"\nPer-benchmark breakdown ({title_suffix}):")
    print("-" * 70)
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        if is_compliance_metric:
            diff_main = data['baseline'] - data['main']  # For non-compliance, lower is better
            diff_inverse = data['baseline'] - data['inverse']
        else:
            diff_main = data['main'] - data['baseline']  # For accuracy, higher is better
            diff_inverse = data['inverse'] - data['baseline']
            
        print(f"{benchmark}:")
        print(f"  Baseline: {data['baseline']:.1f}% ± {data['baseline_std']:.1f}% (n={data['baseline_count']})")
        print(f"  Promptpex: {data['main']:.1f}% ± {data['main_std']:.1f}% (n={data['main_count']})")
        if has_inverse and is_compliance_metric:
            print(f"  Promptpex Inverse: {data['inverse']:.1f}% ± {data['inverse_std']:.1f}% (n={data['inverse_count']})")
        print(f"  Improvement (Promptpex): {diff_main:+.1f}%")
        if has_inverse and is_compliance_metric:
            print(f"  Improvement (Promptpex Inverse): {diff_inverse:+.1f}%")
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


def generate_plot_results_style_analysis(benchmarks, evalsDir, outputDir):
    """
    Generate plot-results.ipynb style analysis and charts.
    Creates comprehensive compliance analysis with multiple chart types.
    """
    print("\n" + "="*60)
    print("PLOT-RESULTS STYLE ANALYSIS")
    print("="*60)
    
    # Set consistent matplotlib style
    plt.rcParams.update({'font.size': 12}) 
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    
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
    
    # 4. PromptPex vs baseline comparison
    with open(f'{outputDir}/pp-compare.csv', 'w') as cfile:
        models = data[benchmarks[0]]["model"]
        pp_sum = pd.Series([0.0 for i in range(len(models))])
        bl_sum = pd.Series([0.0 for i in range(len(models))])
        
        print("Model, PromptPex % Non-Compliance, Baseline % Non-Compliance", file=cfile)
        
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
    _plot_non_compliance_by_benchmark(outputDir)
    
    # Generate Chart 2: Rule vs Inverse Rule comparison
    _plot_rule_vs_inverse_rule(outputDir)
    
    # Generate Chart 3: PromptPex vs Baseline comparison
    _plot_promptpex_vs_baseline(outputDir)
    
    # Generate Chart 4: Test validity chart
    _plot_test_validity(outputDir)
    
    # Generate Chart 5: Rules count chart
    _plot_rules_count(outputDir)
    
    print(f"Plot-results style analysis complete! Files saved to {outputDir}")


def _plot_non_compliance_by_benchmark(outputDir):
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
        ax.set_xticklabels(df.index, rotation=45, ha='right', fontsize=10)
        ax.set_xlabel('Benchmark', fontsize=12)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-cpct.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-cpct.pdf")
        
    except Exception as e:
        print(f"Error generating non-compliance chart: {e}")


def _plot_rule_vs_inverse_rule(outputDir):
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
        ax.set_xticklabels(df_filtered['Model'], rotation=0, ha='center', fontsize=11)
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pos-neg-cpct.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pos-neg-cpct.pdf")
        
    except Exception as e:
        print(f"Error generating rule vs inverse rule chart: {e}")


def _plot_promptpex_vs_baseline(outputDir):
    """Generate PromptPex vs Baseline comparison chart."""
    try:
        df = pd.read_csv(f'{outputDir}/pp-compare.csv')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bar_width = 0.35
        indices = range(len(df))
        
        ax.bar(indices, df[' PromptPex % Non-Compliance'] * 100, bar_width, 
               label='PromptPex', alpha=0.8, color='lightcoral', edgecolor='darkred', linewidth=0.8)
        ax.bar([i + bar_width for i in indices], df[' Baseline % Non-Compliance'] * 100, bar_width, 
               label='Baseline', alpha=0.8, color='lightsteelblue', edgecolor='darkblue', linewidth=0.8)
        
        ax.set_xticks([i + bar_width / 2 for i in indices])
        ax.set_xticklabels(df['Model'], rotation=0, ha='center', fontsize=11)
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Percentage Non-Compliance', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-compare.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-compare.pdf")
        
    except Exception as e:
        print(f"Error generating PromptPex vs Baseline chart: {e}")


def _plot_test_validity(outputDir):
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
        ax.set_xticklabels(df['Benchmark'], rotation=45, ha='right', fontsize=10)
        ax.set_xlabel('Benchmark', fontsize=12)
        ax.set_ylabel('Number of Tests', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-test-validity.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-test-validity.pdf")
        
    except Exception as e:
        print(f"Error generating test validity chart: {e}")


def _plot_rules_count(outputDir):
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
        ax.set_xticklabels(df['benchmark'], rotation=45, ha='right', fontsize=10)
        ax.set_xlabel('Benchmark', fontsize=12)
        ax.set_ylabel('Number of Rules', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'{outputDir}/pp-grounded-rules.pdf', bbox_inches='tight')
        plt.show()
        plt.close()
        print(f"Saved: {outputDir}/pp-grounded-rules.pdf")
        
    except Exception as e:
        print(f"Error generating rules count chart: {e}")


def plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, model_filter, metric_column="tests compliant", outputDir=None, show_error_bars=False):
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
                    'main': main_avg,
                    'baseline': baseline_avg,
                    'inverse': inverse_avg,
                    'main_std': main_std,
                    'baseline_std': baseline_std,
                    'inverse_std': inverse_std,
                    'main_count': len(main_valid),
                    'baseline_count': len(baseline_valid),
                    'inverse_count': len(inverse_valid)
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
    main_values = [benchmark_data[b]['main'] for b in benchmark_names]
    baseline_values = [benchmark_data[b]['baseline'] for b in benchmark_names]
    inverse_values = [benchmark_data[b]['inverse'] for b in benchmark_names]
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
    bars2 = ax.bar(x, all_main_values_plot, width, label='Promptpex', 
                   color='orange', alpha=0.8, edgecolor='darkorange', linewidth=0.8,
                   yerr=all_main_errors_plot if show_error_bars else None, 
                   error_kw=error_kw)
    
    # Add third bar only if we have inverse data and this is a compliance metric
    bars3 = None
    if has_inverse:
        bars3 = ax.bar(x + width, all_inverse_values_plot, width, label='Promptpex Inverse', 
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
                   f'{value:.1f}%', ha='center', va='bottom', fontsize=8, weight='bold')
    
    add_value_labels(bars1, all_baseline_values_plot, all_baseline_errors_plot)
    add_value_labels(bars2, all_main_values_plot, all_main_errors_plot)
    if bars3:
        add_value_labels(bars3, all_inverse_values_plot, all_inverse_errors_plot)
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    title_suffix_error = " (with Overall Average ± SD)" if show_error_bars else " (with Overall Average)"
    inverse_title_part = " vs Promptpex Inverse" if has_inverse else ""
    ax.set_title(f'{metric_column.title()} {title_suffix} - Baseline vs Promptpex{inverse_title_part} for {model_filter} Model{title_suffix_error}', 
                 fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(all_benchmark_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
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
                ha='center', va='top', fontsize=10, style='italic', alpha=0.7)
    
    # Add model name annotation
    ax.text(0.02, 0.98, f'Model: {model_filter}', transform=ax.transAxes, fontsize=12, 
            color='darkblue', alpha=0.8, weight='bold', va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(f'{outputDir}/pp-baseline-comparison-{model_filter}-{metric_column.replace(" ", "-").replace("/", "-")}.pdf', bbox_inches='tight')
    plt.show()
    
    # Print summary statistics with standard deviations
    print(f"\nSummary Statistics for {metric_column} {title_suffix} - {model_filter} Model:")
    print("=" * 80)
    
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
    print(f"Overall Average (Promptpex): {overall_main_avg:.2f}% ± {overall_main_std:.2f}%")
    if has_inverse:
        print(f"Overall Average (Promptpex Inverse): {overall_inverse_avg:.2f}% ± {overall_inverse_std:.2f}%")
    print(f"Overall Improvement (Promptpex): {improvement_main:+.2f}% ({improvement_word})")
    if has_inverse:
        print(f"Overall Improvement (Promptpex Inverse): {improvement_inverse:+.2f}% ({improvement_word_inverse})")
    print(f"Number of benchmarks: {len(benchmark_names)}")
    print(f"Total data points: {len(all_baseline_values)} baseline, {len(all_main_values)} promptpex" + 
          (f", {len(all_inverse_values)} inverse" if all_inverse_values else ""))
    
    print(f"\nPer-benchmark breakdown for {model_filter} ({title_suffix}):")
    print("-" * 80)
    for benchmark in benchmark_names:
        data = benchmark_data[benchmark]
        if is_compliance_metric:
            diff_main = data['baseline'] - data['main']  # For non-compliance, lower is better
            diff_inverse = data['baseline'] - data['inverse']
        else:
            diff_main = data['main'] - data['baseline']  # For accuracy, higher is better
            diff_inverse = data['inverse'] - data['baseline']
            
        print(f"{benchmark}:")
        print(f"  Baseline: {data['baseline']:.1f}% ± {data['baseline_std']:.1f}% (n={data['baseline_count']})")
        print(f"  Promptpex: {data['main']:.1f}% ± {data['main_std']:.1f}% (n={data['main_count']})")
        if has_inverse:
            print(f"  Promptpex Inverse: {data['inverse']:.1f}% ± {data['inverse_std']:.1f}% (n={data['inverse_count']})")
        print(f"  Improvement (Promptpex): {diff_main:+.1f}%")
        if has_inverse:
            print(f"  Improvement (Promptpex Inverse): {diff_inverse:+.1f}%")
        print()


def run_full_analysis(evalsDir, benchmarks=None, outputDir=None, 
                     skip_individual=False, skip_aggregated=False, skip_baseline=False, skip_plotresults=False):
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
            analyze_benchmark_metrics(benchmark, evalsDir, prettyBenchmarkNames, outputDir)
    
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
            plot_grouped_bar_chart(model_metric_avg, outputDir, evalsDir)
            
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
            plot_avg_bar(averages, outputDir, evalsDir)
            
            # Grouped analysis
            print("\nRunning grouped analysis...")
            if 'tests compliant' in all_metrics:
                plot_grouped_barplot_by_benchmark_and_model(benchmarks, evalsDir, "tests compliant", outputDir)
    
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
            plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, "tests compliant", outputDir)
            
            # Try accuracy comparison if available
            csv_path = os.path.join(evalsDir, benchmarks[0], benchmarks[0], "overview.csv")
            if os.path.isfile(csv_path):
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                accuracy_cols = [col for col in df.columns if 'accuracy' in col.lower()]
                if accuracy_cols:
                    print(f"\nRunning accuracy baseline comparison for: {accuracy_cols[0]}")
                    plot_baseline_vs_main_metrics_by_benchmark(benchmarks, evalsDir, accuracy_cols[0], outputDir)
            
            # Run single model analysis for gpt-oss if available
            print("\nRunning single model analysis for gpt-oss...")
            plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, "gpt-oss", "tests compliant", outputDir)
            if 'accuracy_cols' in locals() and accuracy_cols:
                plot_baseline_vs_main_metrics_by_benchmark_single_model(benchmarks, evalsDir, "gpt-oss", accuracy_cols[0], outputDir)
        else:
            print("No baseline data found. Skipping baseline comparison.")
    
    # Plot-results style analysis
    if not skip_plotresults:
        print("\n" + "="*60)
        print("PLOT-RESULTS STYLE ANALYSIS")
        print("="*60)
        
        generate_plot_results_style_analysis(benchmarks, evalsDir, outputDir)
    
    print(f"\nAnalysis complete! Plots saved to {outputDir}")
    

def main():
    """Main command line interface."""
    parser = argparse.ArgumentParser(
        description='Analyze PromptPex evaluation results and generate plots',
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
        skip_plotresults=args.skip_plotresults
    )


if __name__ == "__main__":
    main()