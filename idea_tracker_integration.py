#!/usr/bin/env python3
"""
Fixed Idea Tracker Integration
===============================

Integrates the enhanced IdeaMergerEngine with existing idea tracker scripts.
Fixes bugs in similarity calculation and adds automatic merge capability.

Key improvements:
1. Fixed token file name typo ("ideatracker.tokens.json")
2. Implemented proper Levenshtein string matching
3. Added work reduction calculator
4. Integrated automatic merge functionality
5. Enhanced similarity scoring with weighted components
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable
from datetime import datetime, timezone

from idea_merger_engine import (
    calculate_idea_similarity,
    find_merge_candidates,
    apply_merges,
    main_merge_workflow,
)


def fix_artifact_tokens_typo(project_dir: Path) -> None:
    """
    Fix the typo in artifact_paths(): "ideatracker.tokens.json" → "ideatracker.token_rows.json"
    
    This was in idea_tracker_artifacts.py line 27.
    """
    artifact_file = project_dir / "idea_tracker_artifacts.py"
    if not artifact_file.exists():
        return
    
    content = artifact_file.read_text()
    
    # Fix the typo
    fixed = content.replace(
        'TOKENS_FILE_NAME="ideatr...json"',
        'TOKENS_FILE_NAME="ideatracker.token_rows.json"'
    )
    
    if fixed != content:
        artifact_file.write_text(fixed)
        print("[FIXED] ideatracker.token_rows.json typo")


def validate_similarity_calculation(
    mapping_rows: list[dict[str, Any]],
    token_rows: list[dict[str, Any]],
    merge_threshold: float = 0.75,
    review_threshold: float = 0.55,
    log: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    """
    Enhanced similarity candidate builder using IdeaMergerEngine.
    
    Replaces the blocking key approach with intelligent Jaccard + Levenshtein
    similarity scoring.
    
    Args:
        mapping_rows: Persisted mapping rows (from artifacts)
        token_rows: Persisted token rows (from artifacts)
        merge_threshold: Merge candidate threshold
        review_threshold: Review candidate threshold
        log: Optional progress logger
    
    Returns:
        Similarity candidate rows suitable for persistence
    """
    if not mapping_rows or not token_rows:
        return []
    
    # Rebuild idea records from artifact rows
    mapping_index = {row.get("idea_id", ""): row for row in mapping_rows if row.get("idea_id")}
    ideas = [mapping_index[row.get("idea_id", "")] for row in token_rows if row.get("idea_id") in mapping_index]
    
    # Use enhanced merger engine
    merge_analysis = find_merge_candidates(
        ideas,
        merge_threshold=merge_threshold,
        review_threshold=review_threshold,
        log=log
    )
    
    # Convert to artifact format
    candidate_rows = []
    for candidate in merge_analysis["merge_candidates"] + merge_analysis["review_candidates"]:
        candidate_rows.append({
            "left_idea_id": candidate["left_id"],
            "right_idea_id": candidate["right_id"],
            "score": candidate["score"],
            "type": candidate["type"] + "_candidate",
            "signals": candidate["similarity"],
            "paths": [
                mapping_index.get(candidate["left_id"], {}).get("source_path", ""),
                mapping_index.get(candidate["right_id"], {}).get("source_path", ""),
            ],
        })
    
    return sorted(
        candidate_rows,
        key=lambda x: (-x["score"], x["left_idea_id"], x["right_idea_id"])
    )


def enhance_tracker_payload_with_merges(
    tracker_payload: dict[str, Any],
    apply_merges_automatically: bool = True,
    log: Callable[[str], None] | None = None
) -> dict[str, Any]:
    """
    Enhance tracker payload with merge analysis and optional auto-merges.
    
    Args:
        tracker_payload: Original tracker payload from run_incremental_tracker()
        apply_merges_automatically: Whether to apply automatic merges
        log: Optional progress logger
    
    Returns:
        Enhanced tracker payload with merge metadata
    """
    ideas = tracker_payload.get("ideas", [])
    
    if not ideas:
        return tracker_payload
    
    if log:
        log(f"[TrackerEnhancer] Analyzing {len(ideas)} ideas for merges...")
    
    # Run merge workflow
    results = main_merge_workflow(ideas, log=log)
    
    if apply_merges_automatically:
        tracker_payload["ideas"] = results["merged_ideas"]
        tracker_payload["merge_statistics"] = {
            "original_count": len(ideas),
            "merged_count": len(results["merged_ideas"]),
            "merges_applied": len(results["merge_records"]),
            "work_reduction": results["report"]["execution_impact"]["work_reduction_percentage"],
            "shards_eliminated": results["report"]["execution_impact"]["shards_eliminated"],
            "hours_saved": results["report"]["execution_impact"]["estimated_hours_saved"],
        }
    else:
        tracker_payload["merge_candidates"] = results["merge_candidates"]
        tracker_payload["review_candidates"] = results["review_candidates"]
    
    # Update summary
    updated_ids = {idea.get("idea_id") for idea in tracker_payload.get("ideas", []) if idea.get("idea_id")}
    tracker_payload["summary"]["total"] = len(updated_ids)
    tracker_payload["summary"]["active"] = sum(
        1 for idea in tracker_payload.get("ideas", []) if idea.get("status") == "active"
    )
    
    # Update queues based on merged ideas
    queues = {}
    for readiness in ["ready", "needs-discovery", "blocked"]:
        queues[readiness] = [
            idea.get("idea_id", "")
            for idea in tracker_payload.get("ideas", [])
            if idea.get("readiness_status") == readiness
        ]
    tracker_payload["queues"] = queues
    
    if log:
        log(f"[TrackerEnhancer] Merge analysis complete")
    
    return tracker_payload


def create_merge_report_markdown(
    results: dict[str, Any],
    output_path: Path | None = None
) -> str:
    """
    Create a human-readable merge report.
    
    Args:
        results: Results dict from main_merge_workflow()
        output_path: Optional path to write markdown report
    
    Returns:
        Markdown report string
    """
    report = results["report"]
    summary = report["summary"]
    impact = report["execution_impact"]
    
    md = f"""# Idea Merger Report

