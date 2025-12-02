"""
Main Streamlit application for CV Job Analyzer.
"""

import streamlit as st
import json
from pathlib import Path
from loguru import logger
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))   # .../SkillBridge/src/cv_analyser
SRC_DIR = os.path.dirname(CURRENT_DIR)                     # .../SkillBridge/src

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)


# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Import modules
from cv_analyser.config import get_settings, Settings
from cv_analyser.utils.pdf_parser import PDFParser, PDFParseError
from cv_analyser.utils.validators import Validators, ValidationError
from cv_analyser.services.groq_service import GroqService, GroqAPIError
from cv_analyser.services.serper_service import SerperService, SerperAPIError
from cv_analyser.models.schemas import AnalysisResponse


# Page configuration
st.set_page_config(
    page_title="CV Job Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .video-card {
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'api_keys_validated' not in st.session_state:
        st.session_state.api_keys_validated = False

def render_sidebar():
    """Render sidebar with configuration."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
        groq_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your API key from https://console.groq.com",
            key="groq_api_key_input"
        )
        
        serper_key = st.text_input(
            "Serper API Key",
            type="password",
            help="Get your API key from https://serper.dev",
            key="serper_api_key_input"
        )
        
        # Validate API keys button
        if st.button("🔐 Validate API Keys", use_container_width=True):
            if not groq_key or not serper_key:
                st.error("Please provide both API keys")
            else:
                with st.spinner("Validating API keys..."):
                    try:
                        # Test Groq
                        groq_service = GroqService(api_key=groq_key)
                        groq_valid = groq_service.test_connection()
                        
                        # Test Serper
                        serper_service = SerperService(api_key=serper_key)
                        serper_valid = serper_service.test_connection()
                        
                        if groq_valid and serper_valid:
                            st.success("✅ Both API keys are valid!")
                            st.session_state.api_keys_validated = True
                            st.session_state.groq_key = groq_key
                            st.session_state.serper_key = serper_key
                        else:
                            if not groq_valid:
                                st.error("❌ Invalid Groq API key")
                            if not serper_valid:
                                st.error("❌ Invalid Serper API key")
                    except Exception as e:
                        st.error(f"Validation error: {str(e)}")
        
        st.markdown("---")
        
        # Model settings
        with st.expander("🎛️ Advanced Settings"):
            st.slider(
                "Analysis Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="Lower = more focused, Higher = more creative",
                key="temperature"
            )
            
            st.number_input(
                "Number of Videos",
                min_value=1,
                max_value=10,
                value=5,
                help="Number of YouTube videos to retrieve",
                key="num_videos"
            )
        
        st.markdown("---")
        
        # About section 
        st.markdown("""
<div style="padding: 15px; border-radius: 10px; background-color: #f7f9fc; color: #111111;">
    <h3 style="margin-bottom: 10px;">📚 About</h3>
    <p style="margin: 0; padding: 0;">
        This app leverages tools to help you understand your skill gaps 
        and bridge them with high-quality learning resources:
    </p>
    <ul style="margin-top: 10px;">
        <li>🚀 <strong>Groq (Llama 4 Scout 17B)</strong> — Ultra-fast AI analysis</li>
        <li>🎥 <strong>Serper API</strong> — Curated YouTube recommendations</li>
        <li>🖥️ <strong>Streamlit</strong> — Clean and interactive user interface</li>
    </ul>

<hr style="margin: 10px 0; border: none; border-top: 1px solid #dddddd;">

<h4 style="margin-bottom: 5px;">👨‍💻 Built by <strong>Olawumi Salaam</strong></h4>
<p style="margin: 0;">AI Engineer</p>

<p style="margin-top: 10px;">
🔗 <a href="https://www.linkedin.com/in/olawumi-salaam" target="_blank" style="color: #0a66c2; text-decoration: none;">LinkedIn Profile</a><br>
💻 <a href="https://github.com/OlawumiSalaam" target="_blank" style="color: #111111; text-decoration: none;">GitHub Portfolio</a>
</p>

<p style="margin-top: 5px; font-size: 0.85rem; color: #555555;">
Crafted with ❤️ to help job seekers level up and land their dream roles.
</p>
</div>        
""", unsafe_allow_html=True)

    return groq_key, serper_key



def render_upload_section():
    """Render CV upload and job description input section."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Upload Your CV")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your CV in PDF format (max 10MB)"
        )
        
        if uploaded_file:
            # Show file info
            file_size = len(uploaded_file.getvalue())
            st.info(f"📄 {uploaded_file.name} ({file_size / 1024:.1f} KB)")
    
    with col2:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
            help="Include all details for better analysis"
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.info(f"📝 {word_count} words")
    
    return uploaded_file, job_description


