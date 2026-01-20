#!/usr/bin/env python3
"""
Particle Naming Engine ⭐ CRITICAL
===================================

Auto-generates particle names from logical architecture.

Naming Rules:
- attention pattern → fx.pattern.attention
- memory pattern → fx.pattern.memory
- chain pattern → fx.pattern.chain
- particle pattern → fx.pattern.particle
- flow pattern → fx.flow.pipeline
- layer pattern → fx.pattern.hierarchical
- default → fx.logic.{reasoning_type}

Features:
- Auto-determine particle type (fx.*) based on concepts+patterns+reasoning
- Handle name conflicts with versioning
- Store naming history as particles (fx.meta.naming) in L7

Author: MR.liou
Philosophy: Dynamic naming evolution based on logical understanding
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.simhash64 import simhash64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NamingDecision:
    """Particle naming decision"""
    particle_name: str
    particle_type: str
    reasoning: str
    confidence: float
    version: int
    timestamp: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ParticleNamingEngine:
    """
    Particle Naming Engine
    
    Automatically generates meaningful particle names from logical architecture.
    """
    
    # Naming rules based on patterns
    PATTERN_TO_TYPE = {
        'attention': 'fx.pattern.attention',
        'memory': 'fx.pattern.memory',
        'merkle': 'fx.pattern.chain',
        'chain': 'fx.pattern.chain',
        'particle': 'fx.pattern.particle',
        'flow': 'fx.flow.pipeline',
        'layer': 'fx.pattern.hierarchical'
    }
    
    # Naming rules based on concepts
    CONCEPT_TO_TYPE = {
        'distributed': 'fx.system.distributed',
        'concurrent': 'fx.system.concurrent',
        'reactive': 'fx.pattern.reactive',
        'functional': 'fx.paradigm.functional',
        'graph': 'fx.structure.graph',
        'state': 'fx.pattern.state',
        'vector': 'fx.math.vector',
        'neural': 'fx.ai.neural',
        'crypto': 'fx.security.crypto',
        'consensus': 'fx.protocol.consensus'
    }
    
    # Reasoning type fallbacks
    REASONING_TYPES = [
        'deductive',
        'inductive',
        'abductive',
        'analogical',
        'causal',
        'probabilistic',
        'temporal',
        'spatial'
    ]
    
    def __init__(self, storage_path: str = './naming_history'):
        """
        Initialize naming engine
        
        Args:
            storage_path: Path to store naming history
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.naming_history = []
        self.name_registry = {}  # Track used names
        self.version_registry = {}  # Track versions
        
        self._load_history()
        
        logger.info(f"ParticleNamingEngine initialized")
    
    def _load_history(self):
        """Load naming history from storage"""
        history_file = os.path.join(self.storage_path, 'naming_history.jsonl')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self.naming_history.append(entry)
                        
                        # Update registries
                        name = entry['particle_name']
                        self.name_registry[name] = entry
                        
                        base_name = self._get_base_name(name)
                        version = entry.get('version', 1)
                        if base_name not in self.version_registry:
                            self.version_registry[base_name] = version
                        else:
                            self.version_registry[base_name] = max(
                                self.version_registry[base_name],
                                version
                            )
            
            logger.info(f"Loaded {len(self.naming_history)} naming records")
    
    def _save_decision(self, decision: NamingDecision):
        """Save naming decision to history"""
        history_file = os.path.join(self.storage_path, 'naming_history.jsonl')
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(decision.to_dict(), ensure_ascii=False) + '\n')
        
        self.naming_history.append(decision.to_dict())
        self.name_registry[decision.particle_name] = decision.to_dict()
    
    def _get_base_name(self, full_name: str) -> str:
        """Extract base name without version suffix"""
        # Remove version suffix like _v2, _v3, etc.
        return re.sub(r'_v\d+$', '', full_name)
    
    def _handle_conflict(self, base_name: str) -> Tuple[str, int]:
        """
        Handle name conflict with versioning
        
        Args:
            base_name: Base particle name
            
        Returns:
            (versioned_name, version_number)
        """
        if base_name not in self.version_registry:
            self.version_registry[base_name] = 1
            return base_name, 1
        
        # Increment version
        version = self.version_registry[base_name] + 1
        self.version_registry[base_name] = version
        
        versioned_name = f"{base_name}_v{version}"
        
        logger.info(f"Name conflict: {base_name} -> {versioned_name}")
        
        return versioned_name, version
    
    def determine_type(
        self,
        patterns: List[str],
        concepts: List[str],
        reasoning_chains: List[str]
    ) -> Tuple[str, str, float]:
        """
        Determine particle type from logical architecture
        
        Args:
            patterns: Detected patterns
            concepts: Detected concepts
            reasoning_chains: Reasoning chains
            
        Returns:
            (particle_type, reasoning, confidence)
        """
        # Priority 1: Pattern-based typing
        for pattern in patterns:
            if pattern in self.PATTERN_TO_TYPE:
                particle_type = self.PATTERN_TO_TYPE[pattern]
                reasoning = f"Primary pattern '{pattern}' detected"
                confidence = 0.9
                return particle_type, reasoning, confidence
        
        # Priority 2: Concept-based typing
        for concept in concepts:
            if concept in self.CONCEPT_TO_TYPE:
                particle_type = self.CONCEPT_TO_TYPE[concept]
                reasoning = f"Primary concept '{concept}' detected"
                confidence = 0.7
                return particle_type, reasoning, confidence
        
        # Priority 3: Reasoning chain analysis
        if reasoning_chains:
            # Analyze reasoning chains for clues
            chain_text = ' '.join(reasoning_chains).lower()
            
            if 'attention' in chain_text or 'query' in chain_text:
                return 'fx.pattern.attention', 'Attention pattern in reasoning chain', 0.6
            elif 'memory' in chain_text or 'storage' in chain_text:
                return 'fx.pattern.memory', 'Memory pattern in reasoning chain', 0.6
            elif 'hash' in chain_text or 'verify' in chain_text:
                return 'fx.pattern.chain', 'Chain pattern in reasoning chain', 0.6
        
        # Default: General logic type
        reasoning_type = 'general'
        if concepts:
            # Infer reasoning type from concepts
            if any(c in ['distributed', 'concurrent'] for c in concepts):
                reasoning_type = 'concurrent'
            elif any(c in ['reactive', 'event'] for c in concepts):
                reasoning_type = 'reactive'
            elif any(c in ['functional', 'immutable'] for c in concepts):
                reasoning_type = 'functional'
        
        particle_type = f'fx.logic.{reasoning_type}'
        reasoning = f"Default logic type (reasoning: {reasoning_type})"
        confidence = 0.5
        
        return particle_type, reasoning, confidence
    
    def generate_name(
        self,
        patterns: List[str],
        concepts: List[str],
        reasoning_chains: List[str],
        source_info: Optional[Dict] = None
    ) -> NamingDecision:
        """
        Generate particle name from logical architecture
        
        Args:
            patterns: Detected patterns
            concepts: Detected concepts
            reasoning_chains: Reasoning chains
            source_info: Source information (repo, file, etc.)
            
        Returns:
            Naming decision with particle name and type
        """
        # Determine particle type
        particle_type, reasoning, confidence = self.determine_type(
            patterns, concepts, reasoning_chains
        )
        
        # Generate descriptive suffix
        suffix_parts = []
        
        # Add primary pattern
        if patterns:
            suffix_parts.append(patterns[0])
        
        # Add primary concept
        if concepts and concepts[0] not in suffix_parts:
            suffix_parts.append(concepts[0])
        
        # Add source info
        if source_info:
            if 'repo' in source_info:
                repo_name = source_info['repo'].split('/')[-1]
                # Sanitize repo name
                repo_clean = re.sub(r'[^a-z0-9]+', '_', repo_name.lower())
                suffix_parts.append(repo_clean[:20])
        
        # Build base name
        if suffix_parts:
            suffix = '_'.join(suffix_parts[:3])  # Limit to 3 parts
            suffix = re.sub(r'[^a-z0-9_]+', '_', suffix.lower())
            base_name = f"{particle_type}.{suffix}"
        else:
            base_name = particle_type
        
        # Handle conflicts
        particle_name, version = self._handle_conflict(base_name)
        
        # Create decision
        decision = NamingDecision(
            particle_name=particle_name,
            particle_type=particle_type,
            reasoning=reasoning,
            confidence=confidence,
            version=version,
            timestamp=datetime.now().isoformat(),
            metadata={
                'patterns': patterns,
                'concepts': concepts,
                'reasoning_chains': reasoning_chains[:3],
                'source_info': source_info or {}
            }
        )
        
        # Save to history
        self._save_decision(decision)
        
        logger.info(f"Generated name: {particle_name} (type: {particle_type}, confidence: {confidence:.2f})")
        
        return decision
    
    def batch_generate(
        self,
        logical_structures: List[Dict]
    ) -> List[NamingDecision]:
        """
        Generate names for multiple logical structures
        
        Args:
            logical_structures: List of logical structure dicts
            
        Returns:
            List of naming decisions
        """
        decisions = []
        
        for i, structure in enumerate(logical_structures):
            logger.info(f"Generating name {i+1}/{len(logical_structures)}")
            
            decision = self.generate_name(
                patterns=structure.get('patterns', []),
                concepts=structure.get('concepts', []),
                reasoning_chains=structure.get('reasoning_chains', []),
                source_info=structure.get('source_info')
            )
            
            decisions.append(decision)
        
        return decisions
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get naming history"""
        return self.naming_history[-limit:]
    
    def get_by_type(self, particle_type: str) -> List[Dict]:
        """Get all particles of a specific type"""
        return [
            entry for entry in self.naming_history
            if entry['particle_type'] == particle_type
        ]
    
    def search_by_pattern(self, pattern: str) -> List[Dict]:
        """Search particles by pattern"""
        results = []
        
        for entry in self.naming_history:
            if pattern in entry['metadata'].get('patterns', []):
                results.append(entry)
        
        return results
    
    def export_registry(self, output_path: str):
        """Export name registry to JSON"""
        registry = {
            'total_particles': len(self.name_registry),
            'types': {},
            'particles': list(self.name_registry.values())
        }
        
        # Count by type
        for entry in self.naming_history:
            ptype = entry['particle_type']
            registry['types'][ptype] = registry['types'].get(ptype, 0) + 1
        
        with open(output_path, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Registry exported to {output_path}")


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Particle Naming Engine')
    parser.add_argument('--test', action='store_true', help='Run test cases')
    parser.add_argument('--export', help='Export registry to JSON file')
    
    args = parser.parse_args()
    
    engine = ParticleNamingEngine('./naming_test')
    
    if args.test:
        print("=== Particle Naming Engine Test ===\n")
        
        # Test case 1: Attention pattern
        print("Test 1: Attention Pattern")
        decision1 = engine.generate_name(
            patterns=['attention', 'memory'],
            concepts=['vector', 'neural'],
            reasoning_chains=['query -> key -> value -> softmax'],
            source_info={'repo': 'user/attention-mechanism', 'language': 'Python'}
        )
        print(f"Name: {decision1.particle_name}")
        print(f"Type: {decision1.particle_type}")
        print(f"Reasoning: {decision1.reasoning}")
        print(f"Confidence: {decision1.confidence:.2%}\n")
        
        # Test case 2: Merkle pattern
        print("Test 2: Merkle Pattern")
        decision2 = engine.generate_name(
            patterns=['merkle', 'chain'],
            concepts=['crypto', 'distributed'],
            reasoning_chains=['data -> hash -> tree -> root'],
            source_info={'repo': 'user/merkle-tree', 'language': 'Go'}
        )
        print(f"Name: {decision2.particle_name}")
        print(f"Type: {decision2.particle_type}")
        print(f"Reasoning: {decision2.reasoning}")
        print(f"Confidence: {decision2.confidence:.2%}\n")
        
        # Test case 3: Name conflict
        print("Test 3: Name Conflict (same as Test 1)")
        decision3 = engine.generate_name(
            patterns=['attention', 'memory'],
            concepts=['vector', 'neural'],
            reasoning_chains=['query -> key -> value -> softmax'],
            source_info={'repo': 'user/attention-mechanism', 'language': 'Python'}
        )
        print(f"Name: {decision3.particle_name}")
        print(f"Version: {decision3.version}")
        print(f"(Should be version 2)\n")
        
        # Test case 4: Default logic type
        print("Test 4: Default Logic Type")
        decision4 = engine.generate_name(
            patterns=[],
            concepts=['functional'],
            reasoning_chains=[],
            source_info={'repo': 'user/generic-lib'}
        )
        print(f"Name: {decision4.particle_name}")
        print(f"Type: {decision4.particle_type}")
        print(f"Reasoning: {decision4.reasoning}\n")
        
        print("=== Naming History ===")
        for entry in engine.get_history():
            print(f"- {entry['particle_name']} ({entry['particle_type']}) @ {entry['timestamp'][:19]}")
    
    if args.export:
        engine.export_registry(args.export)
        print(f"Registry exported to {args.export}")
