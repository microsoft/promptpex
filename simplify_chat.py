#!/usr/bin/env python3
"""
Copilot Chat Log Analysis and Simplification Tool

This script processes raw VS Code Copilot chat logs and extracts comprehensive analysis
including conversation flow, tool usage patterns, AI model performance metrics, and data
transfer statistics.

FUNCTIONALITY:
==============

1. CONVERSATION EXTRACTION:
   - Extracts user requests and assistant responses
   - Maintains conversation flow and context
   - Preserves request/response relationships

2. TOOL USAGE ANALYSIS:
   - Detailed tool call tracking with arguments and results
   - Success/failure status monitoring
   - MCP (Model Context Protocol) server categorization
   - Tool efficiency and usage pattern analysis

3. AI MODEL PERFORMANCE METRICS:
   - Response timing analysis (startup vs processing time)
   - Response pattern categorization (quick, moderate, slow startup)
   - Efficiency metrics and consistency scoring
   - Latency classification and performance distribution

4. DATA TRANSFER ANALYSIS:
   - Input/output data size tracking for each tool call
   - Per-tool data volume statistics
   - Data efficiency analysis (input/output ratios)
   - Largest data transfer identification

5. COMPREHENSIVE REPORTING:
   - Executive summary with key metrics
   - MCP server breakdown and tool categorization
   - Timing statistics and performance analysis
   - Data volume analysis and efficiency metrics

INPUT REQUIREMENTS:
==================

Input File Format: Raw VS Code Copilot chat log (JSON)
Expected Structure:
{
  "requesterUsername": "string",
  "responderUsername": "string", 
  "requests": [
    {
      "requestId": "string",
      "message": {"text": "string"},
      "response": [...],
      "result": {
        "timings": {"firstProgress": int, "totalElapsed": int},
        "metadata": {
          "toolCallRounds": [...],
          "toolCallResults": {...}
        }
      }
    }
  ]
}

OUTPUT FORMAT:
=============

Simplified JSON with enhanced analysis:
{
  "conversation_summary": {...},
  "messages": [...],
  "mcp_analysis": {
    "summary": {...},
    "timing_statistics": {...},
    "data_size_statistics": {...},
    "tool_usage_frequency": {...},
    "tools_by_mcp_server": {...}
  }
}

USAGE:
======

Command Line:
  python3 simplify_chat.py <input_chat_log.json> <output_simplified.json>

Programmatic:
  from simplify_chat import simplify_chat_log
  simplify_chat_log("input.json", "output.json")

DEPENDENCIES:
============
- json (built-in)
- collections.Counter, defaultdict (built-in)
- re (built-in)

AUTHORS: Enhanced for comprehensive chat log analysis
VERSION: 2.0 - Added AI performance metrics and data size analysis
"""

import json
import sys
import re
from collections import Counter, defaultdict

def extract_file_path(uri_or_message):
    """
    Extract file path from URI object or message text.
    
    Args:
        uri_or_message (dict|str): URI object with 'path' field or message string
        
    Returns:
        str|None: Extracted file path or None if no path found
        
    Examples:
        >>> extract_file_path({"path": "/home/user/file.py"})
        "/home/user/file.py"
        >>> extract_file_path("Reading file.py, lines 1-10")
        "file.py"
    """
    if isinstance(uri_or_message, dict) and "path" in uri_or_message:
        return uri_or_message["path"]
    elif isinstance(uri_or_message, str):
        # Try to extract file path from messages like "Reading file.py, lines 1-10"
        match = re.search(r'([/\w\-\.]+\.(py|js|ts|json|md|ipynb))', uri_or_message)
        if match:
            return match.group(1)
    return None

def truncate_string(s, max_length=100):
    """
    Truncate string to specified length, adding ellipsis if needed.
    
    Args:
        s (str): String to truncate
        max_length (int): Maximum length (default: 100)
        
    Returns:
        str: Truncated string with '...' suffix if truncated
        
    Examples:
        >>> truncate_string("This is a very long string", 10)
        "This is a..."
    """
    if not s or len(s) <= max_length:
        return s
    return s[:max_length] + "..."

