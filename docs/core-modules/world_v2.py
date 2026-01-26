#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World Module v2
Author: MR.liou
Date: 2026-01-26
origin_signature: MrLiouWord

This module provides the core World functionality for the MrLiouWord system.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorldState:
    """Represents the current state of the World module."""
    version: str = "2.0.0"
    active: bool = False
    entities: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []


class World:
    """
    World v2 - Core world management module for MrLiouWord system.
    
    怎麼過去，就怎麼回來
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize World module with optional configuration."""
        self.config = config or {}
        self.state = WorldState()
        logger.info(f"World v2 initialized - origin_signature: MrLiouWord")
    
    def activate(self) -> bool:
        """Activate the World module."""
        try:
            self.state.active = True
            logger.info("World module activated")
            return True
        except Exception as e:
            logger.error(f"Failed to activate World module: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the World module."""
        try:
            self.state.active = False
            logger.info("World module deactivated")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate World module: {e}")
            return False
    
    def add_entity(self, entity: Dict[str, Any]) -> bool:
        """Add an entity to the World."""
        try:
            self.state.entities.append(entity)
            logger.info(f"Entity added: {entity.get('id', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to add entity: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current World state."""
        return asdict(self.state)
    
    def export_state(self, filepath: str) -> bool:
        """Export World state to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.get_state(), f, indent=2, ensure_ascii=False)
            logger.info(f"State exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export state: {e}")
            return False
    
    def import_state(self, filepath: str) -> bool:
        """Import World state from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.state = WorldState(**data)
            logger.info(f"State imported from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import state: {e}")
            return False


def main():
    """Main function for testing World module."""
    world = World()
    world.activate()
    
    # Add sample entity
    world.add_entity({
        "id": "entity-001",
        "type": "test",
        "data": {"name": "Test Entity"}
    })
    
    # Print state
    print(json.dumps(world.get_state(), indent=2, ensure_ascii=False))
    
    world.deactivate()


if __name__ == "__main__":
    main()
