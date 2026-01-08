import sys

import os
# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from crewai.flow.flow import Flow, listen, start, router
from scraping.crews.web_analyser_crew.web_analyser import Web_analyser_Crew
from scraping.crews.web_scraper_crew.web_scraper import Web_scraper_Crew

from scraping.crews.web_scraper_crew2.web_scraper_crew2 import Web_scraper_Crew2
from scraping.crews.router_crew.router_crew import router_Crew
from scraping.crews.quary_crew.quary_crew import quary_Crew

from crewai_tools import ScrapeWebsiteTool
from pydantic import BaseModel,Field
from typing import Optional, List
from pathlib import Path
import datetime
import json
from typing import Any, Dict, Optional
import re

class WebScrapingState(BaseModel):
    url: str = Field(default="", description="Target URL to scrape")
    user_requirements: str = Field(default="", description="User's scraping requirements")
    analysis_complete: bool = Field(default=False, description="Whether analysis is complete")
    scraping_complete: bool = Field(default=False, description="Whether scraping is complete")
    analysis_results: Optional[Dict[str, Any]] = Field(default=None, description="Analysis results data")
    path: str = Field(default="", description="Base file path")
    analysis_results_path: str = Field(default="", description="Path to analysis results file")
    scraped_data_path: str = Field(default="", description="Path to scraped data file") # a regler
    final_report: str = Field(default="", description="Final report content")
    current_stage: str = Field(default="initialization", description="Current workflow stage")
    output_dir: str = Field(default="", description="Output directory path")