def extract_detailed_tool_calls(request):
    """
    Extract comprehensive tool call information from a request.
    
    Analyzes VS Code Copilot request metadata to extract detailed information
    about tool calls including arguments, results, success status, and data sizes.
    
    Args:
        request (dict): VS Code Copilot request object containing:
            - result.metadata.toolCallRounds: Tool call execution rounds
            - result.metadata.toolCallResults: Results of tool calls
            - result.timings: Response timing information
            
    Returns:
        tuple: (tool_calls, timing_info) where:
            - tool_calls (list): List of detailed tool call dictionaries
            - timing_info (dict): Timing information with firstProgress, totalElapsed
            
    Tool Call Dictionary Structure:
        {
            "tool": str,                    # Tool name
            "arguments": dict,              # Tool arguments
            "file": str|None,              # Associated file path
            "result_summary": str,          # Human-readable result summary
            "success": bool|None,          # Success status
            "tool_id": str,                # Unique tool call ID
            "timing_ms": int|None,         # Individual timing (if available)
            "arguments_size_bytes": int,   # Size of arguments in bytes
            "result_size_bytes": int       # Size of result in bytes
        }
    """
    tool_calls = []
    
    # Get toolCallRounds from the correct location: request.result.metadata.toolCallRounds
    tool_rounds = []
    tool_results = {}
    timing_info = {}
    
    # Check the nested structure
    if "result" in request and isinstance(request["result"], dict):
        result = request["result"]
        if "metadata" in result and isinstance(result["metadata"], dict):
            metadata = result["metadata"]
            tool_rounds = metadata.get("toolCallRounds", [])
            tool_results = metadata.get("toolCallResults", {})
        
        # Extract timing information from the result
        if "timings" in result:
            timing_info = result["timings"]
    
    # Also check if toolCallRounds is directly in the request (fallback)
    if not tool_rounds:
        tool_rounds = request.get("toolCallRounds", [])
        tool_results = request.get("toolCallResults", {})
    
    for round_data in tool_rounds:
        round_tool_calls = round_data.get("toolCalls", [])
        for tool_call in round_tool_calls:
            tool_name = tool_call.get("name", "unknown")
            tool_id = tool_call.get("id", "")
            arguments_str = tool_call.get("arguments", "{}")
            
            # Parse arguments JSON
            try:
                arguments = json.loads(arguments_str)
            except:
                arguments = {"raw": arguments_str}
            
            # Get result if available
            result = None
            result_summary = None
            success = None
            if tool_id in tool_results:
                result_data = tool_results[tool_id]
                success = True  # If we have results, assume success
                # Try to extract meaningful result summary
                if isinstance(result_data, dict):
                    if "content" in result_data:
                        content = result_data["content"]
                        if isinstance(content, list) and len(content) > 0:
                            first_content = content[0]
                            if isinstance(first_content, dict) and "value" in first_content:
                                value = first_content["value"]
                                if isinstance(value, dict) and "node" in value:
                                    # This looks like a file content result
                                    result_summary = "File content returned"
                                elif isinstance(value, str):
                                    result_summary = truncate_string(value, 150)
                                else:
                                    result_summary = "Complex data structure returned"
                            else:
                                result_summary = "Content returned"
                    else:
                        result_summary = "Result data available"
                result = result_data  # Keep full result for detailed analysis if needed
            else:
                success = False
                result_summary = "No result available"
            
            # Extract file path from arguments
            file_path = None
            if isinstance(arguments, dict):
                file_path = arguments.get("filePath")
                if not file_path:
                    # Try other common file argument names
                    for key in ["file", "path", "uri"]:
                        if key in arguments:
                            file_path = arguments[key]
                            break
            
            # Calculate data sizes
            arguments_size = calculate_data_size(arguments)
            result_size = calculate_data_size(result)
            
            tool_call_detail = {
                "tool": tool_name,
                "arguments": arguments,
                "file": file_path,
                "result_summary": result_summary,
                "success": success,
                "tool_id": tool_id,
                "timing_ms": None,  # Individual tool timings not available in this data structure
                "arguments_size_bytes": arguments_size,
                "result_size_bytes": result_size
            }
            tool_calls.append(tool_call_detail)
    
    # Fallback: check response items for tool invocations (less detailed)
    if not tool_calls:
        for response in request.get("response", []):
            if isinstance(response, dict) and response.get("kind") == "toolInvocationSerialized":
                tool_id = response.get("toolId", "unknown")
                invocation_msg = response.get("invocationMessage", {})
                is_complete = response.get("isComplete", False)
                
                if isinstance(invocation_msg, dict):
                    msg_text = invocation_msg.get("value", "")
                else:
                    msg_text = str(invocation_msg)
                
                file_path = extract_file_path(msg_text)
                
                # Calculate data sizes for fallback case
                arguments = {"message": msg_text}
                arguments_size = calculate_data_size(arguments)
                result_size = 0  # No detailed result data available in fallback
                
                tool_call_detail = {
                    "tool": tool_id.replace("copilot_", ""),
                    "arguments": arguments,
                    "file": file_path,
                    "result_summary": "Success" if is_complete else "Failed/Unknown",
                    "success": is_complete,
                    "tool_id": response.get("toolCallId", ""),
                    "timing_ms": None,  # Individual tool timings not available in fallback
                    "arguments_size_bytes": arguments_size,
                    "result_size_bytes": result_size
                }
                tool_calls.append(tool_call_detail)
    
    # Return both tool calls and timing info
    return tool_calls, timing_info

