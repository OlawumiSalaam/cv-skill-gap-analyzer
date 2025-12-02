"""
Groq API service for CV analysis using Llama models.
Uses settings from .env file for model configuration.
"""

import json
from typing import Optional

# Import Groq SDK
try:
    from groq import Groq
except ImportError as e:
    raise ImportError(
        "Groq SDK not installed. Please run: pip install groq"
    ) from e

from loguru import logger
from cv_analyser.models.schemas import CVAnalysis
from cv_analyser.config import get_settings


class GroqAPIError(Exception):
    """Custom exception for Groq API errors."""
    pass


class GroqService:
    """Service for interacting with Groq API using official SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq service.
        
        Args:
            api_key: Groq API key (if None, loads from settings)
        """
        try:
            self.settings = get_settings()
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
            self.settings = None
        
        self.api_key = api_key or (self.settings.groq_api_key if self.settings else None)
        
        if not self.api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable.")
        
        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
            logger.debug("Groq client initialized successfully")
        except Exception as e:
            raise GroqAPIError(f"Failed to initialize Groq client: {str(e)}")
    
    def _get_model_config(self):
        """Get model configuration from settings or use defaults."""
        defaults = {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "max_tokens": 8192,
        }
        
        if self.settings:
            return {
                "model": getattr(self.settings, "groq_model", defaults["model"]),
                "temperature": getattr(self.settings, "groq_temperature", defaults["temperature"]),
                "max_tokens": getattr(self.settings, "groq_max_tokens", defaults["max_tokens"]),
            }
        return defaults
    
    def _build_analysis_prompt(self, cv_text: str, job_description: str) -> str:
        """
        Build a robust prompt that FORCES the model to output meaningful JSON only.
        Prevents:
        - echoing the CV / JD
        - empty / all-zero analysis
        """

        # Truncate inputs to avoid model drift from very long prompts
        max_cv_length = 2800
        max_jd_length = 1800

        if len(cv_text) > max_cv_length:
            cv_text = cv_text[:max_cv_length] + "..."
            logger.warning(f"CV truncated to {max_cv_length} characters")

        if len(job_description) > max_jd_length:
            job_description = job_description[:max_jd_length] + "..."
            logger.warning(f"Job description truncated to {max_jd_length} characters")

        return f"""
SYSTEM INSTRUCTION (READ CAREFULLY AND FOLLOW STRICTLY):

You are an AI career analyst. Your ONLY task is to compare a CV to a Job Description and return a STRICT JSON object.

ABSOLUTE RULES:
- DO NOT repeat or rewrite the CV text.
- DO NOT repeat or rewrite the Job Description text.
- DO NOT output explanations, markdown, commentary, or any text outside the JSON.
- The output MUST:
  - Start with '{{'
  - End with '}}'
  - Contain EXACTLY the required keys (no more, no less).
  - NEVER omit any field.
  - NEVER return all zeros or empty lists.
  - NEVER leave skill_gap_analysis_summary empty.

You must deeply analyze the CV against the Job Description and produce a realistic, non-trivial evaluation.

REQUIRED JSON FORMAT (KEYS AND TYPES):

{{
  "overall_score": 0,
  "skills_match": 0,
  "experience_match": 0,
  "education_match": 0,
  "matching_skills": [],
  "missing_skills": [],
  "youtube_search_query": "",
  "skill_gap_analysis_summary": ""
}}

MEANINGS:
- overall_score: integer 0–100, overall match between candidate and role.
- skills_match: integer 0–100, how well their skills align with the JD.
- experience_match: integer 0–100, how well their years/type of experience align.
- education_match: integer 0–100, how well education fits the requirements.
- matching_skills: list of STRINGS describing strong or matching skills.
- missing_skills: list of STRINGS describing concrete missing/weak skills.
- youtube_search_query: a single STRING query for the most important missing skill.
  - MUST end with ", latest on youtube".
- skill_gap_analysis_summary: 150–250 word professional narrative summarising:
  - key strengths
  - most critical gaps
  - how gaps affect readiness
  - what to learn next.

IMPORTANT CONSTRAINTS:
- DO NOT use nested objects inside matching_skills or missing_skills.
  Example: ["TensorFlow", "Kubernetes", "Azure DevOps"], NOT [{{"name": "TensorFlow"}}].
- DO NOT return placeholder or dummy analysis.
- DO NOT return all scores as 0.
- DO NOT return empty arrays for both matching_skills and missing_skills.
- DO NOT leave skill_gap_analysis_summary blank.

BAD OUTPUT EXAMPLE (NEVER DO THIS):
{{
  "overall_score": 0,
  "skills_match": 0,
  "experience_match": 0,
  "education_match": 0,
  "matching_skills": [],
  "missing_skills": [],
  "youtube_search_query": "",
  "skill_gap_analysis_summary": ""
}}

GOOD OUTPUT EXAMPLE (STRUCTURE ONLY, CONTENT WILL DIFFER):
{{
  "overall_score": 68,
  "skills_match": 72,
  "experience_match": 65,
  "education_match": 80,
  "matching_skills": [
    "Strong Python for data engineering and ML",
    "Hands-on experience with AWS (Lambda, S3, SageMaker)",
    "Good foundation in ML model training and evaluation"
  ],
  "missing_skills": [
    "Kubernetes for container orchestration",
    "Experience with Spark for large-scale data processing",
    "Formal MLOps tools such as MLflow"
  ],
  "youtube_search_query": "Kubernetes for data engineers tutorial, latest on youtube",
    "skill_gap_analysis_summary": "..."
}}

NOW ANALYZE THE FOLLOWING DATA:

CV TEXT (DO NOT ECHO THIS BACK):
{cv_text}

JOB DESCRIPTION TEXT (DO NOT ECHO THIS BACK):
{job_description}

NOW OUTPUT ONLY A VALID, NON-EMPTY JSON OBJECT IN THE REQUIRED FORMAT.
START WITH '{{' AND END WITH '}}'. NO OTHER TEXT.
"""
    
    def analyze_cv(self, cv_text: str, job_description: str) -> CVAnalysis:
        """
        Analyze CV against job description using Groq API.
        
        Args:
            cv_text: Candidate's CV text
            job_description: Job description text
            
        Returns:
            CVAnalysis: Analysis results
            
        Raises:
            GroqAPIError: If API call fails
        """
        try:
            # Build prompt
            prompt = self._build_analysis_prompt(cv_text, job_description)
            
            # Get model configuration from .env
            config = self._get_model_config()
            
            # Log configuration being used
            logger.info(f"Using model: {config['model']}")
            logger.info(f"Temperature: {config['temperature']}, Max tokens: {config['max_tokens']}")
            
            # Make API request using official SDK
            logger.info("Sending request to Groq API...")
            logger.info(f"Prompt length: {len(prompt)} characters")
            logger.debug(f"Prompt preview: {prompt[:300]}...")
            
            completion = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career coach AI that helps job seekers to improve their skills so they are qualified for desired jobs.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=config["temperature"],
                max_completion_tokens=config["max_tokens"],
            )
            
            # Extract response content
            result_text = completion.choices[0].message.content
            logger.info(f"Received response, length: {len(result_text)} characters")
            logger.debug(f"Raw API response (first 300 chars): {result_text[:300]}")
            
            # Parse JSON response
            try:
                clean_text = result_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                analysis_data = json.loads(clean_text)
                logger.debug("Successfully parsed JSON response")
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Response text (first 500 chars): {result_text[:500]}")
                
                # Try to find JSON in the response
                import re
                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group(0))
                        logger.info("Successfully extracted JSON using regex")
                    except Exception:
                        raise GroqAPIError(
                            "Model returned invalid JSON even after extraction. "
                            "Try again, or slightly shorten your CV / job description."
                        )
                else:
                    raise GroqAPIError(
                        "Model did not return JSON format. "
                        f"Current model: {config['model']}"
                    )
            
            # Log what we received to debug
            logger.info(f"Received JSON keys: {list(analysis_data.keys())}")
            logger.info(f"Full JSON response: {json.dumps(analysis_data, indent=2)}")
            
            # Convert to our CVAnalysis model
            try:
                # Extract values with all possible key variations
                overall = (
                    analysis_data.get("overall_score")
                    or analysis_data.get("Overall Match Score")
                    or analysis_data.get("Match Score")
                    or analysis_data.get("match_score")
                    or 0
                )

                skills = (
                    analysis_data.get("skills_match")
                    or analysis_data.get("Skills Match")
                    or 0
                )

                experience = (
                    analysis_data.get("experience_match")
                    or analysis_data.get("Experience Match")
                    or 0
                )

                education = (
                    analysis_data.get("education_match")
                    or analysis_data.get("Education Match")
                    or 0
                )

                strengths = (
                    analysis_data.get("matching_skills")
                    or analysis_data.get("strong_skills")
                    or analysis_data.get("matching_strong_skills")
                    or analysis_data.get("Matching/Strong Skills")
                    or analysis_data.get("Matching / strong skills")
                    or analysis_data.get("Matching Skills")
                    or []
                )

                missing = (
                    analysis_data.get("missing_skills")
                    or analysis_data.get("missing_weak_skills")
                    or analysis_data.get("Missing/Weak Skills")
                    or analysis_data.get("Missing / weak skills")
                    or analysis_data.get("Missing Skills")
                    or []
                )

                summary = (
                    analysis_data.get("skill_gap_analysis_summary")
                    or analysis_data.get("Summary")
                    or analysis_data.get("Skill Gap Summary")
                    or ""
                )

                query = (
                    analysis_data.get("youtube_search_query")
                    or analysis_data.get("Search Query")
                    or analysis_data.get("YouTube search query")
                    or analysis_data.get("YouTube Search Query")
                    or ""
                )

                logger.info(
                    f"Extracted values - Overall: {overall}, Skills: {skills}, "
                    f"Exp: {experience}, Edu: {education}"
                )
                logger.info(
                    f"Strengths count (raw): {len(strengths)}, Missing count (raw): {len(missing)}"
                )

                # ---- Helper to detect nearly-empty lists ----
                def _is_truly_empty_list(lst):
                    if not lst:
                        return True
                    cleaned = [
                        str(x).strip().lower()
                        for x in lst
                        if str(x).strip()
                    ]
                    if not cleaned:
                        return True
                    if all(x in ("not specified", "n/a", "none") for x in cleaned):
                        return True
                    return False

                # 🔹 Normalize strengths to list[str]
                strengths_norm = []
                if isinstance(strengths, list):
                    for item in strengths:
                        if isinstance(item, str):
                            strengths_norm.append(item)
                        elif isinstance(item, dict):
                            # e.g. {"name": "Python", "importance": 9}
                            name = item.get("name") or item.get("skill") or str(item)
                            importance = item.get("importance")
                            if importance is not None:
                                strengths_norm.append(f"{name} (importance {importance}/10)")
                            else:
                                strengths_norm.append(name)
                        else:
                            strengths_norm.append(str(item))
                elif isinstance(strengths, str):
                    strengths_norm = [strengths]

                # 🔹 Normalize missing_skills to list[str]
                missing_norm = []
                if isinstance(missing, list):
                    for item in missing:
                        if isinstance(item, str):
                            missing_norm.append(item)
                        elif isinstance(item, dict):
                            name = item.get("name") or item.get("skill") or str(item)
                            importance = item.get("importance")
                            if importance is not None:
                                missing_norm.append(f"{name} (importance {importance}/10)")
                            else:
                                missing_norm.append(name)
                        else:
                            missing_norm.append(str(item))
                elif isinstance(missing, str):
                    missing_norm = [missing]

                logger.info(
                    f"Normalized strengths: {strengths_norm}, "
                    f"Normalized missing_skills: {missing_norm}"
                )

                # --- Sanity check: detect completely empty / useless analysis ---
                all_zero_scores = (
                    int(overall) == 0
                    and int(skills) == 0
                    and int(experience) == 0
                    and int(education) == 0
                )

                no_real_strengths = _is_truly_empty_list(strengths_norm)
                no_real_missing = _is_truly_empty_list(missing_norm)
                empty_summary = not summary or not summary.strip()
                empty_query = not query or not query.strip()

                if (
                    all_zero_scores
                    and no_real_strengths
                    and no_real_missing
                    and empty_summary
                    and empty_query
                ):
                    logger.error("Model returned structurally valid but COMPLETELY EMPTY analysis.")
                    raise GroqAPIError(
                        "The AI returned an empty analysis. "
                        "Please try again or slightly shorten your CV / job description."
                    )

                converted_data = {
                    "overall_score": int(overall),
                    "skills_match": int(skills),
                    "experience_match": int(experience),
                    "education_match": int(education),
                    "strengths": strengths_norm if strengths_norm else ["Not specified"],
                    "missing_skills": missing_norm if missing_norm else ["Not specified"],
                    "gaps_analysis": (
                        summary.strip()
                        if summary and summary.strip()
                        else "Analysis not available. Please review the strengths and missing skills above."
                    ),
                    "youtube_search_query": query if query else "skill improvement tutorial",
                }

                # Log what we're trying to create
                logger.debug(f"Converted data: {converted_data}")

                # Validate using Pydantic model
                analysis = CVAnalysis(**converted_data)

                logger.info("✅ Analysis complete!")
                logger.info(f"Overall: {analysis.overall_score}/100")
                logger.info(
                    f"Skills: {analysis.skills_match}/100, "
                    f"Experience: {analysis.experience_match}/100, "
                    f"Education: {analysis.education_match}/100"
                )

                return analysis

            except Exception as e:
                logger.error(f"Error converting response to CVAnalysis: {str(e)}")
                logger.error(f"Response data: {analysis_data}")
                raise GroqAPIError(f"Failed to parse API response into valid format: {str(e)}")
            
        except GroqAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in analyze_cv: {str(e)}")
            logger.exception("Full traceback:")
            
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise GroqAPIError("Invalid API key. Please check your GROQ_API_KEY in .env file.")
            elif "rate limit" in error_msg or "429" in error_msg:
                raise GroqAPIError("Rate limit exceeded. Please wait a moment and try again.")
            elif "timeout" in error_msg:
                raise GroqAPIError("Request timed out. Please try again.")
            elif "model" in error_msg and "not found" in error_msg:
                raise GroqAPIError(
                    f"Model not found. Check GROQ_MODEL in .env file. Current: {self._get_model_config()['model']}"
                )
            else:
                raise GroqAPIError(f"Analysis failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Groq API.
        
        Returns:
            bool: True if connection successful
        """
        try:
            config = self._get_model_config()
            self.client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": "test"}],
                max_completion_tokens=10,
            )
            logger.debug(f"Connection test successful with model: {config['model']}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
