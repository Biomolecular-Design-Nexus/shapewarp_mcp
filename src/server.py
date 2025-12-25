#!/usr/bin/env python3
"""
SHAPEwarp MCP Server

Provides both synchronous and asynchronous (submit) APIs for all tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager

# Create MCP server
mcp = FastMCP("shapewarp")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def search_shape_profiles(
    query_file: str,
    database_file: str,
    output_dir: Optional[str] = None,
    config_file: Optional[str] = None,
    max_reactivity: Optional[float] = None,
    max_align_overlap: Optional[float] = None,
    use_mock: bool = True
) -> dict:
    """
    Search for structurally similar RNA sequences using SHAPE reactivity profiles.

    Fast operation suitable for single queries (typically <1 minute).
    For batch processing of multiple queries, use submit_shape_search.

    Args:
        query_file: Path to query file containing RNA sequences with SHAPE reactivities
        database_file: Path to database file with reference structures
        output_dir: Optional directory to save search results
        config_file: Optional path to configuration JSON file
        max_reactivity: Maximum reactivity value threshold (default: 1.0)
        max_align_overlap: Maximum alignment overlap (default: 0.5)
        use_mock: Use mock search results (default: True for testing)

    Returns:
        Dictionary with search results, statistics, and output file path

    Example:
        search_shape_profiles("examples/data/query.txt", "examples/data/test.db", "results/search")
    """
    from scripts.shape_search import run_shape_search

    try:
        kwargs = {}
        if max_reactivity is not None:
            kwargs["max_reactivity"] = max_reactivity
        if max_align_overlap is not None:
            kwargs["max_align_overlap"] = max_align_overlap
        kwargs["use_mock"] = use_mock

        result = run_shape_search(
            query_file=query_file,
            database_file=database_file,
            output_dir=output_dir,
            config=config_file,
            **kwargs
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def convert_database_format(
    input_file: str,
    output_file: Optional[str] = None,
    config_file: Optional[str] = None,
    output_format: str = "binary"
) -> dict:
    """
    Convert between SHAPEwarp database formats and analyze contents.

    Fast operation suitable for single databases (typically <1 minute).
    For batch processing of multiple databases, use submit_database_conversion.

    Args:
        input_file: Path to input database file (XML format)
        output_file: Optional path to save converted database
        config_file: Optional path to configuration JSON file
        output_format: Output format ("binary", "csv", "json")

    Returns:
        Dictionary with conversion results, analysis, and output files

    Example:
        convert_database_format("examples/data/test_db.xml", "results/converted.db")
    """
    from scripts.database_conversion import run_database_conversion

    try:
        kwargs = {"output_format": output_format}

        result = run_database_conversion(
            input_file=input_file,
            output_file=output_file,
            config=config_file,
            **kwargs
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def analyze_reactivity_profiles(
    input_file: str,
    output_dir: Optional[str] = None,
    config_file: Optional[str] = None,
    normalize: bool = False,
    window_size: int = 10,
    reactivity_threshold: Optional[float] = None
) -> dict:
    """
    Analyze SHAPE reactivity profiles with statistics, classification, and sliding window analysis.

    Fast operation suitable for single profiles (typically <1 minute).
    For batch processing of multiple profiles, use submit_reactivity_analysis.

    Args:
        input_file: Path to input file containing RNA sequences with SHAPE reactivities
        output_dir: Optional directory to save analysis results
        config_file: Optional path to configuration JSON file
        normalize: Whether to normalize reactivity values (default: False)
        window_size: Size of sliding window for analysis (default: 10)
        reactivity_threshold: Custom threshold for nucleotide classification

    Returns:
        Dictionary with analysis results, statistics, and output files

    Example:
        analyze_reactivity_profiles("examples/data/query.txt", "results/analysis", normalize=True)
    """
    from scripts.reactivity_analysis import run_reactivity_analysis

    try:
        kwargs = {
            "normalize": normalize,
            "window_size": window_size
        }
        if reactivity_threshold is not None:
            kwargs["reactivity_threshold"] = reactivity_threshold

        result = run_reactivity_analysis(
            input_file=input_file,
            output_dir=output_dir,
            config=config_file,
            **kwargs
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations > 10 min or batch processing)
# ==============================================================================

@mcp.tool()
def submit_shape_search(
    query_file: str,
    database_file: str,
    output_dir: Optional[str] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit SHAPE profile search for background processing.

    Use this for batch processing of multiple queries or when you need to
    run searches in the background. For single quick searches, use search_shape_profiles.

    Args:
        query_file: Path to query file containing RNA sequences with SHAPE reactivities
        database_file: Path to database file with reference structures
        output_dir: Directory to save outputs
        config_file: Optional path to configuration JSON file
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        submit_shape_search("examples/data/query.txt", "examples/data/test.db", "results/batch")
    """
    script_path = str(SCRIPTS_DIR / "shape_search.py")

    args = {
        "query": query_file,
        "database": database_file
    }
    if output_dir:
        args["output"] = output_dir
    if config_file:
        args["config"] = config_file

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"shape_search_{Path(query_file).stem}"
    )

