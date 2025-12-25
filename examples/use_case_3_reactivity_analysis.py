#!/usr/bin/env python3
"""
SHAPEwarp Use Case 3: SHAPE Reactivity Profile Analysis

This script demonstrates analyzing SHAPE reactivity profiles for RNA sequences,
including statistical analysis, visualization, and comparison.

Usage:
    python examples/use_case_3_reactivity_analysis.py --input examples/data/query.txt --output results/analysis/
"""

import argparse
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from loguru import logger

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze SHAPE reactivity profiles for RNA sequences"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="examples/data/query.txt",
        help="Path to query file containing RNA sequences and SHAPE reactivities"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results/reactivity_analysis",
        help="Output directory for analysis results"
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize reactivity values to [0, 1] range"
    )
    parser.add_argument(
        "--max-reactivity",
        type=float,
        default=10.0,
        help="Maximum reactivity value for filtering outliers"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=10,
        help="Window size for sliding window analysis"
    )
    parser.add_argument(
        "--create-plots",
        action="store_true",
        help="Generate reactivity profile plots"
    )

    return parser.parse_args()

def parse_query_file(query_file):
    """Parse SHAPEwarp query file format."""
    logger.info(f"Parsing query file: {query_file}")

    query_entries = []

    try:
        with open(query_file, 'r') as f:
            lines = f.readlines()

        # SHAPEwarp query format: id, sequence, reactivities (comma-separated)
        for i in range(0, len(lines), 4):  # Every 4 lines is one entry
            if i + 2 < len(lines):
                entry_id = lines[i].strip()
                sequence = lines[i + 1].strip()
                reactivities_str = lines[i + 2].strip()

                # Parse reactivities
                reactivities = []
                for r in reactivities_str.split(','):
                    try:
                        reactivities.append(float(r))
                    except ValueError:
                        reactivities.append(np.nan)

                query_entries.append({
                    'id': entry_id,
                    'sequence': sequence,
                    'reactivities': np.array(reactivities)
                })

                logger.info(f"Parsed: {entry_id}, length: {len(sequence)}, reactivities: {len(reactivities)}")

    except Exception as e:
        logger.error(f"Error parsing query file: {e}")
        return []

    return query_entries

def calculate_basic_statistics(reactivities):
    """Calculate basic statistics for reactivity profile."""
    valid_reactivities = reactivities[~np.isnan(reactivities)]

    if len(valid_reactivities) == 0:
        return {
            'count': 0,
            'mean': np.nan,
            'median': np.nan,
            'std': np.nan,
            'min': np.nan,
            'max': np.nan,
            'q25': np.nan,
            'q75': np.nan,
            'coverage': 0.0
        }

    stats = {
        'count': len(valid_reactivities),
        'mean': np.mean(valid_reactivities),
        'median': np.median(valid_reactivities),
        'std': np.std(valid_reactivities),
        'min': np.min(valid_reactivities),
        'max': np.max(valid_reactivities),
        'q25': np.percentile(valid_reactivities, 25),
        'q75': np.percentile(valid_reactivities, 75),
        'coverage': len(valid_reactivities) / len(reactivities)
    }

    return stats

def classify_nucleotides(sequence, reactivities, high_threshold=0.7, medium_threshold=0.3):
    """Classify nucleotides based on reactivity levels."""
    classification = []

    for i, (nt, react) in enumerate(zip(sequence, reactivities)):
        if np.isnan(react):
            reactivity_class = 'unknown'
        elif react >= high_threshold:
            reactivity_class = 'high'
        elif react >= medium_threshold:
            reactivity_class = 'medium'
        else:
            reactivity_class = 'low'

        classification.append({
            'position': i + 1,
            'nucleotide': nt,
            'reactivity': react,
            'class': reactivity_class
        })

    return classification

def sliding_window_analysis(reactivities, window_size=10):
    """Perform sliding window analysis of reactivity profile."""
    if len(reactivities) < window_size:
        logger.warning(f"Sequence too short for window size {window_size}")
        return []

    windows = []

    for i in range(len(reactivities) - window_size + 1):
        window_data = reactivities[i:i + window_size]
        valid_data = window_data[~np.isnan(window_data)]

        if len(valid_data) > 0:
            window_stats = {
                'start': i + 1,
                'end': i + window_size,
                'center': i + window_size // 2 + 1,
                'mean_reactivity': np.mean(valid_data),
                'max_reactivity': np.max(valid_data),
                'std_reactivity': np.std(valid_data),
                'coverage': len(valid_data) / window_size
            }
        else:
            window_stats = {
                'start': i + 1,
                'end': i + window_size,
                'center': i + window_size // 2 + 1,
                'mean_reactivity': np.nan,
                'max_reactivity': np.nan,
                'std_reactivity': np.nan,
                'coverage': 0.0
            }

        windows.append(window_stats)

    return windows

