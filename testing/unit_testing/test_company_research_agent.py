# from pathlib import Path
# import sys

# # Get the absolute path of the parent directory
# parent_dir = str(Path(__file__).resolve().parent.parent)

# # Insert the parent directory into the system path
# sys.path.insert(0, parent_dir)

# # Now you can import directly from the parent folder

from dotenv import load_dotenv
import os

from agent_core.company_research_agent import CompanyResearchAgent

load_dotenv()

def create_test_agent() -> CompanyResearchAgent:
    return CompanyResearchAgent(name="CompanyCoreResearchAgent", config={"OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY")})

def test_does_company_name_probably_exist():
    agent = create_test_agent()
    assert agent.does_company_name_probably_exist("Microsoft") == True
    assert agent.does_company_name_probably_exist("ExistentCompanyXYZ") == False

def test_get_company_info():
    agent = create_test_agent()
    info = agent.get_company_info("Microsoft", "financial performance", "last 5 years")
    assert isinstance(info, str)
    assert len(info) > 0

def test_is_time_frame_valid():
    agent = create_test_agent()
    assert agent.is_time_frame_valid("last 5 years") == True
    assert agent.is_time_frame_valid("time frame") == False

def test_do_analysis_on_data_collections():
    agent = create_test_agent()
    data_collection_info = {
        "ai_responses": [
            "Data point 1",
            "Data point 2",
            "Data point 3",
            "Data point 4"
        ]
    }
    analysis = agent.do_analysis_on_data_collections(data_collection_info, "trend analysis")
    assert isinstance(analysis, str)
    assert len(analysis) > 0

def test_generate_report():
    agent = create_test_agent()
    data_analysis_info = {
        "ai_responses": [
            "Analysis point 1",
            "Analysis point 2",
            "Analysis point 3"
        ]
    }
    report = agent.generate_report(data_analysis_info, "executive summary")
    assert isinstance(report, str)
    assert len(report) > 0
