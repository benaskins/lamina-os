#!/usr/bin/env python3
"""
Model Serving Example

Demonstrates using lamina-llm-serve for model management and serving
with breath-aware request handling and mindful caching.
"""

import asyncio


class MockModelManager:
    """Mock model manager for demonstration."""

    def __init__(self):
        self.available_models = {
            "llama3.2-1b-instruct": {
                "name": "llama3.2-1b-instruct",
                "size": "1.3GB",
                "type": "instruct",
                "backend": "llama.cpp",
                "loaded": False,
                "breath_compatible": True,
            },
            "phi-3.5-mini": {
                "name": "phi-3.5-mini",
                "size": "2.1GB",
                "type": "chat",
                "backend": "ollama",
                "loaded": False,
                "breath_compatible": True,
            },
            "qwen2.5-7b": {
                "name": "qwen2.5-7b",
                "size": "4.8GB",
                "type": "general",
                "backend": "vllm",
                "loaded": False,
                "breath_compatible": False,  # Too reactive for breath-first
            },
        }
        self.loaded_models = {}
        self.request_history = []

    async def list_models(self) -> list[dict]:
        """List available models with breath-compatibility info."""
        await asyncio.sleep(0.2)  # Mindful query time
        return list(self.available_models.values())

    async def load_model(self, model_name: str) -> bool:
        """Load model with breath-aware initialization."""
        if model_name not in self.available_models:
            return False

        model_info = self.available_models[model_name]
        print(f"🔄 Loading {model_name}...")
        print(f"   Size: {model_info['size']}")
        print(f"   Backend: {model_info['backend']}")
        print(f"   Breath compatible: {model_info['breath_compatible']}")

        # Simulate mindful loading time
        load_time = 2.0 if "7b" in model_name else 1.0
        await asyncio.sleep(load_time)

        self.loaded_models[model_name] = model_info
        self.available_models[model_name]["loaded"] = True

        print(f"✅ {model_name} loaded and ready")
        return True

    async def unload_model(self, model_name: str) -> bool:
        """Unload model with graceful shutdown."""
        if model_name in self.loaded_models:
            print(f"🔄 Gracefully unloading {model_name}...")
            await asyncio.sleep(0.5)  # Graceful shutdown

            del self.loaded_models[model_name]
            self.available_models[model_name]["loaded"] = False
            print(f"✅ {model_name} unloaded")
            return True
        return False

    async def generate(self, model_name: str, prompt: str, breath_aware: bool = True) -> str:
        """Generate response with breath-aware processing."""
        if model_name not in self.loaded_models:
            raise ValueError(f"Model {model_name} not loaded")

        model_info = self.loaded_models[model_name]

        # Log request
        self.request_history.append(
            {
                "model": model_name,
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "breath_aware": breath_aware,
            }
        )

        # Breath-aware processing
        if breath_aware and model_info["breath_compatible"]:
            print(f"   🧘 {model_name} taking mindful pause...")
            await asyncio.sleep(0.5)  # Mindful consideration

        # Simulate generation time
        generation_time = 1.5 if breath_aware else 0.3
        await asyncio.sleep(generation_time)

        # Mock responses based on model type
        if "instruct" in model_name:
            response = f"[{model_name}] I understand your request. Let me offer a thoughtful response that considers multiple perspectives..."
        elif "chat" in model_name:
            response = f"[{model_name}] Thank you for your question. I'm taking time to provide a measured, helpful response..."
        else:
            response = f"[{model_name}] Processing complete. Here's my analysis..."

        return response


class BreathAwareServer:
    """Breath-aware model serving with mindful request handling."""

    def __init__(self):
        self.model_manager = MockModelManager()
        self.request_queue = []
        self.processing = False
        self.stats = {"total_requests": 0, "breath_aware_requests": 0, "mindful_pauses": 0}

    async def start_server(self):
        """Start the breath-aware serving loop."""
        print("🌱 Starting breath-aware model server...")
        self.processing = True

        # Load a default model
        await self.model_manager.load_model("llama3.2-1b-instruct")

        print("✅ Server ready for mindful requests")

    async def stop_server(self):
        """Stop server with graceful shutdown."""
        print("🔄 Gracefully shutting down server...")
        self.processing = False

        # Unload all models
        for model_name in list(self.model_manager.loaded_models.keys()):
            await self.model_manager.unload_model(model_name)

        print("✅ Server shutdown complete")

    async def queue_request(self, prompt: str, model_name: str = None, breath_aware: bool = True):
        """Queue a request with breath-aware processing."""
        if not model_name:
            # Use first loaded model
            if self.model_manager.loaded_models:
                model_name = list(self.model_manager.loaded_models.keys())[0]
            else:
                raise ValueError("No models loaded")

        request = {
            "prompt": prompt,
            "model": model_name,
            "breath_aware": breath_aware,
            "timestamp": asyncio.get_event_loop().time(),
        }

        self.request_queue.append(request)
        print(f"📥 Queued request for {model_name} (breath_aware: {breath_aware})")

        return await self._process_request(request)

    async def _process_request(self, request: dict) -> str:
        """Process individual request with breath awareness."""
        self.stats["total_requests"] += 1

        if request["breath_aware"]:
            self.stats["breath_aware_requests"] += 1
            self.stats["mindful_pauses"] += 1

            print("   🧘 Taking mindful pause before processing...")
            await asyncio.sleep(0.3)

        # Generate response
        response = await self.model_manager.generate(
            request["model"], request["prompt"], request["breath_aware"]
        )

        return response

    def get_stats(self) -> dict:
        """Get server statistics."""
        return {
            **self.stats,
            "loaded_models": len(self.model_manager.loaded_models),
            "queue_length": len(self.request_queue),
            "breath_aware_percentage": (
                (self.stats["breath_aware_requests"] / max(1, self.stats["total_requests"])) * 100
            ),
        }