def get_mcp_tool_definitions():
    """Return comprehensive MCP tool definitions and analysis"""
    return {
        "vscode_builtin": {
            "description": "Built-in VS Code functionality exposed through MCP interface",
            "tools": {
                "read_file": {
                    "purpose": "Read contents of files in the workspace",
                    "parameters": ["filePath", "startLine", "endLine"],
                    "category": "file_operations"
                },
                "replace_string_in_file": {
                    "purpose": "Edit existing files by replacing specific text content",
                    "parameters": ["filePath", "oldString", "newString"],
                    "category": "file_operations"
                },
                "run_in_terminal": {
                    "purpose": "Execute shell commands in the integrated terminal",
                    "parameters": ["command", "explanation", "isBackground"],
                    "category": "system_operations"
                },
                "file_search": {
                    "purpose": "Search for files by glob pattern",
                    "parameters": ["query", "maxResults"],
                    "category": "file_operations"
                },
                "grep_search": {
                    "purpose": "Search for text content within files",
                    "parameters": ["query", "isRegexp", "includePattern", "maxResults"],
                    "category": "file_operations"
                },
                "semantic_search": {
                    "purpose": "Semantic search across workspace content",
                    "parameters": ["query"],
                    "category": "file_operations"
                },
                "list_dir": {
                    "purpose": "List directory contents",
                    "parameters": ["path"],
                    "category": "file_operations"
                },
                "create_file": {
                    "purpose": "Create new files with specified content",
                    "parameters": ["filePath", "content"],
                    "category": "file_operations"
                }
            }
        },
        "jupyter_notebook_mcp": {
            "description": "Jupyter notebook integration for VS Code through MCP",
            "tools": {
                "copilot_getNotebookSummary": {
                    "purpose": "Get overview of notebook cells, their types, and execution status",
                    "parameters": ["filePath"],
                    "category": "notebook_operations"
                },
                "read_notebook_cell_output": {
                    "purpose": "Retrieve the output from specific notebook cells",
                    "parameters": ["filePath", "cellId"],
                    "category": "notebook_operations"
                },
                "run_notebook_cell": {
                    "purpose": "Execute code cells in Jupyter notebooks",
                    "parameters": ["filePath", "cellId", "reason"],
                    "category": "notebook_operations"
                },
                "edit_notebook_file": {
                    "purpose": "Edit notebook cells (insert, delete, or modify)",
                    "parameters": ["filePath", "editType", "cellId", "language", "newCode"],
                    "category": "notebook_operations"
                },
                "configure_notebook": {
                    "purpose": "Configure notebook environment and kernel",
                    "parameters": ["filePath"],
                    "category": "notebook_operations"
                }
            }
        },
        "python_environment_mcp": {
            "description": "Python environment management and package installation",
            "tools": {
                "configure_python_environment": {
                    "purpose": "Set up and configure Python environment",
                    "parameters": ["resourcePath"],
                    "category": "environment_operations"
                },
                "install_python_packages": {
                    "purpose": "Install Python packages in the environment",
                    "parameters": ["packageList", "resourcePath"],
                    "category": "environment_operations"
                },
                "get_python_environment_details": {
                    "purpose": "Get details about the current Python environment",
                    "parameters": ["resourcePath"],
                    "category": "environment_operations"
                },
                "get_python_executable_details": {
                    "purpose": "Get Python executable path and command details",
                    "parameters": ["resourcePath"],
                    "category": "environment_operations"
                }
            }
        },
        "task_management_mcp": {
            "description": "VS Code task management and execution",
            "tools": {
                "create_and_run_task": {
                    "purpose": "Create and run build/run tasks in VS Code",
                    "parameters": ["task", "workspaceFolder"],
                    "category": "task_operations"
                },
                "runTests": {
                    "purpose": "Run unit tests in the workspace",
                    "parameters": ["files", "testNames"],
                    "category": "task_operations"
                }
            }
        },
        "workspace_management_mcp": {
            "description": "Workspace and project management tools",
            "tools": {
                "create_new_workspace": {
                    "purpose": "Create new project workspace with full structure",
                    "parameters": ["query"],
                    "category": "workspace_operations"
                },
                "get_project_setup_info": {
                    "purpose": "Get project setup information",
                    "parameters": ["projectType"],
                    "category": "workspace_operations"
                }
            }
        },
        "azure_devops_mcp": {
            "description": "Azure DevOps (ADO) integration for work item management, pull requests, and project operations",
            "tools": {
                "ado_createWorkItem": {
                    "purpose": "Create a new work item (bug, task, user story, etc.) in Azure DevOps",
                    "parameters": ["project", "workItemType", "title", "description", "assignedTo", "tags"],
                    "category": "ado_work_items"
                },
                "ado_getWorkItem": {
                    "purpose": "Retrieve details of a specific work item by ID",
                    "parameters": ["workItemId", "project"],
                    "category": "ado_work_items"
                },
                "ado_updateWorkItem": {
                    "purpose": "Update an existing work item's fields and properties",
                    "parameters": ["workItemId", "updates", "project"],
                    "category": "ado_work_items"
                },
                "ado_queryWorkItems": {
                    "purpose": "Query work items using WIQL (Work Item Query Language)",
                    "parameters": ["query", "project"],
                    "category": "ado_work_items"
                },
                "ado_getWorkItemComments": {
                    "purpose": "Get comments and discussion from a work item",
                    "parameters": ["workItemId", "project"],
                    "category": "ado_work_items"
                },
                "ado_addWorkItemComment": {
                    "purpose": "Add a comment to an existing work item",
                    "parameters": ["workItemId", "comment", "project"],
                    "category": "ado_work_items"
                },
                "ado_createPullRequest": {
                    "purpose": "Create a new pull request in Azure DevOps repository",
                    "parameters": ["repository", "sourceBranch", "targetBranch", "title", "description", "reviewers"],
                    "category": "ado_pull_requests"
                },
                "ado_getPullRequest": {
                    "purpose": "Get details of a specific pull request",
                    "parameters": ["pullRequestId", "repository", "project"],
                    "category": "ado_pull_requests"
                },
                "ado_updatePullRequest": {
                    "purpose": "Update pull request properties (title, description, reviewers, etc.)",
                    "parameters": ["pullRequestId", "updates", "repository", "project"],
                    "category": "ado_pull_requests"
                },
                "ado_getPullRequestComments": {
                    "purpose": "Get comments and threads from a pull request",
                    "parameters": ["pullRequestId", "repository", "project"],
                    "category": "ado_pull_requests"
                },
                "ado_addPullRequestComment": {
                    "purpose": "Add a comment or review to a pull request",
                    "parameters": ["pullRequestId", "comment", "repository", "project"],
                    "category": "ado_pull_requests"
                },
                "ado_completePullRequest": {
                    "purpose": "Complete (merge) a pull request",
                    "parameters": ["pullRequestId", "repository", "project", "deleteSourceBranch"],
                    "category": "ado_pull_requests"
                },
                "ado_getRepositories": {
                    "purpose": "List repositories in an Azure DevOps project",
                    "parameters": ["project"],
                    "category": "ado_repositories"
                },
                "ado_getRepository": {
                    "purpose": "Get details of a specific repository",
                    "parameters": ["repository", "project"],
                    "category": "ado_repositories"
                },
                "ado_getBranches": {
                    "purpose": "List branches in a repository",
                    "parameters": ["repository", "project"],
                    "category": "ado_repositories"
                },
                "ado_createBranch": {
                    "purpose": "Create a new branch in a repository",
                    "parameters": ["repository", "branchName", "sourceBranch", "project"],
                    "category": "ado_repositories"
                },
                "ado_getCommits": {
                    "purpose": "Get commit history for a repository or branch",
                    "parameters": ["repository", "branch", "project", "limit"],
                    "category": "ado_repositories"
                },
                "ado_getProjects": {
                    "purpose": "List available Azure DevOps projects",
                    "parameters": ["organization"],
                    "category": "ado_organization"
                },
                "ado_getProject": {
                    "purpose": "Get details of a specific project",
                    "parameters": ["project"],
                    "category": "ado_organization"
                },
                "ado_getTeams": {
                    "purpose": "List teams in a project",
                    "parameters": ["project"],
                    "category": "ado_organization"
                },
                "ado_getTeamMembers": {
                    "purpose": "Get members of a specific team",
                    "parameters": ["team", "project"],
                    "category": "ado_organization"
                },
                "ado_getIterations": {
                    "purpose": "Get sprint/iteration information for a team",
                    "parameters": ["team", "project"],
                    "category": "ado_planning"
                },
                "ado_getCurrentIteration": {
                    "purpose": "Get current active sprint/iteration for a team",
                    "parameters": ["team", "project"],
                    "category": "ado_planning"
                },
                "ado_getCapacity": {
                    "purpose": "Get team capacity for a specific iteration",
                    "parameters": ["team", "iteration", "project"],
                    "category": "ado_planning"
                },
                "ado_getBuildDefinitions": {
                    "purpose": "List build definitions in a project",
                    "parameters": ["project"],
                    "category": "ado_builds"
                },
                "ado_getBuild": {
                    "purpose": "Get details of a specific build",
                    "parameters": ["buildId", "project"],
                    "category": "ado_builds"
                },
                "ado_queueBuild": {
                    "purpose": "Queue a new build",
                    "parameters": ["buildDefinitionId", "branch", "project"],
                    "category": "ado_builds"
                },
                "ado_getReleaseDefinitions": {
                    "purpose": "List release definitions in a project",
                    "parameters": ["project"],
                    "category": "ado_releases"
                },
                "ado_getRelease": {
                    "purpose": "Get details of a specific release",
                    "parameters": ["releaseId", "project"],
                    "category": "ado_releases"
                },
                "ado_createRelease": {
                    "purpose": "Create a new release",
                    "parameters": ["releaseDefinitionId", "artifacts", "project"],
                    "category": "ado_releases"
                }
            }
        }
    }

