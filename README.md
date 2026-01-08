# Scraping Crew

Multi-agent web analysis and scraping pipeline built on [crewAI](https://crewai.com). It analyzes a target site, plans extraction, scrapes structured data, and optionally chats with or analyzes the scraped output.

## What it does
- **Analyze first:** Inspects site structure to map zones, selectors, and challenges.
- **Scrape flexibly:** Selenium/static scraping tools plus Scrapfly for resilient fetching.
- **Route by data type:** Chooses analysis vs. chat flows based on scraped file types.
- **Chat/Analyze:** Query scraped data or run pandas-ai style analysis with configurable LLMs.

## Installation

Requirements: Python >=3.10 <3.14 and [uv](https://docs.astral.sh/uv/).

1) Install uv (if needed):
```bash
pip install uv
```
2) Install dependencies:
```bash
uv sync
```

## Environment Variables
Create a `.env` file in the project root (already gitignored) with:
```
NVIDIA_API_KEY_1=your_primary_nvidia_key
NVIDIA_API_KEY_2=your_secondary_nvidia_key
GOOGLE_API_KEY=your_google_key
SCRAPFLY_API_KEY=your_scrapfly_key
```

## Quick start
1) Add your keys to `.env`.
2) Run an interactive flow:
```bash
crewai run
```
3) Follow prompts to provide the target URL and requirements. Outputs are stored under `scraping_output/`.

## Project structure
- `src/scraping/main.py` — flow entrypoint (setup → analyze → scrape → route).
- `src/scraping/crews/` — specialized crews:
  - `web_analyser_crew/` — site analysis.
  - `web_scraper_crew2/` — primary scraper (Selenium, Scrapfly, etc.).
  - `router_crew/` — decides next step (analysis vs. chat).
  - `quary_crew/` — Q&A over scraped artifacts.
- `src/scraping/config.py` — loads API keys from environment.
- `scraping_output/` — generated results (analysis JSON, scraped data).

## Customizing
- Update `src/scraping/config/agents.yaml` to define agents.
- Update `src/scraping/config/tasks.yaml` to define tasks.
- Adjust crews in `src/scraping/crew.py` and `src/scraping/main.py` as needed.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the scraping Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The scraping Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Scraping Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
