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

import os
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeSnippet:
    """Code snippet from GitHub search"""
    repo: str
    path: str
    language: str
    code: str
    url: str
    score: float
    
class GitHubSearchEngine:
    """GitHub Code Search API integration"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub search engine
        
        Args:
            token: GitHub personal access token (or from GITHUB_TOKEN env)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        self.rate_limit_remaining = 30
        self.rate_limit_reset = 0
    
    def _check_rate_limit(self):
        """Check and wait for rate limit if needed"""
        if self.rate_limit_remaining < 5:
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
        languages: Optional[List[str]] = None,
        min_stars: int = 10,
        exclude_forks: bool = True
    ) -> str:
        """
        Build semantic GitHub search query
        
        Args:
            pattern: Search pattern (e.g., "attention mechanism", "merkle tree")
            languages: Filter by languages (e.g., ["Python", "TypeScript"])
            min_stars: Minimum repository stars
            exclude_forks: Exclude forked repositories
            
        Returns:
            GitHub search query string
        """
        query_parts = [pattern]
        
        if languages:
            lang_queries = ' OR '.join([f'language:{lang}' for lang in languages])
            query_parts.append(f'({lang_queries})')
        
        if min_stars > 0:
            query_parts.append(f'stars:>={min_stars}')
        
        if exclude_forks:
            query_parts.append('fork:false')
        
        return ' '.join(query_parts)
    
    def search_code(
        self,
        pattern: str,
        languages: Optional[List[str]] = None,
        limit: int = 30,
        min_stars: int = 10
    ) -> List[CodeSnippet]:
        """
        Search GitHub code globally
        
        Args:
            pattern: Search pattern
            languages: Filter languages
            limit: Maximum results
            min_stars: Minimum stars
            
        Returns:
            List of code snippets
        """
        query = self.build_query(pattern, languages, min_stars)
        logger.info(f"Searching GitHub: {query}")
        
        self._check_rate_limit()
        
        url = f'{self.base_url}/search/code'
        params = {
            'q': query,
            'per_page': min(limit, 100),
            'sort': 'stars',
            'order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self._update_rate_limit(response)
            
            if response.status_code == 403:
                logger.error("Rate limit exceeded")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            snippets = []
            for item in data.get('items', [])[:limit]:
                # Fetch file content
                content = self._fetch_file_content(item['url'])
                if content:
                    snippets.append(CodeSnippet(
                        repo=item['repository']['full_name'],
                        path=item['path'],
                        language=item.get('language', 'Unknown'),
                        code=content,
                        url=item['html_url'],
                        score=item.get('score', 0.0)
                    ))
            
            logger.info(f"Found {len(snippets)} snippets")
            return snippets
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _fetch_file_content(self, url: str) -> Optional[str]:
        """Fetch file content from GitHub API"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                import base64
                content_b64 = response.json().get('content', '')
                return base64.b64decode(content_b64).decode('utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"Content fetch error: {e}")
        return None
    
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
