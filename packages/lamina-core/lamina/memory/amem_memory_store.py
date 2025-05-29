# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

#!/usr/bin/env python3
"""
A-MEM (Agentic Memory) integration for Lamina.

This module integrates the A-MEM agentic memory system with Lamina's architecture,
providing dynamic memory organization, evolution, and intelligent linking.

Based on the research paper:
"A-MEM: Agentic Memory for LLM Agents"
by Wujiang Xu, Kai Mei, Hang Gao, Juntao Tan, Zujie Liang, Yongfeng Zhang
arXiv:2502.12110 (2025)

Original research: https://github.com/agiresearch/A-mem
Paper: https://arxiv.org/abs/2502.12110

This implementation adapts A-MEM principles for Lamina while adding:
- Local LLM integration via Ollama
- ChromaDB vector storage
- Graceful fallback mechanisms
- Simplified API for agent integration
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import Any

import chromadb
import numpy as np
import requests
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from lamina.agent_config import build_provider_url, get_provider_config
from lamina.logging_config import get_logger
from lamina.system_config import get_memory_config

logger = get_logger(__name__)


class MemoryNote:
    """A memory note that represents a single unit of information in the memory system."""

    def __init__(
        self,
        content: str,
        id: str | None = None,
        keywords: list[str] | None = None,
        links: list[str] | None = None,
        retrieval_count: int | None = None,
        timestamp: str | None = None,
        last_accessed: str | None = None,
        context: str | None = None,
        evolution_history: list | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ):
        # Core content and ID
        self.content = content
        self.id = id or str(uuid.uuid4())

        # Semantic metadata
        self.keywords = keywords or []
        self.links = links or []
        self.context = context or "General"
        self.category = category or "Uncategorized"
        self.tags = tags or []

        # Temporal information
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        self.timestamp = timestamp or current_time
        self.last_accessed = last_accessed or current_time

        # Usage and evolution data
        self.retrieval_count = retrieval_count or 0
        self.evolution_history = evolution_history or []

    def to_dict(self) -> dict[str, Any]:
        """Convert memory note to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "keywords": self.keywords,
            "links": self.links,
            "context": self.context,
            "category": self.category,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "retrieval_count": self.retrieval_count,
            "evolution_history": self.evolution_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryNote":
        """Create memory note from dictionary."""
        return cls(**data)


