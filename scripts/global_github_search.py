#!/usr/bin/env python3
"""
GitHub Global Search Engine
============================

Searches GitHub globally for logical architecture patterns using the GitHub Code Search API.

Features:
- Semantic query builder
- Multi-language support
- Code snippet extraction
- Rate limit handling

Author: MR.liou
"""

import base64
import hashlib
import os
import re
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import PurePosixPath
from urllib.parse import parse_qs, urlsplit
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FILE_LANGUAGES = {
    '.py': 'Python', '.pyw': 'Python',
    '.ts': 'TypeScript', '.tsx': 'TypeScript',
    '.js': 'JavaScript', '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.sh': 'Shell', '.bash': 'Shell', '.md': 'Markdown',
    '.go': 'Go', '.rs': 'Rust', '.java': 'Java',
}

@dataclass
class CodeSnippet:
    """Code snippet from GitHub search"""
    repo: str
    path: str
    language: str
    code: str
    url: str
    score: float
    original_name: Optional[str] = None
    commit_sha: Optional[str] = None
    blob_sha: Optional[str] = None
    
class GitHubSearchEngine:
    """GitHub Code Search API integration"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub search engine
        
        Args:
            token: GitHub personal access token (or from GITHUB_TOKEN env)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        # Validate token exists and warn if not provided
        if not self.token or not self.token.strip():
            logger.warning(
                "No GitHub token provided. API rate limits will be significantly lower "
                "(60 requests/hour vs 5000 requests/hour with authentication). "
                "Set GITHUB_TOKEN environment variable or provide token parameter."
            )
            self.token = None
        
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        self.rate_limit_remaining = 30
        self.rate_limit_reset = 0
        self._repo_star_counts: Dict[str, int] = {}
    
    def _check_rate_limit(self):
        """Check and wait for rate limit if needed"""
        if self.rate_limit_remaining == 0:
            wait_time = max(0, self.rate_limit_reset - time.time())
            if wait_time > 0:
                logger.warning(f"Rate limit low, waiting {wait_time:.0f}s")
                time.sleep(wait_time + 1)
    
    def _update_rate_limit(self, response):
        """Update rate limit from response headers"""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
    
    def build_query(
        self,
        pattern: str,
        language: Optional[str] = None,
        exclude_forks: bool = True
    ) -> str:
        """Build a GitHub REST code-search query for one language."""
        query_parts = [pattern]
        if language:
            query_parts.append(f'language:{language}')
        if not exclude_forks:
            query_parts.append('fork:true')
        return ' '.join(query_parts)
    
    def search_code(
        self,
        pattern: str,
        languages: Optional[List[str]] = None,
        limit: int = 30,
        min_stars: int = 10,
        exclude_forks: bool = True
    ) -> List[CodeSnippet]:
        """
        Search GitHub code globally
        
        Args:
            pattern: Search pattern
            languages: Filter languages
            limit: Maximum results
            min_stars: Minimum stars
            exclude_forks: Exclude forked repositories
            
        Returns:
            List of code snippets
        """
        url = f'{self.base_url}/search/code'
        results_by_language = []
        for language in dict.fromkeys(languages or [None]):
            query = self.build_query(pattern, language, exclude_forks)
            logger.info("Searching GitHub: %s", query)
            self._check_rate_limit()
            params = {'q': query, 'per_page': min(limit, 100)}
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self._update_rate_limit(response)
            response.raise_for_status()
            results_by_language.append([
                (language, item) for item in response.json()['items']
            ])

        # Take candidates in relevance order within each language and share the
        # overall limit across languages.
        snippets = []
        seen = set()
        for row in zip_longest(*results_by_language):
            for hit in row:
                if hit is None:
                    continue
                language, item = hit
                repository = item['repository']
                source_url = item['html_url']
                blob_sha = item['sha']
                source_identity = (source_url, blob_sha)
                if source_identity in seen or (exclude_forks and repository.get('fork')):
                    continue
                if min_stars > 0 and self._get_repo_stars(repository) < min_stars:
                    continue
                contents_url = item['url']
                ref = parse_qs(urlsplit(contents_url).query).get('ref', [''])[0]
                path = PurePosixPath(item['path'])
                snippets.append(CodeSnippet(
                    repo=repository['full_name'],
                    path=item['path'],
                    language=item.get('language') or language or FILE_LANGUAGES.get(
                        path.suffix.lower(), 'Unknown'
                    ),
                    code=self._fetch_file_content(contents_url, blob_sha),
                    url=source_url,
                    score=item.get('score', 0.0),
                    original_name=item.get('name') or path.name,
                    commit_sha=ref if re.fullmatch(r'[a-f0-9]{40}', ref) else None,
                    blob_sha=blob_sha,
                ))
                seen.add(source_identity)
                if len(snippets) == limit:
                    return snippets
        return snippets

    def _get_repo_stars(self, repository: Dict) -> int:
        """Read repository metadata when a search result omits its star count."""
        name = repository['full_name']
        if name not in self._repo_star_counts:
            stars = repository.get('stargazers_count')
            if stars is None:
                response = requests.get(repository['url'], headers=self.headers, timeout=10)
                response.raise_for_status()
                stars = response.json()['stargazers_count']
            self._repo_star_counts[name] = stars
        return self._repo_star_counts[name]

    def _fetch_file_content(self, url: str, expected_blob_sha: str) -> str:
        """Verify the exact Git blob before decoding it for analysis."""
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        raw = base64.b64decode(response.json()['content'])
        blob_header = f'blob {len(raw)}\0'.encode('ascii')
        if hashlib.sha1(blob_header + raw).hexdigest() != expected_blob_sha:
            raise ValueError(f'Git blob SHA mismatch for {url}')
        return raw.decode('utf-8', errors='replace')
    
    def search_repositories(
        self,
        pattern: str,
        languages: Optional[List[str]] = None,
        limit: int = 10,
        min_stars: int = 100
    ) -> List[Dict]:
        """
        Search GitHub repositories
        
        Args:
            pattern: Search pattern
            languages: Filter languages
            limit: Maximum results
            min_stars: Minimum stars
            
        Returns:
            List of repository metadata
        """
        query_parts = [pattern]
        
        if languages:
            lang_queries = ' OR '.join([f'language:{lang}' for lang in languages])
            query_parts.append(f'({lang_queries})')
        
        if min_stars > 0:
            query_parts.append(f'stars:>={min_stars}')
        
        query = ' '.join(query_parts)
        logger.info(f"Searching repos: {query}")
        
        self._check_rate_limit()
        
        url = f'{self.base_url}/search/repositories'
        params = {
            'q': query,
            'per_page': min(limit, 100),
            'sort': 'stars',
            'order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self._update_rate_limit(response)
            response.raise_for_status()
            
            data = response.json()
            repos = []
            
            for item in data.get('items', [])[:limit]:
                repos.append({
                    'name': item['full_name'],
                    'description': item.get('description', ''),
                    'language': item.get('language', 'Unknown'),
                    'stars': item['stargazers_count'],
                    'url': item['html_url'],
                    'topics': item.get('topics', [])
                })
            
            logger.info(f"Found {len(repos)} repositories")
            return repos
            
        except Exception as e:
            logger.error(f"Repo search error: {e}")
            return []


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Global Search')
    parser.add_argument('pattern', help='Search pattern')
    parser.add_argument('--languages', nargs='+', help='Filter by languages')
    parser.add_argument('--limit', type=int, default=10, help='Max results')
    parser.add_argument('--stars', type=int, default=10, help='Min stars')
    
    args = parser.parse_args()
    
    engine = GitHubSearchEngine()
    snippets = engine.search_code(
        pattern=args.pattern,
        languages=args.languages,
        limit=args.limit,
        min_stars=args.stars
    )
    
    for snippet in snippets:
        print(f"\n{'='*80}")
        print(f"Repo: {snippet.repo}")
        print(f"Path: {snippet.path}")
        print(f"Language: {snippet.language}")
        print(f"URL: {snippet.url}")
        print(f"Score: {snippet.score}")
        print(f"\nCode Preview (first 500 chars):")
        print(snippet.code[:500])