def identify_structured_regions(reactivities, low_threshold=0.3, min_length=5):
    """Identify potentially structured regions (low reactivity)."""
    structured_regions = []
    current_region = None

    for i, react in enumerate(reactivities):
        if not np.isnan(react) and react <= low_threshold:
            if current_region is None:
                current_region = {'start': i + 1, 'reactivities': [react]}
            else:
                current_region['reactivities'].append(react)
        else:
            if current_region is not None and len(current_region['reactivities']) >= min_length:
                current_region['end'] = i
                current_region['length'] = len(current_region['reactivities'])
                current_region['mean_reactivity'] = np.mean(current_region['reactivities'])
                structured_regions.append(current_region)
            current_region = None

    # Check last region
    if current_region is not None and len(current_region['reactivities']) >= min_length:
        current_region['end'] = len(reactivities)
        current_region['length'] = len(current_region['reactivities'])
        current_region['mean_reactivity'] = np.mean(current_region['reactivities'])
        structured_regions.append(current_region)

    return structured_regions

def analyze_nucleotide_preferences(sequence, reactivities):
    """Analyze reactivity preferences for different nucleotides."""
    nucleotide_data = {'A': [], 'C': [], 'G': [], 'U': [], 'T': []}

    for nt, react in zip(sequence, reactivities):
        nt = nt.upper()
        if nt in nucleotide_data and not np.isnan(react):
            if nt == 'T':  # Convert T to U for RNA
                nucleotide_data['U'].append(react)
            else:
                nucleotide_data[nt].append(react)

    # Calculate statistics for each nucleotide
    nt_stats = {}
    for nt, values in nucleotide_data.items():
        if values:
            nt_stats[nt] = {
                'count': len(values),
                'mean': np.mean(values),
                'median': np.median(values),
                'std': np.std(values)
            }
        else:
            nt_stats[nt] = {
                'count': 0,
                'mean': np.nan,
                'median': np.nan,
                'std': np.nan
            }

    return nt_stats

