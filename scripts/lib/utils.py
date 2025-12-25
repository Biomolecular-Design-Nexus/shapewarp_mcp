"""
Utility functions for SHAPEwarp MCP scripts.

Extracted and simplified from original use case scripts.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple, Union, Optional


def normalize_reactivities(reactivities: List[float],
                         max_value: Optional[float] = None) -> List[float]:
    """
    Normalize SHAPE reactivity values.

    Inlined from examples/use_case_3_reactivity_analysis.py

    Args:
        reactivities: List of reactivity values
        max_value: Maximum value for capping (optional)

    Returns:
        Normalized reactivity values
    """
    # Convert to numpy array, handling NaN values
    values = np.array(reactivities, dtype=float)

    # Remove NaN values for normalization calculation
    valid_values = values[~np.isnan(values)]

    if len(valid_values) == 0:
        return reactivities  # All NaN, return as-is

    # Cap values if max_value is specified
    if max_value is not None:
        valid_values = np.clip(valid_values, None, max_value)

    # Normalize to [0, 1] range
    min_val = np.min(valid_values)
    max_val = np.max(valid_values)

    if max_val == min_val:
        # All values are the same, set to 0.5
        normalized = np.full_like(values, 0.5)
    else:
        # Standard min-max normalization
        normalized = (values - min_val) / (max_val - min_val)

    return normalized.tolist()


def classify_nucleotides(reactivities: List[float],
                        thresholds: Tuple[float, float] = (0.3, 0.7)) -> List[str]:
    """
    Classify nucleotides based on SHAPE reactivity.

    Inlined from examples/use_case_3_reactivity_analysis.py

    Args:
        reactivities: List of reactivity values
        thresholds: (low_threshold, high_threshold) for classification

    Returns:
        List of classifications ('structured', 'intermediate', 'flexible', 'no_data')
    """
    low_threshold, high_threshold = thresholds
    classifications = []

    for reactivity in reactivities:
        if np.isnan(reactivity):
            classifications.append('no_data')
        elif reactivity < low_threshold:
            classifications.append('structured')
        elif reactivity > high_threshold:
            classifications.append('flexible')
        else:
            classifications.append('intermediate')

    return classifications


def calculate_sliding_window_stats(reactivities: List[float],
                                 window_size: int = 15) -> pd.DataFrame:
    """
    Calculate sliding window statistics.

    Inlined from examples/use_case_3_reactivity_analysis.py

    Args:
        reactivities: List of reactivity values
        window_size: Size of sliding window

    Returns:
        DataFrame with window statistics
    """
    results = []
    values = np.array(reactivities, dtype=float)

    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        valid_window = window[~np.isnan(window)]

        if len(valid_window) > 0:
            stats = {
                'position': i + 1,
                'start': i + 1,
                'end': i + window_size,
                'mean_reactivity': np.mean(valid_window),
                'median_reactivity': np.median(valid_window),
                'std_reactivity': np.std(valid_window),
                'min_reactivity': np.min(valid_window),
                'max_reactivity': np.max(valid_window),
                'coverage': len(valid_window) / window_size
            }
        else:
            stats = {
                'position': i + 1,
                'start': i + 1,
                'end': i + window_size,
                'mean_reactivity': np.nan,
                'median_reactivity': np.nan,
                'std_reactivity': np.nan,
                'min_reactivity': np.nan,
                'max_reactivity': np.nan,
                'coverage': 0.0
            }

        results.append(stats)

    return pd.DataFrame(results)


def analyze_reactivity_profile(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a single SHAPE reactivity profile.

    Consolidated from examples/use_case_3_reactivity_analysis.py

    Args:
        entry: Dictionary with 'id', 'sequence', 'reactivities'

    Returns:
        Dictionary with analysis results
    """
    reactivities = entry['reactivities']
    sequence = entry['sequence']

    # Basic statistics
    valid_reactivities = [r for r in reactivities if not np.isnan(r)]

    if len(valid_reactivities) > 0:
        stats = {
            'entry_id': entry['id'],
            'sequence_length': len(sequence),
            'total_measurements': len(reactivities),
            'valid_measurements': len(valid_reactivities),
            'coverage': len(valid_reactivities) / len(reactivities),
            'mean_reactivity': np.mean(valid_reactivities),
            'median_reactivity': np.median(valid_reactivities),
            'std_reactivity': np.std(valid_reactivities),
            'min_reactivity': np.min(valid_reactivities),
            'max_reactivity': np.max(valid_reactivities)
        }
    else:
        stats = {
            'entry_id': entry['id'],
            'sequence_length': len(sequence),
            'total_measurements': len(reactivities),
            'valid_measurements': 0,
            'coverage': 0.0,
            'mean_reactivity': np.nan,
            'median_reactivity': np.nan,
            'std_reactivity': np.nan,
            'min_reactivity': np.nan,
            'max_reactivity': np.nan
        }

    # Nucleotide classification
    classifications = classify_nucleotides(reactivities)
    class_counts = {}
    for cls in ['structured', 'intermediate', 'flexible', 'no_data']:
        class_counts[f'{cls}_count'] = classifications.count(cls)
        class_counts[f'{cls}_fraction'] = classifications.count(cls) / len(classifications)

    stats.update(class_counts)

    return stats


