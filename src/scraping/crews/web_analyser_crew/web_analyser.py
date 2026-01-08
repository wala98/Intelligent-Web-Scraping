from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crewai import LLM
from crewai_tools import SeleniumScrapingTool , ScrapeWebsiteTool
from scraping.config import NVIDIA_API_KEY_2

llm = LLM(
    model="qwen/qwen3-coder-480b-a35b-instruct",
    base_url= "https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY_2,
    temperature=0.5,
    top_p=0.95,
    max_tokens=65536,
    frequency_penalty=0,
    presence_penalty=0,
)

from pydantic import BaseModel, Field
from typing import List, Optional

class ContentZone(BaseModel):
    zone_name: str = Field(description="Name of the content zone, e.g. 'Product title area'")
    css_selector: str = Field(description="CSS selector targeting the content zone")
    description: str = Field(description="Explanation of what this zone contains")

class DataField(BaseModel):
    field_name: str = Field(description="Name of the data field, e.g. 'Price'")
    css_selector: str = Field(description="CSS selector targeting the data field")
    data_type: str = Field(description="Type of data (text, link, image, etc.)")

class WebAnalysisOutput(BaseModel):
    summary: str = Field(
        description="Natural language summary starting with "
                    "'After analyzing the {website_url}, here's what information can be scraped:' "
                    "followed by user-friendly item list"
    )
    page_classification: str = Field(description="Overall classification of the page, e.g. 'E-commerce product page'")
    content_type: Optional[str] = Field(default=None, description="Type of content delivery (static HTML, dynamic, API-based, etc.)")
    content_zones: List[ContentZone] = Field(description="Identified content zones with CSS selectors")
    data_fields: List[DataField] = Field(description="Catalog of available data fields with their selectors and types")
    structural_characteristics: List[str] = Field(description="List of structural traits, e.g. repeated blocks, pagination")
    scraping_challenges: List[str] = Field(description="List of potential scraping challenges, e.g. CAPTCHA, infinite scroll")

selenium = SeleniumScrapingTool()
scrape = ScrapeWebsiteTool ()
@CrewBase
class Web_analyser_Crew():
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def web_analyser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['web_analyser_agent'],
            verbose=True,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm,   
            tools=  [selenium, scrape]  ,
            output_json= WebAnalysisOutput,
          
        )

  
    @task
    def web_analyser_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_analyser_task'],
            agent=self.web_analyser_agent() ,   
            output_json = WebAnalysisOutput,
        )

   
    @crew
    def crew(self) -> Crew:
        """Creates the StructureArchitectCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            function_calling_llm=llm,   
        )