def create_reactivity_plots(entry, output_dir):
    """Create reactivity profile plots."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        logger.warning("Matplotlib/Seaborn not available for plotting")
        return

    entry_id = entry['id']
    sequence = entry['sequence']
    reactivities = entry['reactivities']

    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'SHAPE Reactivity Analysis: {entry_id}', fontsize=16)

    # 1. Reactivity profile plot
    ax1 = axes[0, 0]
    positions = np.arange(1, len(reactivities) + 1)
    ax1.plot(positions, reactivities, 'o-', markersize=3, linewidth=1)
    ax1.set_xlabel('Position')
    ax1.set_ylabel('SHAPE Reactivity')
    ax1.set_title('Reactivity Profile')
    ax1.grid(True, alpha=0.3)

    # 2. Reactivity histogram
    ax2 = axes[0, 1]
    valid_reactivities = reactivities[~np.isnan(reactivities)]
    if len(valid_reactivities) > 0:
        ax2.hist(valid_reactivities, bins=20, alpha=0.7, edgecolor='black')
        ax2.axvline(np.mean(valid_reactivities), color='red', linestyle='--', label='Mean')
        ax2.axvline(np.median(valid_reactivities), color='green', linestyle='--', label='Median')
        ax2.legend()
    ax2.set_xlabel('SHAPE Reactivity')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Reactivity Distribution')

    # 3. Nucleotide-specific reactivity
    ax3 = axes[1, 0]
    nt_stats = analyze_nucleotide_preferences(sequence, reactivities)
    nucleotides = ['A', 'C', 'G', 'U']
    means = [nt_stats[nt]['mean'] for nt in nucleotides]
    counts = [nt_stats[nt]['count'] for nt in nucleotides]

    # Filter out nucleotides with no data
    valid_data = [(nt, mean, count) for nt, mean, count in zip(nucleotides, means, counts) if not np.isnan(mean)]
    if valid_data:
        nts, means, counts = zip(*valid_data)
        bars = ax3.bar(nts, means, alpha=0.7)

        # Add count labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}', ha='center', va='bottom', fontsize=9)

    ax3.set_xlabel('Nucleotide')
    ax3.set_ylabel('Mean SHAPE Reactivity')
    ax3.set_title('Nucleotide-Specific Reactivity')

    # 4. Structure annotation
    ax4 = axes[1, 1]
    structured_regions = identify_structured_regions(reactivities)

    # Create a color map for the sequence
    colors = []
    for i, react in enumerate(reactivities):
        if np.isnan(react):
            colors.append('gray')
        elif react > 0.7:
            colors.append('red')  # Highly reactive
        elif react > 0.3:
            colors.append('orange')  # Moderately reactive
        else:
            colors.append('blue')  # Low reactivity (structured)

    # Plot as a heatmap-style representation
    if len(colors) > 0:
        ax4.imshow([colors], aspect='auto', extent=[1, len(sequence), -0.5, 0.5])

        # Add structured region annotations
        for region in structured_regions:
            ax4.axvspan(region['start'], region['end'], alpha=0.3, color='blue',
                       label=f"Structured ({region['start']}-{region['end']})")

    ax4.set_xlim(1, len(sequence))
    ax4.set_xlabel('Position')
    ax4.set_title('Reactivity Map (Blue=Low, Orange=Med, Red=High)')
    ax4.set_yticks([])

    # Adjust layout and save
    plt.tight_layout()

    plot_file = os.path.join(output_dir, f"{entry_id}_reactivity_analysis.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Reactivity plot saved: {plot_file}")

def analyze_entry(entry, args):
    """Perform comprehensive analysis on a single entry."""
    entry_id = entry['id']
    sequence = entry['sequence']
    reactivities = entry['reactivities']

    logger.info(f"Analyzing entry: {entry_id}")

    # Apply max reactivity filter
    if args.max_reactivity:
        reactivities = np.where(reactivities > args.max_reactivity, args.max_reactivity, reactivities)

    # Normalize if requested
    if args.normalize:
        valid_reactivities = reactivities[~np.isnan(reactivities)]
        if len(valid_reactivities) > 0:
            min_val = np.min(valid_reactivities)
            max_val = np.max(valid_reactivities)
            if max_val > min_val:
                reactivities = (reactivities - min_val) / (max_val - min_val)
        entry['reactivities'] = reactivities  # Update for plotting

    # Basic statistics
    basic_stats = calculate_basic_statistics(reactivities)

    # Nucleotide classification
    classification = classify_nucleotides(sequence, reactivities)

    # Sliding window analysis
    windows = sliding_window_analysis(reactivities, args.window_size)

    # Structured regions
    structured_regions = identify_structured_regions(reactivities)

    # Nucleotide preferences
    nt_stats = analyze_nucleotide_preferences(sequence, reactivities)

    analysis_result = {
        'entry_id': entry_id,
        'sequence_length': len(sequence),
        'basic_stats': basic_stats,
        'classification': classification,
        'windows': windows,
        'structured_regions': structured_regions,
        'nucleotide_stats': nt_stats
    }

    return analysis_result

def export_results(analysis_results, output_dir):
    """Export analysis results to files."""
    os.makedirs(output_dir, exist_ok=True)

    # Summary statistics
    summary_data = []
    for result in analysis_results:
        basic_stats = result['basic_stats']
        summary_data.append({
            'entry_id': result['entry_id'],
            'sequence_length': result['sequence_length'],
            'mean_reactivity': basic_stats['mean'],
            'median_reactivity': basic_stats['median'],
            'std_reactivity': basic_stats['std'],
            'max_reactivity': basic_stats['max'],
            'coverage': basic_stats['coverage'],
            'structured_regions': len(result['structured_regions'])
        })

    summary_df = pd.DataFrame(summary_data)
    summary_file = os.path.join(output_dir, "summary_statistics.csv")
    summary_df.to_csv(summary_file, index=False)
    logger.info(f"Summary statistics saved: {summary_file}")

    # Detailed classification results
    all_classifications = []
    for result in analysis_results:
        for classification in result['classification']:
            classification['entry_id'] = result['entry_id']
            all_classifications.append(classification)

    if all_classifications:
        class_df = pd.DataFrame(all_classifications)
        class_file = os.path.join(output_dir, "nucleotide_classifications.csv")
        class_df.to_csv(class_file, index=False)
        logger.info(f"Nucleotide classifications saved: {class_file}")

    # Window analysis results
    all_windows = []
    for result in analysis_results:
        for window in result['windows']:
            window['entry_id'] = result['entry_id']
            all_windows.append(window)

    if all_windows:
        windows_df = pd.DataFrame(all_windows)
        windows_file = os.path.join(output_dir, "sliding_window_analysis.csv")
        windows_df.to_csv(windows_file, index=False)
        logger.info(f"Sliding window analysis saved: {windows_file}")

def main():
    """Main function."""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")

    # Parse arguments
    args = parse_arguments()

    logger.info("Starting SHAPE reactivity profile analysis")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output directory: {args.output}")

    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file does not exist: {args.input}")
        return 1

    # Parse query file
    entries = parse_query_file(args.input)
    if not entries:
        logger.error("No valid entries found in input file")
        return 1

    logger.info(f"Loaded {len(entries)} entries for analysis")

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Analyze each entry
    analysis_results = []
    for entry in entries:
        result = analyze_entry(entry, args)
        analysis_results.append(result)

        # Create plots if requested
        if args.create_plots:
            create_reactivity_plots(entry, args.output)

    # Export results
    export_results(analysis_results, args.output)

    # Print summary
    logger.info("Analysis Summary:")
    for result in analysis_results:
        logger.info(f"  {result['entry_id']}: {result['sequence_length']} nt, "
                   f"{result['basic_stats']['coverage']:.2f} coverage, "
                   f"{len(result['structured_regions'])} structured regions")

    logger.info(f"Analysis completed. Results saved to: {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())