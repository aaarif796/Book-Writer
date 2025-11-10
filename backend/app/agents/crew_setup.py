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

class CrewManager:
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def load_from_folder(cls, folder: str = None):
        if folder is None:
            folder = Path(__file__).parent
        agents = {}
        for p in Path(folder).glob("*_agent.yaml"):
            try:
                cfg = yaml.safe_load(p.read_text())
                agents[cfg['name']] = cfg
            except Exception as e:
                logger.exception(f"Failed to load {p}: {e}")
        return cls(agents)

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