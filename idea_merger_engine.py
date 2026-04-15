#!/usr/bin/env python3
"""
Enhanced Idea Merger Engine
============================

Intelligent deduplication and merging system for 200K+ ideas.
Reduces execution workload by automatically merging similar ideas
while preserving important distinctions.

Key features:
- Multi-stage similarity analysis (title, references, tokens)
- Configurable merge thresholds (0.7 = merge, 0.5 = review)
- Automatic parent-child relationship detection
- Merge conflict resolution with audit trail
- Work reduction calculator
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class IdeaMergeRecord:
    """Records a merge operation."""
    source_id: str
    target_id: str
    reason: str
    score: float
    timestamp: str
    merged_fields: dict[str, Any]
    work_reduction: float


@dataclass
class SimilarityScore:
    """Quantifies similarity between two ideas."""
    overall_score: float
    title_similarity: float
    category_similarity: float
    reference_similarity: float
    token_similarity: float
    components: dict[str, float]


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words, filtered for noise."""
    if not text:
        return set()
    
    # Remove common noise words
    noise_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "is", "are", "was", "be", "been", "have", "has", "do", "does",
        "did", "will", "would", "could", "should", "may", "might", "can",
        "by", "with", "this", "that", "these", "those", "i", "you", "he",
        "she", "it", "we", "they", "what", "which", "who", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more", "most",
        "some", "such", "no", "nor", "not", "only", "own", "so", "than",
        "too", "very", "just", "as", "if", "because", "as", "until", "while"
    }
    
    tokens = text.lower().split()
    return {
        token.strip(".,;:!?\"'()[]{}") 
        for token in tokens 
        if token.strip(".,;:!?\"'()[]{}") and token.lower() not in noise_words
    }


