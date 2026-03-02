from .fused import (
    FusedMoEConfig,
    FusedMoEParallelConfig,
    FusedMoEQuantConfig,
    FusedMoEMethodBase,
    UnquantizedFusedMoEMethod,
    SparseDispatcher,
    determine_expert_map,
    FusedMoELayer,
    AdaptiveMoELayer,
    HierarchicalMoELayer,
)


class ExpertPlacementStrategy:
    """Placeholder ExpertPlacementStrategy for compatibility during test collection."""


class DenseDispatcher:
    """Minimal placeholder for DenseDispatcher used during test collection."""


__all__ = [
    "FusedMoEConfig",
    "FusedMoEParallelConfig",
    "FusedMoEQuantConfig",
    "FusedMoEMethodBase",
    "UnquantizedFusedMoEMethod",
    "SparseDispatcher",
    "determine_expert_map",
    "FusedMoELayer",
    "AdaptiveMoELayer",
    "HierarchicalMoELayer",
    "DenseDispatcher",
    "ExpertPlacementStrategy",
]