def display_analysis_results(analysis, serper_key: str, num_videos: int = 5):
    """Display analysis results and video recommendations."""
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Overall score with gauge
    score = analysis.overall_score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Match", f"{score}/100")
        st.progress(score / 100)
    
    with col2:
        st.metric("Skills Match", f"{analysis.skills_match}/100")
        st.progress(analysis.skills_match / 100)
    
    with col3:
        st.metric("Experience Match", f"{analysis.experience_match}/100")
        st.progress(analysis.experience_match / 100)
    
    with col4:
        st.metric("Education Match", f"{analysis.education_match}/100")
        st.progress(analysis.education_match / 100)
    
    # Score interpretation
    if score >= 80:
        st.success("🎯 Excellent Match - You're highly qualified!")
    elif score >= 60:
        st.info("✅ Good Match - Strong candidate with room to improve")
    elif score >= 40:
        st.warning("⚠️ Moderate Match - Significant skill development needed")
    else:
        st.error("❌ Low Match - Consider building foundational skills first")
    
    st.markdown("---")
    
    # Strengths and Missing Skills
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💪 Your Strengths")
        if analysis.strengths:
            for i, strength in enumerate(analysis.strengths, 1):
                st.markdown(f"**{i}.** {strength}")
        else:
            st.markdown("Not specified")
    
    with col2:
        st.subheader("📈 Skills to Develop")
        if analysis.missing_skills:
            for i, skill in enumerate(analysis.missing_skills, 1):
                st.markdown(f"**{i}.** {skill}")
        else:
            st.markdown("No major gaps identified 🎉")
    
    # Gap Analysis
    st.markdown("---")
    st.subheader("🔍 Detailed Gap Analysis")
    st.info(analysis.gaps_analysis)
    
    # 🎯 Focused YouTube Recommendations based on missing skill selected by user
    st.markdown("---")
    st.header("🎥 Recommended Learning Resources")

    if not serper_key:
        st.error("Serper API key is missing. Please add it in the sidebar to see video recommendations.")
        return

    # Filter out placeholder / junk values like "Not specified"
    raw_missing = analysis.missing_skills or []
    real_missing_skills = [
        s for s in raw_missing
        if isinstance(s, str) and s.strip() and s.strip().lower() != "not specified"
    ]

    if not real_missing_skills:
        st.info("No clear skill gaps detected, so there are no specific learning resources to show.")
        return

    st.subheader("Choose a skill to get focused learning videos")

    # Let the user pick which skill to focus on
    selected_skill = st.selectbox(
        "Which skill do you want to learn first?",
        options=real_missing_skills,
        index=0,
        help="Pick the first skill you want to focus on. The app will fetch the best YouTube tutorials for it."
    )

    # Build a dynamic YouTube query from the selected skill
    search_query = f"{selected_skill} tutorial, latest on youtube"
    st.markdown(f"**Search Query:** `{search_query}`")

    from cv_analyser.services.serper_service import SerperService, SerperAPIError

    # Fetch videos for the selected skill
    try:
        with st.spinner(f"🔎 Finding YouTube tutorials for **{selected_skill}**..."):
            serper_service = SerperService(api_key=serper_key)
            videos = serper_service.search_youtube_videos(
                search_query,
                num_results=num_videos,
            )
    except SerperAPIError as e:
        st.error(f"Search Error: {str(e)}")
        logger.error(f"Serper API error: {str(e)}")
        videos = []
    except Exception as e:
        st.error(f"Unexpected error during video search: {str(e)}")
        logger.exception("Unexpected error in YouTube search")
        videos = []

    if videos:
        st.subheader("Top YouTube Videos to Bridge Your Skill Gap")
        for idx, video in enumerate(videos, 1):
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if getattr(video, "thumbnail", None):
                        st.image(video.thumbnail, use_container_width=True)  # 🔁 updated arg
                
                with col2:
                    st.markdown(f"### {idx}. [{video.title}]({video.link})")
                    st.caption(f"📺 **{video.channel}** | ⏱️ {video.duration}")
                
                st.markdown("---")
    else:
        st.info("No videos found for this skill. Try selecting a different one.")

    # Download results
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Prepare data for download
        download_data = {
            "analysis": analysis.dict(),
            "focus_skill": selected_skill,
            "search_query": search_query,
            # We don't serialize videos here to avoid complexity; optional
        }
        
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=json.dumps(download_data, indent=2),
            file_name="cv_analysis.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Analyze Another CV", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()


