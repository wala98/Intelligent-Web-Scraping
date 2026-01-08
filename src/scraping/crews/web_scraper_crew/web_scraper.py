from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crewai import LLM
from crewai_tools import SeleniumScrapingTool , ScrapeWebsiteTool , ScrapeElementFromWebsiteTool , HyperbrowserLoadTool ,FirecrawlScrapeWebsiteTool , ScrapflyScrapeWebsiteTool


llm = LLM(
    model="qwen/qwen3-next-80b-a3b-instruct",
    base_url= "https://integrate.api.nvidia.com/v1",
    api_key= "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" ,
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

from pathlib import Path




selenium = SeleniumScrapingTool(wait_time = 30)
scrape = ScrapeWebsiteTool ()
Scrape_Element_From_Website_Tool = ScrapeElementFromWebsiteTool()
#Hyper_browser_Load_Tool = HyperbrowserLoadTool ()
#Fire_crawl_Scrape_Website_Tool = FirecrawlScrapeWebsiteTool(),
#Scrap_fly_Scrape_Website_Tool =  ScrapflyScrapeWebsiteTool()



#llm = LLM(
 #   model="gemini/gemini-2.5-flash",
    
  #  api_key="AIzaSyANWqZp6fpzdBzSDAgKqkaC0CrnFsQVbZI",
    
#)



@CrewBase
class Web_scraper_Crew():
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, output_dir) :

        self.output_dir = output_dir  

        super().__init__()


    @agent
    def manager_Agent(self) -> Agent:
        return Agent(
            config=self.agents_config['manager_Agent'],
            verbose=True,
            allow_delegation=True,
            llm=llm,
            function_calling_llm=llm,   
            
          
        )

    # HTML Scraper Agent
    @agent
    def static_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['static_agent'],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm,
            tools=  [selenium, scrape ,Scrape_Element_From_Website_Tool] 
        )


    # JS Scraper Agent
    @agent
    def dynamic_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['dynamic_agent'],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm,
            #tools=[selenium ,Hyper_browser_Load_Tool] ,
            tools=  [selenium, scrape ,Scrape_Element_From_Website_Tool] ,
            async_execution = True ,
        )


    # API Scraper Agent
    @agent
    def api_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['api_agent'],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm,
           # tools=[Scrap_fly_Scrape_Website_Tool ,Fire_crawl_Scrape_Website_Tool],
            tools=  [selenium, scrape ,Scrape_Element_From_Website_Tool] ,
        )

  
    @task
    def static_task(self) -> Task:
        return Task(
            config=self.tasks_config['static_task'],
            agent=self.static_agent() ,  
            create_directory = True , 
            #output_file = str(self.output_dir / "static_data.csv")
            human_input =True ,
            output_file = r"C:\Users\walam\Desktop\scraping\scraping_output\static_data.csv" 
        )

    @task
    def dynamic_task(self) -> Task:
        return Task(
            config=self.tasks_config['dynamic_task'],
            agent=self.dynamic_agent() ,   
           # output_file = str(self.output_dir / "dynamic_data.csv")
            create_directory = True ,
            output_file = r"C:\Users\walam\Desktop\scraping\scraping_output\dynamic_data.csv",
            human_input =True ,

        )

    @task
    def api_task(self) -> Task:
        return Task(
            config=self.tasks_config['api_task'],
            agent=self.api_agent() ,   
            #output_file = str(self.output_dir / "api_data.csv")
            create_directory = True ,
            human_input =True ,
            output_file = r"C:\Users\walam\Desktop\scraping\scraping_output\api_data.csv",
        )

    @task
    def manager_task(self) -> Task:
        return Task(
            config=self.tasks_config['manager_task'],
            agent=self.manager_Agent(),  
            human_input =True ,

           
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StructureArchitectCrew crew"""
        return Crew(
            agents=[
            self.api_agent(),
            self.dynamic_agent(), 
            self.static_agent(),
            
            ],
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.manager_Agent(),
            verbose=True,
            manager_llm= llm, 
            function_calling_llm=llm,
            planning=True,  
            planning_llm=llm,
            
        )