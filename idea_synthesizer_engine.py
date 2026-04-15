#!/usr/bin/env python3
"""
Intelligent Idea Synthesizer Engine
====================================

Creates NEW synthesized ideas by merging similar concepts together.
Instead of just keeping one idea and discarding duplicates, this engine:

1. Identifies clusters of similar ideas
2. Synthesizes a NEW idea that combines the best aspects
3. Includes cross-references to source ideas
4. Produces more comprehensive and powerful consolidated concepts
5. Maintains full traceability

Example:
  Input: 
    - "Implement FastAPI REST endpoints for users"
    - "Create REST API for user CRUD operations"
    - "Build user management HTTP interface"
  
  Output:
    - NEW idea: "Comprehensive User Management API"
      (combines best aspects, has full test coverage, includes all requirements)
      References: [original_3_ideas]
"""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional
from difflib import SequenceMatcher
import re


@dataclass
class SynthesizedIdea:
    """A new idea created by merging similar source ideas."""
    idea_id: str
    title: str
    description: str
    planned_project_ids: list[str]
    source_references: list[str]
    source_idea_ids: list[str]  # ← NEW: which ideas were merged to create this
    scoring: dict[str, float]
    synthesis_metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "active"


@dataclass
class MergeCluster:
    """A group of similar ideas that should be synthesized together."""
    cluster_id: str
    member_ids: list[str]
    member_ideas: list[dict[str, Any]]
    average_similarity: float
    dominant_theme: str


def _tokenize(text: str) -> set[str]:
    """Tokenize text into meaningful words."""
    if not text:
        return set()
    
    noise_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "is", "are", "was", "be", "been", "have", "has", "do", "does",
        "did", "will", "would", "could", "should", "may", "might", "can",
        "by", "with", "this", "that", "these", "those", "i", "you", "he",
        "she", "it", "we", "they", "what", "which", "who", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more", "most",
        "some", "such", "no", "nor", "not", "only", "own", "so", "than",
        "too", "very", "just", "as", "if", "because", "until", "while", "implementation"
    }
    
    tokens = text.lower().split()
    return {
        token.strip(".,;:!?\"'()[]{}") 
        for token in tokens 
        if token.strip(".,;:!?\"'()[]{}") and token.lower() not in noise_words
    }


def _similarity(idea1: dict, idea2: dict) -> float:
    """Calculate overall similarity between two ideas (0-1)."""
    # Title similarity
    title1_tokens = _tokenize(idea1.get("title", ""))
    title2_tokens = _tokenize(idea2.get("title", ""))
    
    if not title1_tokens or not title2_tokens:
        return 0.0
    
    title_overlap = len(title1_tokens & title2_tokens) / max(len(title1_tokens | title2_tokens), 1)
    
    # Category similarity (exact match)
    cat1 = set(idea1.get("planned_project_ids", []))
    cat2 = set(idea2.get("planned_project_ids", []))
    category_similarity = len(cat1 & cat2) / max(len(cat1 | cat2), 1) if (cat1 or cat2) else 0.0
    
    # Description token similarity
    desc1_tokens = _tokenize(idea1.get("description", ""))
    desc2_tokens = _tokenize(idea2.get("description", ""))
    desc_overlap = len(desc1_tokens & desc2_tokens) / max(len(desc1_tokens | desc2_tokens), 1)
    
    # Weighted average
    similarity = (0.5 * title_overlap + 0.2 * category_similarity + 0.3 * desc_overlap)
    return min(similarity, 1.0)