class AgenticMemoryStore:
    """
    A-MEM based memory store that provides dynamic memory organization,
    evolution, and intelligent linking capabilities.
    """

    def __init__(
        self,
        agent_name: str,
        db_name: str = None,
        model_name: str = None,
        evolution_threshold: int = None,
    ):
        """
        Initialize the agentic memory store.

        Args:
            agent_name: Name of the agent
            db_name: Name of the database (uses config default if None)
            model_name: Sentence transformer model name (uses config default if None)
            evolution_threshold: Number of memories before triggering evolution (uses config default if None)
        """
        self.agent_name = agent_name

        # Load memory configuration
        memory_config = get_memory_config()

        # Use provided values or fall back to configuration
        self.db_name = db_name or memory_config.get("default_database", "long-term")
        self.model_name = model_name or memory_config.get("embedding_model", "all-MiniLM-L6-v2")
        self.evolution_threshold = evolution_threshold or memory_config.get(
            "evolution_threshold", 5
        )

        # Set up storage path (for fallback/local development)
        self.db_path = os.path.join("sanctuary", "agents", agent_name, "memory", db_name)

        # Initialize ChromaDB - try HTTP client first (containerized), fallback to local
        embedding_fn = SentenceTransformerEmbeddingFunction(model_name=model_name)

        try:
            # Try to connect to containerized ChromaDB service directly (internal Docker network)
            # Use internal container name and port instead of nginx proxy
            self.client = chromadb.HttpClient(
                host="chromadb",  # Internal Docker service name
                port=8000,  # Internal ChromaDB port
                ssl=False,  # No SSL for internal communication
                headers={"Authorization": "Bearer lamina_chroma_token"},
            )

            # Test connection
            self.client.heartbeat()
            logger.info("[AgenticMemoryStore] Connected to containerized ChromaDB at chromadb:8000")

        except Exception as e:
            logger.warning(f"[AgenticMemoryStore] Failed to connect to containerized ChromaDB: {e}")
            logger.info("[AgenticMemoryStore] Falling back to local ChromaDB")

            # Fallback to local PersistentClient - but skip if in container environment
            if os.path.exists("/.dockerenv"):
                # We're in a container, don't try local file access
                logger.error(
                    "[AgenticMemoryStore] Cannot create local ChromaDB in container environment"
                )
                raise Exception(
                    "ChromaDB connection failed and local fallback not available in container"
                )
            else:
                # Local development environment
                os.makedirs(self.db_path, exist_ok=True)
                self.client = chromadb.PersistentClient(path=self.db_path)

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=f"{agent_name}_{db_name}", embedding_function=embedding_fn
        )

        # Initialize sentence transformer for embeddings
        try:
            self.sentence_model = SentenceTransformer(self.model_name)
            logger.info(f"[AgenticMemoryStore] Loaded sentence transformer: {self.model_name}")
        except Exception as e:
            logger.warning(
                f"[AgenticMemoryStore] Failed to load sentence transformer {self.model_name}: {e}"
            )
            logger.info("[AgenticMemoryStore] Falling back to simple similarity")
            self.sentence_model = None

        # Memory storage
        self.memories = {}
        self.evolution_count = 0

        logger.info(f"[AgenticMemoryStore] Initialized for agent '{agent_name}' at {self.db_path}")

    def simple_tokenize(self, text: str) -> list[str]:
        """Simple tokenization using regex."""
        # Convert to lowercase and extract words
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Filter out common stop words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "its",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "who",
            "boy",
            "did",
            "she",
            "use",
            "way",
            "what",
            "when",
            "with",
            "this",
            "that",
            "they",
            "them",
            "than",
            "then",
            "from",
            "have",
            "been",
            "were",
            "said",
            "each",
            "which",
            "their",
            "time",
            "will",
            "about",
            "would",
            "there",
            "could",
            "other",
            "after",
            "first",
            "well",
            "also",
            "where",
            "much",
        }

        return [word for word in words if word not in stop_words]

    def analyze_content(self, content: str) -> dict[str, Any]:
        """
        Analyze content to extract semantic metadata using local LLM when available.

        Falls back to simple analysis if local LLM is not available.
        """
        # Try local LLM analysis first (using Ollama)
        try:
            prompt = (
                """Generate a structured analysis of the following content by:
1. Identifying the most salient keywords (focus on nouns, verbs, and key concepts)
2. Extracting core themes and contextual elements
3. Creating relevant categorical tags

Format the response as a JSON object:
{
    "keywords": [
        // several specific, distinct keywords that capture key concepts
        // Order from most to least important, at least 3 keywords
    ],
    "context":
        // one sentence summarizing main topic/domain and key points
    ,
    "tags": [
        // several broad categories/themes for classification
        // Include domain, format, and type tags, at least 3 tags
    ]
}

Content to analyze: """
                + content
            )

            # Try AI provider API (local model) - get URL from configuration
            provider_url = build_provider_url("ollama", "generate")
            provider_config = get_provider_config("ollama")

            # Get model from provider configuration or use default
            model_name = provider_config.get("model_parameters", {}).get(
                "default_model", "llama3.2:3b"
            )

            response = requests.post(
                provider_url,
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 200},
                },
                timeout=10,
            )

            if response.status_code == 200:
                result_text = response.json()["response"]

                # Extract JSON from response
                import json
                import re

                # Try to find JSON in the response
                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    logger.info(
                        f"[AgenticMemoryStore] Local LLM analysis successful for: {content[:50]}..."
                    )
                    return result
                else:
                    logger.warning(
                        "[AgenticMemoryStore] Could not parse JSON from local LLM response"
                    )
            else:
                logger.warning(
                    f"[AgenticMemoryStore] Local LLM request failed with status {response.status_code}"
                )

        except requests.exceptions.ConnectionError:
            logger.warning("[AgenticMemoryStore] Ollama not available (connection refused)")
        except requests.exceptions.Timeout:
            logger.warning("[AgenticMemoryStore] Local LLM request timed out")
        except Exception as e:
            logger.warning(f"[AgenticMemoryStore] Local LLM analysis failed: {e}")

        # Fall back to simple analysis
        logger.info(f"[AgenticMemoryStore] Using simple analysis fallback for: {content[:50]}...")

        # Simple analysis (our current implementation)
        tokens = self.simple_tokenize(content)

        # Take top keywords (unique)
        keywords = list(set(tokens))[:5]

        # Simple context extraction (first sentence or first 50 chars)
        context = content.split(".")[0] if "." in content else content[:50]

        # Dynamic tags based on semantic analysis
        tags = self._extract_semantic_tags(content, keywords)

        return {"keywords": keywords, "context": context, "tags": tags}

    def _extract_semantic_tags(self, content: str, keywords: list[str]) -> list[str]:
        """
        Extract semantic tags dynamically using pure linguistic analysis.

        This approach uses no hardcoded categories - tags emerge naturally from content.
        """
        import spacy

        try:
            # Use spaCy for linguistic analysis
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(content)

            tags = set()

            # Use named entity labels directly as tags (no mapping)
            for ent in doc.ents:
                if ent.label_:
                    tags.add(ent.label_.lower())

            # Use the most significant nouns as tags
            nouns = [
                token.lemma_.lower()
                for token in doc
                if token.pos_ == "NOUN"
                and len(token.lemma_) > 2
                and not token.is_stop
                and token.is_alpha
            ]

            # Add top 2-3 most frequent nouns as tags
            if nouns:
                noun_freq = {}
                for noun in nouns:
                    noun_freq[noun] = noun_freq.get(noun, 0) + 1

                # Sort by frequency and take top ones
                top_nouns = sorted(noun_freq.items(), key=lambda x: x[1], reverse=True)[:3]
                for noun, _ in top_nouns:
                    tags.add(noun)

            # Use the most significant verbs as tags
            verbs = [
                token.lemma_.lower()
                for token in doc
                if token.pos_ == "VERB"
                and len(token.lemma_) > 2
                and not token.is_stop
                and token.is_alpha
            ]

            # Add the main verb (usually the most meaningful one)
            if verbs:
                verb_freq = {}
                for verb in verbs:
                    verb_freq[verb] = verb_freq.get(verb, 0) + 1

                # Take the most frequent verb
                main_verb = max(verb_freq.items(), key=lambda x: x[1])[0]
                tags.add(main_verb)

            # Use keywords directly as tags (they're already meaningful)
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                if len(keyword) > 2:
                    tags.add(keyword.lower())

            # If we still have no tags, use the root word of the sentence
            if not tags:
                for token in doc:
                    if token.dep_ == "ROOT" and token.is_alpha and len(token.lemma_) > 2:
                        tags.add(token.lemma_.lower())
                        break

                # Final fallback: use first meaningful word
                if not tags:
                    for token in doc:
                        if token.is_alpha and len(token.text) > 2 and not token.is_stop:
                            tags.add(token.lemma_.lower())
                            break

            # Convert to list and limit to reasonable number
            return list(tags)[:5]

        except Exception as e:
            logger.warning(f"[AgenticMemoryStore] Semantic tagging failed: {e}")
            # Minimal fallback: use first meaningful word from content
            words = content.lower().split()
            for word in words:
                if len(word) > 2 and word.isalpha():
                    return [word]
            return ["content"]

    def store(self, memory_text: str, metadata: dict | None = None) -> str:
        """
        Store a new memory with agentic processing.

        Args:
            memory_text: The text content to store
            metadata: Optional metadata dictionary

        Returns:
            The ID of the stored memory
        """
        logger.info(f"[AgenticMemoryStore] Storing memory: '{memory_text[:50]}...'")

        # Analyze content
        analysis = self.analyze_content(memory_text)

        # Create memory note
        memory_note = MemoryNote(
            content=memory_text,
            keywords=analysis["keywords"],
            context=analysis["context"],
            tags=analysis["tags"],
            category=metadata.get("category", "general") if metadata else "general",
        )

        # Store in local memory
        self.memories[memory_note.id] = memory_note

        # Process memory for evolution and linking
        self._process_memory(memory_note)

        # Store in ChromaDB
        self._store_in_chromadb(memory_note)

        logger.info(f"[AgenticMemoryStore] Stored memory with ID: {memory_note.id}")
        return memory_note.id

    def _process_memory(self, memory_note: MemoryNote):
        """Process memory for evolution and linking."""
        # Find related memories
        related_memories = self._find_related_memories(memory_note.content)

        if related_memories:
            # Create links
            memory_note.links = [mem_id for mem_id, _ in related_memories[:3]]

            # Update related memories to link back
            for mem_id, _similarity in related_memories[:3]:
                if mem_id in self.memories:
                    related_memory = self.memories[mem_id]
                    if memory_note.id not in related_memory.links:
                        related_memory.links.append(memory_note.id)

        # Increment evolution counter
        self.evolution_count += 1

        # Trigger evolution if threshold reached
        if self.evolution_count >= self.evolution_threshold:
            self._evolve_memories()
            self.evolution_count = 0

    def _find_related_memories(self, content: str, k: int = 5) -> list[tuple[str, float]]:
        """Find memories related to the given content."""
        if not self.memories:
            return []

        # If sentence model is not available, use simple keyword matching
        if self.sentence_model is None:
            return self._find_related_memories_simple(content, k)

        try:
            # Get embedding for the content
            content_embedding = self.sentence_model.encode([content])

            # Get embeddings for all existing memories
            memory_contents = [mem.content for mem in self.memories.values()]
            memory_ids = list(self.memories.keys())

            if not memory_contents:
                return []

            memory_embeddings = self.sentence_model.encode(memory_contents)

            # Calculate similarities
            similarities = cosine_similarity(content_embedding, memory_embeddings)[0]

            # Get top k similar memories
            top_indices = np.argsort(similarities)[::-1][:k]

            related = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Similarity threshold
                    related.append((memory_ids[idx], similarities[idx]))

            return related

        except Exception as e:
            logger.warning(f"[AgenticMemoryStore] Embedding similarity failed: {e}")
            return self._find_related_memories_simple(content, k)

    def _find_related_memories_simple(self, content: str, k: int = 5) -> list[tuple[str, float]]:
        """Simple keyword-based memory similarity as fallback."""
        if not self.memories:
            return []

        content_words = set(self.simple_tokenize(content.lower()))
        if not content_words:
            return []

        similarities = []
        for memory_id, memory in self.memories.items():
            memory_words = set(self.simple_tokenize(memory.content.lower()))
            if memory_words:
                # Simple Jaccard similarity
                intersection = len(content_words & memory_words)
                union = len(content_words | memory_words)
                similarity = intersection / union if union > 0 else 0.0

                if similarity > 0.1:  # Lower threshold for simple matching
                    similarities.append((memory_id, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def _evolve_memories(self):
        """Evolve memories by updating their metadata and relationships."""
        logger.info("[AgenticMemoryStore] Evolving memories...")

        # Simple evolution: update tags and contexts based on links
        for memory in self.memories.values():
            if memory.links:
                # Collect tags from linked memories
                linked_tags = set(memory.tags)
                for link_id in memory.links:
                    if link_id in self.memories:
                        linked_memory = self.memories[link_id]
                        linked_tags.update(linked_memory.tags)

                # Update tags
                memory.tags = list(linked_tags)

                # Update evolution history
                memory.evolution_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "tag_evolution",
                        "details": f"Updated tags based on {len(memory.links)} linked memories",
                    }
                )

    def _store_in_chromadb(self, memory_note: MemoryNote):
        """Store memory note in ChromaDB."""
        try:
            # Prepare metadata for ChromaDB
            chroma_metadata = {
                "keywords": json.dumps(memory_note.keywords),
                "context": memory_note.context,
                "tags": json.dumps(memory_note.tags),
                "timestamp": memory_note.timestamp,
                "category": memory_note.category,
                "retrieval_count": memory_note.retrieval_count,
            }

            self.collection.add(
                documents=[memory_note.content],
                ids=[memory_note.id],
                metadatas=[chroma_metadata],
            )

        except Exception as e:
            logger.error(f"[AgenticMemoryStore] Error storing in ChromaDB: {e}")

    def recall(self, query: str, n_results: int = 3, score_threshold: float = 2.0) -> list[dict]:
        """
        Recall memories using hybrid search (semantic + keyword).

        Args:
            query: Search query
            n_results: Number of results to return
            score_threshold: Distance threshold for filtering

        Returns:
            List of memory dictionaries
        """
        logger.info(f"[AgenticMemoryStore] Recalling memories for query: '{query}'")

        try:
            # Try semantic search using ChromaDB first
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results * 2, 10),  # Get more results for filtering
            )

            memories = []
            if results["documents"] and results["documents"][0]:
                for _i, (doc, distance, metadata) in enumerate(
                    zip(
                        results["documents"][0],
                        results["distances"][0],
                        results["metadatas"][0],
                        strict=False,
                    )
                ):
                    if distance < score_threshold:
                        memory_dict = {
                            "text": doc,
                            "score": distance,
                            "metadata": metadata,
                        }
                        memories.append(memory_dict)

            # Sort by score and limit results
            memories = sorted(memories, key=lambda x: x["score"])[:n_results]

            logger.info(f"[AgenticMemoryStore] Found {len(memories)} relevant memories")
            return memories

        except Exception as e:
            logger.warning(f"[AgenticMemoryStore] ChromaDB recall failed: {e}")
            # Fallback to simple keyword search
            return self._recall_simple(query, n_results)

    def _recall_simple(self, query: str, n_results: int = 3) -> list[dict]:
        """Simple keyword-based recall as fallback."""
        logger.info(f"[AgenticMemoryStore] Using simple recall for query: '{query}'")

        query_words = set(self.simple_tokenize(query.lower()))
        if not query_words:
            return []

        matches = []
        for memory in self.memories.values():
            memory_words = set(self.simple_tokenize(memory.content.lower()))
            if memory_words:
                # Simple keyword matching
                intersection = len(query_words & memory_words)
                if intersection > 0:
                    # Calculate simple relevance score
                    score = intersection / len(query_words)
                    matches.append(
                        {
                            "text": memory.content,
                            "score": score,
                            "metadata": {
                                "timestamp": memory.timestamp,
                                "keywords": memory.keywords,
                                "tags": memory.tags,
                            },
                        }
                    )

        # Sort by score (higher is better for simple matching)
        matches.sort(key=lambda x: x["score"], reverse=True)

        logger.info(
            f"[AgenticMemoryStore] Found {len(matches[:n_results])} relevant memories (simple)"
        )
        return matches[:n_results]

    def get_memory(self, memory_id: str) -> MemoryNote | None:
        """Get a specific memory by ID."""
        return self.memories.get(memory_id)

    def update_memory(self, memory_id: str, **kwargs) -> bool:
        """Update a memory with new information."""
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]

        # Update fields
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)

        # Update last accessed time
        memory.last_accessed = datetime.now().strftime("%Y%m%d%H%M")

        # Re-store in ChromaDB
        self._store_in_chromadb(memory)

        return True

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id not in self.memories:
            return False

        # Remove from local storage
        del self.memories[memory_id]

        # Remove from ChromaDB
        try:
            self.collection.delete(ids=[memory_id])
        except Exception as e:
            logger.error(f"[AgenticMemoryStore] Error deleting from ChromaDB: {e}")

        return True

    def count_memories(self) -> int:
        """Get the total number of memories."""
        return len(self.memories)

    def debug_all_memories(self):
        """Debug function to print all memories."""
        logger.info("[AgenticMemoryStore] MEMORY DUMP")
        for i, (_mem_id, memory) in enumerate(self.memories.items()):
            logger.info(f"[{i}] {memory.content} | {memory.to_dict()}")

    def purge(self):
        """Purge all memories."""
        try:
            self.memories.clear()
            # Get all document IDs first
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            logger.info("[AgenticMemoryStore] Purged all memories")
        except Exception as e:
            logger.error(f"[AgenticMemoryStore] Error purging memories: {e}")
