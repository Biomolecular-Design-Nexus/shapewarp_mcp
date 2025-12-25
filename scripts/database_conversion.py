#!/usr/bin/env python3
"""
Script: database_conversion.py
Description: Convert between SHAPEwarp database formats and analyze database contents

Original Use Case: examples/use_case_2_database_conversion.py
Dependencies Removed: subprocess (SHAPEwarp binary), complex logging setup

Usage:
    python scripts/database_conversion.py --input <xml_file> --output <database_file>

Example:
    python scripts/database_conversion.py --input examples/data/test_db.xml --output results/converted.db
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
import os
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

import pandas as pd
import numpy as np

# Import shared library functions
import sys
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from lib.io import parse_xml_database, save_dataframe, save_json
from lib.utils import create_mock_binary_database

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "max_reactivity": 1.0,
    "output_format": "binary",
    "analyze_only": False,
    "generate_reports": True,
    "use_mock": True  # Default to mock mode for MCP compatibility
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_database_conversion(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convert SHAPEwarp database formats and analyze database contents.

    Args:
        input_file: Path to input XML database file
        output_file: Path to output database file (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - database_info: Parsed database information
            - output_file: Path to output file (if created)
            - analysis: Database analysis results
            - metadata: Execution metadata

    Example:
        >>> result = run_database_conversion("input.xml", "output.db")
        >>> print(f"Converted database with {len(result['database_info']['transcripts'])} transcripts")
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Parse input XML database
    try:
        database_info = parse_xml_database(input_file)
    except Exception as e:
        raise ValueError(f"Failed to parse XML database: {e}")

    if not database_info['transcripts']:
        raise ValueError("No transcripts found in database")

    # Analyze database contents
    analysis = analyze_database_contents(database_info, config)

    # Convert to binary format (if not analyze-only)
    output_path = None
    if not config.get("analyze_only", False) and output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if config.get("use_mock", True):
            # Create mock binary database
            create_mock_binary_database(output_path, database_info)
            conversion_method = "mock"
        else:
            # In production, this would call the actual SHAPEwarp conversion
            # For now, we use mock conversion
            create_mock_binary_database(output_path, database_info)
            conversion_method = "mock_fallback"

    # Generate additional reports if requested
    report_files = {}
    if config.get("generate_reports", True) and output_file:
        output_dir = Path(output_file).parent
        report_files = generate_analysis_reports(database_info, analysis, output_dir)

    return {
        "database_info": database_info,
        "output_file": str(output_path) if output_path else None,
        "analysis": analysis,
        "report_files": report_files,
        "metadata": {
            "input_file": str(input_file),
            "num_transcripts": len(database_info['transcripts']),
            "config": config,
            "conversion_method": conversion_method if output_path else None
        }
    }


def analyze_database_contents(database_info: Dict[str, Any],
                            config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze database contents and generate statistics.

    Inlined from examples/use_case_2_database_conversion.py

    Args:
        database_info: Parsed database information
        config: Configuration dictionary

    Returns:
        Dictionary with analysis results
    """
    transcripts = database_info['transcripts']

    if not transcripts:
        return {"error": "No transcripts to analyze"}

    # Overall statistics
    total_transcripts = len(transcripts)
    total_sequence_length = sum(t['length'] for t in transcripts)
    total_reactivities = sum(len(t['reactivities']) for t in transcripts)

    # Per-transcript analysis
    transcript_stats = []
    reactivity_values = []

    for transcript in transcripts:
        # Extract reactivity values
        react_values = [r['value'] for r in transcript['reactivities']]
        reactivity_values.extend(react_values)

        # Calculate per-transcript statistics
        if react_values:
            stats = {
                'id': transcript['id'],
                'sequence_length': transcript['length'],
                'organism': transcript.get('organism', ''),
                'probe': transcript.get('probe', ''),
                'num_reactivities': len(react_values),
                'coverage': len(react_values) / transcript['length'] if transcript['length'] > 0 else 0,
                'mean_reactivity': np.mean(react_values),
                'median_reactivity': np.median(react_values),
                'std_reactivity': np.std(react_values),
                'min_reactivity': np.min(react_values),
                'max_reactivity': np.max(react_values)
            }
        else:
            stats = {
                'id': transcript['id'],
                'sequence_length': transcript['length'],
                'organism': transcript.get('organism', ''),
                'probe': transcript.get('probe', ''),
                'num_reactivities': 0,
                'coverage': 0.0,
                'mean_reactivity': np.nan,
                'median_reactivity': np.nan,
                'std_reactivity': np.nan,
                'min_reactivity': np.nan,
                'max_reactivity': np.nan
            }

        transcript_stats.append(stats)

    # Global reactivity statistics
    if reactivity_values:
        global_stats = {
            'total_reactivities': len(reactivity_values),
            'mean_reactivity': np.mean(reactivity_values),
            'median_reactivity': np.median(reactivity_values),
            'std_reactivity': np.std(reactivity_values),
            'min_reactivity': np.min(reactivity_values),
            'max_reactivity': np.max(reactivity_values),
            'q25_reactivity': np.percentile(reactivity_values, 25),
            'q75_reactivity': np.percentile(reactivity_values, 75)
        }
    else:
        global_stats = {
            'total_reactivities': 0,
            'mean_reactivity': np.nan,
            'median_reactivity': np.nan,
            'std_reactivity': np.nan,
            'min_reactivity': np.nan,
            'max_reactivity': np.nan,
            'q25_reactivity': np.nan,
            'q75_reactivity': np.nan
        }

    return {
        "summary": {
            "total_transcripts": total_transcripts,
            "total_sequence_length": total_sequence_length,
            "total_reactivities": total_reactivities,
            "average_transcript_length": total_sequence_length / total_transcripts if total_transcripts > 0 else 0,
            "average_reactivities_per_transcript": total_reactivities / total_transcripts if total_transcripts > 0 else 0
        },
        "global_reactivity_stats": global_stats,
        "transcript_stats": transcript_stats
    }


