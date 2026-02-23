import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and caches YAML configuration files."""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file and cache it."""
        if filename not in self._cache:
            file_path = self.config_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"Config file not found: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                self._cache[filename] = yaml.safe_load(f)
        return self._cache[filename]

    def get_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get agent configuration by name."""
        agents = self._load_yaml("agents.yaml")
        if agent_name not in agents:
            raise ValueError(f"Agent '{agent_name}' not found in config")
        return agents[agent_name]

    def get_task(self, task_name: str) -> Dict[str, Any]:
        """Get task configuration by name."""
        tasks = self._load_yaml("tasks.yaml")
        if task_name not in tasks:
            raise ValueError(f"Task '{task_name}' not found in config")
        return tasks[task_name]

    def get_model(self, model_name: str) -> Dict[str, Any]:
        """Get model configuration by name."""
        models = self._load_yaml("models.yaml")
        if model_name not in models:
            raise ValueError(f"Model '{model_name}' not found in config")
        return models[model_name]

    def get_tool(self, tool_name: str) -> Dict[str, Any]:
        """Get tool configuration by name."""
        tools = self._load_yaml("tools.yaml")
        if tool_name not in tools:
            raise ValueError(f"Tool '{tool_name}' not found in config")
        return tools[tool_name]


# Global instance
config_loader = ConfigLoader()