def classify_latency(avg_total_ms):
    """Classify response latency into categories"""
    if avg_total_ms < 10000:  # < 10 seconds
        return "very_fast"
    elif avg_total_ms < 30000:  # < 30 seconds
        return "fast" 
    elif avg_total_ms < 60000:  # < 1 minute
        return "moderate"
    elif avg_total_ms < 120000:  # < 2 minutes
        return "slow"
    else:
        return "very_slow"

def calculate_data_size(data):
    """
    Calculate size in bytes of data (parameters or response).
    
    Converts data to JSON string and calculates UTF-8 byte size.
    Handles non-serializable data by converting to string.
    
    Args:
        data (any): Data to measure (dict, list, str, etc.)
        
    Returns:
        int: Size in bytes
        
    Examples:
        >>> calculate_data_size({"key": "value"})
        17
        >>> calculate_data_size("hello world")
        13
    """
    if data is None:
        return 0
    
    import json
    try:
        # Convert to JSON string to get byte size
        json_str = json.dumps(data, ensure_ascii=False)
        return len(json_str.encode('utf-8'))
    except (TypeError, ValueError):
        # If it can't be serialized to JSON, convert to string
        return len(str(data).encode('utf-8'))

def calculate_consistency_score(times):
    """Calculate consistency score (1 = very consistent, 0 = very inconsistent)"""
    if len(times) <= 1:
        return 1.0
    
    mean_time = sum(times) / len(times)
    if mean_time == 0:
        return 1.0
    
    # Calculate standard deviation manually
    variance = sum((t - mean_time) ** 2 for t in times) / len(times)
    std_dev = variance ** 0.5
    
    # Coefficient of variation, inverted and capped
    cv = std_dev / mean_time
    consistency = max(0, 1 - cv)
    return min(1, consistency)