class WebScrapingFlow(Flow[WebScrapingState]):
    
    def __init__(self, url: str = None, output_dir: Optional[Path] = None, interactive_mode: bool = True):
            super().__init__()
            self.interactive_mode = interactive_mode
            self.output_dir = output_dir or Path("./scraping_output")
            self.output_dir.mkdir(exist_ok=True)
            self.state.output_dir = str(self.output_dir)
            
            # Set initial state
            if url:
                self.state.url = url
            
            # Save metadata
            metadata = {
                "Project ID": f"scraping_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "Started": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "URL": url,
                "Interactive Mode": interactive_mode
            }

    @start()     
    def greeting_and_setup(self):
            
            """Initialize the scraping flow and collect requirements"""
            print("\n=== app ASSISTANT ===")
            print("👋 Hello! I specialize in analyzing websites and extracting structured data.")
            print("I can help you scrape any website and generate comprehensive analysis reports.")
        
            
            self.state.current_stage = "setup"
            
            if not self.interactive_mode:
                # Skip interaction if not in interactive mode
                return
                
            # Get URL if not provided
            if not self.state.url:
                url = input("\nPlease provide the URL you want to analyze and scrape: ").strip()
                if not url.startswith("http"):
                    print("❌ Please enter a valid URL (must start with http or https)")
                self.state.url = url
            
            print(f"\n✅ Setup complete! Starting analysis of {self.state.url}")

    @listen(greeting_and_setup)
    def analyse_website(self):
            """Analyze website structure and content"""
            print(f"\n=== WEBSITE ANALYSIS STAGE ===")
            print(f"🔍 Analyzing: {self.state.url}")
            
            self.state.current_stage = "analysis"
            
            analysis_crew = Web_analyser_Crew().crew()
            result = analysis_crew.kickoff(inputs={"website_url": self.state.url})
            self.state.analysis_results = result

            self.state.analysis_complete = True
            
            print("✅ Website analysis completed!")     



    @listen(analyse_website)
    def save_analysed_website(self):
        """Save analyzed website structure and content into a JSON file"""
        print(f"\n=== SAVING WEBSITE INFORMATION STAGE ===")

        self.state.current_stage = "saving_website_information"

        # Ensure we actually have analysis results
        if not self.state.analysis_results:
            print("⚠️ No analysis results found. Did you run analyse_website first?")
            return

        # Ensure save directory exists
        save_dir = "website_analysis_results"
        path = os.path.join(self.output_dir, save_dir)
        os.makedirs(path, exist_ok=True)
        self.path = path

        # Build a safe filename using domain
        domain = (
            self.state.url.replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
            .replace(":", "_")
        )
        # Remove invalid Windows filename chars:  < > : " / \ | ? *
        domain = re.sub(r'[<>:"/\\|?*]', "_", domain)
        filename = f"{domain}.json"

        # Store path in the object for later use
        self.analysis_results_path = os.path.join(path, filename)

        # Extract only "json_dict" and save it
        json_data = getattr(self.state.analysis_results, "json_dict", None)

        if json_data is None:
            print("⚠️ No 'json_dict' found in analysis results. Saving entire output instead.")
            json_data = self.state.analysis_results.model_dump()

        with open(self.analysis_results_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Website analysis saved to {self.analysis_results_path}")
        summary = json_data.get("summary")
        print(f"\n📄 Analysis Summary:\n{summary}")

        requirements = input("\nWhat specific data do you want to extract? : ").strip()
        self.state.user_requirements = requirements

    @listen(save_analysed_website)
    def scraping_data(self) :
        print(f"\n=== scraping WEBSITE INFORMATION STAGE ===")
        print(f"📊 Extracting data based on analysis...")
        self.state.current_stage = "scraping_website_information"
        scraper_crew = Web_scraper_Crew2().crew()
        scraper_result = scraper_crew.kickoff(inputs={"analysis_results": self.state.analysis_results.model_dump(),
                                              "user_requirements" : self.state.user_requirements})
        print( scraper_result )
        self.state.scraping_complete = True  
        print("✅ Data scraping completed!")
        self.scraped_data_path = os.path.join(self.output_dir,"scrapped_data")
        print("***************************************")
        print(self.scraped_data_path)
        print("***************************************")

    
   

    @router(scraping_data)
    def router(self):
        requirements = input("\n do you want to chat with your scraped data !(yes or no): ").strip().lower()
        while requirements not in ["yes","no"] :
            requirements = input("\n do you want to chat with your scraped data !enter only (yes or no): ").strip().lower()
        self.state.user_requirements = requirements
        if   self.state.user_requirements == 'no' :
            print('==================== by see you ==============')
            return None
        else :
            router_crew = router_Crew().crew()
            router_result = router_crew.kickoff(inputs = {"scraped_data_path" : self.scraped_data_path})
            file_ext = router_result.raw.strip().lower()

            print("===========")
            print(file_ext)
            print("===========")
            if     file_ext in ["csv","json"] : 
                return 'analyse'
            else :
                return "chat"
        
    @listen('analyse')
    def analyse_data(self) :
        print(f"\n=== Analysing data  STAGE ===")
        self.state.current_stage = "Analysing_data_STAGE"

        import pandasai as pai
        llm = LLM(
                model="qwen/qwen3-coder-480b-a35b-instruct",
                base_url= "https://integrate.api.nvidia.com/v1",
                api_key=  ,
                temperature=0.5,
                top_p=0.95,
                max_tokens=65536,
                frequency_penalty=0,
                presence_penalty=0,
            )

            # Configure PandasAI to use this LLM
        pai.config.set({
            "llm": llm
        })
        df_customers = pai.read_csv("customers.csv")
        question = input ('what you want to know : ').strip() 
        while question.lower() != 'exit' :
            response = df_customers.chat(question)
            print(response)

    @listen('chat')
    def chat_with_data(self) :
        print(f"\n=== Chating with data INFORMATION STAGE ===")
        self.state.current_stage = "Chating_with_data_INFORMATION_STAGE"
        question = input ('chat with your data: ').strip()
        while question.lower() != 'exit' :
            quary_crew = quary_Crew().crew()
            answer = quary_crew.kickoff(inputs = {"user_questions" : question})
            print(answer)
            question = input ('chat with your data: ').strip()

        print('======== by ======== ')



      

                

      




# Usage functions
def kickoff_scraping_flow(url: str = None, requirements: str = None, output_dir: Path = None, interactive: bool = True):
    """Start the web scraping flow"""
    flow = WebScrapingFlow(url=url, output_dir=output_dir, interactive_mode=interactive)
    
    # Set requirements if provided
    if requirements and not interactive:
        flow.state.user_requirements = requirements
    
    # Execute the flow
    flow.kickoff()
    return flow




def plot_flow():
    """Plot the flow structure"""
    flow = WebScrapingFlow()
    flow.plot()
    print("📊 Flow plotting completed")

# Example usage
if __name__ == "__main__":
    # Interactive mode
    flow = kickoff_scraping_flow(interactive=True , output_dir = Path("c:/Users/walam/Desktop/scraping/scraping_output"))
    
    # Or non-interactive mode
    # flow = kickoff_scraping_flow(
    #     url="https://example-ecommerce.com/products",
    #     requirements="Extract product names, prices, ratings, and availability",
    #     interactive=False
    # )
