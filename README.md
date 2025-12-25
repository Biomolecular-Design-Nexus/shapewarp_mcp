# SHAPEwarp MCP

> Search for structurally similar RNA sequences using SHAPE chemical probing reactivity profiles

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

SHAPEwarp MCP provides tools for analyzing RNA secondary structure through SHAPE (Selective 2'-Hydroxyl Acylation analyzed by Primer Extension) chemical probing data. This MCP server wraps the high-performance Rust-based SHAPEwarp tool with Python scripts for easy integration with AI assistants.

### Features
- **SHAPE Profile Search**: Find structurally similar RNA sequences using reactivity patterns
- **Database Management**: Convert between XML and binary database formats with analysis
- **Reactivity Analysis**: Comprehensive statistical analysis of chemical probing data
- **Dual API Design**: Fast sync operations and background batch processing
- **Mock Mode Support**: Test functionality without compiling Rust dependencies

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   ├── server.py           # MCP server
│   └── jobs/               # Job management system
├── scripts/
│   ├── shape_search.py     # SHAPE profile similarity search
│   ├── database_conversion.py # Database format conversion and analysis
│   ├── reactivity_analysis.py # SHAPE reactivity statistical analysis
│   └── lib/                # Shared utilities (15 functions)
├── examples/
│   └── data/               # Demo data (11 test files)
├── configs/                # Configuration files (4 configs)
└── repo/                   # Original SHAPEwarp repository
```

---

## Installation

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- Git (for cloning)

### Create Environment

Please strictly follow the information in `reports/step3_environment.md` to obtain the procedure to setup the environment. An example workflow is shown below.

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/shapewarp_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install dependencies
pip install fastmcp loguru click pandas numpy tqdm matplotlib seaborn scipy scikit-learn --ignore-installed
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/shape_search.py` | Search for structurally similar RNA sequences using SHAPE profiles | See below |
| `scripts/database_conversion.py` | Convert between database formats and analyze contents | See below |
| `scripts/reactivity_analysis.py` | Analyze SHAPE reactivity with statistics and classification | See below |

### Script Examples

#### SHAPE Profile Search

```bash
# Activate environment
mamba activate ./env

# Run SHAPE similarity search
python scripts/shape_search.py \
  --query examples/data/query.txt \
  --database examples/data/test.db \
  --output results/search_results \
  --max-reactivity 1.0
```

**Parameters:**
- `--query, -q`: Query file with RNA sequences and SHAPE reactivities (required)
- `--database, -d`: Database file with reference structures (required)
- `--output, -o`: Output directory for search results (default: results/)
- `--max-reactivity`: Maximum reactivity value threshold (default: 1.0)
- `--max-align-overlap`: Maximum alignment overlap (default: 0.5)
- `--config, -c`: Configuration file (optional)

#### Database Format Conversion

```bash
python scripts/database_conversion.py \
  --input examples/data/test_db.xml \
  --output results/converted.db \
  --output-format binary
```

**Parameters:**
- `--input, -i`: Input XML database file (required)
- `--output, -o`: Output file path (default: auto-generated)
- `--output-format`: Output format - "binary", "csv", "json" (default: "binary")
- `--config, -c`: Configuration file (optional)

#### SHAPE Reactivity Analysis

```bash
python scripts/reactivity_analysis.py \
  --input examples/data/query.txt \
  --output results/analysis \
  --normalize \
  --window-size 15
```

**Parameters:**
- `--input, -i`: RNA sequences with SHAPE reactivities (required)
- `--output, -o`: Output directory for analysis results (default: results/)
- `--normalize`: Normalize reactivity values (flag)
- `--window-size`: Sliding window size for analysis (default: 10)
- `--reactivity-threshold`: Custom threshold for nucleotide classification (optional)

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name SHAPEwarp
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add SHAPEwarp -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "SHAPEwarp": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/shapewarp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/shapewarp_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from SHAPEwarp?
```

#### Basic Usage
```
Use search_shape_profiles with query_file @examples/data/query.txt and database_file @examples/data/test.db
```

#### With Configuration
```
Run analyze_reactivity_profiles on @examples/data/query.txt using normalize True and window_size 15
```

#### Long-Running Tasks (Submit API)
```
Submit submit_shape_search with query_file @examples/data/query.txt and database_file @examples/data/test.db
Then check the job status
```

#### Batch Processing
```
Process these files in batch using submit_batch_shape_search:
- @examples/data/query.txt
- @examples/data/query_align.txt
- @examples/data/valid_query.txt
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/query.txt` | Reference a specific query file |
| `@examples/data/test_db.xml` | Reference a database file |
| `@configs/shape_search_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "SHAPEwarp": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/shapewarp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/shapewarp_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Use search_shape_profiles with query_file examples/data/query.txt and database_file examples/data/test.db
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 1 second):

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_shape_profiles` | Search for similar RNA structures using SHAPE profiles | `query_file`, `database_file`, `output_dir`, `config_file`, `max_reactivity`, `max_align_overlap`, `use_mock` |
| `convert_database_format` | Convert between database formats and analyze | `input_file`, `output_file`, `config_file`, `output_format` |
| `analyze_reactivity_profiles` | Analyze SHAPE reactivity with statistics | `input_file`, `output_dir`, `config_file`, `normalize`, `window_size`, `reactivity_threshold` |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes if large datasets):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_shape_search` | Background SHAPE profile search | `query_file`, `database_file`, `job_name` |
| `submit_database_conversion` | Background database conversion | `input_file`, `output_file`, `job_name` |
| `submit_reactivity_analysis` | Background reactivity analysis | `input_file`, `output_dir`, `job_name` |
| `submit_batch_shape_search` | Batch search multiple query files | `input_files`, `database_file`, `job_name` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and timestamps |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs (with tail option) |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with status filtering |

