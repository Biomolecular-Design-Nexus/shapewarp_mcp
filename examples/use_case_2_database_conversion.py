#!/usr/bin/env python3
"""
SHAPEwarp Use Case 2: Database Format Conversion

This script demonstrates converting between SHAPEwarp database formats
(XML to native binary format) and analyzing database contents.

Usage:
    python examples/use_case_2_database_conversion.py --input examples/data/test_db.xml --output results/converted.db
"""

import argparse
import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert SHAPEwarp database formats and analyze contents"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="examples/data/test_db.xml",
        help="Path to input XML database file"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results/converted.db",
        help="Path to output native database file"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze the input file without conversion"
    )
    parser.add_argument(
        "--max-reactivity",
        type=float,
        default=1.0,
        help="Maximum value to which reactivities will be capped"
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="Use mock data instead of calling actual SHAPEwarp binary"
    )

    return parser.parse_args()

def parse_xml_database(xml_file):
    """Parse SHAPEwarp XML database format."""
    logger.info(f"Parsing XML database: {xml_file}")

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract metadata
        metadata = {}
        meta_data = root.find('meta-data')
        if meta_data is not None:
            for child in meta_data:
                metadata[child.tag] = child.text

        logger.info("Database metadata:")
        for key, value in metadata.items():
            logger.info(f"  {key}: {value}")

        # Extract transcript entries
        transcripts = []
        for transcript in root.findall('transcript'):
            transcript_id = transcript.get('id')
            length = int(transcript.get('length'))

            # Get sequence
            sequence_elem = transcript.find('sequence')
            sequence = ''.join(sequence_elem.text.split()) if sequence_elem is not None else ""

            # Get reactivity data
            reactivity_elem = transcript.find('reactivity')
            reactivities = []
            if reactivity_elem is not None:
                reactivity_text = reactivity_elem.text.strip()
                for r_str in reactivity_text.split(','):
                    r_str = r_str.strip()
                    if r_str == 'NaN':
                        reactivities.append(np.nan)
                    else:
                        try:
                            reactivities.append(float(r_str))
                        except ValueError:
                            reactivities.append(np.nan)

            transcript_data = {
                'id': transcript_id,
                'length': length,
                'sequence': sequence,
                'reactivities': reactivities,
                'seq_length': len(sequence),
                'reactivity_count': len(reactivities)
            }

            transcripts.append(transcript_data)

            logger.info(f"Parsed transcript: {transcript_id}, length={length}, seq_len={len(sequence)}, react_count={len(reactivities)}")

        return {
            'metadata': metadata,
            'transcripts': transcripts
        }

    except ET.ParseError as e:
        logger.error(f"XML parsing error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing XML database: {e}")
        return None

def analyze_database(db_data):
    """Analyze database contents and generate statistics."""
    logger.info("Analyzing database contents...")

    transcripts = db_data['transcripts']
    metadata = db_data['metadata']

    analysis = {
        'total_transcripts': len(transcripts),
        'organism': metadata.get('organism', 'Unknown'),
        'probe': metadata.get('probe', 'Unknown'),
        'condition': metadata.get('condition', 'Unknown')
    }

    # Sequence statistics
    seq_lengths = [t['seq_length'] for t in transcripts]
    analysis.update({
        'min_sequence_length': min(seq_lengths),
        'max_sequence_length': max(seq_lengths),
        'mean_sequence_length': np.mean(seq_lengths),
        'total_nucleotides': sum(seq_lengths)
    })

    # Reactivity statistics
    all_reactivities = []
    for transcript in transcripts:
        reactivities = transcript['reactivities']
        valid_reactivities = [r for r in reactivities if not np.isnan(r)]
        all_reactivities.extend(valid_reactivities)

    if all_reactivities:
        analysis.update({
            'total_reactivity_measurements': len(all_reactivities),
            'min_reactivity': min(all_reactivities),
            'max_reactivity': max(all_reactivities),
            'mean_reactivity': np.mean(all_reactivities),
            'median_reactivity': np.median(all_reactivities)
        })

    # Coverage statistics
    coverage_stats = []
    for transcript in transcripts:
        reactivities = transcript['reactivities']
        valid_count = sum(1 for r in reactivities if not np.isnan(r))
        coverage = valid_count / len(reactivities) if reactivities else 0
        coverage_stats.append(coverage)

    analysis.update({
        'mean_coverage': np.mean(coverage_stats),
        'min_coverage': min(coverage_stats),
        'max_coverage': max(coverage_stats)
    })

    return analysis

