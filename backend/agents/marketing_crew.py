from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import yaml
import os
from backend.agents.base_agent import BaseAgent, AgentResponse

# Helper to load yaml config
def load_config(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

class MarketingCrewWrapper(BaseAgent):
    def __init__(self):
        super().__init__(name="MarketingCrew")
        # Load configs
        cwd = os.getcwd()
        self.agents_config = load_config(os.path.join(cwd, "backend/config/agents.yaml"))
        self.tasks_config = load_config(os.path.join(cwd, "backend/config/tasks.yaml"))

    async def initialize_tools(self):
        pass

    def _create_crew(self, inputs: dict) -> Crew:
        # Agents
        market_researcher = Agent(
            config=self.agents_config['market_researcher'],
            verbose=True,
            allow_delegation=False,
            llm="gpt-4o" # Uses env OPENAI_API_KEY
        )
        
        content_strategist = Agent(
            config=self.agents_config['content_strategist'],
            verbose=True,
            llm="gpt-4o"
        )
        
        copywriter = Agent(
            config=self.agents_config['copywriter'],
            verbose=True,
            llm="gpt-4o"
        )

        # Tasks
        task_research = Task(
            config=self.tasks_config['market_research'],
            agent=market_researcher
        )

        task_strategy = Task(
            config=self.tasks_config['content_strategy'],
            agent=content_strategist
        )

        task_copywriting = Task(
            config=self.tasks_config['copywriting'],
            agent=copywriter
        )

        # Crew
        return Crew(
            agents=[market_researcher, content_strategist, copywriter],
            tasks=[task_research, task_strategy, task_copywriting],
            process=Process.sequential,
            verbose=True
        )

    async def process(self, message: str, context: dict = None) -> AgentResponse:
        # In a real scenario, we'd extract specific inputs from the message
        # For now, we use defaults or simple extraction
        
        inputs = {
            'current_date': '2026-05-20',
            'instagram_description': 'A premium GenAI platform for enterprise businesses.',
            'topic_of_the_week': message or 'AI in Marketing'
        }
        
        # CrewAI is synchronous by default, so we might want to run this in a thread/executor
        # For MVP, we run it directly (blocking) but in production use run_in_executor
        crew = self._create_crew(inputs)
        result = crew.kickoff(inputs=inputs)
        
        return AgentResponse(
            response=f"**Marketing Campaign Strategy**\n\n{result}",
            metadata={"source": "CrewAI"}
        )