def analyze_mcp_usage(detailed_tool_calls, timing_data):
    """Analyze MCP tool usage patterns from detailed tool calls"""
    tool_definitions = get_mcp_tool_definitions()
    
    # Count tool usage
    tool_usage = Counter()
    mcp_server_usage = Counter()
    category_usage = Counter()
    tools_by_server = defaultdict(list)
    success_stats = {"total": 0, "successful": 0, "failed": 0, "unknown": 0}
    
    # Enhanced timing analysis with AI model execution metrics
    timing_stats = {
        "request_timings": [],
        "total_conversations": len(timing_data),
        "avg_first_progress_ms": 0,
        "avg_total_elapsed_ms": 0,
        "avg_thinking_time_ms": 0,
        "min_total_elapsed_ms": float('inf'),
        "max_total_elapsed_ms": 0,
        "min_first_progress_ms": float('inf'),
        "max_first_progress_ms": 0,
        "min_thinking_time_ms": float('inf'),
        "max_thinking_time_ms": 0,
        "ai_model_analysis": {
            "response_patterns": [],
            "efficiency_metrics": {},
            "timing_breakdown": {}
        }
    }
    
    first_progress_times = []
    total_elapsed_times = []
    thinking_times = []  # Time between first progress and completion
    
    # Analyze request-level timing with AI model focus
    for i, timing_info in enumerate(timing_data):
        if timing_info:
            first_progress = timing_info.get("firstProgress", 0)
            total_elapsed = timing_info.get("totalElapsed", 0)
            
            # Calculate AI model "thinking time" (generation time after first response)
            thinking_time = max(0, total_elapsed - first_progress)
            
            timing_entry = {
                "first_progress_ms": first_progress,
                "total_elapsed_ms": total_elapsed,
                "thinking_time_ms": thinking_time,
                "first_progress_ratio": (first_progress / total_elapsed) if total_elapsed > 0 else 0
            }
            
            timing_stats["request_timings"].append(timing_entry)
            first_progress_times.append(first_progress)
            total_elapsed_times.append(total_elapsed)
            thinking_times.append(thinking_time)
            
            # Categorize response patterns for AI analysis
            pattern = "unknown"
            if first_progress < 5000:  # < 5 seconds
                if thinking_time < 10000:  # < 10 seconds additional
                    pattern = "quick_response"
                else:
                    pattern = "quick_start_long_processing"
            elif first_progress < 15000:  # < 15 seconds
                pattern = "moderate_startup"
            else:
                pattern = "slow_startup"
            
            timing_stats["ai_model_analysis"]["response_patterns"].append({
                "conversation": i + 1,
                "pattern": pattern,
                "startup_time_ms": first_progress,
                "processing_time_ms": thinking_time,
                "total_time_ms": total_elapsed
            })
            
            if total_elapsed > 0:
                timing_stats["min_total_elapsed_ms"] = min(timing_stats["min_total_elapsed_ms"], total_elapsed)
                timing_stats["max_total_elapsed_ms"] = max(timing_stats["max_total_elapsed_ms"], total_elapsed)
            if first_progress > 0:
                timing_stats["min_first_progress_ms"] = min(timing_stats["min_first_progress_ms"], first_progress)
                timing_stats["max_first_progress_ms"] = max(timing_stats["max_first_progress_ms"], first_progress)
            if thinking_time > 0:
                timing_stats["min_thinking_time_ms"] = min(timing_stats["min_thinking_time_ms"], thinking_time)
                timing_stats["max_thinking_time_ms"] = max(timing_stats["max_thinking_time_ms"], thinking_time)
    
    # Calculate enhanced statistics
    if timing_stats["request_timings"]:
        timing_stats["avg_first_progress_ms"] = sum(first_progress_times) / len(first_progress_times)
        timing_stats["avg_total_elapsed_ms"] = sum(total_elapsed_times) / len(total_elapsed_times)
        timing_stats["avg_thinking_time_ms"] = sum(thinking_times) / len(thinking_times)
        
        # AI Model Performance Analysis
        ai_analysis = timing_stats["ai_model_analysis"]
        avg_first = timing_stats["avg_first_progress_ms"]
        avg_thinking = timing_stats["avg_thinking_time_ms"]
        avg_total = timing_stats["avg_total_elapsed_ms"]
        
        # Efficiency metrics
        ai_analysis["efficiency_metrics"] = {
            "startup_efficiency": (avg_first / avg_total) if avg_total > 0 else 0,
            "processing_efficiency": (avg_thinking / avg_total) if avg_total > 0 else 0,
            "consistency_score": calculate_consistency_score(total_elapsed_times),
            "response_latency_category": classify_latency(avg_total)
        }
        
        # Timing breakdown analysis
        ai_analysis["timing_breakdown"] = {
            "average_breakdown": {
                "startup_percent": (avg_first / avg_total * 100) if avg_total > 0 else 0,
                "processing_percent": (avg_thinking / avg_total * 100) if avg_total > 0 else 0
            },
            "timing_distribution": {
                "fast_responses": len([t for t in total_elapsed_times if t < 30000]),  # < 30s
                "moderate_responses": len([t for t in total_elapsed_times if 30000 <= t <= 60000]),  # 30-60s
                "slow_responses": len([t for t in total_elapsed_times if t > 60000])  # > 60s
            }
        }
    
    
    # Count tool usage and data sizes
    tool_usage = Counter()
    mcp_server_usage = Counter()
    category_usage = Counter()
    tools_by_server = defaultdict(list)
    success_stats = {"total": 0, "successful": 0, "failed": 0, "unknown": 0}
    
    # Data size statistics
    data_size_stats = {
        "total_arguments_bytes": 0,
        "total_result_bytes": 0,
        "tool_data_sizes": defaultdict(lambda: {"arguments_bytes": 0, "result_bytes": 0, "count": 0}),
        "largest_argument": {"tool": "unknown", "size_bytes": 0, "details": ""},
        "largest_result": {"tool": "unknown", "size_bytes": 0, "details": ""}
    }
    
    for tool_call in detailed_tool_calls:
        tool_name = tool_call.get("tool", "unknown")
        tool_usage[tool_name] += 1
        
        # Track data sizes
        arg_size = tool_call.get("arguments_size_bytes", 0)
        result_size = tool_call.get("result_size_bytes", 0)
        
        data_size_stats["total_arguments_bytes"] += arg_size
        data_size_stats["total_result_bytes"] += result_size
        data_size_stats["tool_data_sizes"][tool_name]["arguments_bytes"] += arg_size
        data_size_stats["tool_data_sizes"][tool_name]["result_bytes"] += result_size
        data_size_stats["tool_data_sizes"][tool_name]["count"] += 1
        
        # Track largest argument and result
        if arg_size > data_size_stats["largest_argument"]["size_bytes"]:
            data_size_stats["largest_argument"] = {
                "tool": tool_name,
                "size_bytes": arg_size,
                "details": truncate_string(str(tool_call.get("arguments", {})), 100)
            }
        
        if result_size > data_size_stats["largest_result"]["size_bytes"]:
            data_size_stats["largest_result"] = {
                "tool": tool_name,
                "size_bytes": result_size,
                "details": truncate_string(tool_call.get("result_summary", ""), 100)
            }
        
        # Track success statistics
        success_stats["total"] += 1
        success = tool_call.get("success")
        if success is True:
            success_stats["successful"] += 1
        elif success is False:
            success_stats["failed"] += 1
        else:
            success_stats["unknown"] += 1
        
        # Find which MCP server this tool belongs to
        found_server = None
        found_tool_info = None
        
        for server_name, server_info in tool_definitions.items():
            if tool_name in server_info["tools"]:
                found_server = server_name
                found_tool_info = server_info["tools"][tool_name]
                mcp_server_usage[server_name] += 1
                category_usage[found_tool_info["category"]] += 1
                tools_by_server[server_name].append({
                    "name": tool_name,
                    "usage_count": tool_usage[tool_name],
                    "purpose": found_tool_info["purpose"],
                    "category": found_tool_info["category"],
                    "success": success
                })
                break
        
        if not found_server:
            # Handle unknown tools
            mcp_server_usage["unknown"] += 1
            category_usage["unknown"] += 1
            tools_by_server["unknown"].append({
                "name": tool_name,
                "usage_count": tool_usage[tool_name],
                "purpose": "Unknown tool - not in MCP definitions",
                "category": "unknown",
                "success": success
            })
    
    # Remove duplicates and aggregate success info
    for server_name in tools_by_server:
        unique_tools = {}
        for tool in tools_by_server[server_name]:
            tool_name = tool["name"]
            if tool_name not in unique_tools:
                unique_tools[tool_name] = {
                    "name": tool_name,
                    "usage_count": tool_usage[tool_name],
                    "purpose": tool["purpose"],
                    "category": tool["category"],
                    "success_count": 0,
                    "failure_count": 0,
                    "unknown_count": 0
                }
            
            # Count success/failure for this tool
            if tool["success"] is True:
                unique_tools[tool_name]["success_count"] += 1
            elif tool["success"] is False:
                unique_tools[tool_name]["failure_count"] += 1
            else:
                unique_tools[tool_name]["unknown_count"] += 1
        
        tools_by_server[server_name] = list(unique_tools.values())
    
    # Calculate success rate
    success_rate = (success_stats["successful"] / success_stats["total"] * 100) if success_stats["total"] > 0 else 0
    
    return {
        "summary": {
            "total_tool_calls": len(detailed_tool_calls),
            "unique_tools_used": len(tool_usage),
            "mcp_servers_used": len([s for s in mcp_server_usage if s != "unknown"]),
            "unknown_tools": mcp_server_usage.get("unknown", 0),
            "success_rate_percent": round(success_rate, 1)
        },
        "success_statistics": success_stats,
        "timing_statistics": timing_stats,
        "data_size_statistics": data_size_stats,
        "tool_usage_frequency": dict(tool_usage.most_common()),
        "mcp_server_usage": dict(mcp_server_usage),
        "category_usage": dict(category_usage),
        "tools_by_mcp_server": dict(tools_by_server),
        "tool_definitions": tool_definitions
    }

