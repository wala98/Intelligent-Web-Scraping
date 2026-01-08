from crewai import Agent, Task, Crew
from crewai_tools import LlamaIndexTool
from llama_index.core import VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader

# Load and index documents
path = "c:/Users/walam/Desktop/scraping/scraping_output"
documents = SimpleDirectoryReader(path).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Create LlamaIndex tool
retrieval_tool = LlamaIndexTool.from_query_engine(
    query_engine,
    name="Document Query Tool",
    description="Search and retrieve information from documents"
)

@CrewBase
class query_Crew():

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Retriever Agent
    @agent
    def retriever_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['retriever_agent'],
            verbose=True,
            llm=llm,
            function_calling_llm=llm,
            tools=[retrieval_tool]
        )

    # Task with user question
    @task
    def retrieval_task(self) -> Task:
        return Task(
            config=self.tasks_config['task_retrieval'],
            agent=self.retriever_agent(),
            markdown = True
        )

    # Crew definition
    @crew
    def crew(self) -> Crew:
        """Creates the QueryCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            function_calling_llm=llm,
        )