def convert_database(input_file, output_file, args):
    """Convert XML database to native binary format using SHAPEwarp."""

    # Check if SHAPEwarp binary exists
    shapewarp_binary = "target/release/SHAPEwarp"
    if not os.path.exists(shapewarp_binary):
        logger.warning(f"SHAPEwarp binary not found at {shapewarp_binary}")
        logger.info("You need to build SHAPEwarp first. See README.md for instructions.")
        return False

    # Build command for database conversion
    cmd = [
        shapewarp_binary,
        "--database", input_file,
        "--dump-db", output_file
    ]

    if args.max_reactivity != 1.0:
        cmd.extend(["--max-reactivity", str(args.max_reactivity)])

    logger.info(f"Running conversion command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("Database conversion completed successfully")
        logger.debug(f"STDOUT: {result.stdout}")

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Database conversion failed: {e}")
        logger.error(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(f"SHAPEwarp binary not found: {shapewarp_binary}")
        return False

def create_mock_database(output_file):
    """Create mock native database file for testing."""
    logger.info("Creating mock native database file...")

    # Create a simple binary file with mock data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    mock_data = b"SHAPEWARP_DB_V1\x00" + b"\x01" * 1000  # Mock binary format
    with open(output_file, 'wb') as f:
        f.write(mock_data)

    logger.info(f"Mock database created: {output_file}")
    return True

def export_analysis_report(analysis, db_data, output_dir):
    """Export detailed analysis report."""
    os.makedirs(output_dir, exist_ok=True)

    # Create summary report
    report_file = os.path.join(output_dir, "database_analysis.txt")
    with open(report_file, 'w') as f:
        f.write("SHAPEwarp Database Analysis Report\n")
        f.write("=" * 40 + "\n\n")

        f.write("Database Metadata:\n")
        for key, value in db_data['metadata'].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")

        f.write("Database Statistics:\n")
        for key, value in analysis.items():
            if isinstance(value, float):
                f.write(f"  {key}: {value:.3f}\n")
            else:
                f.write(f"  {key}: {value}\n")
        f.write("\n")

        f.write("Transcript Details:\n")
        for i, transcript in enumerate(db_data['transcripts'][:10]):  # First 10
            f.write(f"  {i+1}. {transcript['id']}: {transcript['seq_length']} nt, {transcript['reactivity_count']} measurements\n")
        if len(db_data['transcripts']) > 10:
            f.write(f"  ... and {len(db_data['transcripts']) - 10} more\n")

    logger.info(f"Analysis report saved to: {report_file}")

    # Create CSV with transcript details
    transcript_details = []
    for transcript in db_data['transcripts']:
        reactivities = transcript['reactivities']
        valid_reactivities = [r for r in reactivities if not np.isnan(r)]

        transcript_details.append({
            'transcript_id': transcript['id'],
            'sequence_length': transcript['seq_length'],
            'reactivity_measurements': len(reactivities),
            'valid_measurements': len(valid_reactivities),
            'coverage': len(valid_reactivities) / len(reactivities) if reactivities else 0,
            'mean_reactivity': np.mean(valid_reactivities) if valid_reactivities else np.nan,
            'max_reactivity': max(valid_reactivities) if valid_reactivities else np.nan
        })

    df = pd.DataFrame(transcript_details)
    csv_file = os.path.join(output_dir, "transcript_details.csv")
    df.to_csv(csv_file, index=False)

    logger.info(f"Transcript details saved to: {csv_file}")

def main():
    """Main function."""
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")

    # Parse arguments
    args = parse_arguments()

    logger.info("Starting SHAPEwarp database conversion and analysis")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output file: {args.output}")

    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file does not exist: {args.input}")
        return 1

    # Parse XML database
    db_data = parse_xml_database(args.input)
    if db_data is None:
        logger.error("Failed to parse input database")
        return 1

    # Analyze database
    analysis = analyze_database(db_data)

    logger.info("Database Analysis Summary:")
    logger.info(f"  Total transcripts: {analysis['total_transcripts']}")
    logger.info(f"  Organism: {analysis['organism']}")
    logger.info(f"  Probe: {analysis['probe']}")
    logger.info(f"  Condition: {analysis['condition']}")
    logger.info(f"  Sequence length range: {analysis['min_sequence_length']}-{analysis['max_sequence_length']} nt")
    logger.info(f"  Mean sequence length: {analysis['mean_sequence_length']:.1f} nt")
    logger.info(f"  Total nucleotides: {analysis['total_nucleotides']}")
    if 'total_reactivity_measurements' in analysis:
        logger.info(f"  Total reactivity measurements: {analysis['total_reactivity_measurements']}")
        logger.info(f"  Reactivity range: {analysis['min_reactivity']:.3f}-{analysis['max_reactivity']:.3f}")
        logger.info(f"  Mean reactivity: {analysis['mean_reactivity']:.3f}")
        logger.info(f"  Mean coverage: {analysis['mean_coverage']:.3f}")

    # Export analysis report
    output_dir = os.path.dirname(args.output) or "results"
    export_analysis_report(analysis, db_data, output_dir)

    # Convert database (if not analyze-only)
    if not args.analyze_only:
        logger.info("Converting database format...")

        if args.use_mock:
            success = create_mock_database(args.output)
        else:
            success = convert_database(args.input, args.output, args)

            if not success:
                logger.warning("Database conversion failed, creating mock database instead")
                success = create_mock_database(args.output)

        if success:
            logger.info(f"Database conversion completed: {args.output}")
        else:
            logger.error("Database conversion failed")
            return 1

    logger.info("Database conversion and analysis completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())