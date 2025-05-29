# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Intent Classification System

Analyzes user messages to determine appropriate routing and handling strategies.
Uses pattern matching and keyword analysis to classify user intents.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent classification"""

    primary_type: str
    secondary_types: list[str]
    confidence: float
    categories: list[str]
    requires_security_review: bool
    involves_personal_data: bool
    metadata: dict[str, Any]


class IntentClassifier:
    """
    Classifies user intents to determine appropriate agent routing.

    Uses a combination of keyword matching, pattern recognition,
    and heuristic analysis to determine message intent.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._load_patterns()
        self._load_keywords()

    def _load_patterns(self):
        """Load intent detection patterns"""

        self.patterns = {
            "analytical": [
                r"\b(analyz|research|investigat|study|examin)\w*\b",
                r"\b(data|statistics|metrics|trends|patterns)\b",
                r"\b(compare|contrast|evaluate|assess)\w*\b",
                r"\b(report|summary|breakdown|analysis)\b",
            ],
            "security": [
                r"\b(secur|vulnerabilit|threat|risk|safe)\w*\b",
                r"\b(hack|attack|breach|malware|virus)\w*\b",
                r"\b(permiss|access|auth|credential)\w*\b",
                r"\b(encrypt|decrypt|password|certificate)\w*\b",
            ],
            "reasoning": [
                r"\b(logic|reason|proof|deduc|induc)\w*\b",
                r"\b(problem|solve|solution|algorithm)\w*\b",
                r"\b(math|calculat|equat|formula)\w*\b",
                r"\b(step|process|method|approach)\w*\b",
            ],
            "conversational": [
                r"\b(hello|hi|hey|greet)\w*\b",
                r"\b(how are you|what.*up|good morning)\b",
                r"\b(tell me|explain|describe|what is)\w*\b",
                r"\b(help|assist|support|guide)\w*\b",
            ],
            "system": [
                r"\b(config|setting|setup|install)\w*\b",
                r"\b(status|health|diagnostic|debug)\w*\b",
                r"\b(restart|reload|refresh|update)\w*\b",
                r"\b(list|show|display|view)\w*\s+(agents|capabilities)\b",
            ],
        }

    def _load_keywords(self):
        """Load keyword sets for classification"""

        self.keywords = {
            "analytical": {
                "data",
                "research",
                "analysis",
                "study",
                "investigate",
                "examine",
                "statistics",
                "metrics",
                "trends",
                "patterns",
                "insights",
                "compare",
                "contrast",
                "evaluate",
                "assess",
                "review",
            },
            "security": {
                "security",
                "vulnerability",
                "threat",
                "risk",
                "safety",
                "safe",
                "hack",
                "attack",
                "breach",
                "malware",
                "virus",
                "exploit",
                "permission",
                "access",
                "authentication",
                "authorization",
                "encrypt",
                "decrypt",
                "password",
                "certificate",
                "firewall",
            },
            "reasoning": {
                "logic",
                "logical",
                "reason",
                "reasoning",
                "proof",
                "prove",
                "deduce",
                "deduction",
                "induction",
                "problem",
                "solve",
                "solution",
                "math",
                "mathematics",
                "calculate",
                "equation",
                "formula",
                "algorithm",
                "step",
                "process",
                "method",
                "approach",
            },
            "conversational": {
                "hello",
                "hi",
                "hey",
                "greetings",
                "chat",
                "talk",
                "conversation",
                "help",
                "assist",
                "support",
                "guide",
                "explain",
                "tell",
                "describe",
            },
            "system": {
                "config",
                "configuration",
                "setting",
                "setup",
                "install",
                "installation",
                "status",
                "health",
                "diagnostic",
                "debug",
                "troubleshoot",
                "restart",
                "reload",
                "refresh",
                "update",
                "agents",
                "capabilities",
            },
        }

    def classify(self, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Classify the intent of a user message.

        Args:
            message: The user's message to classify
            context: Optional context information

        Returns:
            Dictionary containing classification results
        """
        message_lower = message.lower()

        # Score each intent type
        scores = {}
        for intent_type in self.patterns.keys():
            scores[intent_type] = self._score_intent(message_lower, intent_type)

        # Determine primary intent
        primary_type = max(scores, key=scores.get)
        primary_confidence = scores[primary_type]

        # Determine secondary intents (score > 0.3 and not primary)
        secondary_types = [
            intent_type
            for intent_type, score in scores.items()
            if score > 0.3 and intent_type != primary_type
        ]

        # Analyze categories
        categories = self._analyze_categories(message_lower)

        # Security and privacy analysis
        requires_security_review = self._requires_security_review(message_lower)
        involves_personal_data = self._involves_personal_data(message_lower)

        return {
            "primary_type": primary_type,
            "secondary_types": secondary_types,
            "confidence": primary_confidence,
            "categories": categories,
            "requires_security_review": requires_security_review,
            "involves_personal_data": involves_personal_data,
            "scores": scores,
        }

    def _score_intent(self, message: str, intent_type: str) -> float:
        """Score how well a message matches an intent type"""

        total_score = 0.0

        # Pattern matching score
        pattern_score = self._score_patterns(message, intent_type)

        # Keyword matching score
        keyword_score = self._score_keywords(message, intent_type)

        # Combine scores (weighted)
        total_score = (pattern_score * 0.6) + (keyword_score * 0.4)

        return min(total_score, 1.0)  # Cap at 1.0

    def _score_patterns(self, message: str, intent_type: str) -> float:
        """Score pattern matches for an intent type"""

        if intent_type not in self.patterns:
            return 0.0

        patterns = self.patterns[intent_type]
        matches = 0

        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1

        return min(matches / len(patterns), 1.0)

    def _score_keywords(self, message: str, intent_type: str) -> float:
        """Score keyword matches for an intent type"""

        if intent_type not in self.keywords:
            return 0.0

        keywords = self.keywords[intent_type]
        words = set(message.split())

        matches = len(words.intersection(keywords))
        return min(matches / 3.0, 1.0)  # Normalize by dividing by 3

    def _analyze_categories(self, message: str) -> list[str]:
        """Analyze message for specific categories"""

        categories = []

        # Technical categories
        if re.search(r"\b(code|program|script|function|class)\b", message):
            categories.append("code")

        if re.search(r"\b(file|document|text|upload|download)\b", message):
            categories.append("file_handling")

        if re.search(r"\b(network|internet|web|api|http)\b", message):
            categories.append("network")

        if re.search(r"\b(database|sql|query|table|record)\b", message):
            categories.append("database")

        return categories

    def _requires_security_review(self, message: str) -> bool:
        """Determine if message requires security review"""

        security_indicators = [
            r"\b(password|credential|secret|key|token)\b",
            r"\b(hack|exploit|vulnerability|attack)\b",
            r"\b(permission|access|auth|login)\b",
            r"\b(admin|root|sudo|privilege)\b",
        ]

        for pattern in security_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return True

        return False

    def _involves_personal_data(self, message: str) -> bool:
        """Determine if message involves personal data"""

        personal_data_indicators = [
            r"\b(name|email|phone|address|birthday)\b",
            r"\b(personal|private|confidential|sensitive)\b",
            r"\b(ssn|social security|credit card|bank)\b",
            r"\b(medical|health|diagnosis|prescription)\b",
        ]

        for pattern in personal_data_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return True

        return False

    def add_custom_pattern(self, intent_type: str, pattern: str):
        """Add a custom pattern for intent classification"""

        if intent_type not in self.patterns:
            self.patterns[intent_type] = []

        self.patterns[intent_type].append(pattern)
        logger.info(f"Added custom pattern for {intent_type}: {pattern}")

    def add_custom_keywords(self, intent_type: str, keywords: list[str]):
        """Add custom keywords for intent classification"""

        if intent_type not in self.keywords:
            self.keywords[intent_type] = set()

        self.keywords[intent_type].update(keywords)
        logger.info(f"Added {len(keywords)} custom keywords for {intent_type}")

    def get_classification_stats(self) -> dict[str, Any]:
        """Get statistics about classification patterns"""

        return {
            "intent_types": list(self.patterns.keys()),
            "total_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "total_keywords": sum(len(keywords) for keywords in self.keywords.values()),
            "patterns_per_type": {
                intent_type: len(patterns) for intent_type, patterns in self.patterns.items()
            },
            "keywords_per_type": {
                intent_type: len(keywords) for intent_type, keywords in self.keywords.items()
            },
        }
