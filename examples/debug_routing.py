#!/usr/bin/env python3
"""Debug routing decisions."""

import asyncio
from lamina.coordination.agent_coordinator import MockIntentClassifier

async def main():
    classifier = MockIntentClassifier()
    
    # Test creative routing
    message = "I need help writing a creative story about time travel"
    result = classifier.classify(message)
    print(f"Message: {message}")
    print(f"Classification result: {result}")
    
    # Test research routing
    message2 = "Can you help me research quantum computing?"
    result2 = classifier.classify(message2)
    print(f"\nMessage: {message2}")
    print(f"Classification result: {result2}")

if __name__ == "__main__":
    asyncio.run(main())