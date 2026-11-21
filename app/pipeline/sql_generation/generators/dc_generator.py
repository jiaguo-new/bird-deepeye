from .base import BaseSQLGenerator
from .value_anchors import format_value_anchors
from app.dataset import DataItem
from app.llm import LLM
from app.logger import logger
from app.prompt import PromptFactory
from typing import Dict, List, Tuple


class DCGenerator(BaseSQLGenerator):

    def generate(self, data_item: DataItem, llm: LLM, sampling_budget: int = 1) -> Tuple[List[str], Dict[str, int]]:
        return self._generate(data_item, llm, sampling_budget, semantic_checks=False)

    def generate_mixed(self, data_item: DataItem, llm: LLM, total_budget: int, semantic_budget: int,
                       include_value_anchors: bool = False, full_schema_budget: int = 0):
        anchors = format_value_anchors(data_item) if include_value_anchors else ""
        standard, standard_usage = self._generate(
            data_item, llm, total_budget - semantic_budget - full_schema_budget,
            semantic_checks=False, anchors=anchors,
        )
        guided, guided_usage = self._generate(
            data_item, llm, semantic_budget, semantic_checks=True, anchors=anchors,
        )
        full, full_usage = self._generate(
            data_item, llm, full_schema_budget, semantic_checks=False, anchors=anchors,
            full_schema=True,
        )
        usage = {key: standard_usage[key] + guided_usage[key] + full_usage[key] for key in standard_usage}
        if standard is None or guided is None or full is None:
            return None, usage
        return standard + guided + full, usage

    def _generate(self, data_item, llm, sampling_budget, *, semantic_checks, anchors="", full_schema=False):
        if sampling_budget == 0:
            return [], {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        db_type = getattr(data_item, "db_type", None)
        
        # Define the prompt format function for DC generator
        def prompt_format_func(schema_profile: str) -> str:
            prompt = PromptFactory.format_dc_sql_generation_prompt(
                schema_profile, 
                data_item.question, 
                data_item.evidence, 
                db_type=db_type
            )
            if semantic_checks:
                prompt += (
                    "\nBefore writing the SQL, check the requested output columns and row grain. "
                    "For each condition in the question and evidence, establish which column, "
                    "comparison and value encode it. Use only conditions supported by the request. "
                    "If a join is needed, verify its keys and whether it duplicates the counted "
                    "entity. For aggregates or rankings, verify grouping, distinctness, and how "
                    "ties should be treated from the wording. Return SQL in the requested format."
                )
            return prompt + anchors
            
        if full_schema:
            schema = getattr(data_item, "database_schema_after_value_retrieval", None) or data_item.database_schema
            final_prompt, level = self._generate_with_progressive_stripping(
                data_item, llm, prompt_format_func, schema_override=schema,
            )
        else:
            final_prompt, level = self._generate_with_progressive_stripping(data_item, llm, prompt_format_func)
        
        if final_prompt is None:
            logger.error(f"CRITICAL: Even minimal DC prompt for item {data_item.question_id} exceeds token limit. Returning empty result.")
            return [], {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            
        extractor = self._get_extractor()
        all_sql_candidates, total_token_usage = extractor.extract_with_retry(
            llm=llm,
            messages=[{"role": "user", "content": final_prompt}],
            rule_parser=self._parse_llm_response,
            fix_end_token=llm.llm_config.fix_end_token,
            end_token="</result>",
            n=sampling_budget
        )
        
        return all_sql_candidates, total_token_usage
