"""
Seed Generator Service — Auto web search + LLM compile
Generates rich seed files from a topic via Tavily + LLM
"""

import os
import json
import time
import traceback
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient

logger = get_logger('mirofish.seed')

# Try import tavily
try:
    from tavily import TavilyClient
    HAS_TAVILY = True
except ImportError:
    HAS_TAVILY = False
    logger.warning("tavily-python not installed, seed generation will use LLM knowledge only")

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

SEED_CATEGORIES = [
    {
        "id": "background",
        "title": "Background & Context",
        "desc": "Background, history, and context of why this topic matters",
        "search_angle": "background history context overview"
    },
    {
        "id": "key_actors",
        "title": "Key Actors & Stakeholders",
        "desc": "Main players, profiles, motivations, positions, relationships",
        "search_angle": "key players stakeholders companies people involved"
    },
    {
        "id": "data_evidence",
        "title": "Data, Statistics & Evidence",
        "desc": "Numbers, benchmarks, statistics, hard facts, empirical evidence",
        "search_angle": "statistics data numbers benchmark evidence research"
    },
    {
        "id": "public_sentiment",
        "title": "Public Sentiment & Opinions",
        "desc": "Public opinion, social media reactions, controversies, debates",
        "search_angle": "public opinion reaction controversy debate social media"
    },
    {
        "id": "scenarios",
        "title": "Timeline & Future Scenarios",
        "desc": "Chronology of events, predictions, future scenarios",
        "search_angle": "timeline prediction future forecast scenario trend"
    }
]


