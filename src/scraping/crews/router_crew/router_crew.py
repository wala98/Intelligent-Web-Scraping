from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crewai import LLM
from scraping.config import NVIDIA_API_KEY_1
from crewai_tools import DirectoryReadTool
from crewai_tools import FileReadTool

# Initialize the tool to read any files the agents knows or lean the path for
file_read_tool = FileReadTool()

# Initialize the tool so the agent can read any directory's content 
# it learns about during execution
DirectoryReadTool = DirectoryReadTool()


llm = LLM(
    model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
    base_url= "https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY_1,
    temperature=0.5,
    top_p=0.95,
    max_tokens=65536,
    frequency_penalty=0,
    presence_penalty=0,
)


@CrewBase
class router_Crew():
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def router_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['router_agent'],
            verbose=True,
            llm=llm,
            function_calling_llm=llm,
            tools = [DirectoryReadTool]
        )

    @task
    def router_task(self) -> Task:
        return Task(
            config=self.tasks_config['router_task'], 
            agent=self.router_agent() ,  
           
        )


  
    @crew
    def crew(self) -> Crew:
        """Creates the routerCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            function_calling_llm=llm,   
       
            
        )