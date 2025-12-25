#!/usr/bin/env python3
"""
Script: reactivity_analysis.py
Description: Analyze SHAPE reactivity profiles for RNA sequences

Original Use Case: examples/use_case_3_reactivity_analysis.py
Dependencies Removed: matplotlib/seaborn (plotting), complex logging setup

Usage:
    python scripts/reactivity_analysis.py --input <query_file> --output <output_dir>

Example:
    python scripts/reactivity_analysis.py --input examples/data/query.txt --output results/analysis
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

import pandas as pd
import numpy as np

# Import shared library functions
import sys
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from lib.io import parse_shape_query_file, save_dataframe, validate_shape_data
from lib.utils import (
    normalize_reactivities, analyze_reactivity_profile,
    classify_nucleotides, calculate_sliding_window_stats
)

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "normalize": False,
    "max_reactivity": 10.0,
    "window_size": 15,
    "classification_thresholds": [0.3, 0.7],
    "output_format": "csv",
    "generate_plots": False  # Disabled due to plotting bug in original
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_reactivity_analysis(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze SHAPE reactivity profiles for RNA sequences.

    Args:
        input_file: Path to query file with RNA sequences and SHAPE reactivities
        output_dir: Directory to save analysis results (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - summary_stats: DataFrame with summary statistics
            - nucleotide_classifications: DataFrame with per-nucleotide analysis
            - sliding_window_analysis: DataFrame with sliding window statistics
            - output_files: Dict of saved file paths (if output_dir provided)
            - metadata: Execution metadata

    Example:
        >>> result = run_reactivity_analysis("query.txt", "output/")
        >>> print(f"Analyzed {len(result['summary_stats'])} sequences")
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Parse input file
    try:
        query_entries = parse_shape_query_file(input_file)
    except Exception as e:
        raise ValueError(f"Failed to parse input file: {e}")

    if not query_entries:
        raise ValueError("No valid entries found in input file")

    # Validate query data
    validation_errors = validate_shape_data(query_entries)
    if validation_errors:
        raise ValueError(f"Input validation failed: {'; '.join(validation_errors)}")

    # Process each entry
    summary_stats_list = []
    nucleotide_data_list = []
    sliding_window_data_list = []

    for entry in query_entries:
        # Apply normalization if requested
        reactivities = entry['reactivities']
        if config.get("normalize", False):
            reactivities = normalize_reactivities(
                reactivities,
                max_value=config.get("max_reactivity")
            )

        # Update entry with potentially normalized reactivities
        processed_entry = {**entry, 'reactivities': reactivities}

        # 1. Summary statistics
        summary_stats = analyze_reactivity_profile(processed_entry)
        summary_stats_list.append(summary_stats)

        # 2. Nucleotide-level classification
        classifications = classify_nucleotides(
            reactivities,
            thresholds=tuple(config.get("classification_thresholds", [0.3, 0.7]))
        )

        # Create per-nucleotide DataFrame
        nucleotide_df = pd.DataFrame({
            'entry_id': [entry['id']] * len(entry['sequence']),
            'position': range(1, len(entry['sequence']) + 1),
            'nucleotide': list(entry['sequence']),
            'reactivity': reactivities,
            'classification': classifications
        })
        nucleotide_data_list.append(nucleotide_df)

        # 3. Sliding window analysis
        window_df = calculate_sliding_window_stats(
            reactivities,
            window_size=config.get("window_size", 15)
        )
        window_df['entry_id'] = entry['id']
        sliding_window_data_list.append(window_df)

    # Combine results
    summary_stats_df = pd.DataFrame(summary_stats_list)
    nucleotide_classifications_df = pd.concat(nucleotide_data_list, ignore_index=True)
    sliding_window_df = pd.concat(sliding_window_data_list, ignore_index=True)

    # Save output files if requested
    output_files = {}
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save summary statistics
        summary_file = output_dir / "summary_statistics.csv"
        save_dataframe(summary_stats_df, summary_file, format="csv")
        output_files["summary_statistics"] = str(summary_file)

        # Save nucleotide classifications
        nucleotide_file = output_dir / "nucleotide_classifications.csv"
        save_dataframe(nucleotide_classifications_df, nucleotide_file, format="csv")
        output_files["nucleotide_classifications"] = str(nucleotide_file)

        # Save sliding window analysis
        window_file = output_dir / "sliding_window_analysis.csv"
        save_dataframe(sliding_window_df, window_file, format="csv")
        output_files["sliding_window_analysis"] = str(window_file)

    # Generate analysis summary
    analysis_summary = generate_analysis_summary(
        summary_stats_df, nucleotide_classifications_df, sliding_window_df
    )

    return {
        "summary_stats": summary_stats_df,
        "nucleotide_classifications": nucleotide_classifications_df,
        "sliding_window_analysis": sliding_window_df,
        "output_files": output_files,
        "metadata": {
            "input_file": str(input_file),
            "num_entries": len(query_entries),
            "total_nucleotides": len(nucleotide_classifications_df),
            "config": config
        },
        "analysis_summary": analysis_summary
    }


def generate_analysis_summary(summary_stats_df: pd.DataFrame,
                            nucleotide_df: pd.DataFrame,
                            window_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate high-level summary of analysis results.

    Args:
        summary_stats_df: Summary statistics DataFrame
        nucleotide_df: Nucleotide classifications DataFrame
        window_df: Sliding window analysis DataFrame

    Returns:
        Dictionary with analysis summary
    """
    if summary_stats_df.empty:
        return {"error": "No data to summarize"}

    # Overall statistics
    total_entries = len(summary_stats_df)
    total_nucleotides = len(nucleotide_df)

    # Reactivity statistics across all entries
    valid_reactivities = nucleotide_df[~pd.isna(nucleotide_df['reactivity'])]['reactivity']

    if len(valid_reactivities) > 0:
        global_reactivity_stats = {
            "mean": float(valid_reactivities.mean()),
            "median": float(valid_reactivities.median()),
            "std": float(valid_reactivities.std()),
            "min": float(valid_reactivities.min()),
            "max": float(valid_reactivities.max())
        }
    else:
        global_reactivity_stats = None

    # Classification distribution
    classification_counts = nucleotide_df['classification'].value_counts().to_dict()

    # Coverage statistics
    coverage_stats = {
        "mean_coverage": float(summary_stats_df['coverage'].mean()),
        "median_coverage": float(summary_stats_df['coverage'].median()),
        "min_coverage": float(summary_stats_df['coverage'].min()),
        "max_coverage": float(summary_stats_df['coverage'].max())
    }

    # Sequence length statistics
    length_stats = {
        "mean_length": float(summary_stats_df['sequence_length'].mean()),
        "median_length": float(summary_stats_df['sequence_length'].median()),
        "min_length": int(summary_stats_df['sequence_length'].min()),
        "max_length": int(summary_stats_df['sequence_length'].max())
    }

    return {
        "total_entries": total_entries,
        "total_nucleotides": total_nucleotides,
        "global_reactivity_stats": global_reactivity_stats,
        "classification_distribution": classification_counts,
        "coverage_stats": coverage_stats,
        "sequence_length_stats": length_stats
    }


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--input', '-i', required=True,
        help='Path to query file containing RNA sequences and SHAPE reactivities'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for analysis results'
    )
    parser.add_argument(
        '--config', '-c',
        help='Configuration file (JSON)'
    )
    parser.add_argument(
        '--normalize', action='store_true',
        help='Normalize reactivity values to [0, 1] range'
    )
    parser.add_argument(
        '--max-reactivity', type=float, default=10.0,
        help='Maximum reactivity value for filtering outliers'
    )
    parser.add_argument(
        '--window-size', type=int, default=15,
        help='Window size for sliding window analysis'
    )

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with CLI arguments
    cli_overrides = {
        "normalize": args.normalize,
        "max_reactivity": args.max_reactivity,
        "window_size": args.window_size
    }

    try:
        # Run analysis
        result = run_reactivity_analysis(
            input_file=args.input,
            output_dir=args.output,
            config=config,
            **cli_overrides
        )

        # Print summary
        print(f"✅ Analysis completed successfully")
        print(f"   Entries analyzed: {result['metadata']['num_entries']}")
        print(f"   Total nucleotides: {result['metadata']['total_nucleotides']}")

        summary = result['analysis_summary']
        if summary.get('global_reactivity_stats'):
            stats = summary['global_reactivity_stats']
            print(f"   Mean reactivity: {stats['mean']:.3f}")
            print(f"   Coverage: {summary['coverage_stats']['mean_coverage']:.3f}")

        # Classification distribution
        if 'classification_distribution' in summary:
            print("   Classification distribution:")
            for cls, count in summary['classification_distribution'].items():
                print(f"     {cls}: {count}")

        # Output files
        for file_type, file_path in result['output_files'].items():
            print(f"   {file_type}: {file_path}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}


if __name__ == '__main__':
    main()