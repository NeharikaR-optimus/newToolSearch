
import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LANGSEARCH_API_KEY, LANGSEARCH_SEARCH_ENDPOINT

class SearchAgent:
    # Class constants
    GITHUB_DOMAIN = 'github.com'
    
    def search_tool(self, tool_name: str) -> List[Dict]:
        """
        Search for a specific tech tool with enhanced parameters for better results.
        """
        headers = {
            "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "query": f"{tool_name} developer programming tool technology",
            "freshness": "oneWeek",  # Focus on recent information
            "summary": True,
            "count": 3,  # Get multiple results for better coverage
            "safeSearch": "moderate",
            "market": "en-US"
        }
        
        try:
            response = requests.post(LANGSEARCH_SEARCH_ENDPOINT, headers=headers, json=body)
            if response.status_code != 200:
                print(f"LangSearch error for {tool_name}: {response.text}")
                return []
            
            data = response.json()
            results = data.get("data", {}).get("webPages", {}).get("value", [])
            
            # Apply content validation
            validated_results = [r for r in results if self._validate_content_quality(r)]
            return validated_results
            
        except Exception as e:
            print(f"Error searching for {tool_name}: {e}")
            return []
    def search_new_ai_tools(self) -> List[Dict]:
        """
        Uses LangSearch Web Search API to find fresh trending tech tools and developer news from the last 7 days.
        Covers all developer-relevant technology trends, not limited to AI.
        Uses dynamic, broad queries to maximize coverage with minimal API calls.
        """
        current_date = datetime.now()
        week_ago = current_date - timedelta(days=7)
        
        # Strategic diverse queries that capture trending developer tech from various ecosystems
        strategic_queries = [
            # AI and ML tools (beyond GitHub)
            "new AI developer tools 2025 trending -github.com programming artificial intelligence",
            
            # Web development frameworks and libraries
            "new web development framework 2025 react vue angular trending -github.com",
            
            # Mobile development and cross-platform tools
            "new mobile development tools 2025 flutter react-native kotlin swift trending",
            
            # DevOps and cloud tools
            "new devops tools 2025 kubernetes docker cloud deployment trending -github.com",
            
            # Programming languages and compilers
            "new programming language 2025 trending rust go python typescript compiler",
            
            # Database and backend innovations
            "new database technology 2025 trending nosql sql mongodb postgresql redis",
            
            # Developer productivity and IDEs
            "new developer productivity tools 2025 IDE editor vscode trending -github.com",
            
            # Security and testing tools
            "new cybersecurity tools 2025 testing framework developer trending -github.com"
        ]
        
        all_results = []
        
        for query in strategic_queries:
            headers = {
                "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Optimized LangSearch parameters for maximum relevant coverage
            body = {
                "query": query,
                "freshness": "oneWeek",  # Strictly last 7 days
                "summary": True,
                "count": 20,  # More results per strategic query
                "safeSearch": "moderate",
                "market": "en-US",
                "category": "ScienceAndTechnology",
                "sortBy": "date"
            }
            
            print(f"Executing strategic search: {query}")
            
            try:
                response = requests.post(LANGSEARCH_SEARCH_ENDPOINT, headers=headers, json=body)
                print(f"LangSearch response status: {response.status_code}")
                
                if response.status_code == 429:
                    print("Rate limit hit, waiting...")
                    time.sleep(5)
                    continue
                    
                if response.status_code != 200:
                    print(f"LangSearch error: {response.text}")
                    continue
                    
                data = response.json()
                results = data.get("data", {}).get("webPages", {}).get("value", [])
                
                # Validate freshness and quality
                validated_results = self._validate_freshness(results, week_ago)
                print(f"Strategic query returned {len(results)} results, {len(validated_results)} validated")
                
                all_results.extend(validated_results)
                
                # Brief delay between API calls
                time.sleep(1)
                
            except Exception as e:
                print(f"Error with strategic query: {e}")
                continue
        
        print(f"Total results from {len(strategic_queries)} strategic queries: {len(all_results)}")
        
        # Enhanced deduplication and intelligent scoring
        unique_results = self._deduplicate_and_score(all_results)
        
        print(f"Final curated results after deduplication: {len(unique_results)}")
        return unique_results[:15]  # Return top 15 most relevant results

    def _validate_freshness(self, results: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """
        Validates that search results are from the last 7 days by checking date published.
        """
        validated_results = []
        
        for result in results:
            if self._is_result_fresh(result, cutoff_date) and self._validate_content_quality(result):
                validated_results.append(result)
        
        return validated_results

    def _is_result_fresh(self, result: Dict, cutoff_date: datetime) -> bool:
        """
        Check if a single result is from the last 7 days.
        """
        date_published = result.get('dateLastCrawled') or result.get('datePublished')
        
        if not date_published:
            return True  # Include if no date info but will validate content separately
            
        try:
            if isinstance(date_published, str):
                if 'T' in date_published:
                    result_date = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
                else:
                    result_date = datetime.strptime(date_published[:10], '%Y-%m-%d')
                
                return result_date.replace(tzinfo=None) >= cutoff_date
        except Exception:
            return True  # Include if date parsing fails
            
        return False

    def _validate_content_quality(self, result: Dict) -> bool:
        """
        Intelligent content quality validation using dynamic scoring.
        """
        snippet = (result.get('snippet', '') + ' ' + result.get('name', '')).lower()
        url = result.get('url', '').lower()
        
        # Dynamic scoring system
        quality_score = 0
        
        # Trusted domains (weighted scoring with diversity promotion)
        trusted_domains = {
            # Tier 1: Official company sources (highest trust)
            'openai.com': 10, 'anthropic.com': 10, 'google.com': 9, 'microsoft.com': 9,
            'meta.com': 8, 'apple.com': 9, 'amazon.com': 8, 'netflix.com': 7,
            'huggingface.co': 8, 'pytorch.org': 8, 'tensorflow.org': 8,
            
            # Tier 2: Tech news and communities (high trust)
            'techcrunch.com': 8, 'theverge.com': 8, 'arstechnica.com': 8,
            'venturebeat.com': 7, 'wired.com': 7, 'hackernews.com': 7,
            'engadget.com': 6, 'zdnet.com': 6, 'cnet.com': 6,
            
            # Tier 3: Developer platforms (balanced scoring)
            'stackoverflow.com': 7, 'dev.to': 6, 'medium.com': 5,
            'producthunt.com': 6, 'kaggle.com': 6, 'reddit.com': 5,
            
            # Tier 4: Specialized tech platforms  
            'npmjs.com': 6, 'pypi.org': 6, 'crates.io': 6, 'packagist.org': 6,
            'dockerhub.com': 6, 'kubernetes.io': 7, 'apache.org': 7,
            
            # Reduced GitHub scoring to promote diversity
            self.GITHUB_DOMAIN: 4  # Reduced from 9 to 4 to allow other sources
        }
        
        # Check domain authority
        for domain, score in trusted_domains.items():
            if domain in url:
                quality_score += score
                break
        
        # Developer/Tech relevance indicators (broad tech ecosystem)
        relevance_indicators = {
            # Trending and viral indicators
            'trending': 4, 'viral': 4, 'popular': 3, 'breakthrough': 4,
            'game-changer': 4, 'revolutionary': 3, 'innovative': 3,
            
            # AI and ML (subset of broader tech)
            'ai': 2, 'artificial intelligence': 2, 'machine learning': 2,
            'neural network': 2, 'deep learning': 2, 'llm': 2, 'model': 2,
            
            # Web development and frameworks
            'react': 2, 'vue': 2, 'angular': 2, 'nodejs': 2, 'typescript': 2,
            'javascript': 2, 'python': 2, 'rust': 2, 'go': 2, 'kotlin': 2,
            
            # Developer tools and platforms
            'developer': 3, 'programming': 2, 'code': 2, 'api': 3,
            'open source': 3, 'github': 2, 'framework': 2, 'library': 2,
            'vscode': 2, 'docker': 2, 'kubernetes': 2, 'cloud': 2,
            
            # DevOps and infrastructure
            'devops': 2, 'ci/cd': 2, 'deployment': 2, 'microservices': 2,
            'serverless': 2, 'aws': 2, 'azure': 2, 'gcp': 2,
            
            # Mobile and emerging tech
            'mobile': 2, 'ios': 2, 'android': 2, 'flutter': 2, 'react native': 2,
            'blockchain': 2, 'web3': 2, 'cryptocurrency': 2, 'nft': 1,
            
            # Database and backend
            'database': 2, 'sql': 2, 'nosql': 2, 'mongodb': 2, 'postgresql': 2,
            'redis': 2, 'elasticsearch': 2, 'graphql': 2, 'rest api': 2,
            
            # Freshness and news indicators
            'announcement': 3, 'launch': 3, 'release': 3, 'beta': 2,
            'new': 2, 'latest': 2, 'just': 3, 'breaking': 4,
            
            # General tech ecosystem
            'startup': 2, 'funding': 2, 'acquisition': 2, 'partnership': 2,
            'innovation': 2, 'technology': 1, 'tech': 1, 'software': 1
        }
        
        # Calculate relevance score
        for term, score in relevance_indicators.items():
            if term in snippet:
                quality_score += score
        
        # Freshness indicators bonus
        freshness_terms = ['new', 'just', 'today', 'this week', 'breaking', 'latest']
        if any(term in snippet for term in freshness_terms):
            quality_score += 2
        
        # Negative indicators (reduce score)
        negative_terms = ['casino', 'gambling', 'adult', 'loan', 'insurance', 'diet']
        if any(term in snippet for term in negative_terms):
            quality_score -= 10
        
        # Minimum content length check
        if len(snippet.strip()) < 20:
            quality_score -= 5
        
        # Dynamic threshold based on overall content ecosystem
        threshold = 5  # Adaptive threshold
        
        return quality_score >= threshold

    def _deduplicate_and_score(self, results: List[Dict]) -> List[Dict]:
        """
        Advanced deduplication and scoring with domain diversity promotion.
        """
        seen_urls = set()
        seen_titles = set()
        domain_count = {}  # Track how many results we have from each domain
        
        MAX_GITHUB_RESULTS = 2
        MAX_OTHER_DOMAIN_RESULTS = 3
        
        # Score and sort results
        scored_results = []
        for result in results:
            url = result.get('url', '')
            title = result.get('name', '').lower().strip()
            
            # Skip if URL or very similar title already seen
            if url in seen_urls or title in seen_titles:
                continue
            
            # Extract domain for diversity tracking
            domain = self._extract_domain(url)
            
            # Promote diversity - limit results per domain
            current_domain_count = domain_count.get(domain, 0)
            if (domain == self.GITHUB_DOMAIN and current_domain_count >= MAX_GITHUB_RESULTS) or \
               (domain != self.GITHUB_DOMAIN and current_domain_count >= MAX_OTHER_DOMAIN_RESULTS):
                continue  # Skip if domain limit reached
                
            if url and title:
                score = self._calculate_relevance_score(result)
                
                # Apply diversity bonus for non-GitHub sources
                if domain != self.GITHUB_DOMAIN:
                    score += 1.0  # Bonus for diversity
                    
                scored_results.append((score, result))
                seen_urls.add(url)
                seen_titles.add(title)
                domain_count[domain] = current_domain_count + 1
        
        # Sort by score (highest first) and return
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for score, result in scored_results]

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for diversity tracking."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except Exception:
            return url.lower()

    def _calculate_relevance_score(self, result: Dict) -> float:
        """
        Calculate relevance score based on multiple factors.
        """
        score = 0.0
        snippet = (result.get('snippet', '') + ' ' + result.get('name', '')).lower()
        url = result.get('url', '').lower()
        
        # High-value keywords (higher scores)
        high_value_keywords = {
            'announcement': 3.0, 'launched': 3.0, 'released': 3.0, 'new': 2.0,
            'developer': 2.5, 'api': 2.5, 'open source': 3.0, 'github': 2.0,
            'ai tool': 3.0, 'artificial intelligence': 2.0, 'machine learning': 2.0,
            'beta': 2.5, 'copilot': 2.5, 'assistant': 2.0, 'framework': 2.0
        }
        
        # Domain authority scores
        domain_scores = {
            'openai.com': 5.0, 'anthropic.com': 5.0, 'google.com': 4.0,
            'microsoft.com': 4.0, 'github.com': 4.0, 'techcrunch.com': 3.5,
            'theverge.com': 3.0, 'arstechnica.com': 3.0, 'hackernews.com': 3.0
        }
        
        # Calculate keyword score
        for keyword, value in high_value_keywords.items():
            if keyword in snippet:
                score += value
        
        # Calculate domain score
        for domain, value in domain_scores.items():
            if domain in url:
                score += value
                break
        
        # Freshness bonus (if we can determine recency)
        if any(word in snippet for word in ['today', 'yesterday', 'this week', 'just', 'breaking']):
            score += 2.0
        
        return score

    def force_fetch_and_store(self, results_path: str = "weekly_tech_tools.json"):
        """
        Force a new fetch and store the results to the given file.
        """
        results = self.search_new_ai_tools()
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)
        print(f"Forced fetch complete. Results written to {results_path}")


