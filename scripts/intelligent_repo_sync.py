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
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from tempfile import mkdtemp
from uuid import uuid4
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from integrations.github.logical_extractor import LogicalStructureExtractor
from integrations.webgpu.attention_filter import AttentionFilter
from integrations.particle.test_recorder import ParticleTestRecorder
from integrations.particle.naming_engine import ParticleNamingEngine
from integrations.particle.memory_storage import ParticleMemoryStorage
from modules.MRL_SystemA_ParticleLayer import UNSIGNED_PENDING
from scripts.global_github_search import GitHubRateLimitError, GitHubSearchEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

NAMING_PATTERNS = {
    'attention_mechanism': 'attention',
    'memory_system': 'memory',
    'merkle_chain': 'merkle',
    'particle_engine': 'particle',
}

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
        self.logical_extractor = LogicalStructureExtractor()
        self.attention_filter = AttentionFilter(
            embedding_dim=self.config.get('attention', {}).get('embedding_dim', 128),
            num_heads=self.config.get('attention', {}).get('num_heads', 4)
        )

        # Each invocation stages new candidates in a fresh directory for Owner review.
        candidate_root = Path('sync_candidates')
        if candidate_root.is_symlink():
            raise ValueError("sync_candidates must be a local directory")
        candidate_root.mkdir(exist_ok=True)
        self.candidate_dir = Path(mkdtemp(prefix='run-', dir=candidate_root)).absolute()
        self.naming_engine = ParticleNamingEngine(
            storage_path=str(self.candidate_dir / 'naming_history')
        )
        self.memory_storage = ParticleMemoryStorage(
            storage_path=str(self.candidate_dir / 'particle_memory')
        )

        logger.info("IntelligentRepoSync initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config not found: {self.config_path}, using defaults")
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.warning(
                    f"Failed to parse YAML config {self.config_path}: {e}. Using defaults"
                )
                return self._default_config()
        
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
        session_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info("Sync session %s, pattern %s", session_id, pattern)

        snippets = []
        structures = []
        attention_pairs = 0
        test_results = {}
        naming_decisions = 0
        particles_created = 0
        errors = []
        rate_limit = None
        stage = 'GitHub search'
        try:
            github_config = self.config.get('github', {})
            snippets = self.search_engine.search_code(
                pattern=pattern,
                languages=github_config.get('languages'),
                limit=limit or github_config.get('max_results', 30),
                min_stars=github_config.get('min_stars', 10),
                exclude_forks=github_config.get('exclude_forks', True),
            )
            if not snippets:
                raise ValueError('No results from GitHub search')

            stage = 'Logical extraction'
            for snippet in snippets:
                structure = self.logical_extractor.extract_from_code(
                    code=snippet.code, language=snippet.language, file_path=snippet.path
                )
                structure['keywords'] = sorted(structure['keywords'])
                source = {
                    'repo': snippet.repo,
                    'path': snippet.path,
                    'url': snippet.url,
                    'language': snippet.language,
                    'original_name': snippet.original_name or PurePosixPath(snippet.path).name,
                    'commit_sha': snippet.commit_sha,
                    'blob_sha': snippet.blob_sha,
                    'source_provenance': UNSIGNED_PENDING,
                }
                structures.append((structure, source))

            stage = 'Attention'
            texts = [
                ' '.join([source['repo'], *structure['patterns']])
                for structure, source in structures
            ]
            threshold = self.config.get('attention', {}).get('similarity_threshold', 0.5)
            attention_pairs = len(self.attention_filter.filter_by_attention(texts, threshold))

            stage = 'Particle validation'
            if self.config.get('testing', {}).get('enabled', True):
                test_dir = self.candidate_dir / 'test_results' / session_id
                recorder = ParticleTestRecorder(storage_path=str(test_dir))
                result = await recorder.run_all_tests()
                with (test_dir / 'report.json').open('w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
                test_results = {
                    'session_id': result.session_id,
                    'total': result.total_tests,
                    'passed': result.passed,
                    'failed': result.failed,
                    'errors': result.errors,
                }
                if not result.passed_all:
                    raise ValueError(f'{result.passed}/{result.total_tests} tests passed; expected 7/7')
            else:
                test_results = {'status': 'skipped'}

            for structure, source in structures:
                stage = 'Candidate naming'
                patterns = list(structure['patterns'])
                decision = self.naming_engine.generate_name(
                    patterns=[NAMING_PATTERNS.get(pattern, pattern) for pattern in patterns],
                    concepts=structure['concepts'],
                    reasoning_chains=[' '.join(chain) for chain in structure['reasoning_chains']],
                    source_info=source,
                )
                naming_decisions += 1

                stage = 'Candidate storage'
                self.memory_storage.store(
                    name=decision.particle_name,
                    particle_type=decision.particle_type,
                    content=json.dumps(structure, indent=2, ensure_ascii=False),
                    source_info=source,
                    tags=patterns + structure['concepts'],
                    metadata={
                        'naming_version': decision.version,
                        'naming_confidence': decision.confidence,
                        'owner_review': 'PENDING',
                    },
                    deduplicate=False,
                )
                particles_created += 1

            stage = 'Candidate Merkle verification'
            valid, merkle_errors = self.memory_storage.verify_merkle_chain()
            if not valid:
                raise ValueError('; '.join(merkle_errors))
        except Exception as exc:
            logger.exception("%s failed for pattern %s", stage, pattern)
            errors.append(f"{stage}: {exc}")
            if isinstance(exc, GitHubRateLimitError):
                rate_limit = exc.details

        report = self._create_report(
            session_id=session_id,
            timestamp=timestamp,
            pattern=pattern,
            github_results=len(snippets),
            extracted_structures=len(structures),
            particles_created=particles_created,
            test_results=test_results,
            naming_decisions=naming_decisions,
            errors=errors,
        )
        report.summary['attention_pairs'] = attention_pairs
        report.summary['owner_review'] = 'PENDING'
        report.summary['storage_scope'] = 'candidate'
        if rate_limit is not None:
            report.summary['github_rate_limit'] = rate_limit
        self._save_report(report)
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
            'success': not errors
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
            errors=errors or [],
            summary=summary
        )
    
    def _save_report(self, report: SyncReport):
        """Save sync report"""
        reports_dir = self.candidate_dir / 'sync_reports'
        reports_dir.mkdir(exist_ok=True)
        report_file = reports_dir / f"sync_{report.session_id}.json"
        with report_file.open('w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info("Report saved: %s", report_file)

    async def sync_all_patterns(self, limit: Optional[int] = None) -> List[SyncReport]:
        """Sync all patterns from config"""
        patterns = self.config.get('patterns', [])
        reports = []
        blocked_by_pattern = None
        
        for pattern in patterns:
            logger.info(f"\n{'='*80}")
            logger.info(f"Syncing pattern: {pattern}")
            logger.info(f"{'='*80}\n")
            
            if blocked_by_pattern is None:
                report = await self.sync_pattern(pattern, limit)
                if 'github_rate_limit' in report.summary:
                    blocked_by_pattern = pattern
            else:
                report = self._create_report(
                    session_id=str(uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    pattern=pattern,
                    errors=[f'Skipped after GitHub rate limit in pattern {blocked_by_pattern}'],
                )
                report.summary.update(
                    storage_scope='candidate',
                    owner_review='PENDING',
                    status='SKIPPED_RATE_LIMIT',
                    blocked_by_pattern=blocked_by_pattern,
                )
                self._save_report(report)
            reports.append(report)

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
    
    if not args.pattern and not args.all:
        parser.print_help()
        return 0

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
        return 0 if report.summary['success'] else 1

    else:
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
        return 0 if reports and all(report.summary['success'] for report in reports) else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
