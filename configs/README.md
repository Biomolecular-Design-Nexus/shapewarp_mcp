# SHAPEwarp MCP Configuration Files

Configuration files for SHAPEwarp MCP scripts, extracted from original use case parameters.

## Configuration Files

| File | Script | Description |
|------|--------|-------------|
| `default_config.json` | All scripts | Default values shared across all scripts |
| `shape_search_config.json` | `shape_search.py` | Search algorithm parameters |
| `database_conversion_config.json` | `database_conversion.py` | Database conversion and analysis settings |
| `reactivity_analysis_config.json` | `reactivity_analysis.py` | Analysis and classification parameters |

## Configuration Structure

### default_config.json
Contains shared settings used across all scripts:

```json
{
  "general": {
    "use_mock": true,
    "verbose": false,
    "validate_inputs": true
  },
  "paths": {
    "models_dir": "models",
    "data_dir": "examples/data",
    "results_dir": "results"
  },
  "output": {
    "default_format": "csv",
    "include_metadata": true
  }
}
```

### shape_search_config.json
Search-specific parameters:

```json
{
  "search": {
    "max_reactivity": 1.0,
    "max_align_overlap": 0.5,
    "use_mock": true
  },
  "mock_settings": {
    "hits_per_query": 3,
    "significant_pvalue_threshold": 1e-5
  }
}
```

### database_conversion_config.json
Database conversion parameters:

```json
{
  "conversion": {
    "max_reactivity": 1.0,
    "output_format": "binary",
    "use_mock": true
  },
  "analysis": {
    "generate_reports": true,
    "include_global_stats": true
  }
}
```

### reactivity_analysis_config.json
Analysis parameters:

```json
{
  "processing": {
    "normalize": false,
    "max_reactivity": 10.0
  },
  "analysis": {
    "window_size": 15,
    "classification_thresholds": [0.3, 0.7]
  }
}
```

## Usage

### Command Line
```bash
# Use configuration file
python scripts/shape_search.py --config configs/shape_search_config.json --query FILE --database FILE

# Override specific parameters
python scripts/reactivity_analysis.py --config configs/reactivity_analysis_config.json --normalize --window-size 20
```

### Programmatic
```python
import json
from scripts.shape_search import run_shape_search

# Load configuration
with open('configs/shape_search_config.json') as f:
    config = json.load(f)

# Use with overrides
result = run_shape_search(
    query_file="query.txt",
    database_file="db.db",
    config=config,
    max_reactivity=2.0  # Override config value
)
```

## Parameter Descriptions

### Search Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_reactivity` | 1.0 | Maximum reactivity value for capping |
| `max_align_overlap` | 0.5 | Maximum alignment overlap fraction |
| `hits_per_query` | 3 | Number of mock hits to generate per query |
| `significant_pvalue_threshold` | 1e-5 | P-value threshold for significance |

### Database Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_format` | "binary" | Database output format |
| `generate_reports` | true | Generate analysis reports |
| `analyze_only` | false | Skip conversion, only analyze |

### Analysis Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `normalize` | false | Normalize reactivity values to [0,1] |
| `max_reactivity` | 10.0 | Maximum reactivity for outlier filtering |
| `window_size` | 15 | Sliding window size for analysis |
| `classification_thresholds` | [0.3, 0.7] | Thresholds for structured/flexible classification |

## Customization

Create custom configuration by copying and modifying existing files:

```bash
# Copy base configuration
cp configs/reactivity_analysis_config.json configs/my_analysis_config.json

# Edit values
{
  "processing": {
    "normalize": true,
    "max_reactivity": 5.0
  },
  "analysis": {
    "window_size": 20,
    "classification_thresholds": [0.2, 0.8]
  }
}

# Use custom config
python scripts/reactivity_analysis.py --config configs/my_analysis_config.json --input FILE
```

## For MCP Integration

Configuration files are designed for easy MCP tool integration:

```python
@mcp.tool()
def analyze_rna_reactivity(
    input_file: str,
    output_dir: str = None,
    config_name: str = "default",
    normalize: bool = None,
    window_size: int = None
):
    """Analyze RNA SHAPE reactivity profiles."""

    # Load configuration
    config_path = f"configs/reactivity_analysis_config.json"
    with open(config_path) as f:
        config = json.load(f)

    # Override with parameters
    overrides = {}
    if normalize is not None:
        overrides["normalize"] = normalize
    if window_size is not None:
        overrides["window_size"] = window_size

    return run_reactivity_analysis(input_file, output_dir, config, **overrides)
```