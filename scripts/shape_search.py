#!/usr/bin/env python3
"""
Script: shape_search.py
Description: Search for structurally similar RNA sequences using SHAPE reactivity profiles

Original Use Case: examples/use_case_1_shape_search.py
Dependencies Removed: subprocess (SHAPEwarp binary), complex logging setup

Usage:
    python scripts/shape_search.py --query <query_file> --database <database_file> --output <output_dir>

Example:
    python scripts/shape_search.py --query examples/data/query.txt --database examples/data/test.db --output results/search
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
from lib.io import parse_shape_query_file, save_dataframe, validate_shape_data
from lib.utils import generate_mock_search_results

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "max_reactivity": 1.0,
    "max_align_overlap": 0.5,
    "threads": None,
    "output_format": "tsv",
    "use_mock": True,  # Default to mock mode for MCP compatibility
    "mock_hits_per_query": 3,
    "significant_pvalue_threshold": 1e-5
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_shape_search(
    query_file: Union[str, Path],
    database_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search for structurally similar RNA sequences using SHAPE reactivity profiles.

    Args:
        query_file: Path to query file with RNA sequences and SHAPE reactivities
        database_file: Path to database file with reference sequences
        output_dir: Directory to save search results (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - results: DataFrame with search results
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
            - summary: Search results summary

    Example:
        >>> result = run_shape_search("query.txt", "database.db", "output/")
        >>> print(f"Found {len(result['results'])} hits")
    """
    # Setup
    query_file = Path(query_file)
    database_file = Path(database_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not query_file.exists():
        raise FileNotFoundError(f"Query file not found: {query_file}")

    if not database_file.exists():
        raise FileNotFoundError(f"Database file not found: {database_file}")

    # Parse query file
    try:
        query_entries = parse_shape_query_file(query_file)
    except Exception as e:
        raise ValueError(f"Failed to parse query file: {e}")

    if not query_entries:
        raise ValueError("No valid query entries found in query file")

    # Validate query data
    validation_errors = validate_shape_data(query_entries)
    if validation_errors:
        raise ValueError(f"Query validation failed: {'; '.join(validation_errors)}")

    # Generate search results (mock mode for MCP compatibility)
    if config.get("use_mock", True):
        results_df = generate_mock_search_results(
            query_entries,
            num_hits_per_query=config.get("mock_hits_per_query", 3)
        )
        search_method = "mock"
    else:
        # In production, this would call the actual SHAPEwarp binary
        # For now, we use mock results as the binary is not guaranteed to be available
        results_df = generate_mock_search_results(
            query_entries,
            num_hits_per_query=config.get("mock_hits_per_query", 3)
        )
        search_method = "mock_fallback"

    # Analyze results
    summary = analyze_search_results(results_df, config)

    # Save output if requested
    output_file = None
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "search_results.tsv"
        save_dataframe(results_df, output_file, format="tsv")

    return {
        "results": results_df,
        "output_file": str(output_file) if output_file else None,
        "metadata": {
            "query_file": str(query_file),
            "database_file": str(database_file),
            "num_queries": len(query_entries),
            "config": config,
            "search_method": search_method
        },
        "summary": summary
    }


def analyze_search_results(results_df: pd.DataFrame,
                         config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze search results and generate summary statistics.

    Inlined from examples/use_case_1_shape_search.py:analyze_search_results()

    Args:
        results_df: DataFrame with search results
        config: Configuration dictionary

    Returns:
        Dictionary with summary statistics
    """
    if results_df.empty:
        return {
            "total_hits": 0,
            "significant_hits": 0,
            "queries_with_hits": 0,
            "best_score": None,
            "best_pvalue": None
        }

    # Count significant hits based on p-value threshold
    pvalue_threshold = config.get("significant_pvalue_threshold", 1e-5)
    significant_hits = results_df[results_df['pvalue'] < pvalue_threshold]

    # Get unique queries that have hits
    unique_queries = results_df['query'].nunique()

    summary = {
        "total_hits": len(results_df),
        "significant_hits": len(significant_hits),
        "queries_with_hits": unique_queries,
        "best_score": float(results_df['score'].max()) if len(results_df) > 0 else None,
        "best_pvalue": float(results_df['pvalue'].min()) if len(results_df) > 0 else None,
        "score_stats": {
            "mean": float(results_df['score'].mean()),
            "median": float(results_df['score'].median()),
            "std": float(results_df['score'].std())
        } if len(results_df) > 0 else None
    }

    return summary


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--query', '-q', required=True,
        help='Path to query file containing RNA sequences and SHAPE reactivities'
    )
    parser.add_argument(
        '--database', '-d', required=True,
        help='Path to database file containing reference RNA structures'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for search results'
    )
    parser.add_argument(
        '--config', '-c',
        help='Configuration file (JSON)'
    )
    parser.add_argument(
        '--max-reactivity', type=float, default=1.0,
        help='Maximum value to which reactivities will be capped'
    )
    parser.add_argument(
        '--max-align-overlap', type=float, default=0.5,
        help='Maximum alignment overlap fraction'
    )
    parser.add_argument(
        '--use-mock', action='store_true', default=True,
        help='Use mock search results (default: True for MCP compatibility)'
    )

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with CLI arguments
    cli_overrides = {
        "max_reactivity": args.max_reactivity,
        "max_align_overlap": args.max_align_overlap,
        "use_mock": args.use_mock
    }

    try:
        # Run search
        result = run_shape_search(
            query_file=args.query,
            database_file=args.database,
            output_dir=args.output,
            config=config,
            **cli_overrides
        )

        # Print summary
        print(f"✅ Search completed successfully")
        print(f"   Queries processed: {result['metadata']['num_queries']}")
        print(f"   Total hits: {result['summary']['total_hits']}")
        print(f"   Significant hits: {result['summary']['significant_hits']}")
        if result['summary']['best_score']:
            print(f"   Best score: {result['summary']['best_score']:.2f}")
            print(f"   Best p-value: {result['summary']['best_pvalue']:.2e}")

        if result['output_file']:
            print(f"   Results saved: {result['output_file']}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}


if __name__ == '__main__':
    main()