---

## Examples

### Example 1: SHAPE Similarity Search

**Goal:** Find RNA sequences with similar secondary structure based on SHAPE reactivity patterns

**Using Script:**
```bash
python scripts/shape_search.py \
  --query examples/data/query.txt \
  --database examples/data/test.db \
  --output results/example1/
```

**Using MCP (in Claude Code):**
```
Use search_shape_profiles to search @examples/data/query.txt against @examples/data/test.db and save results to results/example1/
```

**Expected Output:**
- `search_results.tsv`: TSV file with search hits, scores, and p-values
- Search statistics: queries processed, total hits, best scores

### Example 2: Database Format Conversion

**Goal:** Convert XML database to binary format and analyze contents

**Using Script:**
```bash
python scripts/database_conversion.py \
  --input examples/data/test_db.xml \
  --output results/example2/converted.db
```

**Using MCP (in Claude Code):**
```
Use convert_database_format to convert @examples/data/test_db.xml to results/example2/converted.db
```

**Expected Output:**
- `converted.db`: Binary format database
- `database_analysis.txt`: Analysis report
- `transcript_details.csv`: Detailed transcript information

### Example 3: Reactivity Profile Analysis

**Goal:** Comprehensive analysis of SHAPE reactivity data with normalization

**Using Script:**
```bash
python scripts/reactivity_analysis.py \
  --input examples/data/query.txt \
  --output results/example3 \
  --normalize \
  --window-size 15
```

**Using MCP (in Claude Code):**
```
Run analyze_reactivity_profiles on @examples/data/query.txt with normalize True and window_size 15, save to results/example3/
```

**Expected Output:**
- `summary_statistics.csv`: Per-entry summary statistics
- `nucleotide_classifications.csv`: Per-nucleotide analysis and classifications
- `sliding_window_analysis.csv`: Sliding window statistics

### Example 4: Batch Processing

**Goal:** Process multiple query files at once

**Using Script:**
```bash
for f in examples/data/query*.txt; do
  python scripts/shape_search.py --query "$f" --database examples/data/test.db --output results/batch/
done
```

