#!/usr/bin/env python3
"""
Logical Architecture Extractor
===============================

Extracts logical concepts, patterns, and relationships from code.

Supported patterns:
- Attention mechanisms
- Memory systems  
- Merkle trees
- Particle systems
- Flow pipelines
- Layer hierarchies

Author: MR.liou
"""

import re
import logging
from typing import List, Dict, Set  # Set preserved for future semantic set operations
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LogicalStructure:
    """Extracted logical structure from code"""
    concepts: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    reasoning_chains: List[str] = field(default_factory=list)
    formula: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class LogicalExtractor:
    """Extract logical architecture from code"""
    
    # Pattern definitions
    PATTERN_SIGNATURES = {
        'attention': [
            r'attention',
            r'query.*key.*value',
            r'softmax',
            r'multi.*head',
            r'self.*attention',
            r'cross.*attention',
            r'scaled.*dot.*product'
        ],
        'memory': [
            r'memory',
            r'cache',
            r'storage',
            r'recall',
            r'commit',
            r'persist',
            r'kv.*store'
        ],
        'merkle': [
            r'merkle',
            r'hash.*tree',
            r'root.*hash',
            r'verify.*chain',
            r'integrity',
            r'tamper.*proof'
        ],
        'particle': [
            r'particle',
            r'quantum',
            r'resonance',
            r'frequency',
            r'oscillat',
            r'wave.*function'
        ],
        'flow': [
            r'pipeline',
            r'stream',
            r'flow',
            r'orchestrat',
            r'workflow',
            r'dag',
            r'dataflow'
        ],
        'layer': [
            r'layer',
            r'hierarchi',
            r'stack',
            r'level',
            r'tier',
            r'stratif'
        ],
        'chain': [
            r'chain',
            r'linked.*list',
            r'prev.*next',
            r'sequence',
            r'blockchain'
        ]
    }
    
    # Concept keywords
    CONCEPT_KEYWORDS = {
        'distributed': ['distributed', 'decentralized', 'peer', 'cluster', 'federation'],
        'concurrent': ['concurrent', 'parallel', 'async', 'thread', 'goroutine'],
        'reactive': ['reactive', 'observer', 'event', 'stream', 'publish'],
        'functional': ['functional', 'pure', 'immutable', 'map', 'reduce', 'filter'],
        'graph': ['graph', 'node', 'edge', 'vertex', 'dag', 'network'],
        'state': ['state', 'fsm', 'stateful', 'transition', 'machine'],
        'vector': ['vector', 'embedding', 'dimension', 'tensor', 'matrix'],
        'neural': ['neural', 'network', 'layer', 'weights', 'activation'],
        'crypto': ['crypto', 'encrypt', 'decrypt', 'hash', 'signature'],
        'consensus': ['consensus', 'raft', 'paxos', 'vote', 'quorum']
    }
    
    def __init__(self):
        """Initialize extractor"""
        pass
    
    def extract(self, code: str, language: str = "unknown") -> LogicalStructure:
        """
        Extract logical structure from code
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Extracted logical structure
        """
        structure = LogicalStructure()
        
        # Normalize code
        normalized = code.lower()
        
        # Extract patterns
        structure.patterns = self._extract_patterns(normalized)
        
        # Extract concepts
        structure.concepts = self._extract_concepts(normalized)
        
        # Extract relationships
        structure.relationships = self._extract_relationships(code, normalized)
        
        # Build reasoning chains
        structure.reasoning_chains = self._build_reasoning_chains(structure)
        
        # Generate formula
        structure.formula = self._generate_formula(structure)
        
        # Calculate confidence
        structure.confidence = self._calculate_confidence(structure, code)
        
        logger.info(f"Extracted: {len(structure.patterns)} patterns, "
                   f"{len(structure.concepts)} concepts, "
                   f"confidence={structure.confidence:.2f}")
        
        return structure
    
    def _extract_patterns(self, normalized: str) -> List[str]:
        """Extract architectural patterns"""
        patterns = []
        
        for pattern_name, signatures in self.PATTERN_SIGNATURES.items():
            matches = 0
            for sig in signatures:
                if re.search(sig, normalized):
                    matches += 1
            
            # Pattern detected if >= 2 signatures match
            if matches >= 2:
                patterns.append(pattern_name)
        
        return patterns
    
    def _extract_concepts(self, normalized: str) -> List[str]:
        """Extract logical concepts"""
        concepts = []
        
        for concept, keywords in self.CONCEPT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in normalized)
            if matches >= 2:
                concepts.append(concept)
        
        return concepts
    
    def _extract_relationships(self, code: str, normalized: str) -> Dict[str, List[str]]:
        """Extract relationships between components"""
        relationships = {}
        
        # Extract class/function relationships
        classes = re.findall(r'class\s+(\w+)', code, re.IGNORECASE)
        functions = re.findall(r'(?:def|function|func)\s+(\w+)', code, re.IGNORECASE)
        
        if classes:
            relationships['classes'] = list(set(classes))[:10]
        if functions:
            relationships['functions'] = list(set(functions))[:10]
        
        # Extract imports/dependencies
        imports = re.findall(r'(?:import|from|require|use)\s+[\w.]+', code, re.IGNORECASE)
        if imports:
            relationships['imports'] = list(set(imports))[:10]
        
        # Extract data flow patterns
        assigns = re.findall(r'(\w+)\s*[=:]\s*(\w+)', code)
        if assigns:
            data_flow = [f"{a}->{b}" for a, b in assigns[:10]]
            relationships['data_flow'] = data_flow
        
        return relationships
    
    def _build_reasoning_chains(self, structure: LogicalStructure) -> List[str]:
        """Build reasoning chains from patterns and concepts"""
        chains = []
        
        # Pattern-based reasoning
        if 'attention' in structure.patterns:
            chains.append("attention -> query/key/value -> similarity -> weighted_sum")
        
        if 'memory' in structure.patterns:
            chains.append("input -> encode -> store -> recall -> decode -> output")
        
        if 'merkle' in structure.patterns:
            chains.append("data -> hash -> tree -> root -> verify")
        
        if 'particle' in structure.patterns:
            chains.append("state -> frequency -> resonance -> collapse")
        
        if 'flow' in structure.patterns:
            chains.append("source -> transform -> sink")
        
        if 'layer' in structure.patterns:
            chains.append("L1 -> L2 -> ... -> Ln")
        
        # Concept-based reasoning
        if 'distributed' in structure.concepts:
            chains.append("local -> sync -> global -> consensus")
        
        if 'reactive' in structure.concepts:
            chains.append("event -> react -> update -> notify")
        
        return chains
    
    def _generate_formula(self, structure: LogicalStructure) -> str:
        """Generate mathematical formula representation"""
        formulas = []
        
        # Pattern formulas
        if 'attention' in structure.patterns:
            formulas.append("Attention(Q,K,V) = softmax(QK^T/√d)V")
        
        if 'memory' in structure.patterns:
            formulas.append("M(t) = f(M(t-1), input(t))")
        
        if 'merkle' in structure.patterns:
            formulas.append("root = H(H(L₁,L₂), H(L₃,L₄))")
        
        if 'particle' in structure.patterns:
            formulas.append("ψ(t) = Σ αᵢe^(iωᵢt)")
        
        if 'layer' in structure.patterns:
            formulas.append("y = f_n(...f_2(f_1(x)))")
        
        return " | ".join(formulas) if formulas else "f: X -> Y"
    
    def _calculate_confidence(self, structure: LogicalStructure, code: str) -> float:
        """Calculate extraction confidence score"""
        # Architectural placeholder: Initialize score to preserve semantic structure
        # for incremental confidence calculation and future multi-stage scoring
        score = 0.0
        
        # Pattern confidence
        pattern_score = min(len(structure.patterns) * 0.15, 0.45)
        
        # Concept confidence
        concept_score = min(len(structure.concepts) * 0.10, 0.30)
        
        # Relationship confidence
        rel_count = sum(len(v) for v in structure.relationships.values())
        rel_score = min(rel_count * 0.02, 0.20)
        
        # Code quality indicators
        code_len = len(code)
        quality_score = 0.0
        if code_len > 1000:
            quality_score = 0.05
        
        score = pattern_score + concept_score + rel_score + quality_score
        
        return min(score, 1.0)
    
    def extract_multi_language(
        self,
        snippets: List[tuple]
    ) -> List[LogicalStructure]:
        """
        Extract from multiple code snippets
        
        Args:
            snippets: List of (code, language) tuples
            
        Returns:
            List of logical structures
        """
        structures = []
        
        for code, language in snippets:
            structure = self.extract(code, language)
            structures.append(structure)
        
        return structures


