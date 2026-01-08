from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import LLM
from scraping.config import NVIDIA_API_KEY_1, GOOGLE_API_KEY, SCRAPFLY_API_KEY
from crewai_tools import SeleniumScrapingTool , ScrapeWebsiteTool , ScrapeElementFromWebsiteTool , HyperbrowserLoadTool ,FirecrawlScrapeWebsiteTool , ScrapflyScrapeWebsiteTool
from src.scraping.tools.custom_tool import alll,fetch_data,extract_data
from crewai_tools import FileWriterTool

# Initialize without parameters
filewriter = FileWriterTool()





llm = LLM(
    model="qwen/qwen3-coder-480b-a35b-instruct",
    base_url= "https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY_1,
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
from crewai_tools import ScrapflyScrapeWebsiteTool

# Initialize the tool
scrape_tool = ScrapflyScrapeWebsiteTool(api_key=SCRAPFLY_API_KEY)



selenium = SeleniumScrapingTool(wait_time = 30)
scrape = ScrapeWebsiteTool ()
Scrape_Element_From_Website_Tool = ScrapeElementFromWebsiteTool()
#Hyper_browser_Load_Tool = HyperbrowserLoadTool ()
#Fire_crawl_Scrape_Website_Tool = FirecrawlScrapeWebsiteTool(),
#Scrap_fly_Scrape_Website_Tool =  ScrapflyScrapeWebsiteTool()
llm1 = LLM(
    model="gemini/gemini-2.5-flash",  
    api_key=GOOGLE_API_KEY,
    
)
@CrewBase
class Web_scraper_Crew2():
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

   


    # HTML Scraper Agent
    @agent
    def universal_scraper_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['universal_scraper_agent'],
            verbose=True,
            allow_delegation=False,
            llm=llm,
            function_calling_llm=llm,
           # max_rpm=4 ,
            
            tools=  [selenium, scrape ,Scrape_Element_From_Website_Tool,filewriter] #don't forget to add alll tool 
        )

    @task
    def universal_scraping_task(self) -> Task:
        return Task(
            config=self.tasks_config['universal_scraping_task'],
            agent=self.universal_scraper_agent() ,  
            create_directory = True , 
            #output_file = str(self.output_dir / "static_data.csv")
            human_input =True ,
            #output_file = r"C:\Users\walam\Desktop\scraping\scraping_output\" 
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