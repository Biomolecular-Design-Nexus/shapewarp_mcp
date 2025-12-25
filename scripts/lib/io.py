"""
I/O utilities for SHAPEwarp MCP scripts.

Extracted and simplified from original use case scripts to minimize dependencies.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import xml.etree.ElementTree as ET


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(file_path) as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save data to JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def parse_shape_query_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Parse SHAPE query file format.

    Inlined from examples/use_case_1_shape_search.py:parse_query_file()

    Format:
        entry_id
        SEQUENCE
        reactivity1,reactivity2,reactivity3,...
        [blank line]

    Args:
        file_path: Path to query file

    Returns:
        List of entries with 'id', 'sequence', and 'reactivities' keys
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Query file not found: {file_path}")

    query_entries = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Parse entries (4 lines per entry: id, sequence, reactivities, blank line)
        for i in range(0, len(lines), 4):
            if i + 2 >= len(lines):
                break

            entry_id = lines[i].strip()
            sequence = lines[i + 1].strip()
            reactivities_str = lines[i + 2].strip()

            # Skip empty entries
            if not entry_id or not sequence or not reactivities_str:
                continue

            # Parse reactivities (handle NaN values)
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

    except Exception as e:
        raise ValueError(f"Error parsing query file {file_path}: {e}")

    return query_entries


def parse_xml_database(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Parse XML database format.

    Inlined from examples/use_case_2_database_conversion.py:parse_xml_database()

    Args:
        file_path: Path to XML database file

    Returns:
        Dictionary with parsed database information
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"XML database file not found: {file_path}")

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        database_info = {
            'metadata': {},
            'transcripts': []
        }

        # Parse metadata
        for elem in root:
            if elem.tag == 'transcript':
                transcript = {
                    'id': elem.get('id', ''),
                    'length': 0,
                    'organism': '',
                    'probe': '',
                    'reactivities': []
                }

                for child in elem:
                    if child.tag == 'sequence':
                        transcript['sequence'] = child.text or ''
                        transcript['length'] = len(transcript['sequence'])
                    elif child.tag == 'organism':
                        transcript['organism'] = child.text or ''
                    elif child.tag == 'probe':
                        transcript['probe'] = child.text or ''
                    elif child.tag == 'reactivity':
                        position = int(child.get('position', 0))
                        value = float(child.get('value', 0.0))
                        transcript['reactivities'].append({
                            'position': position,
                            'value': value
                        })

                database_info['transcripts'].append(transcript)

        return database_info

    except Exception as e:
        raise ValueError(f"Error parsing XML database {file_path}: {e}")


def save_dataframe(df: pd.DataFrame, file_path: Union[str, Path],
                   format: str = 'csv') -> None:
    """
    Save DataFrame to file.

    Args:
        df: DataFrame to save
        file_path: Output file path
        format: File format ('csv', 'tsv', 'json')
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if format.lower() == 'csv':
        df.to_csv(file_path, index=False)
    elif format.lower() == 'tsv':
        df.to_csv(file_path, sep='\t', index=False)
    elif format.lower() == 'json':
        df.to_json(file_path, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")


def validate_shape_data(entries: List[Dict[str, Any]]) -> List[str]:
    """
    Validate SHAPE data entries.

    Args:
        entries: List of parsed SHAPE entries

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    for i, entry in enumerate(entries):
        # Check required fields
        if 'id' not in entry or not entry['id']:
            errors.append(f"Entry {i}: Missing or empty ID")

        if 'sequence' not in entry or not entry['sequence']:
            errors.append(f"Entry {i}: Missing or empty sequence")

        if 'reactivities' not in entry:
            errors.append(f"Entry {i}: Missing reactivities")
            continue

        # Check sequence/reactivity length match
        seq_len = len(entry['sequence'])
        react_len = len(entry['reactivities'])

        if seq_len != react_len:
            errors.append(f"Entry {i} ({entry['id']}): Sequence length ({seq_len}) != reactivity length ({react_len})")

        # Check for valid nucleotides
        valid_bases = set('ACGTUN')
        invalid_bases = set(entry['sequence'].upper()) - valid_bases
        if invalid_bases:
            errors.append(f"Entry {i} ({entry['id']}): Invalid bases: {invalid_bases}")

    return errors