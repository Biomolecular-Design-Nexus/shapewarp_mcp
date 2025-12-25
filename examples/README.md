# SHAPEwarp Examples and Demo Data

This directory contains use case scripts and demo data for the SHAPEwarp MCP server.

## Use Case Scripts

### 1. use_case_1_shape_search.py
**Purpose**: Search for structurally similar RNA sequences using SHAPE reactivity profiles

**Features**:
- Parse SHAPEwarp query and database files
- Perform similarity searches (with mock mode support)
- Generate search results with statistical significance
- Analyze and summarize search hits

**Usage**:
```bash
# Basic search with mock data
python use_case_1_shape_search.py --use-mock

# Search with custom parameters
python use_case_1_shape_search.py \
    --query data/query.txt \
    --database data/test.db \
    --output ../results/search \
    --max-reactivity 2.0 \
    --threads 4
```

### 2. use_case_2_database_conversion.py
**Purpose**: Convert between XML and binary database formats and analyze contents

**Features**:
- Parse XML database format with metadata
- Convert to native binary format (when SHAPEwarp binary available)
- Generate comprehensive database statistics
- Export detailed transcript information

**Usage**:
```bash
# Convert database format
python use_case_2_database_conversion.py \
    --input data/test_db.xml \
    --output ../results/converted.db

# Analyze database only
python use_case_2_database_conversion.py \
    --input data/test_db.xml \
    --analyze-only
```

### 3. use_case_3_reactivity_analysis.py
**Purpose**: Comprehensive analysis of SHAPE reactivity profiles

**Features**:
- Statistical analysis of reactivity data
- Nucleotide-level classification (high/medium/low reactivity)
- Sliding window analysis
- Identification of structured regions
- Reactivity profile visualization (when matplotlib available)

**Usage**:
```bash
# Basic analysis
python use_case_3_reactivity_analysis.py --input data/query.txt

# Full analysis with plots
python use_case_3_reactivity_analysis.py \
    --input data/query.txt \
    --output ../results/analysis \
    --normalize \
    --create-plots \
    --window-size 15
```

## Demo Data Files

### Core Data Files

#### `query.txt`
- **Purpose**: Sample query sequence for SHAPE similarity search
- **Format**: SHAPEwarp query format (ID, sequence, reactivities)
- **Content**: 16S rRNA fragment (100 nucleotides) with SHAPE reactivity measurements
- **Usage**: Primary test data for all use cases

#### `test.db`
- **Purpose**: Binary format database for similarity searches
- **Format**: SHAPEwarp native binary format
- **Content**: Reference RNA sequences with reactivity profiles
- **Usage**: Database target for similarity searches

#### `test_db.xml`
- **Purpose**: XML format database with full metadata
- **Format**: SHAPEwarp XML format
- **Content**: Same data as test.db but with organism, probe, and experimental metadata
- **Usage**: Database conversion and analysis examples

### Validation Data Files

#### `valid_query.txt`
- **Purpose**: Minimal valid query for format validation
- **Content**: Short valid sequence for testing parsers

#### `query_align.txt`
- **Purpose**: Query sequence with alignment gaps (NaN values)
- **Content**: Sequence with partial reactivity coverage
- **Usage**: Testing handling of missing data

### Error Case Files

#### `query_empty_sequence.txt`
- **Purpose**: Test case with empty sequence field
- **Usage**: Error handling validation

#### `query_invalid_base.txt`
- **Purpose**: Test case with invalid nucleotide characters
- **Usage**: Input validation testing

#### `query_invalid_lengths.txt`
- **Purpose**: Test case where sequence and reactivity lengths don't match
- **Usage**: Data integrity validation

#### `query_invalid_reactivity.txt`
- **Purpose**: Test case with invalid reactivity values
- **Usage**: Numeric parsing validation

#### `query_truncated_*.txt`
- **Purpose**: Test cases with incomplete data
- **Usage**: Robustness testing

## Data Format Specifications

### Query File Format
```
sequence_id
NUCLEOTIDE_SEQUENCE
reactivity1,reactivity2,reactivity3,...

```

**Example**:
```
16S_750
TGACGCTCAGGTGCGAAAGCGTGGGGAGCAAACAGGATTAGATACCCTGGTAGTCCACGCC
0.102,0.083,0.066,0.040,0.075,0.061,0.573,0.631,0.427,0.265

```

### XML Database Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<data combined="FALSE" maxmutrate="1" norm="Box-plot" ...>
    <meta-data>
        <organism>Saccharomyces cerevisiae</organism>
        <probe>2A3</probe>
        <condition>in vivo</condition>
    </meta-data>
    <transcript id="..." length="...">
        <sequence>NUCLEOTIDE_SEQUENCE</sequence>
        <reactivity>value1,value2,value3,...</reactivity>
    </transcript>
</data>
```

## Running Examples

### Prerequisites
```bash
# Activate the environment
mamba activate ../env

# Optional: Install visualization dependencies
pip install matplotlib seaborn
```

### Basic Workflow
```bash
# 1. Search for similar structures
python use_case_1_shape_search.py --use-mock --output ../results/search

# 2. Analyze database contents
python use_case_2_database_conversion.py --input data/test_db.xml --analyze-only

# 3. Analyze reactivity profiles
python use_case_3_reactivity_analysis.py --input data/query.txt --output ../results/analysis
```

### Advanced Usage
```bash
# Search with real SHAPEwarp binary (if compiled)
python use_case_1_shape_search.py \
    --query data/query.txt \
    --database data/test.db \
    --output ../results/search_real \
    --max-reactivity 2.0 \
    --max-align-overlap 0.3 \
    --threads 8

# Full reactivity analysis with visualization
python use_case_3_reactivity_analysis.py \
    --input data/query.txt \
    --output ../results/full_analysis \
    --normalize \
    --create-plots \
    --window-size 20 \
    --max-reactivity 3.0
```

## Output Examples

### Search Results (`search_results.tsv`)
```
query	db_entry	query_start	query_end	db_start	db_end	score	pvalue	evalue	status
16S_750	16S_Bsubtilis	0	99	758	857	109.103	5.665e-8	1.003e-5	!
```

### Analysis Summary (`summary_statistics.csv`)
```
entry_id,sequence_length,mean_reactivity,median_reactivity,coverage,structured_regions
16S_750,100,0.456,0.312,1.0,2
```

### Database Analysis Report
```
SHAPEwarp Database Analysis Report
====================================

Database Metadata:
  organism: Saccharomyces cerevisiae
  probe: 2A3
  condition: in vivo

Database Statistics:
  Total transcripts: 1
  Total nucleotides: 1800
  Mean sequence length: 1800.0 nt
  Total reactivity measurements: 1756
  Mean reactivity: 2.847
  Mean coverage: 0.976
```

## Error Handling

All scripts include comprehensive error handling for:
- Missing or invalid input files
- Malformed data formats
- Missing dependencies (Rust binary, plotting libraries)
- File permission issues
- Network/resource constraints

Scripts automatically fall back to mock mode when the SHAPEwarp binary is not available.

## Integration with MCP Server

These use case scripts serve as the foundation for MCP tools:
- Function signatures map to MCP tool parameters
- Output formats are standardized for API responses
- Error handling provides meaningful feedback for client applications
- Mock mode enables testing without external dependencies