@mcp.tool()
def submit_database_conversion(
    input_file: str,
    output_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit database conversion for background processing.

    Use this for large databases or when you need to run conversions in the background.
    For single quick conversions, use convert_database_format.

    Args:
        input_file: Path to input database file (XML format)
        output_file: Optional path to save converted database
        output_dir: Alternative directory to save outputs
        config_file: Optional path to configuration JSON file
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the conversion job

    Example:
        submit_database_conversion("examples/data/test_db.xml", "results/converted.db")
    """
    script_path = str(SCRIPTS_DIR / "database_conversion.py")

    args = {"input": input_file}
    if output_file:
        args["output"] = output_file
    elif output_dir:
        args["output"] = str(Path(output_dir) / "converted.db")
    if config_file:
        args["config"] = config_file

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"db_conversion_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_reactivity_analysis(
    input_file: str,
    output_dir: Optional[str] = None,
    config_file: Optional[str] = None,
    normalize: bool = False,
    window_size: int = 10,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit reactivity analysis for background processing.

    Use this for large datasets or when you need to run analysis in the background.
    For single quick analyses, use analyze_reactivity_profiles.

    Args:
        input_file: Path to input file containing RNA sequences with SHAPE reactivities
        output_dir: Directory to save outputs
        config_file: Optional path to configuration JSON file
        normalize: Whether to normalize reactivity values
        window_size: Size of sliding window for analysis
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the analysis job

    Example:
        submit_reactivity_analysis("examples/data/query.txt", "results/analysis")
    """
    script_path = str(SCRIPTS_DIR / "reactivity_analysis.py")

    args = {"input": input_file}
    if output_dir:
        args["output"] = output_dir
    if config_file:
        args["config"] = config_file
    if normalize:
        args["normalize"] = ""  # Boolean flag for CLI
    if window_size != 10:
        args["window-size"] = window_size

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"reactivity_analysis_{Path(input_file).stem}"
    )

# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_shape_search(
    input_files: List[str],
    database_file: str,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch SHAPE profile search for multiple query files.

    Processes multiple query files against the same database in a single job.
    Suitable for:
    - Processing many query sequences at once
    - Large-scale SHAPE profile searches
    - Parallel processing of independent queries

    Args:
        input_files: List of query file paths to process
        database_file: Path to database file with reference structures
        output_dir: Directory to save all outputs
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job

    Example:
        submit_batch_shape_search(["query1.txt", "query2.txt"], "database.db", "results/batch")
    """
    from scripts.shape_search import run_shape_search
    import json

    # Create a batch job that processes multiple files
    job_id = f"batch_search_{len(input_files)}_files"

    # For now, we'll process files sequentially in the background
    # In a production system, you might want parallel processing
    args = {
        "input_files": ",".join(input_files),  # Pass as comma-separated string
        "database": database_file,
        "batch_mode": "true"
    }
    if output_dir:
        args["output"] = output_dir

    # We would need to create a batch processing script for this
    # For now, let's submit the first file and note that batch processing would need enhancement
    script_path = str(SCRIPTS_DIR / "shape_search.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={"query": input_files[0], "database": database_file, "output": output_dir},
        job_name=job_name or f"batch_search_{len(input_files)}_files"
    )

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()