**Using MCP (in Claude Code):**
```
Submit submit_batch_shape_search with input_files [@examples/data/query.txt, @examples/data/query_align.txt, @examples/data/valid_query.txt] and database_file @examples/data/test.db
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `query.txt` | Main query sequence with SHAPE reactivity data | All tools |
| `query_align.txt` | Query sequence for alignment testing | Shape search |
| `valid_query.txt` | Minimal valid query for validation | All tools |
| `test.db` | Binary format database with reference sequences | Shape search |
| `test_db.xml` | XML format database with metadata | Database conversion |
| `query_*.txt` | Various test cases (invalid formats, edge cases) | Error testing |

### SHAPE Data Format

Query files follow SHAPEwarp's format:
```
sequence_id
RNA_SEQUENCE_STRING
reactivity1,reactivity2,reactivity3,...

```

Where:
- `sequence_id`: Unique identifier for the RNA sequence
- `RNA_SEQUENCE_STRING`: RNA nucleotide sequence (A, C, G, U)
- `reactivity values`: Comma-separated SHAPE reactivity measurements (float values, NaN for missing data)

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `default_config.json` | Shared default values | General settings, paths, validation |
| `shape_search_config.json` | Search parameters | max_reactivity (1.0), max_align_overlap (0.5), use_mock (true) |
| `database_conversion_config.json` | Conversion settings | output_format, analysis options |
| `reactivity_analysis_config.json` | Analysis parameters | normalize (false), window_size (10), thresholds |

### Config Example

```json
{
  "max_reactivity": 1.0,
  "max_align_overlap": 0.5,
  "use_mock": true,
  "output_format": "tsv"
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install fastmcp loguru pandas numpy tqdm
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp; print('Server loaded:', mcp.name)"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove SHAPEwarp
claude mcp add SHAPEwarp -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
from src.server import mcp
print('Available tools:', list(mcp.list_tools().keys()))
"
```

**Problem:** Path issues
```bash
# Use absolute paths in configuration
echo "Current directory: $(pwd)"
echo "Environment path: $(pwd)/env/bin/python"
echo "Server path: $(pwd)/src/server.py"
```

### Script Issues

**Problem:** Script execution fails
```bash
# Test script independently
mamba activate ./env
python scripts/shape_search.py --help
```

**Problem:** Missing data files
```bash
# Verify demo data exists
ls -la examples/data/
# Should show: query.txt, test.db, test_db.xml, etc.
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/
# View job contents if exists
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

### Performance Issues

**Problem:** Tools running slowly
- Current tools execute in <1 second with mock data
- For real Rust binary, install FFTW and compile SHAPEwarp:
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install libfftw3-dev
cd repo/SHAPEwarp
cargo build --release
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run integration tests
python tests/run_integration_tests.py

# Test individual scripts
python scripts/shape_search.py --query examples/data/query.txt --database examples/data/test.db
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py

# Test with MCP inspector
npx @anthropic/mcp-inspector src/server.py
```

### Mock vs Real Mode

All tools support mock mode for testing:
- **Mock Mode** (default): Uses generated data, runs instantly
- **Real Mode**: Requires compiled SHAPEwarp binary, provides actual analysis

---

## License

This project wraps the SHAPEwarp tool. Please refer to the original repository for licensing information.

## Credits

Based on [SHAPEwarp](https://github.com/Kobe-UT/SHAPEwarp) - A tool for finding RNA sequences with similar secondary structures using SHAPE reactivity profiles.

---

## Performance Notes

- **Python Scripts**: Fast startup (<1 second), good for API endpoints
- **Rust Binary**: High performance for large-scale searches (requires compilation)
- **Mock Mode**: Instant results for testing and development
- **Memory Usage**: Minimal (pandas/numpy only)
- **Scalability**: Submit API available for large datasets

## Quick Reference

```bash
# Essential commands
mamba activate ./env                    # Activate environment
claude mcp list                        # Check MCP status
python scripts/shape_search.py --help  # Script help
```

For detailed usage examples and troubleshooting, see the sections above.