def generate_mock_search_results(query_entries: List[Dict[str, Any]],
                                num_hits_per_query: int = 3) -> pd.DataFrame:
    """
    Generate mock search results for testing.

    Extracted from examples/use_case_1_shape_search.py:generate_mock_results()

    Args:
        query_entries: List of query entries
        num_hits_per_query: Number of mock hits to generate per query

    Returns:
        DataFrame with mock search results
    """
    mock_results = []

    for query in query_entries:
        # Generate mock matches
        for i in range(num_hits_per_query):
            mock_results.append({
                'query': query['id'],
                'db_entry': f"16S_Bsubtilis_{i}",
                'query_start': np.random.randint(0, 20),
                'query_end': np.random.randint(50, min(99, len(query['sequence']))),
                'db_start': np.random.randint(700, 800),
                'db_end': np.random.randint(850, 900),
                'query_seed': f"{np.random.randint(10, 30)}-{np.random.randint(70, 90)}",
                'db_seed': f"{np.random.randint(770, 790)}-{np.random.randint(830, 850)}",
                'score': np.random.uniform(80, 150),
                'pvalue': np.random.uniform(1e-8, 1e-5),
                'evalue': np.random.uniform(1e-6, 1e-3),
                'status': '!' if i == 0 else '?'  # First hit is significant
            })

    return pd.DataFrame(mock_results)


def create_mock_binary_database(output_path: Union[str, Path],
                               database_info: Dict[str, Any]) -> None:
    """
    Create a mock binary database file.

    Simplified from examples/use_case_2_database_conversion.py

    Args:
        output_path: Path for output database file
        database_info: Parsed database information
    """
    # Create a simple mock binary file
    # In reality, this would use SHAPEwarp's binary format
    with open(output_path, 'wb') as f:
        # Write a simple header
        f.write(b'SHAPEWARP_DB_V1\x00')

        # Write number of transcripts
        num_transcripts = len(database_info['transcripts'])
        f.write(num_transcripts.to_bytes(4, byteorder='little'))

        # Write transcript data (simplified)
        for transcript in database_info['transcripts']:
            # Write transcript ID
            tid_bytes = transcript['id'].encode('utf-8')
            f.write(len(tid_bytes).to_bytes(4, byteorder='little'))
            f.write(tid_bytes)

            # Write sequence length
            seq_len = len(transcript['sequence'])
            f.write(seq_len.to_bytes(4, byteorder='little'))

            # Write number of reactivities
            num_react = len(transcript['reactivities'])
            f.write(num_react.to_bytes(4, byteorder='little'))