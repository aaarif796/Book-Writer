from typing import Dict, Any
from .config_loader import config_loader
from .llm_factory import LLMFactory


class CrewEngine:
    """Core execution engine for AI tasks."""

    async def execute(self, task_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task by:
        1. Loading task config
        2. Getting assigned agent
        3. Getting model config
        4. Building system prompt
        5. Calling LLM
        6. Returning result
        """
        # Load task config
        task_config = config_loader.get_task(task_name)

        # Get assigned agent
        agent_name = task_config["agent"]
        agent_config = config_loader.get_agent(agent_name)

        # Get model config
        model_name = agent_config["model"]
        model_config = config_loader.get_model(model_name)

        # Build system prompt (simplified - in real implementation, load from templates)
        system_prompt = self._build_system_prompt(agent_config, inputs)

        # Create LLM provider
        provider_name = model_config["provider"]
        llm = LLMFactory.create(provider_name, model_config)

        # Generate response
        response = await llm.generate(system_prompt)

        return {
            "task": task_name,
            "agent": agent_name,
            "model": model_name,
            "output": response,
            "provider": provider_name
        }

    def _build_system_prompt(self, agent_config: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Build system prompt from agent config and inputs."""
        role = agent_config["role"]
        # Simplified prompt building - in production, load from template files
        prompt_parts = [f"You are a {role}."]

        # Add input data
        for key, value in inputs.items():
            prompt_parts.append(f"{key}: {value}")

        return "\n\n".join(prompt_parts)