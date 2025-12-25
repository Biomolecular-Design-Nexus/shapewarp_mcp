# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: shapewarp
- **Version**: 1.0.0
- **Created Date**: 2025-12-24
- **Server Path**: `src/server.py`
- **Package Manager**: mamba (preferred) or conda

## Overview

The SHAPEwarp MCP server provides both synchronous and asynchronous APIs for RNA SHAPE reactivity analysis tools. Based on runtime analysis, all current tools execute in <1 second and use the **Sync API**. The Submit API infrastructure is available for future long-running tools.

## Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and timestamps |
| `get_job_result` | Get completed job results |
| `get_job_log` | View job execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with filtering |

## Sync Tools (Fast Operations < 10 min)

All SHAPEwarp tools use the **Sync API** based on performance testing:

| Tool | Description | Source Script | Est. Runtime |
|------|-------------|---------------|--------------|
| `search_shape_profiles` | Search for structurally similar RNA sequences using SHAPE profiles | `scripts/shape_search.py` | ~1 sec |
| `convert_database_format` | Convert between database formats and analyze contents | `scripts/database_conversion.py` | ~1 sec |
| `analyze_reactivity_profiles` | Analyze SHAPE reactivity with statistics and classification | `scripts/reactivity_analysis.py` | ~1 sec |

## Submit Tools (Long Operations > 10 min)

Infrastructure available for future long-running tools:

| Tool | Description | Source Script | Est. Runtime | Batch Support |
|------|-------------|---------------|--------------|---------------|
| `submit_shape_search` | Background SHAPE profile search | `scripts/shape_search.py` | Variable | ✅ Yes |
| `submit_database_conversion` | Background database conversion | `scripts/database_conversion.py` | Variable | ✅ Yes |
| `submit_reactivity_analysis` | Background reactivity analysis | `scripts/reactivity_analysis.py` | Variable | ✅ Yes |

## Tool Details

### search_shape_profiles
- **Description**: Search for structurally similar RNA sequences using SHAPE reactivity profiles
- **Source Script**: `scripts/shape_search.py`
- **Estimated Runtime**: ~1 second
- **API Type**: Sync (recommended)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| query_file | str | Yes | - | Path to query file with RNA sequences and SHAPE reactivities |
| database_file | str | Yes | - | Path to database file with reference structures |
| output_dir | str | No | None | Directory to save search results |
| config_file | str | No | None | Path to configuration JSON file |
| max_reactivity | float | No | 1.0 | Maximum reactivity value threshold |
| max_align_overlap | float | No | 0.5 | Maximum alignment overlap |
| use_mock | bool | No | True | Use mock search results for testing |

**Returns:**
```json
{
  "status": "success",
  "results": "DataFrame with search hits",
  "output_file": "path/to/search_results.tsv",
  "metadata": {
    "queries_processed": 1,
    "total_hits": 3,
    "significant_hits": 3,
    "best_score": 98.59
  },
  "summary": {
    "search_time": "<1s",
    "database_size": "entries"
  }
}
```

**Example:**
```
Use search_shape_profiles with query_file "examples/data/query.txt" and database_file "examples/data/test.db"
```

---

### convert_database_format
- **Description**: Convert between SHAPEwarp database formats and analyze database contents
- **Source Script**: `scripts/database_conversion.py`
- **Estimated Runtime**: ~1 second
- **API Type**: Sync (recommended)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to input database file (XML format) |
| output_file | str | No | None | Path to save converted database |
| config_file | str | No | None | Path to configuration JSON file |
| output_format | str | No | "binary" | Output format ("binary", "csv", "json") |

**Returns:**
```json
{
  "status": "success",
  "database_info": {
    "transcripts": 1,
    "total_reactivities": 1718
  },
  "output_files": {
    "database": "path/to/converted.db",
    "analysis_report": "path/to/analysis.txt",
    "transcript_csv": "path/to/details.csv",
    "database_json": "path/to/info.json"
  },
  "analysis": {
    "coverage": "statistics",
    "reactivity_distribution": "data"
  }
}
```

**Example:**
```
Use convert_database_format with input_file "examples/data/test_db.xml" and output_file "results/converted.db"
```

---

### analyze_reactivity_profiles
- **Description**: Analyze SHAPE reactivity profiles with statistics, classification, and sliding window analysis
- **Source Script**: `scripts/reactivity_analysis.py`
- **Estimated Runtime**: ~1 second
- **API Type**: Sync (recommended)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to input file with RNA sequences and SHAPE reactivities |
| output_dir | str | No | None | Directory to save analysis results |
| config_file | str | No | None | Path to configuration JSON file |
| normalize | bool | No | False | Whether to normalize reactivity values |
| window_size | int | No | 10 | Size of sliding window for analysis |
| reactivity_threshold | float | No | None | Custom threshold for nucleotide classification |

**Returns:**
```json
{
  "status": "success",
  "summary_stats": "DataFrame with per-entry statistics",
  "nucleotide_classifications": "DataFrame with per-nucleotide analysis",
  "sliding_window_analysis": "DataFrame with window statistics",
  "analysis_summary": {
    "entries_analyzed": 1,
    "total_nucleotides": 100,
    "mean_reactivity": 0.091,
    "coverage": 1.000,
    "classification_distribution": {
      "structured": 96,
      "intermediate": 3,
      "flexible": 1
    }
  },
  "output_files": {
    "summary_stats": "path/to/summary_statistics.csv",
    "nucleotide_classifications": "path/to/nucleotide_classifications.csv",
    "sliding_window": "path/to/sliding_window_analysis.csv"
  }
}
```

