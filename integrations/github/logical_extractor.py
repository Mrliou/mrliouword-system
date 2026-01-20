#!/usr/bin/env python3
"""
Logical Structure Extractor - 邏輯架構提取器

從代碼中提取邏輯架構：
- 核心概念 (Core Concepts)
- 因果關係 (Causal Relations)
- 推理鏈 (Reasoning Chains)
- 架構模式 (Architectural Patterns)

支援跨語言：Python, TypeScript, JavaScript, Shell, Markdown

Author: MR.liou
"""

import re
import os
import ast
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LogicalStructure:
    """邏輯架構"""
    concepts: List[str]                    # 核心概念
    patterns: Dict[str, List[str]]         # 架構模式
    relationships: List[Dict]              # 因果關係
    reasoning_chains: List[List[str]]      # 推理鏈
    functions: List[Dict]                  # 函數/類定義
    imports: List[str]                     # 依賴關係
    keywords: Set[str]                     # 關鍵字
    complexity: float                      # 複雜度分數


class LogicalStructureExtractor:
    """
    邏輯架構提取器
    
    核心功能：
    1. 提取代碼的邏輯架構
    2. 識別架構模式（attention, memory, particle 等）
    3. 分析因果關係和推理鏈
    4. 支援多語言
    """
    
    # 架構模式關鍵字
    PATTERN_KEYWORDS = {
        'attention_mechanism': [
            'attention', 'query', 'key', 'value', 'qkv', 'multihead',
            'self_attention', 'cross_attention', 'softmax', 'scaled_dot_product'
        ],
        'memory_system': [
            'memory', 'cache', 'buffer', 'storage', 'persist', 'recall',
            'remember', 'forget', 'merkle', 'chain', 'history'
        ],
        'particle_engine': [
            'particle', 'atom', 'granular', 'simhash', 'fingerprint',
            'vector', 'embedding', 'tensor', 'quantum'
        ],
        'frequency_resonance': [
            'frequency', 'resonance', 'harmonic', 'wave', 'oscillation',
            'schumann', 'phi', 'golden_ratio', 'vibration'
        ],
        'merkle_chain': [
            'merkle', 'hash', 'chain', 'tree', 'verification', 'integrity',
            'proof', 'root', 'leaf'
        ],
        'logical_reasoning': [
            'infer', 'deduce', 'reason', 'logic', 'causal', 'consequence',
            'therefore', 'because', 'if', 'then', 'implies'
        ]
    }
    
    def __init__(self):
        self.language_extractors = {
            'python': self._extract_python,
            'typescript': self._extract_typescript,
            'javascript': self._extract_javascript,
            'shell': self._extract_shell,
            'markdown': self._extract_markdown
        }
    
    def extract_from_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> Dict:
        """
        提取代碼的邏輯架構
        
        Args:
            code: 代碼內容
            language: 編程語言
            file_path: 可選檔案路徑
            
        Returns:
            邏輯架構字典
        """
        language = language.lower()
        
        # 選擇對應的提取器
        extractor = self.language_extractors.get(language, self._extract_generic)
        
        # 提取基礎結構
        structure = extractor(code, file_path)
        
        # 識別架構模式
        structure['patterns'] = self._identify_patterns(code, structure)
        
        # 提取推理鏈
        structure['reasoning_chains'] = self._extract_reasoning_chains(code, structure)
        
        # 計算複雜度
        structure['complexity'] = self._compute_complexity(structure)
        
        return structure
    
    def _extract_python(self, code: str, file_path: Optional[str]) -> Dict:
        """提取 Python 代碼結構"""
        structure = {
            'concepts': [],
            'functions': [],
            'imports': [],
            'relationships': [],
            'keywords': set()
        }
        
        try:
            tree = ast.parse(code)
            
            # 提取導入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        structure['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        if module:
                            structure['imports'].append(f"{module}.{alias.name}")
                        else:
                            structure['imports'].append(alias.name)
                
                # 提取函數和類
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        'type': 'function',
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'lineno': node.lineno,
                        'docstring': ast.get_docstring(node) or ''
                    }
                    structure['functions'].append(func_info)
                    structure['concepts'].append(node.name)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'type': 'class',
                        'name': node.name,
                        'bases': [self._get_name(base) for base in node.bases],
                        'lineno': node.lineno,
                        'docstring': ast.get_docstring(node) or ''
                    }
                    structure['functions'].append(class_info)
                    structure['concepts'].append(node.name)
                    
                    # 提取類中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'type': 'method',
                                'class': node.name,
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'lineno': item.lineno
                            }
                            structure['functions'].append(method_info)
            
            # 提取關鍵字（變數名、函數調用等）
            structure['keywords'] = self._extract_keywords(code)
            
            # 提取因果關係（if-then, try-except 等）
            structure['relationships'] = self._extract_relationships_python(tree)
            
        except SyntaxError as e:
            print(f"Python 語法錯誤: {e}")
        
        return structure
    
    def _extract_typescript(self, code: str, file_path: Optional[str]) -> Dict:
        """提取 TypeScript/JavaScript 代碼結構"""
        structure = {
            'concepts': [],
            'functions': [],
            'imports': [],
            'relationships': [],
            'keywords': set()
        }
        
        # 提取導入
        import_pattern = r'import\s+(?:{[^}]+}|[\w]+)\s+from\s+["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, code):
            structure['imports'].append(match.group(1))
        
        # 提取函數定義
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'(\w+)\s*\([^)]*\)\s*{',  # 類方法
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, code):
                func_name = match.group(1)
                structure['functions'].append({
                    'type': 'function',
                    'name': func_name,
                    'lineno': code[:match.start()].count('\n') + 1
                })
                structure['concepts'].append(func_name)
        
        # 提取類定義
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            base_class = match.group(2)
            structure['functions'].append({
                'type': 'class',
                'name': class_name,
                'bases': [base_class] if base_class else [],
                'lineno': code[:match.start()].count('\n') + 1
            })
            structure['concepts'].append(class_name)
        
        # 提取關鍵字
        structure['keywords'] = self._extract_keywords(code)
        
        # 提取因果關係
        structure['relationships'] = self._extract_relationships_generic(code)
        
        return structure
    
    def _extract_javascript(self, code: str, file_path: Optional[str]) -> Dict:
        """JavaScript 使用與 TypeScript 相同的提取器"""
        return self._extract_typescript(code, file_path)
    
    def _extract_shell(self, code: str, file_path: Optional[str]) -> Dict:
        """提取 Shell 腳本結構"""
        structure = {
            'concepts': [],
            'functions': [],
            'imports': [],
            'relationships': [],
            'keywords': set()
        }
        
        # 提取函數定義
        func_pattern = r'function\s+(\w+)|(\w+)\s*\(\)\s*{'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1) or match.group(2)
            structure['functions'].append({
                'type': 'function',
                'name': func_name,
                'lineno': code[:match.start()].count('\n') + 1
            })
            structure['concepts'].append(func_name)
        
        # 提取外部命令（視為依賴）
        command_pattern = r'\b(git|npm|pip|docker|kubectl|curl|wget)\s+'
        for match in re.finditer(command_pattern, code):
            structure['imports'].append(match.group(1))
        
        structure['keywords'] = self._extract_keywords(code)
        structure['relationships'] = self._extract_relationships_generic(code)
        
        return structure
    
    def _extract_markdown(self, code: str, file_path: Optional[str]) -> Dict:
        """從 Markdown 文檔提取概念"""
        structure = {
            'concepts': [],
            'functions': [],
            'imports': [],
            'relationships': [],
            'keywords': set()
        }
        
        # 提取標題作為概念
        heading_pattern = r'^#+\s+(.+)$'
        for match in re.finditer(heading_pattern, code, re.MULTILINE):
            concept = match.group(1).strip()
            structure['concepts'].append(concept)
        
        # 提取代碼塊
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(code_block_pattern, code, re.DOTALL):
            lang = match.group(1) or 'unknown'
            if lang in self.language_extractors:
                # 遞歸提取代碼塊內容
                block_code = match.group(2)
                block_structure = self.extract_from_code(block_code, lang)
                structure['functions'].extend(block_structure['functions'])
                structure['imports'].extend(block_structure['imports'])
        
        structure['keywords'] = self._extract_keywords(code)
        
        return structure
    
    def _extract_generic(self, code: str, file_path: Optional[str]) -> Dict:
        """通用提取器（未知語言）"""
        return {
            'concepts': [],
            'functions': [],
            'imports': [],
            'relationships': [],
            'keywords': self._extract_keywords(code)
        }
    
    def _extract_keywords(self, code: str) -> Set[str]:
        """提取關鍵字（識別符、常量名等）"""
        # 提取識別符（變數名、函數名等）
        identifier_pattern = r'\b([a-z_][a-z0-9_]*)\b'
        keywords = set(re.findall(identifier_pattern, code.lower()))
        
        # 過濾常見停用詞
        stopwords = {
            'if', 'else', 'for', 'while', 'return', 'const', 'let', 'var',
            'function', 'class', 'import', 'from', 'as', 'is', 'in', 'and',
            'or', 'not', 'true', 'false', 'null', 'undefined', 'this', 'self'
        }
        
        return keywords - stopwords
    
    def _identify_patterns(self, code: str, structure: Dict) -> Dict[str, List[str]]:
        """識別架構模式"""
        patterns = {}
        
        code_lower = code.lower()
        all_keywords = structure['keywords'] | {
            func['name'].lower() for func in structure['functions']
        } | {
            concept.lower() for concept in structure['concepts']
        }
        
        for pattern_name, pattern_keywords in self.PATTERN_KEYWORDS.items():
            matches = []
            for keyword in pattern_keywords:
                # 檢查關鍵字是否出現在代碼中
                if keyword in code_lower or keyword in all_keywords:
                    matches.append(keyword)
            
            if matches:
                patterns[pattern_name] = matches
        
        return patterns
    
    def _extract_relationships_python(self, tree: ast.AST) -> List[Dict]:
        """提取 Python 代碼的因果關係"""
        relationships = []
        
        for node in ast.walk(tree):
            # if-else 關係
            if isinstance(node, ast.If):
                condition = ast.unparse(node.test) if hasattr(ast, 'unparse') else 'condition'
                relationships.append({
                    'type': 'conditional',
                    'condition': condition,
                    'lineno': node.lineno
                })
            
            # try-except 關係
            elif isinstance(node, ast.Try):
                relationships.append({
                    'type': 'error_handling',
                    'lineno': node.lineno
                })
            
            # 函數調用關係
            elif isinstance(node, ast.Call):
                func_name = self._get_name(node.func)
                relationships.append({
                    'type': 'function_call',
                    'function': func_name,
                    'lineno': node.lineno
                })
        
        return relationships
    
    def _extract_relationships_generic(self, code: str) -> List[Dict]:
        """提取通用因果關係（基於模式匹配）"""
        relationships = []
        
        # if-then 模式
        if_pattern = r'\bif\s*\('
        for match in re.finditer(if_pattern, code):
            relationships.append({
                'type': 'conditional',
                'lineno': code[:match.start()].count('\n') + 1
            })
        
        # try-catch 模式
        try_pattern = r'\btry\s*{'
        for match in re.finditer(try_pattern, code):
            relationships.append({
                'type': 'error_handling',
                'lineno': code[:match.start()].count('\n') + 1
            })
        
        return relationships
    
    def _extract_reasoning_chains(
        self,
        code: str,
        structure: Dict
    ) -> List[List[str]]:
        """
        提取推理鏈
        
        根據函數調用順序、因果關係等構建推理鏈
        """
        chains = []
        
        # 簡單實現：根據函數定義順序構建鏈
        functions = [func['name'] for func in structure['functions']]
        if len(functions) >= 2:
            # 每連續 3 個函數構成一個推理鏈
            for i in range(len(functions) - 2):
                chain = functions[i:i+3]
                chains.append(chain)
        
        return chains
    
    def _compute_complexity(self, structure: Dict) -> float:
        """
        計算代碼複雜度分數（0-1）
        
        考慮因素：
        - 函數數量
        - 關係數量
        - 導入數量
        - 概念數量
        """
        num_functions = len(structure.get('functions', []))
        num_relationships = len(structure.get('relationships', []))
        num_imports = len(structure.get('imports', []))
        num_concepts = len(structure.get('concepts', []))
        
        # 加權計算
        complexity = (
            num_functions * 0.3 +
            num_relationships * 0.25 +
            num_imports * 0.15 +
            num_concepts * 0.3
        ) / 100.0  # 正規化到 0-1
        
        return min(complexity, 1.0)
    
    def _get_name(self, node) -> str:
        """獲取 AST 節點名稱"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return str(type(node).__name__)
    
    def match_logical_patterns(
        self,
        local_structures: List[Dict],
        remote_structures: List[Dict],
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """
        匹配本地和遠端的邏輯架構模式
        
        Args:
            local_structures: 本地代碼結構列表
            remote_structures: 遠端代碼結構列表
            similarity_threshold: 相似度閾值
            
        Returns:
            匹配結果列表
        """
        matches = []
        
        for remote in remote_structures:
            remote_patterns = set(remote.get('patterns', {}).keys())
            
            for local in local_structures:
                local_patterns = set(local.get('patterns', {}).keys())
                
                # 計算模式重疊度
                if not remote_patterns or not local_patterns:
                    continue
                
                overlap = len(remote_patterns & local_patterns)
                total = len(remote_patterns | local_patterns)
                similarity = overlap / total if total > 0 else 0
                
                if similarity >= similarity_threshold:
                    matches.append({
                        'local': local,
                        'remote': remote,
                        'similarity': similarity,
                        'shared_patterns': list(remote_patterns & local_patterns)
                    })
        
        # 按相似度排序
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches


# 測試
if __name__ == '__main__':
    extractor = LogicalStructureExtractor()
    
    # 測試 Python 代碼
    python_code = """
import numpy as np
from typing import List

class AttentionMechanism:
    '''多頭注意力機制'''
    
    def __init__(self, dim: int, num_heads: int):
        self.dim = dim
        self.num_heads = num_heads
    
    def forward(self, query, key, value):
        # 計算注意力分數
        scores = query @ key.T
        weights = self.softmax(scores)
        return weights @ value
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()
"""
    
    structure = extractor.extract_from_code(python_code, 'python')
    
    print("=== Logical Structure ===")
    print(json.dumps({
        'concepts': structure['concepts'],
        'patterns': structure['patterns'],
        'functions': structure['functions'],
        'complexity': structure['complexity']
    }, indent=2, ensure_ascii=False))
