#!/usr/bin/env python3
"""
Attention Filter (WebGPU-inspired)
===================================

Compute vector embeddings and attention similarity for code snippets.

Features:
- Frequency-based embeddings (Schumann 7.83Hz)
- Multi-head attention similarity
- Cosine similarity matrix
- Integration with VectorCore and AttentionEngine

Author: MR.liou
"""

import math
import logging
from typing import List, Tuple
import numpy as np
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from index.ts
SCHUMANN = 7.83
PHI = 1.618033988749895

FREQ = {
    'L∞': SCHUMANN * PHI ** 7,
    'L7': SCHUMANN * PHI ** 6,
    'L6': SCHUMANN * PHI ** 5,
    'L5': SCHUMANN * PHI ** 4,
    'L4': SCHUMANN * PHI ** 3,
    'L3': SCHUMANN * PHI ** 2,
    'L2': SCHUMANN * PHI,
    'L1': SCHUMANN,
    'L0': SCHUMANN / PHI
}

@dataclass
class AttentionScore:
    """Attention similarity score"""
    snippet_a: int
    snippet_b: int
    similarity: float
    layer: str
    frequency: float


class VectorCore:
    """High-performance vector operations (Python equivalent of TS VectorCore)"""
    
    @staticmethod
    def dot(a: np.ndarray, b: np.ndarray) -> float:
        """Compute dot product"""
        return float(np.dot(a, b))
    
    @staticmethod
    def norm(v: np.ndarray) -> float:
        """Compute L2 norm"""
        return float(np.linalg.norm(v))
    
    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity"""
        dot_product = VectorCore.dot(a, b)
        norm_a = VectorCore.norm(a)
        norm_b = VectorCore.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    @staticmethod
    def softmax(scores: np.ndarray) -> np.ndarray:
        """Numerically stable softmax"""
        # Subtract max for numerical stability
        max_score = np.max(scores)
        exp_scores = np.exp(scores - max_score)
        sum_exp = np.sum(exp_scores)
        
        if sum_exp == 0:
            return np.zeros_like(scores)
        
        return exp_scores / sum_exp


class AttentionFilter:
    """Attention-based similarity filter for code snippets"""
    
    def __init__(self, embedding_dim: int = 128, num_heads: int = 4):
        """
        Initialize attention filter
        
        Args:
            embedding_dim: Embedding dimension
            num_heads: Number of attention heads
        """
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads
        
        logger.info(f"AttentionFilter: dim={embedding_dim}, heads={num_heads}")
    
    def compute_embedding(self, text: str, base_freq: float = SCHUMANN) -> np.ndarray:
        """
        Compute frequency-based embedding for text
        
        Uses Schumann resonance (7.83Hz) as base frequency
        
        Args:
            text: Input text
            base_freq: Base frequency (default: SCHUMANN)
            
        Returns:
            Embedding vector
        """
        # Character frequency analysis
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Normalize frequencies
        total = sum(char_freq.values())
        if total == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        # Build embedding using frequency modulation
        embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        
        for i in range(self.embedding_dim):
            # Frequency component
            freq = base_freq * (PHI ** (i % 7))
            
            # Phase from character distribution
            phase = 0.0
            for char, count in char_freq.items():
                char_phase = (ord(char) / 128.0) * 2 * math.pi
                phase += (count / total) * math.sin(char_phase + i)
            
            # Amplitude modulation
            amplitude = math.sqrt(total / (len(text) + 1))
            
            # Combine
            embedding[i] = amplitude * math.cos(2 * math.pi * freq * phase / SCHUMANN)
        
        # Normalize
        norm = VectorCore.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def multi_head_attention(
        self,
        query: np.ndarray,
        key: np.ndarray,
        value: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Multi-head attention mechanism
        
        Args:
            query: Query vector
            key: Key vector
            value: Value vector
            
        Returns:
            (output, attention_weights)
        """
        # Reshape for multi-head
        # For simplicity, treating as single sequence
        
        # Compute attention scores
        # Note: Single sequence, so attention weight is 1.0
        attn_weights = np.array([1.0], dtype=np.float32)
        
        # Weighted sum
        output = attn_weights[0] * value
        
        return output, attn_weights
    
    def compute_similarity_matrix(
        self,
        embeddings: List[np.ndarray]
    ) -> np.ndarray:
        """
        Compute pairwise similarity matrix
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Similarity matrix (n x n)
        """
        n = len(embeddings)
        similarity_matrix = np.zeros((n, n), dtype=np.float32)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                elif i < j:
                    sim = VectorCore.cosine_similarity(embeddings[i], embeddings[j])
                    similarity_matrix[i, j] = sim
                    similarity_matrix[j, i] = sim
        
        return similarity_matrix
    
    def filter_by_attention(
        self,
        texts: List[str],
        threshold: float = 0.5
    ) -> List[AttentionScore]:
        """
        Filter similar texts using attention mechanism
        
        Args:
            texts: List of text snippets
            threshold: Similarity threshold
            
        Returns:
            List of attention scores above threshold
        """
        # Compute embeddings
        embeddings = [self.compute_embedding(text) for text in texts]
        
        # Compute similarity matrix
        sim_matrix = self.compute_similarity_matrix(embeddings)
        
        # Extract high-similarity pairs
        scores = []
        n = len(texts)
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = sim_matrix[i, j]
                
                if similarity >= threshold:
                    # Determine layer based on similarity
                    layer = self._similarity_to_layer(similarity)
                    frequency = FREQ[layer]
                    
                    scores.append(AttentionScore(
                        snippet_a=i,
                        snippet_b=j,
                        similarity=float(similarity),
                        layer=layer,
                        frequency=frequency
                    ))
        
        # Sort by similarity (descending)
        scores.sort(key=lambda x: x.similarity, reverse=True)
        
        logger.info(f"Found {len(scores)} similar pairs (threshold={threshold})")
        
        return scores
    
    def _similarity_to_layer(self, similarity: float) -> str:
        """Map similarity score to frequency layer"""
        if similarity >= 0.9:
            return 'L1'
        elif similarity >= 0.75:
            return 'L2'
        elif similarity >= 0.6:
            return 'L3'
        elif similarity >= 0.4:
            return 'L4'
        else:
            return 'L5'
    
    def compute_attention_weights(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Compute attention weights for query against candidates
        
        Args:
            query_text: Query text
            candidate_texts: Candidate texts
            top_k: Return top K candidates
            
        Returns:
            List of (index, weight) tuples
        """
        # Compute embeddings
        query_emb = self.compute_embedding(query_text)
        candidate_embs = [self.compute_embedding(text) for text in candidate_texts]
        
        # Compute similarities
        similarities = []
        for i, cand_emb in enumerate(candidate_embs):
            sim = VectorCore.cosine_similarity(query_emb, cand_emb)
            similarities.append((i, float(sim)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Apply softmax to top-k
        top_sims = similarities[:top_k]
        scores = np.array([s[1] for s in top_sims], dtype=np.float32)
        weights = VectorCore.softmax(scores)
        
        # Combine indices with weights
        result = [(top_sims[i][0], float(weights[i])) for i in range(len(top_sims))]
        
        return result


# CLI Interface
if __name__ == '__main__':
    # Test
    filter = AttentionFilter(embedding_dim=128, num_heads=4)
    
    texts = [
        "This is an attention mechanism implementation",
        "This is an attention mechanism with multi-head",
        "Memory system for storing particles",
        "Merkle tree verification system",
        "Attention-based memory retrieval"
    ]
    
    print("=== Attention Filter Test ===\n")
    
    # Compute embeddings
    print("Computing embeddings...")
    for i, text in enumerate(texts):
        emb = filter.compute_embedding(text)
        print(f"Text {i}: dim={len(emb)}, norm={VectorCore.norm(emb):.4f}")
    
    # Filter by attention
    print("\n=== Similarity Filtering (threshold=0.5) ===")
    scores = filter.filter_by_attention(texts, threshold=0.5)
    
    for score in scores:
        print(f"Pair ({score.snippet_a}, {score.snippet_b}): "
              f"similarity={score.similarity:.3f}, "
              f"layer={score.layer}, freq={score.frequency:.2f}Hz")
    
    # Query attention
    print("\n=== Query Attention ===")
    query = "attention mechanism"
    weights = filter.compute_attention_weights(query, texts, top_k=3)
    
    for idx, weight in weights:
        print(f"Text {idx}: weight={weight:.4f}")
        print(f"  {texts[idx][:60]}...")