def _levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculate string similarity using Levenshtein distance."""
    if not s1 or not s2:
        return 0.0
    
    # Cache for dynamic programming
    rows = len(s1) + 1
    cols = len(s2) + 1
    
    if rows > 100 or cols > 100:  # Avoid massive computation
        return 0.0
    
    dp = [[0] * cols for _ in range(rows)]
    
    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j
    
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
    
    distance = dp[-1][-1]
    max_len = max(len(s1), len(s2))
    return 1.0 - (distance / max_len)


def _jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    
    union = set1 | set2
    if not union:
        return 0.0
    
    return len(set1 & set2) / len(union)


def calculate_idea_similarity(
    left_idea: dict[str, Any],
    right_idea: dict[str, Any],
    weights: dict[str, float] | None = None
) -> SimilarityScore:
    """
    Calculate comprehensive similarity between two ideas.
    
    Args:
        left_idea: Left idea record
        right_idea: Right idea record
        weights: Optional custom weights (sum must = 1.0)
    
    Returns:
        SimilarityScore with breakdown
    """
    if weights is None:
        weights = {
            "title": 0.35,
            "category": 0.15,
            "references": 0.25,
            "tokens": 0.25
        }
    
    # Title similarity (Levenshtein + token-based)
    left_title = left_idea.get("title", "").lower()
    right_title = right_idea.get("title", "").lower()
    
    title_levenshtein = _levenshtein_ratio(left_title, right_title)
    title_tokens = _jaccard_similarity(
        _tokenize(left_title),
        _tokenize(right_title)
    )
    title_sim = 0.6 * title_levenshtein + 0.4 * title_tokens
    
    # Category/project similarity
    left_categories = set(left_idea.get("planned_project_ids", []))
    right_categories = set(right_idea.get("planned_project_ids", []))
    category_sim = _jaccard_similarity(left_categories, right_categories)
    
    # Reference similarity
    left_refs = set(left_idea.get("source_references", []))
    right_refs = set(right_idea.get("source_references", []))
    reference_sim = _jaccard_similarity(left_refs, right_refs)
    
    # Token similarity (description/content)
    left_tokens = _tokenize(left_idea.get("description", "") + " " + left_idea.get("title", ""))
    right_tokens = _tokenize(right_idea.get("description", "") + " " + right_idea.get("title", ""))
    token_sim = _jaccard_similarity(left_tokens, right_tokens)
    
    overall_score = (
        weights["title"] * title_sim +
        weights["category"] * category_sim +
        weights["references"] * reference_sim +
        weights["tokens"] * token_sim
    )
    
    return SimilarityScore(
        overall_score=round(overall_score, 4),
        title_similarity=round(title_sim, 4),
        category_similarity=round(category_sim, 4),
        reference_similarity=round(reference_sim, 4),
        token_similarity=round(token_sim, 4),
        components={
            "title": round(title_sim, 4),
            "category": round(category_sim, 4),
            "references": round(reference_sim, 4),
            "tokens": round(token_sim, 4),
        }
    )


def find_merge_candidates(
    ideas: list[dict[str, Any]],
    merge_threshold: float = 0.75,
    review_threshold: float = 0.55,
    log: Callable[[str], None] | None = None
) -> dict[str, Any]:
    """
    Identify merge candidates from ideas list.
    
    Args:
        ideas: List of idea records
        merge_threshold: Score >= this → automatic merge candidate
        review_threshold: Score >= this → manual review candidate
        log: Optional progress logger
    
    Returns:
        Dict with merge/review candidates and statistics
    """
    if not ideas:
        return {
            "merge_candidates": [],
            "review_candidates": [],
            "statistics": {
                "total_ideas": 0,
                "potential_merges": 0,
                "work_reduction": 0.0
            }
        }
    
    # Index ideas by various blocking keys for efficiency
    idea_map = {idea.get("idea_id"): idea for idea in ideas}
    
    # Build blocking indices
    title_blocks = defaultdict(list)
    category_blocks = defaultdict(list)
    reference_blocks = defaultdict(list)
    
    for idea in ideas:
        idea_id = idea.get("idea_id", "")
        
        # Title blocking (first 3 words)
        title_tokens = sorted(_tokenize(idea.get("title", "")))
        if title_tokens:
            title_key = "|".join(title_tokens[:3])
            if title_key:
                title_blocks[title_key].append(idea_id)
        
        # Category blocking
        for category in idea.get("planned_project_ids", []):
            category_blocks[category].append(idea_id)
        
        # Reference blocking
        for ref in idea.get("source_references", []):
            reference_blocks[ref].append(idea_id)
    
    # Combine all blocks
    all_blocks = list(title_blocks.values()) + list(category_blocks.values()) + list(reference_blocks.values())
    
    if log:
        log(f"[IdeaMerger] Built {len(all_blocks)} blocking groups from {len(ideas)} ideas")
    
    merge_candidates = []
    review_candidates = []
    seen_pairs = set()
    
    for block in all_blocks:
        if len(block) < 2:
            continue
        
        # Compare all pairs in the block
        for i in range(len(block)):
            for j in range(i + 1, len(block)):
                left_id = block[i]
                right_id = block[j]
                
                pair_key = (min(left_id, right_id), max(left_id, right_id))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                
                left_idea = idea_map.get(left_id)
                right_idea = idea_map.get(right_id)
                
                if not left_idea or not right_idea:
                    continue
                
                # Calculate similarity
                similarity = calculate_idea_similarity(left_idea, right_idea)
                
                if similarity.overall_score < review_threshold:
                    continue
                
                candidate = {
                    "left_id": pair_key[0],
                    "right_id": pair_key[1],
                    "score": similarity.overall_score,
                    "type": "merge" if similarity.overall_score >= merge_threshold else "review",
                    "similarity": asdict(similarity),
                    "left_title": left_idea.get("title", ""),
                    "right_title": right_idea.get("title", ""),
                }
                
                if similarity.overall_score >= merge_threshold:
                    merge_candidates.append(candidate)
                else:
                    review_candidates.append(candidate)
    
    # Sort by score descending
    merge_candidates.sort(key=lambda x: -x["score"])
    review_candidates.sort(key=lambda x: -x["score"])
    
    # Calculate work reduction
    work_reduction = len(merge_candidates) * 0.5  # Each merge saves ~50% work on one idea
    
    if log:
        log(f"[IdeaMerger] Found {len(merge_candidates)} merge candidates, {len(review_candidates)} review candidates")
        log(f"[IdeaMerger] Estimated work reduction: {work_reduction:.1f} shards ({work_reduction/422*100:.1f}%)")
    
    return {
        "merge_candidates": merge_candidates,
        "review_candidates": review_candidates,
        "statistics": {
            "total_ideas": len(ideas),
            "potential_merges": len(merge_candidates),
            "potential_reviews": len(review_candidates),
            "work_reduction": round(work_reduction, 1),
            "work_reduction_percentage": round((work_reduction / len(ideas)) * 100, 2)
        }
    }


def apply_merges(
    ideas: list[dict[str, Any]],
    merge_candidates: list[dict[str, Any]],
    log: Callable[[str], None] | None = None
) -> tuple[list[dict[str, Any]], list[IdeaMergeRecord]]:
    """
    Apply automatic merges to ideas list.
    
    Strategy:
    - Keep the "better" idea (by readiness score)
    - Merge references, categories, and metadata
    - Track merge lineage
    
    Args:
        ideas: Original ideas list
        merge_candidates: List of merge candidates
        log: Optional progress logger
    
    Returns:
        (merged_ideas, merge_records)
    """
    idea_map = {idea.get("idea_id"): idea for idea in ideas}
    merged_away = {}  # Maps removed IDs to target IDs
    merge_records = []
    
    for candidate in merge_candidates:
        left_id = candidate["left_id"]
        right_id = candidate["right_id"]
        score = candidate["score"]
        
        # Skip if either idea was already merged away
        if left_id in merged_away or right_id in merged_away:
            continue
        
        left_idea = idea_map.get(left_id)
        right_idea = idea_map.get(right_id)
        
        if not left_idea or not right_idea:
            continue
        
        # Determine which is "better" (higher readiness score)
        left_readiness = left_idea.get("scoring", {}).get("implementation_readiness", 0)
        right_readiness = right_idea.get("scoring", {}).get("implementation_readiness", 0)
        
        if left_readiness >= right_readiness:
            target_idea = left_idea
            source_idea = right_idea
            target_id = left_id
            source_id = right_id
        else:
            target_idea = right_idea
            source_idea = left_idea
            target_id = right_id
            source_id = left_id
        
        # Merge metadata
        merged_fields = {
            "source_references": list(set(
                target_idea.get("source_references", []) + 
                source_idea.get("source_references", [])
            )),
            "planned_project_ids": list(set(
                target_idea.get("planned_project_ids", []) + 
                source_idea.get("planned_project_ids", [])
            )),
        }
        
        # Update target
        target_idea["source_references"] = merged_fields["source_references"]
        target_idea["planned_project_ids"] = merged_fields["planned_project_ids"]
        target_idea["merged_from"] = target_idea.get("merged_from", []) + [source_id]
        
        # Mark source as merged away
        merged_away[source_id] = target_id
        del idea_map[source_id]
        
        # Record merge
        merge_record = IdeaMergeRecord(
            source_id=source_id,
            target_id=target_id,
            reason=f"Similar ideas (score: {score:.2f})",
            score=score,
            timestamp=datetime.now(timezone.utc).isoformat(),
            merged_fields=merged_fields,
            work_reduction=1.0  # One fewer shard to process
        )
        merge_records.append(merge_record)
        
        if log:
            log(f"[IdeaMerger] Merged {source_id} → {target_id} (score: {score:.2f})")
    
    merged_ideas = list(idea_map.values())
    
    if log:
        log(f"[IdeaMerger] Applied {len(merge_records)} merges, reduced from {len(ideas)} to {len(merged_ideas)} ideas")
    
    return merged_ideas, merge_records


def generate_merge_report(
    original_count: int,
    merged_count: int,
    merge_records: list[IdeaMergeRecord],
    merge_analysis: dict[str, Any]
) -> dict[str, Any]:
    """Generate comprehensive merge statistics report."""
    total_work_reduction = sum(record.work_reduction for record in merge_records)
    original_shards = (original_count + 474) // 475
    merged_shards = (merged_count + 474) // 475
    
    return {
        "summary": {
            "original_ideas": original_count,
            "merged_ideas": merged_count,
            "ideas_removed": original_count - merged_count,
            "removal_percentage": round(((original_count - merged_count) / original_count * 100), 2),
        },
        "execution_impact": {
            "original_shards": original_shards,
            "merged_shards": merged_shards,
            "shards_eliminated": original_shards - merged_shards,
            "work_reduction_percentage": round(((original_shards - merged_shards) / original_shards * 100), 2),
            "estimated_hours_saved": (original_shards - merged_shards) * 3,  # 3 hours per shard
        },
        "merge_analysis": {
            "total_candidates": merge_analysis.get("statistics", {}).get("potential_merges", 0) + 
                               merge_analysis.get("statistics", {}).get("potential_reviews", 0),
            "automatic_merges": len(merge_records),
            "merge_threshold_used": 0.75,
            "review_threshold_used": 0.55,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main_merge_workflow(
    ideas: list[dict[str, Any]],
    merge_threshold: float = 0.75,
    review_threshold: float = 0.55,
    log: Callable[[str], None] | None = None
) -> dict[str, Any]:
    """
    Complete merge workflow: analyze → find candidates → apply merges → report.
    
    Args:
        ideas: List of idea records
        merge_threshold: Automatic merge threshold
        review_threshold: Manual review threshold
        log: Optional progress logger
    
    Returns:
        Results dict with merged ideas, reports, and statistics
    """
    if log:
        log(f"[IdeaMerger] Starting merge workflow for {len(ideas)} ideas...")
    
    # Analyze for candidates
    merge_analysis = find_merge_candidates(
        ideas,
        merge_threshold=merge_threshold,
        review_threshold=review_threshold,
        log=log
    )
    
    # Apply automatic merges
    merged_ideas, merge_records = apply_merges(
        ideas,
        merge_analysis["merge_candidates"],
        log=log
    )
    
    # Generate report
    report = generate_merge_report(
        len(ideas),
        len(merged_ideas),
        merge_records,
        merge_analysis
    )
    
    return {
        "merged_ideas": merged_ideas,
        "merge_records": merge_records,
        "merge_candidates": merge_analysis["merge_candidates"],
        "review_candidates": merge_analysis["review_candidates"],
        "report": report,
        "analysis": merge_analysis["statistics"]
    }


if __name__ == "__main__":
    # Load ideas from file or use examples
    if len(sys.argv) > 1:
        ideas_file = Path(sys.argv[1])
        if ideas_file.exists():
            with open(ideas_file) as f:
                data = json.load(f)
                # Handle both raw list and embedded list
                ideas = data if isinstance(data, list) else data.get("ideas", [])
        else:
            print(f"[ERROR] File not found: {ideas_file}")
            sys.exit(1)
    else:
        # Example usage
        ideas = [
            {
                "idea_id": "idea-001",
                "title": "Implement FastAPI endpoints for user management",
                "description": "Create REST API endpoints for user CRUD operations",
                "planned_project_ids": ["backend", "api"],
                "source_references": ["docs/user-api.md"],
                "scoring": {"implementation_readiness": 8}
            },
            {
                "idea_id": "idea-002",
                "title": "FastAPI user API endpoints implementation",
                "description": "Implement REST endpoints for creating, reading, updating users",
                "planned_project_ids": ["backend"],
                "source_references": ["docs/api.md"],
                "scoring": {"implementation_readiness": 7}
            },
        ]
    
    def simple_log(msg: str):
        print(msg)
    
    results = main_merge_workflow(ideas, log=simple_log)
    print("\n=== Merge Results ===")
    print(json.dumps(results["report"], indent=2))
    
    # Save merged ideas
    output_file = Path(sys.argv[1]).parent / "MERGED_RESULTS.json" if len(sys.argv) > 1 else Path("MERGED_RESULTS.json")
    with open(output_file, "w") as f:
        json.dump({
            "merged_ideas": results["merged_ideas"],
            "merge_records": [asdict(r) for r in results["merge_records"]],
            "report": results["report"],
            "analysis": results["analysis"]
        }, f, indent=2, default=str)
    print(f"\n✅ Results saved to {output_file}")
