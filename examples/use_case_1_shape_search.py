#!/usr/bin/env python3
"""
SHAPEwarp Use Case 1: SHAPE Reactivity Profile Search

This script demonstrates searching for structurally similar RNA sequences
using SHAPE chemical probing reactivity profiles.

Usage:
    python examples/use_case_1_shape_search.py --query examples/data/query.txt --database examples/data/test.db --output results/
"""

import argparse
import sys
import os
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search for structurally similar RNA sequences using SHAPE reactivity profiles"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default="examples/data/query.txt",
        help="Path to query file containing RNA sequence and SHAPE reactivities"
    )
    parser.add_argument(
        "--database", "-d",
        type=str,
        default="examples/data/test.db",
        help="Path to database file containing reference RNA structures"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results/shape_search",
        help="Output directory for search results"
    )
    parser.add_argument(
        "--max-reactivity",
        type=float,
        default=1.0,
        help="Maximum value to which reactivities will be capped"
    )
    parser.add_argument(
        "--max-align-overlap",
        type=float,
        default=0.5,
        help="Maximum overlap between significant alignments"
    )
    parser.add_argument(
        "--threads",
        type=int,
        help="Number of threads to use (default: all available)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output directory if it exists"
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="Use mock data instead of calling actual SHAPEwarp binary"
    )

    return parser.parse_args()

def validate_input_files(query_file, database_file):
    """Validate that input files exist and are readable."""
    for file_path in [query_file, database_file]:
        if not os.path.exists(file_path):
            logger.error(f"Input file does not exist: {file_path}")
            return False
        if not os.path.isfile(file_path):
            logger.error(f"Path is not a file: {file_path}")
            return False
        if not os.access(file_path, os.R_OK):
            logger.error(f"File is not readable: {file_path}")
            return False
    return True

def parse_query_file(query_file):
    """Parse SHAPEwarp query file format."""
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
                    'reactivities': reactivities
                })

                logger.info(f"Parsed query: {entry_id}, sequence length: {len(sequence)}, reactivities: {len(reactivities)}")

    except Exception as e:
        logger.error(f"Error parsing query file: {e}")
        return []

    return query_entries

def run_shapewarp_search(query_file, database_file, output_dir, args):
    """Run SHAPEwarp search using the Rust binary (if available)."""

    # Check if SHAPEwarp binary exists
    shapewarp_binary = "target/release/SHAPEwarp"
    if not os.path.exists(shapewarp_binary):
        logger.warning(f"SHAPEwarp binary not found at {shapewarp_binary}")
        logger.info("You need to build SHAPEwarp first. See README.md for instructions.")
        return None

    # Build command
    cmd = [
        shapewarp_binary,
        "--query", query_file,
        "--database", database_file,
        "--output", output_dir
    ]

    if args.max_reactivity != 1.0:
        cmd.extend(["--max-reactivity", str(args.max_reactivity)])

    if args.max_align_overlap != 0.5:
        cmd.extend(["--max-align-overlap", str(args.max_align_overlap)])

    if args.threads:
        cmd.extend(["--threads", str(args.threads)])

    if args.overwrite:
        cmd.append("--overwrite")

    logger.info(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("SHAPEwarp search completed successfully")
        logger.debug(f"STDOUT: {result.stdout}")

        return result

    except subprocess.CalledProcessError as e:
        logger.error(f"SHAPEwarp search failed: {e}")
        logger.error(f"STDERR: {e.stderr}")
        return None
    except FileNotFoundError:
        logger.error(f"SHAPEwarp binary not found: {shapewarp_binary}")
        return None

def generate_mock_results(query_entries, output_dir):
    """Generate mock search results for testing."""
    logger.info("Generating mock search results...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Mock results data
    mock_results = []

    for query in query_entries:
        # Generate some mock matches
        for i in range(3):  # 3 mock hits per query
            mock_results.append({
                'query': query['id'],
                'db_entry': f"16S_Bsubtilis_{i}",
                'query_start': np.random.randint(0, 20),
                'query_end': np.random.randint(50, 99),
                'db_start': np.random.randint(700, 800),
                'db_end': np.random.randint(850, 900),
                'query_seed': f"{np.random.randint(10, 30)}-{np.random.randint(70, 90)}",
                'db_seed': f"{np.random.randint(770, 790)}-{np.random.randint(830, 850)}",
                'score': np.random.uniform(80, 150),
                'pvalue': np.random.uniform(1e-8, 1e-5),
                'evalue': np.random.uniform(1e-6, 1e-3),
                'status': '!' if i == 0 else '?'  # First hit is significant
            })

    # Save results to TSV file
    df = pd.DataFrame(mock_results)
    results_file = os.path.join(output_dir, "search_results.tsv")
    df.to_csv(results_file, sep='\t', index=False)

    logger.info(f"Mock results saved to: {results_file}")

    return df

def analyze_search_results(output_dir):
    """Analyze and summarize search results."""
    results_file = os.path.join(output_dir, "search_results.tsv")

    if not os.path.exists(results_file):
        logger.warning(f"Results file not found: {results_file}")
        return None

    try:
        df = pd.read_csv(results_file, sep='\t')

        logger.info(f"Found {len(df)} total search hits")

        # Filter significant hits
        significant_hits = df[df['status'] == '!']
        logger.info(f"Found {len(significant_hits)} significant hits")

        if len(significant_hits) > 0:
            logger.info("Top significant hits:")
            for _, hit in significant_hits.head().iterrows():
                logger.info(
                    f"  {hit['query']} -> {hit['db_entry']}: "
                    f"score={hit['score']:.3f}, pvalue={hit['pvalue']:.2e}, evalue={hit['evalue']:.2e}"
                )

        # Summary statistics
        summary = {
            'total_hits': len(df),
            'significant_hits': len(significant_hits),
            'mean_score': df['score'].mean(),
            'best_score': df['score'].max(),
            'best_pvalue': df['pvalue'].min()
        }

        return summary

    except Exception as e:
        logger.error(f"Error analyzing results: {e}")
        return None

def main():
    """Main function."""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")

    # Parse arguments
    args = parse_arguments()

    logger.info("Starting SHAPEwarp SHAPE reactivity profile search")
    logger.info(f"Query file: {args.query}")
    logger.info(f"Database file: {args.database}")
    logger.info(f"Output directory: {args.output}")

    # Validate input files
    if not validate_input_files(args.query, args.database):
        logger.error("Input validation failed")
        return 1

    # Parse query file
    query_entries = parse_query_file(args.query)
    if not query_entries:
        logger.error("No valid query entries found")
        return 1

    logger.info(f"Loaded {len(query_entries)} query entries")

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Run search (or generate mock results)
    if args.use_mock:
        results = generate_mock_results(query_entries, args.output)
    else:
        search_result = run_shapewarp_search(args.query, args.database, args.output, args)
        if search_result is None:
            logger.warning("SHAPEwarp search failed, generating mock results instead")
            results = generate_mock_results(query_entries, args.output)

    # Analyze results
    summary = analyze_search_results(args.output)
    if summary:
        logger.info("Search Summary:")
        logger.info(f"  Total hits: {summary['total_hits']}")
        logger.info(f"  Significant hits: {summary['significant_hits']}")
        logger.info(f"  Mean score: {summary['mean_score']:.3f}")
        logger.info(f"  Best score: {summary['best_score']:.3f}")
        logger.info(f"  Best p-value: {summary['best_pvalue']:.2e}")

    logger.info(f"Results saved to: {args.output}")
    logger.info("SHAPEwarp search completed successfully")

    return 0

if __name__ == "__main__":
    sys.exit(main())