def generate_analysis_reports(database_info: Dict[str, Any],
                            analysis: Dict[str, Any],
                            output_dir: Path) -> Dict[str, str]:
    """
    Generate analysis reports in multiple formats.

    Args:
        database_info: Parsed database information
        analysis: Analysis results
        output_dir: Output directory

    Returns:
        Dictionary with paths to generated report files
    """
    report_files = {}

    # 1. Database analysis text report
    analysis_file = output_dir / "database_analysis.txt"
    with open(analysis_file, 'w') as f:
        f.write("SHAPEwarp Database Analysis Report\n")
        f.write("=" * 40 + "\n\n")

        # Summary
        summary = analysis['summary']
        f.write("Summary:\n")
        f.write(f"  Total transcripts: {summary['total_transcripts']}\n")
        f.write(f"  Total sequence length: {summary['total_sequence_length']} nt\n")
        f.write(f"  Total reactivities: {summary['total_reactivities']}\n")
        f.write(f"  Average transcript length: {summary['average_transcript_length']:.1f} nt\n")
        f.write(f"  Average reactivities per transcript: {summary['average_reactivities_per_transcript']:.1f}\n\n")

        # Global reactivity statistics
        global_stats = analysis['global_reactivity_stats']
        f.write("Global Reactivity Statistics:\n")
        f.write(f"  Mean: {global_stats['mean_reactivity']:.3f}\n")
        f.write(f"  Median: {global_stats['median_reactivity']:.3f}\n")
        f.write(f"  Std Dev: {global_stats['std_reactivity']:.3f}\n")
        f.write(f"  Min: {global_stats['min_reactivity']:.3f}\n")
        f.write(f"  Max: {global_stats['max_reactivity']:.3f}\n")
        f.write(f"  Q25: {global_stats['q25_reactivity']:.3f}\n")
        f.write(f"  Q75: {global_stats['q75_reactivity']:.3f}\n\n")

        # Per-transcript details
        f.write("Transcript Details:\n")
        for stats in analysis['transcript_stats']:
            f.write(f"  {stats['id']}:\n")
            f.write(f"    Length: {stats['sequence_length']} nt\n")
            f.write(f"    Organism: {stats['organism']}\n")
            f.write(f"    Probe: {stats['probe']}\n")
            f.write(f"    Reactivities: {stats['num_reactivities']}\n")
            f.write(f"    Coverage: {stats['coverage']:.3f}\n")
            if not np.isnan(stats['mean_reactivity']):
                f.write(f"    Mean reactivity: {stats['mean_reactivity']:.3f}\n")
            f.write("\n")

    report_files['analysis_report'] = str(analysis_file)

    # 2. Transcript details CSV
    transcript_csv = output_dir / "transcript_details.csv"
    transcript_df = pd.DataFrame(analysis['transcript_stats'])
    save_dataframe(transcript_df, transcript_csv, format='csv')
    report_files['transcript_csv'] = str(transcript_csv)

    # 3. Database info JSON
    database_json = output_dir / "database_info.json"
    save_json(database_info, database_json)
    report_files['database_json'] = str(database_json)

    return report_files


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
        help='Path to input XML database file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Path to output database file'
    )
    parser.add_argument(
        '--config', '-c',
        help='Configuration file (JSON)'
    )
    parser.add_argument(
        '--analyze-only', action='store_true',
        help='Only analyze the input file without conversion'
    )
    parser.add_argument(
        '--max-reactivity', type=float, default=1.0,
        help='Maximum value to which reactivities will be capped'
    )
    parser.add_argument(
        '--use-mock', action='store_true', default=True,
        help='Use mock conversion (default: True for MCP compatibility)'
    )

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with CLI arguments
    cli_overrides = {
        "analyze_only": args.analyze_only,
        "max_reactivity": args.max_reactivity,
        "use_mock": args.use_mock
    }

    try:
        # Run conversion/analysis
        result = run_database_conversion(
            input_file=args.input,
            output_file=args.output,
            config=config,
            **cli_overrides
        )

        # Print summary
        print(f"✅ Database processing completed successfully")
        print(f"   Transcripts: {result['metadata']['num_transcripts']}")
        print(f"   Total reactivities: {result['analysis']['summary']['total_reactivities']}")

        if result['output_file']:
            print(f"   Database saved: {result['output_file']}")

        for report_type, report_path in result['report_files'].items():
            print(f"   {report_type}: {report_path}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}


if __name__ == '__main__':
    main()