def main():
    """Main application logic."""
    # Initialize
    initialize_session_state()
    
    
    # Header
    st.markdown('<div class="main-header">📄 CV Job Analyzer</div>', unsafe_allow_html=True)
    st.markdown("Upload your CV and paste a job description to get AI-powered analysis and personalized learning recommendations.")
    
    # Sidebar
    groq_key, serper_key = render_sidebar()
    
    # Main content
    if st.session_state.analysis_result:
        # Display cached results with interactive skill selection
        serper_key_in_state = st.session_state.get("serper_key", "")
        display_analysis_results(
            st.session_state.analysis_result,
            serper_key_in_state,
            num_videos=st.session_state.get('num_videos', 5)
        )
        
    else:
        # Upload and input section
        uploaded_file, job_description = render_upload_section()
        
        # Analyze button
        st.markdown("---")
        if st.button("🔍 Analyze CV", type="primary", use_container_width=True):
            # Validation
            errors = []
            
            if not uploaded_file:
                errors.append("Please upload a CV (PDF file)")
            
            if not job_description:
                errors.append("Please paste a job description")
            
            if not groq_key:
                errors.append("Please enter your Groq API key")
            
            if not serper_key:
                errors.append("Please enter your Serper API key")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    # Extract CV text
                    with st.spinner("📄 Extracting text from CV..."):
                        pdf_parser = PDFParser()
                        cv_text = pdf_parser.extract_text(uploaded_file)
                        logger.info(f"Extracted {len(cv_text)} characters from CV")
                    
                    # Validate inputs
                    validators = Validators()
                    
                    cv_valid, cv_msg = validators.validate_text_length(cv_text, min_length=100)
                    if not cv_valid:
                        st.error(f"CV validation failed: {cv_msg}")
                        return
                    
                    jd_valid, jd_msg = validators.validate_text_length(job_description, min_length=50)
                    if not jd_valid:
                        st.error(f"Job description validation failed: {jd_msg}")
                        return
                    
                    # Show warnings if content doesn't look typical
                    _, cv_warning = validators.validate_cv_content(cv_text)
                    if cv_warning:
                        st.warning(cv_warning)
                    
                    _, jd_warning = validators.validate_job_description(job_description)
                    if jd_warning:
                        st.warning(jd_warning)
                    
                    # Analyze with Groq
                    with st.spinner("🤖 Analyzing CV with AI... This may take 10-20 seconds"):
                        groq_service = GroqService(api_key=groq_key)
                        try:
                            analysis = groq_service.analyze_cv(cv_text, job_description)
                            logger.info("Analysis complete")
                        except GroqAPIError as e:
                            error_msg = str(e)
                            st.error(f"AI Analysis Error: {error_msg}")
                            
                            # Show helpful debug info
                            with st.expander("🔍 Debug Information"):
                                st.code(f"Error: {error_msg}")
                                st.info("""
                                **Possible causes:**
                                1. API returned unexpected format
                                2. Model didn't follow JSON instructions
                                3. Response was too long or truncated
                                
                                **Try:**
                                - Shorten your CV or job description
                                - Try again (sometimes works on retry)
                                - Check API status at console.groq.com
                                """)
                            logger.error(f"Groq API error: {error_msg}")
                            return
                    
                    st.success("✅ Analysis complete!")
                  
        
                    # Cache just the analysis; videos will be fetched dynamically per selected skill
                    st.session_state.analysis_result = analysis

                    # Display results (will handle YouTube search inside)
                    display_analysis_results(
                        analysis,
                        serper_key,
                        num_videos=st.session_state.get('num_videos', 5)
                    )
                    
                except PDFParseError as e:
                    st.error(f"PDF Error: {str(e)}")
                    logger.error(f"PDF parse error: {str(e)}")
                except GroqAPIError as e:
                    st.error(f"Analysis Error: {str(e)}")
                    logger.error(f"Groq API error: {str(e)}")
                except SerperAPIError as e:
                    st.error(f"Search Error: {str(e)}")
                    logger.error(f"Serper API error: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected Error: {str(e)}")
                    logger.exception("Unexpected error in main")


if __name__ == "__main__":
    main()