def _find_clusters(ideas: list[dict], threshold: float = 0.65) -> list[MergeCluster]:
    """
    Identify clusters of similar ideas that should be merged together.
    Uses hierarchical clustering based on similarity.
    """
    if not ideas:
        return []
    
    # Build similarity matrix
    n = len(ideas)
    similarities = {}
    for i in range(n):
        for j in range(i + 1, n):
            sim = _similarity(ideas[i], ideas[j])
            if sim >= threshold:
                key = (i, j)
                similarities[key] = sim
    
    # Group ideas into clusters using simple union-find
    parent = {i: i for i in range(n)}
    
    def find_root(x):
        if parent[x] != x:
            parent[x] = find_root(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find_root(x), find_root(y)
        if px != py:
            parent[px] = py
    
    # Union ideas based on similarity
    for (i, j), sim in sorted(similarities.items(), key=lambda x: -x[1]):
        union(i, j)
    
    # Group by root
    clusters_dict = defaultdict(list)
    for i in range(n):
        root = find_root(i)
        clusters_dict[root].append(i)
    
    # Build cluster objects (only for groups with 2+)
    clusters = []
    cluster_num = 0
    for root, indices in clusters_dict.items():
        if len(indices) >= 2:  # Only cluster if 2+ ideas
            member_ideas = [ideas[i] for i in indices]
            
            # Calculate average similarity within cluster
            pair_sims = []
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    sim = _similarity(ideas[indices[i]], ideas[indices[j]])
                    pair_sims.append(sim)
            avg_sim = sum(pair_sims) / len(pair_sims) if pair_sims else 0.0
            
            # Find dominant theme (most common keyword)
            all_tokens = []
            for idea in member_ideas:
                all_tokens.extend(_tokenize(idea.get("title", "") + " " + idea.get("description", "")))
            
            theme = max(set(all_tokens), key=all_tokens.count) if all_tokens else "Integration"
            
            clusters.append(MergeCluster(
                cluster_id=f"cluster-{cluster_num:06d}",
                member_ids=[idea["idea_id"] for idea in member_ideas],
                member_ideas=member_ideas,
                average_similarity=avg_sim,
                dominant_theme=theme
            ))
            cluster_num += 1
    
    return clusters


def _synthesize_title(cluster: MergeCluster) -> str:
    """Generate a comprehensive title for synthesized idea."""
    # Extract key concepts from all ideas
    themes = []
    for idea in cluster.member_ideas:
        tokens = _tokenize(idea.get("title", ""))
        if tokens:
            # Get longest meaningful token (usually the main concept)
            longest = max(tokens, key=len)
            if longest not in themes and len(longest) > 3:
                themes.append(longest)
    
    # Build theme-based title
    if len(themes) >= 2:
        concepts = ", ".join(themes[:3])
        return f"Unified {concepts.title()} System"
    elif themes:
        return f"Comprehensive {themes[0].title()} Implementation"
    else:
        return f"Integrated {cluster.dominant_theme.title()} Solution"


def _synthesize_description(cluster: MergeCluster) -> str:
    """Generate a comprehensive description by combining key aspects."""
    descriptions = []
    
    # Collect all unique requirements/features
    all_features = set()
    for idea in cluster.member_ideas:
        desc = idea.get("description", "")
        # Extract key requirements
        sentences = desc.replace(".", "\n").split("\n")
        for sent in sentences:
            sent = sent.strip()
            if sent and len(sent) > 10:
                all_features.add(sent)
    
    # Build comprehensive description
    parts = [
        f"Unified implementation combining {len(cluster.member_ideas)} related concepts."
    ]
    
    if all_features:
        parts.append("Key features:")
        for feature in sorted(all_features)[:5]:  # Top 5 features
            parts.append(f"  • {feature}")
    
    # Add integration note
    parts.append(f"\nSynthesized from {len(cluster.member_ideas)} source ideas for comprehensive coverage.")
    
    return "\n".join(parts)


def _synthesize_metadata(cluster: MergeCluster) -> dict[str, Any]:
    """Extract and synthesize metadata from cluster members."""
    # Merge all categories
    all_categories = set()
    for idea in cluster.member_ideas:
        all_categories.update(idea.get("planned_project_ids", []))
    
    # Merge all references
    all_refs = []
    for idea in cluster.member_ideas:
        all_refs.extend(idea.get("source_references", []))
    all_refs = list(set(all_refs))  # Deduplicate
    
    # Average readiness score
    readiness_scores = []
    for idea in cluster.member_ideas:
        score = idea.get("scoring", {}).get("implementation_readiness", 5)
        readiness_scores.append(score)
    avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 6
    
    return {
        "merged_from_count": len(cluster.member_ids),
        "member_idea_ids": cluster.member_ids,
        "combined_categories": sorted(all_categories),
        "combined_references": all_refs,
        "average_readiness": round(avg_readiness, 1),
        "synthesis_confidence": cluster.average_similarity,
        "synthesis_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def synthesize_idea_cluster(cluster: MergeCluster) -> SynthesizedIdea:
    """Transform a cluster of similar ideas into one new synthesized idea."""
    # Generate new unique ID
    new_id = f"merged-{str(uuid.uuid4())[:8]}"
    
    # Synthesize components
    title = _synthesize_title(cluster)
    description = _synthesize_description(cluster)
    categories = sorted(set().union(*[set(i.get("planned_project_ids", [])) for i in cluster.member_ideas]))
    all_refs = []
    for idea in cluster.member_ideas:
        all_refs.extend(idea.get("source_references", []))
    references = list(set(all_refs))
    
    # Synthesize metadata
    metadata = _synthesize_metadata(cluster)
    
    # Create synthesized idea
    synthesized = SynthesizedIdea(
        idea_id=new_id,
        title=title,
        description=description,
        planned_project_ids=categories,
        source_references=references,
        source_idea_ids=cluster.member_ids,
        scoring={
            "implementation_readiness": metadata["average_readiness"],
            "synthesis_confidence": metadata["synthesis_confidence"],
        },
        synthesis_metadata=metadata,
        status="active"
    )
    
    return synthesized


def synthesize_ideas(ideas: list[dict], threshold: float = 0.65, log: Optional[Callable] = None) -> dict:
    """
    Main synthesis engine: merge similar ideas into new consolidated concepts.
    
    Returns:
        Dict with synthesized ideas, original ungrouped ideas, and synthesis report
    """
    log = log or (lambda x: print(x))
    
    log(f"\n🔬 [IdeaSynthesizer] Starting synthesis for {len(ideas)} ideas...")
    
    # Find clusters
    clusters = _find_clusters(ideas, threshold=threshold)
    log(f"✓ Found {len(clusters)} clusters of similar ideas (≥2 members each)")
    
    # Create mapping of clustered idea IDs
    clustered_ids = set()
    for cluster in clusters:
        clustered_ids.update(cluster.member_ids)
    
    # Separate synthesized ideas from ungrouped
    synthesized = []
    ungrouped = []
    
    for cluster in clusters:
        new_idea = synthesize_idea_cluster(cluster)
        synthesized.append(new_idea)
        log(f"  ✓ Synthesized: {new_idea.title}")
        log(f"    From {len(cluster.member_ids)} ideas, confidence: {cluster.average_similarity:.2f}")
    
    # Keep original ungrouped ideas
    for idea in ideas:
        if idea["idea_id"] not in clustered_ids:
            ungrouped.append(idea)
    
    # Build synthesis records
    synthesis_records = []
    for cluster in clusters:
        synthesis_records.append({
            "source_idea_ids": cluster.member_ids,
            "synthesized_idea_id": None,  # Will be filled below
            "theme": cluster.dominant_theme,
            "confidence": cluster.average_similarity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    
    # Fill in synthesized idea IDs
    for i, record in enumerate(synthesis_records):
        if i < len(synthesized):
            record["synthesized_idea_id"] = synthesized[i].idea_id
    
    # Report
    total_original = len(ideas)
    total_synthesized = len(synthesized) + len(ungrouped)
    reduction = total_original - total_synthesized
    reduction_pct = (reduction / total_original * 100) if total_original > 0 else 0
    
    report = {
        "summary": {
            "original_ideas": total_original,
            "synthesized_ideas": len(synthesized),
            "ungrouped_ideas": len(ungrouped),
            "total_new_ideas": total_synthesized,
            "ideas_consolidated": reduction,
            "consolidation_percentage": round(reduction_pct, 1),
        },
        "synthesis_analysis": {
            "clusters_found": len(clusters),
            "avg_cluster_size": len(clustered_ids) / len(clusters) if clusters else 0,
            "synthesis_threshold": threshold,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    
    log(f"\n📊 Synthesis Report:")
    log(f"  Original ideas: {total_original}")
    log(f"  Clusters found: {len(clusters)}")
    log(f"  Synthesized ideas: {len(synthesized)} (new)")
    log(f"  Ungrouped ideas: {len(ungrouped)} (kept as-is)")
    log(f"  Total: {total_synthesized} (consolidated from {total_original})")
    log(f"  Consolidation: {reduction} ideas merged ({reduction_pct:.1f}%)")
    
    return {
        "synthesized_ideas": synthesized,
        "ungrouped_ideas": ungrouped,
        "synthesis_records": synthesis_records,
        "report": report,
        "clusters": clusters,
    }


if __name__ == "__main__":
    import sys
    
    # Load ideas from file or use examples
    if len(sys.argv) > 1:
        ideas_file = Path(sys.argv[1])
        if ideas_file.exists():
            with open(ideas_file) as f:
                data = json.load(f)
                ideas = data if isinstance(data, list) else data.get("ideas", [])
        else:
            print(f"[ERROR] File not found: {ideas_file}")
            sys.exit(1)
    else:
        # Example: 3 similar ideas that should be synthesized into 1
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
            {
                "idea_id": "idea-003",
                "title": "Build HTTP API for user management",
                "description": "Create REST interface for managing user accounts and profiles",
                "planned_project_ids": ["api", "backend"],
                "source_references": ["docs/http-api.md"],
                "scoring": {"implementation_readiness": 8}
            },
            {
                "idea_id": "idea-004",
                "title": "Dashboard analytics system",
                "description": "Create analytics dashboard for tracking metrics",
                "planned_project_ids": ["frontend"],
                "source_references": ["docs/dashboard.md"],
                "scoring": {"implementation_readiness": 6}
            },
        ]
    
    def simple_log(msg: str):
        print(msg)
    
    results = synthesize_ideas(ideas, threshold=0.65, log=simple_log)
    
    print("\n" + "="*70)
    print("🎯 SYNTHESIZED IDEAS (NEW)")
    print("="*70)
    for idea in results["synthesized_ideas"]:
        print(f"\n✨ {idea.title}")
        print(f"   ID: {idea.idea_id}")
        print(f"   From {idea.synthesis_metadata['merged_from_count']} ideas: {', '.join(idea.source_idea_ids)}")
        print(f"   Categories: {', '.join(idea.planned_project_ids)}")
        print(f"   Readiness: {idea.scoring['implementation_readiness']:.1f}/10")
        print(f"   Confidence: {idea.scoring['synthesis_confidence']:.2f}")
    
    print("\n" + "="*70)
    print("📌 UNGROUPED IDEAS (KEPT AS-IS)")
    print("="*70)
    for idea in results["ungrouped_ideas"]:
        print(f"\n  {idea['title']}")
        print(f"     ID: {idea['idea_id']}")
        print(f"     Readiness: {idea['scoring'].get('implementation_readiness', 5)}/10")
    
    # Save results
    output_file = Path(sys.argv[1]).parent / "SYNTHESIZED_RESULTS.json" if len(sys.argv) > 1 else Path("SYNTHESIZED_RESULTS.json")
    with open(output_file, "w") as f:
        json.dump({
            "synthesized_ideas": [asdict(idea) for idea in results["synthesized_ideas"]],
            "ungrouped_ideas": results["ungrouped_ideas"],
            "synthesis_records": results["synthesis_records"],
            "report": results["report"],
        }, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to {output_file}")