async def demonstrate_model_management():
    """Demonstrate model management capabilities."""
    print("📦 Model Management Demo")
    print("-" * 30)

    manager = MockModelManager()

    # List available models
    models = await manager.list_models()
    print("Available models:")
    for model in models:
        compat = "✅" if model["breath_compatible"] else "⚠️"
        print(f"   {compat} {model['name']} ({model['size']}, {model['backend']})")

    print("\n🔄 Loading breath-compatible models...")

    # Load breath-compatible models
    for model in models:
        if model["breath_compatible"]:
            await manager.load_model(model["name"])

    print(f"\n✅ Loaded {len(manager.loaded_models)} breath-compatible models")


async def demonstrate_breath_aware_serving():
    """Demonstrate breath-aware request serving."""
    print("\n🌱 Breath-Aware Serving Demo")
    print("-" * 35)

    server = BreathAwareServer()
    await server.start_server()

    # Example requests with different breath awareness levels
    requests = [
        ("Explain the concept of breath-first development", True),
        ("What's 2+2?", False),  # Simple math doesn't need breath
        ("Help me process a difficult emotional situation", True),
        ("List the benefits of mindful AI systems", True),
        ("Quick factual lookup: what year was Python created?", False),
    ]

    print(f"\n📨 Processing {len(requests)} requests...")

    for i, (prompt, breath_aware) in enumerate(requests, 1):
        print(f"\n--- Request {i} ---")
        print(f"Prompt: {prompt}")
        print(f"Breath-aware: {breath_aware}")

        response = await server.queue_request(prompt, breath_aware=breath_aware)
        print(f"Response: {response}")

    # Show statistics
    stats = server.get_stats()
    print("\n📊 Server Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Breath-aware requests: {stats['breath_aware_requests']}")
    print(f"   Breath-aware percentage: {stats['breath_aware_percentage']:.1f}%")
    print(f"   Mindful pauses taken: {stats['mindful_pauses']}")

    await server.stop_server()


async def demonstrate_model_selection():
    """Demonstrate intelligent model selection for different tasks."""
    print("\n🎯 Intelligent Model Selection Demo")
    print("-" * 40)

    # Mock intelligent router
    class ModelRouter:
        def __init__(self, model_manager):
            self.model_manager = model_manager

        async def select_model(self, task_type: str, breath_requirement: str) -> str:
            """Select appropriate model based on task and breath requirements."""
            models = await self.model_manager.list_models()

            # Filter breath-compatible models for mindful tasks
            if breath_requirement == "mindful":
                models = [m for m in models if m["breath_compatible"]]

            # Select based on task type
            if task_type == "instruct":
                preferred = [m for m in models if "instruct" in m["name"]]
            elif task_type == "chat":
                preferred = [m for m in models if "chat" in m["name"] or "phi" in m["name"]]
            else:
                preferred = models

            if preferred:
                return preferred[0]["name"]
            elif models:
                return models[0]["name"]
            else:
                raise ValueError("No suitable models available")

    manager = MockModelManager()
    router = ModelRouter(manager)

    # Load models for demo
    await manager.load_model("llama3.2-1b-instruct")
    await manager.load_model("phi-3.5-mini")

    # Test different task types
    test_cases = [
        ("instruct", "mindful", "Thoughtful analysis task"),
        ("chat", "reactive", "Quick factual question"),
        ("general", "mindful", "Complex reasoning task"),
    ]

    for task_type, breath_req, description in test_cases:
        selected_model = await router.select_model(task_type, breath_req)
        print(f"🎯 {description}")
        print(f"   Task type: {task_type}")
        print(f"   Breath requirement: {breath_req}")
        print(f"   Selected model: {selected_model}")
        print()


async def main():
    """Main demonstration of model serving capabilities."""
    print("🚀 Lamina LLM Serve Demonstration")
    print("=" * 50)

    try:
        # Import real classes if available
        from lamina_llm_serve import ModelManager, Server  # noqa: F401

        print("✅ Using real lamina-llm-serve implementation")
    except ImportError:
        print("📝 Using mock implementation for demonstration")

    # Run demonstrations
    await demonstrate_model_management()
    await demonstrate_breath_aware_serving()
    await demonstrate_model_selection()

    print("\n🙏 Model serving demonstration complete")
    print("=" * 50)


if __name__ == "__main__":
    print("🤖 Lamina LLM Serve Example")
    print("Demonstrating breath-aware model serving")
    print()
    asyncio.run(main())