def simplify_chat_log(input_file, output_file):
    """
    Extract and simplify Copilot chat log with comprehensive analysis.
    
    Main function that processes raw VS Code Copilot chat logs and generates
    simplified JSON with enhanced analysis including conversation flow, tool usage
    patterns, AI performance metrics, and data transfer statistics.
    
    Args:
        input_file (str): Path to raw VS Code Copilot chat log (JSON format)
        output_file (str): Path for output simplified JSON file
        
    Input File Requirements:
        - Valid JSON file from VS Code Copilot chat export
        - Must contain 'requests' array with conversation data
        - Each request should have message, response, and result metadata
        
    Output File Structure:
        {
            "conversation_summary": {
                "requester": str,           # Username of person making requests
                "responder": str,           # Assistant name (GitHub Copilot)
                "total_requests": int       # Number of conversations
            },
            "messages": [                   # Simplified conversation flow
                {
                    "request_id": int,
                    "user": str,            # User's request text
                    "assistant": [str],     # Assistant responses
                    "tools_used": [...],    # Summary of tools used
                    "detailed_tool_calls": [...] # Detailed tool call analysis
                }
            ],
            "mcp_analysis": {               # Comprehensive analysis
                "summary": {...},           # Executive summary statistics
                "timing_statistics": {...}, # AI performance metrics
                "data_size_statistics": {...}, # Data transfer analysis
                "tool_usage_frequency": {...}, # Tool usage patterns
                "tools_by_mcp_server": {...}   # MCP server breakdown
            }
        }
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input file is not valid JSON
        KeyError: If required fields are missing from input
        
    Example:
        >>> simplify_chat_log("raw_chat.json", "simplified.json")
        # Creates simplified.json with comprehensive analysis
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all detailed tool calls for analysis
    all_detailed_tool_calls = []
    all_timing_data = []
    
    simplified = {
        "conversation_summary": {
            "requester": data.get("requesterUsername", "Unknown"),
            "responder": data.get("responderUsername", "Unknown"),
            "total_requests": len(data.get("requests", []))
        },
        "messages": []
    }
    
    for i, request in enumerate(data.get("requests", [])):
        # Extract user message
        user_msg = request.get("message", {}).get("text", "")
        
        # Extract assistant responses
        assistant_responses = []
        for response in request.get("response", []):
            if isinstance(response, dict) and "value" in response:
                text = response["value"].strip()
                if text and not text.startswith("{") and len(text) > 10:
                    assistant_responses.append(text)
        
        # Extract detailed tool calls - check both locations
        detailed_tool_calls, timing_info = extract_detailed_tool_calls(request)
        
        # Add to the global collections for analysis
        all_detailed_tool_calls.extend(detailed_tool_calls)
        all_timing_data.append(timing_info)
        
        # If no detailed tool calls found in the main request, check if there's a nested structure
        if not detailed_tool_calls:
            # Sometimes toolCallRounds might be nested deeper
            for response in request.get("response", []):
                if isinstance(response, dict) and "toolCallRounds" in response:
                    temp_request = {"toolCallRounds": response["toolCallRounds"], "toolCallResults": response.get("toolCallResults", {})}
                    nested_calls, nested_timing = extract_detailed_tool_calls(temp_request)
                    detailed_tool_calls.extend(nested_calls)
                    if nested_timing and not timing_info:  # Only use if we don't have timing already
                        timing_info = nested_timing
        
        # Create summary for backward compatibility
        tool_summary = []
        if detailed_tool_calls:
            tool_groups = {}
            for tool in detailed_tool_calls:
                tool_name = tool["tool"]
                if tool_name not in tool_groups:
                    tool_groups[tool_name] = []
                tool_groups[tool_name].append(tool)
            
            for tool_name, calls in tool_groups.items():
                files_touched = [call["file"] for call in calls if call.get("file")]
                files_touched = list(set(filter(None, files_touched)))
                
                summary_item = {
                    "tool": tool_name,
                    "count": len(calls),
                    "files": files_touched[:5],
                    "sample_action": str(calls[0].get("arguments", {}))[:100] if calls[0].get("arguments") else ""
                }
                tool_summary.append(summary_item)
        
        # Add to simplified structure
        message_pair = {
            "request_id": i + 1,
            "user": user_msg,
            "assistant": assistant_responses,
            "tools_used": tool_summary,
            "detailed_tool_calls": detailed_tool_calls
        }
        
        simplified["messages"].append(message_pair)
    
    # Add MCP tool analysis to the simplified output
    mcp_analysis = analyze_mcp_usage(all_detailed_tool_calls, all_timing_data)
    simplified["mcp_analysis"] = mcp_analysis
    
    # Write simplified version
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, indent=2, ensure_ascii=False)
    
    # Calculate statistics
    total_tools = len(all_detailed_tool_calls)
    unique_tools = set()
    for tool_call in all_detailed_tool_calls:
        unique_tools.add(tool_call.get("tool", "unknown"))
    
    print(f"Simplified chat log created: {output_file}")
    print(f"Original size: {len(open(input_file).read())} characters")
    print(f"Simplified size: {len(open(output_file).read())} characters")
    print(f"Tool calls found: {total_tools} total, {len(unique_tools)} unique tools")
    if unique_tools:
        print(f"Tools used: {', '.join(sorted(unique_tools))}")
    print(f"MCP analysis included with {len(mcp_analysis['tools_by_mcp_server'])} MCP servers identified")
    
    # Print timing summary
    timing_stats = mcp_analysis.get("timing_statistics", {})
    if timing_stats.get("total_conversations", 0) > 0:
        avg_time = timing_stats.get("avg_total_elapsed_ms", 0)
        min_time = timing_stats.get("min_total_elapsed_ms", 0)
        max_time = timing_stats.get("max_total_elapsed_ms", 0)
        print(f"Timing analysis: {timing_stats['total_conversations']} requests, avg {avg_time:.0f}ms, range {min_time}-{max_time}ms")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 simplify_chat.py <input_file> <output_file>")
        sys.exit(1)
    
    simplify_chat_log(sys.argv[1], sys.argv[2])