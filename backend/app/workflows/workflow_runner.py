from app.agents.crew_setup import CrewManager
from app.utils.logger import logger
import asyncio

class WorkflowRunner:
    def __init__(self):
        self.crew = CrewManager.load_from_folder()

    async def run_book_workflow_async(self, prompt: str):
        writer = await self.crew.run_agent_async('writer', prompt=prompt)
        reviewer = await self.crew.run_agent_async('reviewer', text=writer.get('draft') or writer.get('text',''))
        designer = await self.crew.run_agent_async('designer', context=writer.get('draft') or writer.get('text',''))
        return {'writer': writer, 'reviewer': reviewer, 'designer': designer}