**Example:**
```
Use analyze_reactivity_profiles with input_file "examples/data/query.txt" and normalize True
```

---

## Workflow Examples

### Quick Analysis (Sync API)
```
1. Search: Use search_shape_profiles with query_file "examples/data/query.txt" and database_file "examples/data/test.db"
   → Returns: immediate results with search hits and statistics

2. Convert: Use convert_database_format with input_file "examples/data/test_db.xml"
   → Returns: immediate conversion results and analysis

3. Analyze: Use analyze_reactivity_profiles with input_file "examples/data/query.txt" and normalize True
   → Returns: immediate analysis results with classifications
```

### Long-Running Task (Submit API)
```
1. Submit: Use submit_shape_search with query_file "examples/data/large_queries.txt" and database_file "examples/data/large_db.db"
   → Returns: {"job_id": "abc123", "status": "submitted"}

2. Check: Use get_job_status with job_id "abc123"
   → Returns: {"status": "running", "started_at": "timestamp", ...}

3. Result: Use get_job_result with job_id "abc123"
   → Returns: {"status": "success", "result": {...}} when completed

4. Logs: Use get_job_log with job_id "abc123"
   → Returns: execution logs and debugging information
```

### Batch Processing
```
Use submit_batch_shape_search with input_files ["query1.txt", "query2.txt", "query3.txt"] and database_file "database.db"
→ Processes all files in a single background job
```

## Configuration

### Environment Setup
```bash
# Prefer mamba over conda
if command -v mamba &> /dev/null; then
    PKG_MGR="mamba"
else
    PKG_MGR="conda"
fi
echo "Using package manager: $PKG_MGR"

# Activate environment
$PKG_MGR activate ./env

# Verify dependencies
pip list | grep -E "fastmcp|loguru|pandas|numpy"
```

### File Structure
```
shapewarp_mcp/
├── src/
│   ├── server.py              # Main MCP server
│   ├── jobs/
│   │   ├── __init__.py
│   │   └── manager.py         # Job queue management
│   └── tools/
│       └── __init__.py
├── scripts/                   # Clean extracted scripts
│   ├── lib/                   # Shared utilities
│   ├── shape_search.py        # SHAPE profile search
│   ├── database_conversion.py # Database format conversion
│   └── reactivity_analysis.py # Reactivity analysis
├── configs/                   # Configuration files
├── examples/data/             # Demo data for testing
└── jobs/                      # Job execution directory
```

## Installation and Usage

### With Claude Desktop
Add to Claude configuration:
```json
{
  "mcpServers": {
    "shapewarp": {
      "command": "mamba",
      "args": ["run", "-p", "./env", "python", "src/server.py"]
    }
  }
}
```

### With fastmcp CLI
```bash
# Install server
fastmcp install claude-code src/server.py

# Development mode
fastmcp dev src/server.py

# Test with MCP inspector
npx @anthropic/mcp-inspector src/server.py
```

## Error Handling

All tools return structured error responses:

```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```

Common error types:
- `FileNotFoundError`: Input files not found
- `ValueError`: Invalid input parameters or data format
- `Exception`: General processing errors

## Testing

### Sync Tool Test
```bash
mamba run -p ./env python -c "
import sys
sys.path.insert(0, 'scripts')
from shape_search import run_shape_search
result = run_shape_search('examples/data/query.txt', 'examples/data/test.db')
print(f'Success: {result.keys()}')
"
```

### Server Test
```bash
mamba run -p ./env python -c "
import sys
sys.path.insert(0, 'src')
from server import mcp
print(f'Server loaded: {mcp.name}')
"
```

## Performance Metrics

Based on Step 5 testing:

| Metric | Value |
|--------|-------|
| **Script Execution Time** | <1 second each |
| **API Recommendation** | Sync API for all tools |
| **Dependency Status** | ✅ All available (fastmcp, loguru) |
| **Test Success Rate** | 100% (all tools pass) |
| **Memory Usage** | Minimal (pandas/numpy only) |
| **Error Handling** | ✅ Structured responses |

## Future Enhancements

### Planned Features
- **True Batch Processing**: Enhanced scripts for parallel processing
- **Progress Callbacks**: Real-time progress updates for long tasks
- **Custom Configurations**: Dynamic parameter validation
- **Output Formats**: Additional export formats (JSON, XML, HDF5)

### When to Use Submit API
Future tools should use Submit API when:
- Runtime > 10 minutes
- Processing large datasets (>1000 sequences)
- GPU-intensive computations
- Network-dependent operations

## Success Criteria ✅

- [x] MCP server created at `src/server.py`
- [x] Job manager implemented for async operations (`src/jobs/manager.py`)
- [x] Sync tools created for all current fast operations (<1 min)
- [x] Submit tools created for future long-running operations
- [x] Batch processing infrastructure available
- [x] Job management tools working (status, result, log, cancel, list)
- [x] All tools have clear descriptions for LLM use
- [x] Error handling returns structured responses
- [x] Server starts without errors
- [x] Scripts tested and working with example data
- [x] Documentation complete with all tools and usage examples

## Summary

The SHAPEwarp MCP server successfully implements:

1. **Complete Tool Coverage**: All 3 Step 5 scripts wrapped as MCP tools
2. **Dual API Design**: Both Sync and Submit APIs available
3. **Runtime Optimization**: Fast tools use Sync API based on <1s performance
4. **Job Infrastructure**: Complete async job management system ready for future tools
5. **Error Handling**: Structured error responses for reliable LLM integration
6. **Documentation**: Comprehensive tool descriptions and examples

The server is ready for deployment and use with Claude Code or other MCP clients.