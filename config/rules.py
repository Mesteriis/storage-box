"""
Rules Engine - Extensible configuration logic.

Instead of scattered if-statements, rules provide a clean
way to manage configuration logic that can be extended
for new materials/printers.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict

from .box_config import BoxConfig
from .enums import ConnectionType, MaterialType


class Rule(ABC):
    """Base class for configuration rules."""
    
    name: str = "base_rule"
    description: str = ""
    
    @abstractmethod
    def evaluate(self, config: BoxConfig) -> Any:
        """Evaluate rule and return computed value."""
        pass
    
    def validate(self, config: BoxConfig) -> List[str]:
        """Return list of warnings. Override for validation."""
        return []


class RuleWallThickness(Rule):
    """Rule for selecting wall thickness."""
    
    name = "wall_thickness"
    description = "Adaptive wall thickness based on size and load"
    
    def evaluate(self, config: BoxConfig) -> float:
        area = config.width * config.height / 1000  # cm²
        base = 2.0
        
        if area > 160:
            base = 3.2
        elif area > 100:
            base = 2.4
        
        if config.stack_levels > 2:
            base += 0.4
        
        if config.mount == "wall":
            base += 0.4
        
        # Round to nozzle multiple
        return round(base / 0.4) * 0.4


class RuleEnableLabel(Rule):
    """Rule for enabling label feature."""
    
    name = "enable_label"
    description = "Enable label based on minimum width"
    
    MIN_WIDTH = 60.0
    
    def evaluate(self, config: BoxConfig) -> bool:
        return config.width >= self.MIN_WIDTH


class RuleChooseConnection(Rule):
    """Rule for auto-selecting connection type."""
    
    name = "connection_type"
    description = "Smart connection type selection"
    
    def evaluate(self, config: BoxConfig) -> ConnectionType:
        # Wall mount -> magnets or clips
        if config.mount == "wall":
            if config.width > 150:
                return ConnectionType.MAGNET
            return ConnectionType.CLIP
        
        # Heavy content -> dovetail
        if config.expected_weight > 1000:
            return ConnectionType.DOVETAIL
        
        # Tall stack -> dovetail
        if config.stack_levels > 3:
            return ConnectionType.DOVETAIL
        
        # Small -> clips
        if config.height < 50:
            return ConnectionType.CLIP
        
        # Default to user selection
        return config.connection


class RuleTolerance(Rule):
    """Rule for base tolerance based on material."""
    
    name = "base_tolerance"
    description = "Material-specific base tolerance"
    
    TOLERANCES = {
        MaterialType.HYPER_PLA: 0.30,
        MaterialType.PETG: 0.40,
        MaterialType.ABS: 0.35,
    }
    
    def evaluate(self, config: BoxConfig) -> float:
        return self.TOLERANCES.get(config.material, 0.35)


class RuleDividerCount(Rule):
    """Rule for calculating divider count."""
    
    name = "divider_count"
    description = "Auto-calculate divider grid based on target cell size"
    
    MIN_CELL_WIDTH = 25.0
    MIN_CELL_DEPTH = 30.0
    
    def evaluate(self, config: BoxConfig) -> tuple:
        from .enums import DividerLayout
        
        if config.dividers == DividerLayout.NONE:
            return (0, 0)
        
        if config.dividers != DividerLayout.AUTO:
            layouts = {
                DividerLayout.GRID_2X2: (1, 1),
                DividerLayout.GRID_2X3: (1, 2),
                DividerLayout.GRID_3X3: (2, 2),
            }
            return layouts.get(config.dividers, (0, 0))
        
        # Estimate inner dimensions
        wall = RuleWallThickness().evaluate(config)
        rail_width = 5.0
        tol = RuleTolerance().evaluate(config)
        
        inner_w = config.width - 2 * wall - 2 * rail_width - 2 * tol
        inner_d = config.depth - 2 * wall
        
        target_w, target_d = config.target_cell_size
        
        cols = max(0, round(inner_w / target_w) - 1)
        rows = max(0, round(inner_d / target_d) - 1)
        
        # Validate minimum cell size
        while cols > 0 and inner_w / (cols + 1) < self.MIN_CELL_WIDTH:
            cols -= 1
        while rows > 0 and inner_d / (rows + 1) < self.MIN_CELL_DEPTH:
            rows -= 1
        
        return (cols, rows)


class RuleEnableSmartCartridge(Rule):
    """Rule for enabling smart cartridge feature."""
    
    name = "enable_smart_cartridge"
    description = "Enable smart cartridge based on minimum dimensions"
    
    MIN_WIDTH = 80.0
    MIN_DEPTH = 100.0
    
    def evaluate(self, config: BoxConfig) -> bool:
        return (
            config.width >= self.MIN_WIDTH
            and config.depth >= self.MIN_DEPTH
        )


class RulesEngine:
    """
    Engine for evaluating configuration rules.
    
    Centralizes all rule logic and makes it extensible.
    """
    
    def __init__(self):
        self.rules: List[Rule] = [
            RuleWallThickness(),
            RuleEnableLabel(),
            RuleChooseConnection(),
            RuleTolerance(),
            RuleDividerCount(),
            RuleEnableSmartCartridge(),
        ]
    
    def add_rule(self, rule: Rule):
        """Add a custom rule."""
        self.rules.append(rule)
    
    def evaluate_all(self, config: BoxConfig) -> Dict[str, Any]:
        """Evaluate all rules and return results."""
        results = {}
        for rule in self.rules:
            results[rule.name] = rule.evaluate(config)
        return results
    
    def validate_all(self, config: BoxConfig) -> List[str]:
        """Run all validation and return warnings."""
        warnings = []
        for rule in self.rules:
            warnings.extend(rule.validate(config))
        return warnings
    
    def get_rule(self, name: str) -> Rule:
        """Get rule by name."""
        for rule in self.rules:
            if rule.name == name:
                return rule
        raise KeyError(f"Rule not found: {name}")
    
    def evaluate(self, config: BoxConfig, rule_name: str) -> Any:
        """Evaluate single rule by name."""
        rule = self.get_rule(rule_name)
        return rule.evaluate(config)
