# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-24
- **Filter Applied**: SHAPE reactivity profile comparison, RNA structure similarity search, chemical probing data analysis
- **Python Version**: 3.10.19
- **Environment Strategy**: single (Python environment for MCP server)
- **Source Language**: Rust (SHAPEwarp) with Python wrappers

## Use Cases

### UC-001: SHAPE Reactivity Profile Search
- **Description**: Search for structurally similar RNA sequences using SHAPE chemical probing reactivity profiles
- **Script Path**: `examples/use_case_1_shape_search.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: README.md, CLI analysis from src/cli.rs

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| query_file | file | Query file with RNA sequences and SHAPE reactivities | --query, -q |
| database_file | file | Database file with reference RNA structures | --database, -d |
| output_dir | directory | Output directory for search results | --output, -o |
| max_reactivity | float | Maximum reactivity value for capping | --max-reactivity |
| max_align_overlap | float | Maximum overlap between alignments | --max-align-overlap |
| threads | integer | Number of threads to use | --threads |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| search_results | TSV file | Search hits with scores, p-values, and alignments |
| summary_stats | log output | Summary statistics of search results |

**Example Usage:**
```bash
# Using mock data
python examples/use_case_1_shape_search.py --query examples/data/query.txt --database examples/data/test.db --use-mock --output results/

# Using actual SHAPEwarp binary (requires compilation)
python examples/use_case_1_shape_search.py --query examples/data/query.txt --database examples/data/test.db --output results/ --threads 4
```

**Example Data**: `examples/data/query.txt`, `examples/data/test.db`

---

### UC-002: Database Format Conversion and Analysis
- **Description**: Convert between XML and binary database formats and analyze database contents
- **Script Path**: `examples/use_case_2_database_conversion.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: CLI analysis from src/cli.rs, test data examination

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | Input XML database file | --input, -i |
| output_file | file | Output native database file | --output, -o |
| max_reactivity | float | Maximum reactivity for capping | --max-reactivity |
| analyze_only | flag | Only analyze without conversion | --analyze-only |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| converted_db | binary file | Native format database file |
| analysis_report | text file | Database analysis report |
| transcript_details | CSV file | Detailed transcript information |

**Example Usage:**
```bash
# Convert XML to binary format
python examples/use_case_2_database_conversion.py --input examples/data/test_db.xml --output results/converted.db --use-mock

# Analyze database content only
python examples/use_case_2_database_conversion.py --input examples/data/test_db.xml --analyze-only
```

**Example Data**: `examples/data/test_db.xml`

---

### UC-003: SHAPE Reactivity Profile Analysis
- **Description**: Comprehensive analysis of SHAPE reactivity profiles including statistics, classification, and visualization
- **Script Path**: `examples/use_case_3_reactivity_analysis.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env`
- **Source**: Analysis of SHAPE data format and RNA structure analysis methods

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | Query file with RNA sequences and reactivities | --input, -i |
| output_dir | directory | Output directory for analysis results | --output, -o |
| normalize | flag | Normalize reactivity values | --normalize |
| max_reactivity | float | Maximum reactivity for outlier filtering | --max-reactivity |
| window_size | integer | Window size for sliding window analysis | --window-size |
| create_plots | flag | Generate reactivity profile plots | --create-plots |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| summary_statistics | CSV file | Summary statistics for all entries |
| nucleotide_classifications | CSV file | Nucleotide-level reactivity classifications |
| sliding_window_analysis | CSV file | Sliding window analysis results |
| reactivity_plots | PNG files | Reactivity profile visualizations |

**Example Usage:**
```bash
# Basic analysis
python examples/use_case_3_reactivity_analysis.py --input examples/data/query.txt --output results/analysis

# Full analysis with plots and normalization
python examples/use_case_3_reactivity_analysis.py --input examples/data/query.txt --output results/analysis --normalize --create-plots --window-size 15
```

**Example Data**: `examples/data/query.txt`

---

## Summary

| Metric | Count |
|--------|-------|
| Total Found | 3 |
| Scripts Created | 3 |
| High Priority | 3 |
| Medium Priority | 0 |
| Low Priority | 0 |
| Demo Data Copied | ✅ |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/SHAPEwarp/test_data/query.txt` | `examples/data/query.txt` | Sample query sequence with SHAPE reactivity data |
| `repo/SHAPEwarp/test_data/test.db` | `examples/data/test.db` | Binary format database with reference sequences |
| `repo/SHAPEwarp/test_data/test_db.xml` | `examples/data/test_db.xml` | XML format database with metadata and reactivity profiles |
| `repo/SHAPEwarp/test_data/query_align.txt` | `examples/data/query_align.txt` | Query sequence for alignment testing |
| `repo/SHAPEwarp/test_data/valid_query.txt` | `examples/data/valid_query.txt` | Minimal valid query for validation |
| `repo/SHAPEwarp/test_data/query_*.txt` | `examples/data/query_*.txt` | Various test cases (invalid formats, edge cases) |

## Use Case Details

### SHAPE Reactivity Profile Format
The query files follow SHAPEwarp's format:
```
sequence_id
RNA_SEQUENCE_STRING
reactivity1,reactivity2,reactivity3,...

```

Where:
- `sequence_id`: Unique identifier for the RNA sequence
- `RNA_SEQUENCE_STRING`: RNA nucleotide sequence (A, C, G, U)
- `reactivity values`: Comma-separated SHAPE reactivity measurements (float values, NaN for missing data)

### Database Formats
1. **XML Format**: Human-readable format with metadata (organism, probe type, conditions)
2. **Binary Format**: Optimized format for fast similarity searches

### Analysis Capabilities
The use cases cover the core SHAPEwarp functionality:

1. **Similarity Search**: Find RNA sequences with similar secondary structures based on SHAPE reactivity patterns
2. **Data Management**: Convert between formats and analyze database contents
3. **Reactivity Analysis**: Statistical analysis of chemical probing data

### Mock Mode Support
All scripts support `--use-mock` flag to enable testing without the Rust binary:
- Generates realistic mock data
- Preserves the same output format
- Allows full MCP development without compilation dependencies

### Integration Points
These use cases map directly to MCP tools for:
- `shape_search`: Search for similar RNA structures
- `database_convert`: Convert and analyze database formats
- `reactivity_analyze`: Comprehensive SHAPE data analysis
- `database_stats`: Get statistics about database contents
- `validate_query`: Validate query file formats

### Performance Notes
- Python scripts: Fast startup, good for API endpoints
- Rust binary: High performance for large-scale searches
- Mock mode: Instant results for testing and development