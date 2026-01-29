#!/usr/bin/env python3
"""
Intelligent Repository Synchronization Orchestrator
===================================================

Main controller for GitHub Global Logical Architecture Synchronization System.

Complete Sync Flow:
1. Search GitHub globally
2. Extract logical architecture
3. Compute attention similarity
4. Test particle access (7 tests)
5. Auto-rename/define particles
6. Store as particles
7. Generate sync report

Author: MR.liou
Philosophy: 怎麼過去，就怎麼回來
"""

import os
import sys
import json
import yaml
import logging
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from integrations.github.logical_extractor import LogicalExtractor
from integrations.webgpu.attention_filter import AttentionFilter
from integrations.particle.test_recorder import ParticleTestRecorder
from integrations.particle.naming_engine import ParticleNamingEngine
from integrations.particle.memory_storage import ParticleMemoryStorage
from scripts.global_github_search import GitHubSearchEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyncReport:
    """Synchronization report"""
    session_id: str
    timestamp: str
    pattern: str
    github_results: int
    extracted_structures: int
    particles_created: int
    particles_merged: int
    test_results: Dict
    naming_decisions: int
    errors: List[str]
    summary: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IntelligentRepoSync:
    """
    Intelligent Repository Synchronization Orchestrator
    
    Coordinates all components for GitHub logical architecture sync.
    """
    
    def __init__(self, config_path: str = './intelligent_sync.yaml'):
        """
        Initialize sync orchestrator
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.search_engine = GitHubSearchEngine(
            token=os.getenv('GITHUB_TOKEN')
        )
        self.logical_extractor = LogicalExtractor()
        self.attention_filter = AttentionFilter(
            embedding_dim=self.config.get('attention', {}).get('embedding_dim', 128),
            num_heads=self.config.get('attention', {}).get('num_heads', 4)
        )
        self.naming_engine = ParticleNamingEngine(
            storage_path=self.config.get('naming', {}).get('storage_path', './naming_history')
        )
        self.memory_storage = ParticleMemoryStorage(
            storage_path=self.config.get('particle_memory', {}).get('storage_path', './particle_memory')
        )
        
        self.errors = []
        
        logger.info("IntelligentRepoSync initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config not found: {self.config_path}, using defaults")
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded config from {self.config_path}")
        return config
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'github': {
                'min_stars': 10,
                'languages': ['Python', 'TypeScript', 'Go', 'Rust'],
                'exclude_forks': True,
                'max_results': 30
            },
            'patterns': [
                'attention mechanism',
                'merkle tree',
                'memory system',
                'particle system'
            ],
            'attention': {
                'embedding_dim': 128,
                'num_heads': 4,
                'similarity_threshold': 0.5
            },
            'particle_memory': {
                'storage_path': './particle_memory',
                'simhash_threshold': 3,
                'layer_assignment': {
                    'L1': 0.9,
                    'L2': 0.75,
                    'L3': 0.6,
                    'L4': 0.4
                }
            },
            'testing': {
                'enabled': True,
                'storage_path': './test_results'
            },
            'naming': {
                'storage_path': './naming_history',
                'auto_version': True
            }
        }
    
    async def sync_pattern(
        self,
        pattern: str,
        limit: Optional[int] = None
    ) -> SyncReport:
        """
        Synchronize a specific pattern from GitHub
        
        Args:
            pattern: Search pattern
            limit: Maximum results (overrides config)
            
        Returns:
            Sync report
        """
        import uuid
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        logger.info(f"="*80)
        logger.info(f"Sync Session: {session_id}")
        logger.info(f"Pattern: {pattern}")
        logger.info(f"="*80)
        
        # Step 1: Search GitHub globally
        logger.info("Step 1: Searching GitHub...")
        github_config = self.config.get('github', {})
        max_results = limit or github_config.get('max_results', 30)
        
        snippets = self.search_engine.search_code(
            pattern=pattern,
            languages=github_config.get('languages'),
            limit=max_results,
            min_stars=github_config.get('min_stars', 10)
        )
        
        logger.info(f"Found {len(snippets)} code snippets")
        
        if not snippets:
            logger.warning("No results from GitHub search")
            return self._create_report(
                session_id, timestamp, pattern,
                github_results=0,
                errors=['No results from GitHub search']
            )
        
        # Step 2: Extract logical architecture
        logger.info("Step 2: Extracting logical architecture...")
        structures = []
        
        for snippet in snippets:
            try:
                structure = self.logical_extractor.extract(
                    code=snippet.code,
                    language=snippet.language
                )
                
                # Add source info
                structure_dict = structure.to_dict()
                structure_dict['source_info'] = {
                    'repo': snippet.repo,
                    'path': snippet.path,
                    'url': snippet.url,
                    'language': snippet.language
                }
                
                structures.append(structure_dict)
                
            except Exception as e:
                logger.error(f"Extraction error: {e}")
                self.errors.append(f"Extraction error for {snippet.repo}: {str(e)}")
        
        logger.info(f"Extracted {len(structures)} logical structures")
        
        # Step 3: Compute attention similarity
        logger.info("Step 3: Computing attention similarity...")
        try:
            texts = [s['source_info']['repo'] + ' ' + ' '.join(s['patterns']) 
                    for s in structures]
            
            similarity_threshold = self.config.get('attention', {}).get('similarity_threshold', 0.5)
            # Architectural placeholder: Preserve attention scores for future
            # particle similarity analysis and world-model consistency
            attention_scores = self.attention_filter.filter_by_attention(
                texts,
                threshold=similarity_threshold
            )
            similar_pairs = attention_scores
            
            logger.info(f"Found {len(similar_pairs)} similar pairs")
            
        except Exception as e:
            logger.error(f"Attention error: {e}")
            self.errors.append(f"Attention computation error: {str(e)}")
            # Maintain structure consistency even in error case
            attention_scores = []
        
        # Step 4: Test particle access (7 tests)
        test_results = {}
        
        if self.config.get('testing', {}).get('enabled', True):
            logger.info("Step 4: Running particle tests...")
            try:
                test_recorder = ParticleTestRecorder(
                    storage_path=self.config.get('testing', {}).get('storage_path', './test_results')
                )
                
                test_report = await test_recorder.run_all_tests()
                
                test_results = {
                    'session_id': test_report.session_id,
                    'total': test_report.total_tests,
                    'passed': test_report.passed,
                    'failed': test_report.failed,
                    'errors': test_report.errors
                }
                
                logger.info(f"Tests: {test_report.passed}/{test_report.total_tests} passed")
                
            except Exception as e:
                logger.error(f"Testing error: {e}")
                self.errors.append(f"Testing error: {str(e)}")
                test_results = {'error': str(e)}
        
        # Step 5: Auto-rename/define particles
        logger.info("Step 5: Generating particle names...")
        naming_decisions = []
        
        try:
            for structure in structures:
                decision = self.naming_engine.generate_name(
                    patterns=structure.get('patterns', []),
                    concepts=structure.get('concepts', []),
                    reasoning_chains=structure.get('reasoning_chains', []),
                    source_info=structure.get('source_info')
                )
                
                naming_decisions.append(decision)
                
                # Add naming to structure
                structure['particle_name'] = decision.particle_name
                structure['particle_type'] = decision.particle_type
            
            logger.info(f"Generated {len(naming_decisions)} particle names")
            
        except Exception as e:
            logger.error(f"Naming error: {e}")
            self.errors.append(f"Naming error: {str(e)}")
        
        # Step 6: Store as particles
        logger.info("Step 6: Storing particles...")
        particles_created = 0
        particles_merged = 0
        
        try:
            for structure in structures:
                # Prepare content
                content = json.dumps({
                    'patterns': structure.get('patterns', []),
                    'concepts': structure.get('concepts', []),
                    'reasoning_chains': structure.get('reasoning_chains', []),
                    'formula': structure.get('formula', ''),
                    'confidence': structure.get('confidence', 0.0)
                }, indent=2)
                
                # Store particle
                particle, is_new = self.memory_storage.store(
                    name=structure.get('particle_name', 'fx.logic.unknown'),
                    particle_type=structure.get('particle_type', 'fx.logic.general'),
                    content=content,
                    source_info=structure.get('source_info', {}),
                    tags=structure.get('patterns', []) + structure.get('concepts', []),
                    metadata={
                        'confidence': structure.get('confidence', 0.0),
                        'formula': structure.get('formula', '')
                    }
                )
                
                if is_new:
                    particles_created += 1
                else:
                    particles_merged += 1
            
            logger.info(f"Stored: {particles_created} new, {particles_merged} merged")
            
        except Exception as e:
            logger.error(f"Storage error: {e}")
            self.errors.append(f"Storage error: {str(e)}")
        
        # Step 7: Generate sync report
        logger.info("Step 7: Generating sync report...")
        
        report = self._create_report(
            session_id=session_id,
            timestamp=timestamp,
            pattern=pattern,
            github_results=len(snippets),
            extracted_structures=len(structures),
            particles_created=particles_created,
            particles_merged=particles_merged,
            test_results=test_results,
            naming_decisions=len(naming_decisions)
        )
        
        # Save report
        self._save_report(report)
        
        logger.info("="*80)
        logger.info(f"Sync complete: {particles_created + particles_merged} particles")
        logger.info("="*80)
        
        return report
    
    def _create_report(
        self,
        session_id: str,
        timestamp: str,
        pattern: str,
        github_results: int = 0,
        extracted_structures: int = 0,
        particles_created: int = 0,
        particles_merged: int = 0,
        test_results: Dict = None,
        naming_decisions: int = 0,
        errors: List[str] = None
    ) -> SyncReport:
        """Create sync report"""
        
        summary = {
            'total_particles': particles_created + particles_merged,
            'new_particles': particles_created,
            'merged_particles': particles_merged,
            'extraction_rate': f"{extracted_structures}/{github_results}" if github_results > 0 else "0/0",
            'success': len(errors or self.errors) == 0
        }
        
        return SyncReport(
            session_id=session_id,
            timestamp=timestamp,
            pattern=pattern,
            github_results=github_results,
            extracted_structures=extracted_structures,
            particles_created=particles_created,
            particles_merged=particles_merged,
            test_results=test_results or {},
            naming_decisions=naming_decisions,
            errors=errors or self.errors,
            summary=summary
        )
    
    def _save_report(self, report: SyncReport):
        """Save sync report"""
        reports_dir = './sync_reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        report_file = os.path.join(
            reports_dir,
            f"sync_{report.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved: {report_file}")
    
    async def sync_all_patterns(self, limit: Optional[int] = None) -> List[SyncReport]:
        """Sync all patterns from config"""
        patterns = self.config.get('patterns', [])
        reports = []
        
        for pattern in patterns:
            logger.info(f"\n{'='*80}")
            logger.info(f"Syncing pattern: {pattern}")
            logger.info(f"{'='*80}\n")
            
            try:
                report = await self.sync_pattern(pattern, limit)
                reports.append(report)
            except Exception as e:
                logger.error(f"Pattern sync failed: {e}")
        
        return reports


# CLI Interface
async def main():
    parser = argparse.ArgumentParser(
        description='Intelligent GitHub Repository Synchronization'
    )
    parser.add_argument(
        '--config',
        default='./intelligent_sync.yaml',
        help='Configuration file path'
    )
    parser.add_argument(
        '--pattern',
        help='Specific pattern to sync (overrides config)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum results per pattern'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Sync all patterns from config'
    )
    
    args = parser.parse_args()
    
    # Validate limit if provided
    if args.limit is not None:
        if args.limit < 1 or args.limit > 100:
            parser.error("--limit must be an integer from 1 to 100 (inclusive)")
    
    # Sanitize and validate pattern if provided
    if args.pattern is not None:
        sanitized_pattern = args.pattern.strip()
        if not sanitized_pattern:
            parser.error("--pattern must not be empty or whitespace-only")
        # Check for control characters (ASCII < 32 or DEL = 127)
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in sanitized_pattern):
            parser.error("--pattern contains invalid control characters")
        args.pattern = sanitized_pattern
    
    # Initialize orchestrator
    sync = IntelligentRepoSync(config_path=args.config)
    
    # Run sync
    if args.pattern:
        # Sync specific pattern
        report = await sync.sync_pattern(args.pattern, args.limit)
        
        # Print summary
        print("\n" + "="*80)
        print("SYNC REPORT")
        print("="*80)
        print(f"Pattern: {report.pattern}")
        print(f"GitHub Results: {report.github_results}")
        print(f"Extracted Structures: {report.extracted_structures}")
        print(f"Particles Created: {report.particles_created}")
        print(f"Particles Merged: {report.particles_merged}")
        print(f"Naming Decisions: {report.naming_decisions}")
        
        if report.test_results:
            print(f"\nTests: {report.test_results.get('passed', 0)}/{report.test_results.get('total', 0)} passed")
        
        if report.errors:
            print(f"\nErrors: {len(report.errors)}")
            for error in report.errors[:5]:
                print(f"  - {error}")
        
        print("="*80)
        
    elif args.all:
        # Sync all patterns
        reports = await sync.sync_all_patterns(args.limit)
        
        # Print summary
        print("\n" + "="*80)
        print("ALL PATTERNS SYNC SUMMARY")
        print("="*80)
        
        for report in reports:
            print(f"\n{report.pattern}:")
            print(f"  Results: {report.github_results}")
            print(f"  Particles: {report.particles_created + report.particles_merged}")
            print(f"  Errors: {len(report.errors)}")
        
        print("="*80)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())
