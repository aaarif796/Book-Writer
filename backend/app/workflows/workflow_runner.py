from app.agents.crew import CrewEngine
from app.utils.logger import logger
import asyncio

class WorkflowRunner:
    def __init__(self):
        self.crew = CrewEngine()

    async def run_book_workflow_async(self, prompt: str):
        # Use the new task-based execution
        result = await self.crew.execute("write_chapter", {"chapter_content": prompt})
        return result
        reviewer = await self.crew.run_agent_async('reviewer', text=writer.get('draft') or writer.get('text',''))
        designer = await self.crew.run_agent_async('designer', context=writer.get('draft') or writer.get('text',''))
        return {'writer': writer, 'reviewer': reviewer, 'designer': designer}