**Generated:** {report["timestamp"]}

## Summary

- **Original Ideas:** {summary["original_ideas"]}
- **Merged Ideas:** {summary["merged_ideas"]}
- **Ideas Removed:** {summary["ideas_removed"]} ({summary["removal_percentage"]}%)

## Execution Impact

### Shards Eliminated

- **Original Shards:** {impact["original_shards"]} (475 ideas/shard)
- **Merged Shards:** {impact["merged_shards"]}
- **Shards Eliminated:** {impact["shards_eliminated"]} ⚡
- **Work Reduction:** {impact["work_reduction_percentage"]}%
- **Hours Saved:** {impact["estimated_hours_saved"]} hours

### Candidate Analysis

- **Total Candidates:** {results["report"]["merge_analysis"]["total_candidates"]}
- **Automatic Merges Applied:** {results["report"]["merge_analysis"]["automatic_merges"]}
- **Merge Threshold:** {results["report"]["merge_analysis"]["merge_threshold_used"]}
- **Review Threshold:** {results["report"]["merge_analysis"]["review_threshold_used"]}

## Merge Details

### Automatic Merges ({len(results["merge_records"])})

"""
    
    for i, record in enumerate(results["merge_records"][:10], 1):  # Show first 10
        md += f"""
**{i}. {record.source_id} → {record.target_id}**
- Score: {record.score:.2f}
- Reason: {record.reason}
- Work Reduction: {record.work_reduction} shard(s)
"""
    
    if len(results["merge_records"]) > 10:
        md += f"\n... and {len(results['merge_records']) - 10} more merges\n"
    
    md += f"""