# CLI Interface
if __name__ == '__main__':
    # Test with sample code
    test_code = """
    class AttentionLayer:
        def forward(self, query, key, value):
            # Compute attention scores
            scores = torch.matmul(query, key.transpose(-2, -1))
            scores = scores / math.sqrt(self.d_k)
            
            # Apply softmax
            attn = F.softmax(scores, dim=-1)
            
            # Weighted sum
            output = torch.matmul(attn, value)
            return output
    
    class MemoryBank:
        def __init__(self):
            self.storage = {}
            self.merkle_chain = []
        
        def commit(self, key, value):
            # Store in memory
            self.storage[key] = value
            
            # Update merkle chain
            prev_hash = self.merkle_chain[-1] if self.merkle_chain else "0"
            new_hash = sha256(key + value + prev_hash)
            self.merkle_chain.append(new_hash)
        
        def verify(self):
            # Verify merkle chain integrity
            for i in range(1, len(self.merkle_chain)):
                # Verify link
                pass
    """
    
    extractor = LogicalExtractor()
    structure = extractor.extract(test_code, "Python")
    
    print("=== Logical Structure ===")
    print(f"Patterns: {structure.patterns}")
    print(f"Concepts: {structure.concepts}")
    print(f"Reasoning: {structure.reasoning_chains}")
    print(f"Formula: {structure.formula}")
    print(f"Confidence: {structure.confidence:.2%}")