class SeedGeneratorService:
    """Generates multi-perspective seed documents from a topic"""

    def __init__(self):
        self.llm = LLMClient()
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY) if HAS_TAVILY else None

    def generate_queries(self, topic: str, num_queries: int = 8) -> list:
        """Generate diverse search queries from topic"""
        prompt = f"""Generate {num_queries} diverse web search queries for comprehensive research.
Topic: {topic}

Distribute across categories: {json.dumps([c["id"] for c in SEED_CATEGORIES])}

Output ONLY a JSON array (no other text):
[{{"query": "search text", "category": "category_id"}}, ...]

Rules: Mix English + local language, be specific, at least 1 per category."""

        try:
            text = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            # Clean markdown blocks
            import re
            text = text.strip()
            text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\n?```\s*$', '', text)
            text = text.strip()
            result = json.loads(text)
            if isinstance(result, list):
                return result
        except Exception as e:
            logger.warning(f"Query generation parse error: {e}")

        # Fallback
        return [{"query": f"{topic} {c['search_angle']}", "category": c["id"]}
                for c in SEED_CATEGORIES]

    def _search_single(self, query: str, max_results: int = 5) -> list:
        """Execute single Tavily search"""
        if not self.tavily:
            return []
        try:
            resp = self.tavily.search(
                query=query, max_results=max_results,
                search_depth="advanced", include_raw_content=False
            )
            return [{"title": h.get("title", ""), "url": h.get("url", ""),
                      "content": h.get("content", ""), "score": h.get("score", 0)}
                    for h in resp.get("results", [])]
        except Exception as e:
            logger.warning(f"Search error for '{query}': {e}")
            return []

    def search_web(self, queries: list, max_results: int = 5,
                   progress_callback=None) -> dict:
        """Parallel web search"""
        results_by_cat = {c["id"]: [] for c in SEED_CATEGORIES}

        if not self.tavily:
            if progress_callback:
                progress_callback("No Tavily API, using LLM knowledge only", 100)
            return results_by_cat

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {}
            for q in queries:
                f = pool.submit(self._search_single, q["query"], max_results)
                futures[f] = q

            done_count = 0
            for f in as_completed(futures):
                q = futures[f]
                cat = q.get("category", "background")
                hits = f.result()
                results_by_cat.setdefault(cat, []).extend(hits)
                done_count += 1
                if progress_callback:
                    pct = int(done_count / len(futures) * 100)
                    progress_callback(f"Searched: {q['query'][:50]}... ({len(hits)} hits)", pct)

        # Dedupe
        for cat_id in results_by_cat:
            seen = set()
            deduped = []
            for r in results_by_cat[cat_id]:
                if r["url"] not in seen:
                    seen.add(r["url"])
                    deduped.append(r)
            results_by_cat[cat_id] = deduped

        return results_by_cat

    def compile_seed(self, topic: str, category: dict,
                     search_results: list, lang: str = "id") -> str:
        """Compile search results into a seed markdown file"""
        sources = ""
        for i, r in enumerate(search_results[:15], 1):
            sources += f"\n--- Source {i}: {r['title']} ---\nURL: {r['url']}\n{r['content']}\n"

        lang_instr = ("Tulis dalam Bahasa Indonesia yang natural dan informatif."
                      if lang == "id" else "Write in English, informative and well-structured.")

        prompt = f"""Expert research analyst creating a seed document for social simulation.

TOPIC: {topic}
CATEGORY: {category['title']} — {category['desc']}

SOURCES:
{sources if sources.strip() else "(No search results — use your own knowledge)"}

Create a comprehensive Markdown document (800-2000 words). {lang_instr}

Rules:
- Proper Markdown: ##/### headers, bullets, tables where needed
- SPECIFIC names, numbers, dates — no vague generalizations
- Real entities with actual roles/positions
- Multiple perspectives where relevant
- Start with # heading
- Output content only, no wrappers"""

        messages = [{"role": "user", "content": prompt}]
        resp = self.llm.chat(messages=messages, temperature=0.4, max_tokens=4096)
        return resp

    def generate_seeds(self, topic: str, lang: str = "id",
                       num_queries: int = 8,
                       progress_callback=None) -> dict:
        """
        Full pipeline: topic → queries → search → compile → return seeds

        Returns:
            {
                "seeds": [{"id": "background", "title": "...", "content": "...md"}, ...],
                "sources_count": 25,
                "combined_text": "all seeds combined"
            }
        """
        if progress_callback:
            progress_callback("Generating search queries...", 5)

        # Step 1: Generate queries
        queries = self.generate_queries(topic, num_queries)
        logger.info(f"Generated {len(queries)} queries for topic: {topic[:50]}")

        if progress_callback:
            progress_callback(f"Generated {len(queries)} search queries", 10)

        # Step 2: Web search (parallel)
        def search_progress(msg, pct):
            if progress_callback:
                # Map 0-100 to 10-40
                mapped = 10 + int(pct * 0.3)
                progress_callback(msg, mapped)

        search_results = self.search_web(queries, progress_callback=search_progress)
        total_hits = sum(len(v) for v in search_results.values())
        logger.info(f"Collected {total_hits} sources")

        if progress_callback:
            progress_callback(f"Collected {total_hits} web sources, compiling...", 40)

        # Step 3: Compile seeds (parallel)
        seeds = []

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {}
            for cat in SEED_CATEGORIES:
                cat_results = search_results.get(cat["id"], []).copy()
                # Cross-pollinate with 2 results from other categories
                for oid, oresults in search_results.items():
                    if oid != cat["id"]:
                        cat_results.extend(oresults[:2])

                f = pool.submit(self.compile_seed, topic, cat, cat_results, lang)
                futures[f] = cat

            done_count = 0
            for f in as_completed(futures):
                cat = futures[f]
                content = f.result()
                seeds.append({
                    "id": cat["id"],
                    "title": cat["title"],
                    "content": content
                })
                done_count += 1
                if progress_callback:
                    pct = 40 + int(done_count / len(futures) * 50)
                    progress_callback(f"Compiled: {cat['title']}", pct)

        # Sort by category order
        cat_order = {c["id"]: i for i, c in enumerate(SEED_CATEGORIES)}
        seeds.sort(key=lambda s: cat_order.get(s["id"], 99))

        # Combine all text
        combined = "\n\n".join([
            f"=== {s['title']} ===\n{s['content']}" for s in seeds
        ])

        if progress_callback:
            progress_callback("Seed generation complete!", 100)

        return {
            "seeds": seeds,
            "sources_count": total_hits,
            "combined_text": combined,
            "total_chars": len(combined)
        }