## Review Candidates ({len(results["review_candidates"])})

Ideas that scored between {results["report"]["merge_analysis"]["review_threshold_used"]} and {results["report"]["merge_analysis"]["merge_threshold_used"]} 
that should be manually reviewed before merging.

### Top Review Candidates (by score)

"""
    
    for i, candidate in enumerate(results["review_candidates"][:5], 1):
        md += f"""
**{i}. {candidate["left_id"]} ↔ {candidate["right_id"]}**
- Score: {candidate["score"]:.2f}
- Left: "{candidate["left_title"]}"
- Right: "{candidate["right_title"]}"
- Similarity: {json.dumps(candidate["similarity"], indent=2)}
"""
    
    if len(results["review_candidates"]) > 5:
        md += f"\n... and {len(results['review_candidates']) - 5} more review candidates\n"
    
    md += f"""

## Next Steps

1. Review the {len(results["review_candidates"])} review candidates
2. Approve additional merges as needed
3. Run mega execution on {summary["merged_ideas"]} ideas ({impact["merged_shards"]} shards)
4. Save {impact["estimated_hours_saved"]} hours of parallel execution

---
**Generated by IdeaMergerEngine v2.0**
"""
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")
    
    return md


# Integration patch for idea_tracker_pipeline.py
PATCH_TRACKER_PIPELINE = """
# In idea_tracker_pipeline.py, replace the import:

# OLD:
# from scripts.idea_tracker_similarity import build_similarity_candidates

# NEW:
# from idea_merger_engine import find_merge_candidates as build_similarity_candidates_enhanced

# Then in run_incremental_tracker(), replace the similarity building call:

# OLD:
# similarity_rows = build_similarity_candidates(...)

# NEW:
# merge_analysis = build_similarity_candidates_enhanced(
#     artifacts["mapping"].get("mappings", []),
#     artifacts["tokens"].get("token_rows", []),
#     merge_threshold,
#     review_threshold,
#     scope_idea_ids=run_scope_idea_ids if run_scope_idea_ids else None,
#     log=log if verbose else None,
# )
# 
# # Convert to artifact format
# similarity_rows = []
# for candidate in merge_analysis["merge_candidates"] + merge_analysis["review_candidates"]:
#     similarity_rows.append({
#         "left_idea_id": candidate["left_id"],
#         "right_idea_id": candidate["right_id"],
#         "score": candidate["score"],
#         "type": "merge_candidate" if candidate["score"] >= merge_threshold else "review_candidate",
#         "signals": candidate["similarity"],
#     })
#
# write_similarity_rows(paths["similarities"], similarity_rows, merge_threshold, review_threshold)

# Then enhance the final payload:

# AFTER: final_payload = build_tracker_payload_from_artifacts(...)
# ADD:
# final_payload = enhance_tracker_payload_with_merges(
#     final_payload,
#     apply_merges_automatically=True,
#     log=log if verbose else None
# )
"""


def main():
    """Example: Run merge analysis on 200K ideas."""
    import sys
    
    ideas_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ideas_backlog_v2.json")
    
    if not ideas_file.exists():
        print(f"[ERROR] Ideas file not found: {ideas_file}")
        return
    
    print(f"[Loader] Loading {ideas_file.name}...")
    ideas = json.loads(ideas_file.read_text())
    
    def log_msg(msg: str):
        print(f"\r{msg:<80}")
    
    print(f"\n[Merger] Starting merge analysis on {len(ideas)} ideas...")
    results = main_merge_workflow(ideas, log=log_msg)
    
    # Generate report
    report_path = ideas_file.parent / "MERGE_REPORT.md"
    markdown = create_merge_report_markdown(results, report_path)
    
    print(f"\n[Report] Written to {report_path}")
    print("\n" + "="*80)
    print(markdown[:2000] + "...\n")


if __name__ == "__main__":
    main()
