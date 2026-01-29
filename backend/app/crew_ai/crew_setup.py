import os, yaml, asyncio
from pathlib import Path
from app.utils.logger import logger
from app.utils.embedding_utils import text_to_vector
from app.utils.config import settings


try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False

try:
    from ollama import LLM
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

class CrewManager:
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def load_from_config(cls, config_dir: str = None):
        """Load agents (and optional tasks) from a centralized config folder.

        - `config/agents.yaml` should map logical agent names to either:
          - a relative path to an existing agent YAML (e.g. ../agents/writer_agent.yaml)
          - an inline YAML mapping for the agent
        - `config/tasks.yaml` can contain named tasks that reference an agent and input variable.
        The method returns a CrewManager instance and attaches `tasks` attribute (dict) if present.
        """
        if config_dir is None:
            # default: ../config relative to this file
            config_dir = Path(__file__).parent.parent / 'config'
        cfg_dir = Path(config_dir)
        agents = {}
        tasks = {}

        agents_file = cfg_dir / 'agents.yaml'
        if agents_file.exists():
            try:
                cfg = yaml.safe_load(agents_file.read_text()) or {}
                for name, entry in (cfg.get('agents') or {}).items():
                    # if entry is a string, treat as path to agent YAML
                    if isinstance(entry, str):
                        p = (agents_file.parent / entry).resolve()
                        try:
                            agentcfg = yaml.safe_load(p.read_text())
                            if agentcfg and 'name' in agentcfg:
                                agents[agentcfg['name']] = agentcfg
                            else:
                                agents[name] = agentcfg
                        except Exception as e:
                            logger.exception(f"Failed to load agent file {p}: {e}")
                    else:
                        agents[name] = entry
            except Exception as e:
                logger.exception(f"Failed to parse {agents_file}: {e}")

        tasks_file = cfg_dir / 'tasks.yaml'
        if tasks_file.exists():
            try:
                tasks = yaml.safe_load(tasks_file.read_text()) or {}
                tasks = tasks.get('tasks', tasks)
            except Exception as e:
                logger.exception(f"Failed to parse {tasks_file}: {e}")

        mgr = cls(agents)
        # attach tasks mapping for caller convenience
        mgr.tasks = tasks
        return mgr

    async def _call_openai(self, prompt, max_tokens=500, temp=0.3):
        if not OPENAI_AVAILABLE or not os.environ.get('OPENAI_API_KEY'):
            raise RuntimeError('OpenAI not configured')
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        resp = await asyncio.to_thread(lambda: openai.Completion.create(engine='text-davinci-003', prompt=prompt, max_tokens=max_tokens, temperature=temp))
        return resp.choices[0].text.strip()

    async def _call_hf(self, model_name, prompt):
        if not HF_AVAILABLE or not os.environ.get('HUGGINGFACEHUB_API_TOKEN'):
            raise RuntimeError('HF not configured')
        client = InferenceClient(os.environ.get('HUGGINGFACEHUB_API_TOKEN'))
        resp = client.text_generation(prompt, model=model_name)
        return resp

    async def _call_ollama(self, model_name, prompt, base_url=None, api_key=None):
        # Prefer official ollama client if available
        if OLLAMA_AVAILABLE:
            try:
                client = LLM(model=model_name, base_url=base_url, api_key=api_key)
                # try common method names
                if hasattr(client, 'generate'):
                    return client.generate(prompt)
                if hasattr(client, 'create'):
                    return client.create(prompt)
                # fallback: string representation
                return str(client)
            except Exception as e:
                logger.exception('Ollama client call failed: %s', e)
                raise

        # Fallback to a raw HTTP call if requests is available
        if REQUESTS_AVAILABLE and base_url:
            try:
                url = f"{base_url.rstrip('/')}/api/generate"
                headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
                resp = requests.post(url, json={'model': model_name, 'prompt': prompt}, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                # try common response shapes
                return data.get('text') or data.get('output') or data
            except Exception as e:
                logger.exception('Ollama HTTP call failed: %s', e)
                raise

        raise RuntimeError('Ollama client not configured')

    async def run_agent_async(self, name, **kwargs):
        if name not in self.agents:
            raise ValueError('Unknown agent: ' + name)
        cfg = self.agents[name]
        provider = cfg.get('model', {}).get('provider', 'simulated')
        temp = cfg.get('model', {}).get('temperature', 0.7)
        # Build prompt based on template
        prompt_file = Path(Path(__file__).parent / cfg.get('prompt_template', ''))
        templ = prompt_file.read_text() if prompt_file.exists() else ''
        if name == 'writer':
            prompt_body = templ.replace('{{prompt}}', kwargs.get('prompt',''))
        elif name == 'reviewer':
            prompt_body = templ.replace('{{text}}', kwargs.get('text',''))
        else:
            prompt_body = templ.replace('{{context}}', kwargs.get('context',''))

        # Try providers
        if 'openai' in provider and OPENAI_AVAILABLE and os.environ.get('OPENAI_API_KEY'):
            try:
                text = await self._call_openai(prompt_body, max_tokens=1200, temp=temp)
                return {'text': text, 'provider': 'openai'}
            except Exception as e:
                logger.exception('OpenAI provider failed: %s', e)
        if 'hf' in provider and HF_AVAILABLE and os.environ.get('HUGGINGFACEHUB_API_TOKEN'):
            try:
                text = await self._call_hf(cfg.get('model', {}).get('name','gpt-like'), prompt_body)
                return {'text': text, 'provider': 'hf'}
            except Exception as e:
                logger.exception('HF provider failed: %s', e)

        # Try Ollama cloud if configured or explicitly requested
        if ('ollama' in provider) or (os.environ.get('OLLAMA_API_KEY') or os.environ.get('OLLAMA_BASE_URL')):
            try:
                model_name = cfg.get('model', {}).get('name', 'gpt-oss:120b-cloud')
                base_url = os.environ.get('OLLAMA_BASE_URL', 'https://ollama.com/v1')
                api_key = os.environ.get('OLLAMA_API_KEY')
                text = await self._call_ollama(model_name, prompt_body, base_url=base_url, api_key=api_key)
                return {'text': text, 'provider': 'ollama'}
            except Exception as e:
                logger.exception('Ollama provider failed: %s', e)

        # Fallback simulated deterministic output
        if name == 'writer':
            p = kwargs.get('prompt','')[:300]
            vec = text_to_vector(p)
            return {'summary':'Simulated summary','draft': f'Simulated draft for: {p}...','vector': vec, 'provider':'simulated'}
        if name == 'reviewer':
            t = kwargs.get('text','')[:300]
            return {'issues':['check tone'],'corrected': f'Corrected: {t}...','provider':'simulated'}
        if name == 'designer':
            c = kwargs.get('context','')[:300]
            return {'cover':'Simulated cover concept','image_prompt': f'Image prompt: {c}...','provider':'simulated'}
        return {'output':'ok'}
    
    