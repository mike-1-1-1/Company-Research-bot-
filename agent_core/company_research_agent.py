from agent_core.agent_core_base import AgentCoreBase

from typing import Any, Dict, Optional

class CompanyResearchAgent(AgentCoreBase):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, base_model: Optional[str] = "gpt-4o-mini", instructions: Optional[str] = "", max_tokens: Optional[int] = 500):
        if(instructions == ""):
            instructions = "You are a witty and concise assistant who helps analysts quickly gather public company information, configure analysis parameters, and generate customized reports through conversational workflows. Use the web search tool to gather relevant information when necessary."
        super().__init__(name, config, base_model, instructions, max_tokens)

    def does_company_name_probably_exist(self, company_name: str) -> bool:
        response = self.get_reply_from_openai(f"Does the company name '{company_name}' probably exist? Please answer with 'Yes' or 'No'.")
        return "yes" in response.strip().lower()

    def get_company_info(self, company_name: str, topic: str, time_frame: str) -> str:
        response = self.get_reply_from_openai(f"Please provide a brief data collection summary of the company '{company_name}', focusing on {topic} within the time frame of {time_frame}.", web_search=True) #Include its industry, headquarters location, and any notable products or services
        return response.strip()
    
    def is_time_frame_valid(self, time_frame: str) -> bool:
        response = self.get_reply_from_openai(f"Is the time frame '{time_frame}' a valid and reasonable time frame for research? Please answer with 'Yes' or 'No'.")
        return "yes" in response.strip().lower()

    def do_analysis_on_data_collections(self, data_collection_info: Dict[str, Any], analysis_type: str) -> str:
        collected_data = data_collection_info.get("ai_responses", [])
        collections_size = len(collected_data)

        collections_suffix_sampling = collected_data[-3:] if collections_size > 3 else collected_data

        analysis_prompt = f"Please analyze the following collected data {collections_suffix_sampling} with the analysis type '{analysis_type}'."
        analysis_response = self.get_reply_from_openai(analysis_prompt)
        return analysis_response.strip()
    def generate_report(self, data_analysis_info: Dict[str, Any], report_style: str) -> str:
        analysis_results = data_analysis_info.get("ai_responses", [])
        analysis_size = len(analysis_results)

        analysis_suffix_sampling = analysis_results[-3:] if analysis_size > 3 else analysis_results

        report_prompt = f"Please generate a report based on the following analysis results {analysis_suffix_sampling} in the format '{report_style}'."
        report_response = self.get_reply_from_openai(report_prompt)
        return report_response.strip()