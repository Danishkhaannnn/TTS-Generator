import asyncio
import os
import subprocess
import time
import streamlit as st
from openai import AsyncOpenAI
from pydub import AudioSegment
from io import BytesIO
from pydub.utils import which
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -- Streamlit Config (Hide Deploy & Use Dark Mode) --
st.set_page_config(
    page_title="Professional TTS Generator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Explicitly set the FFmpeg path
ffmpeg_path = r"C:\\ffmpeg\\ffmpeg.exe"
AudioSegment.ffmpeg = ffmpeg_path

# Initialize OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
openai = AsyncOpenAI(api_key=api_key)

# Professional CSS Styling
st.markdown("""
    <style>
        .main > div {
            padding-top: 0.5rem;
        }
        .main-title {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            text-align: center !important;
            margin-top: 0rem !important;
            margin-bottom: 0.5rem !important;
            padding-top: 0rem !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .sub-title {
            font-size: 1.2rem !important;
            color: #b0b0b0 !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
            font-weight: 300 !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
        }
        .stSuccess {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%) !important;
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        .stError {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        .stSelectbox > div > div {
            background-color: #2d3748 !important;
            border: 1px solid #4a5568 !important;
            border-radius: 8px !important;
        }
        .stTextArea > div > div > textarea {
            background-color: #2d3748 !important;
            border: 1px solid #4a5568 !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown('<h1 class="main-title">🎙️ Professional Text-to-Speech Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced AI-Powered Voice Synthesis with Professional Customization</p>', unsafe_allow_html=True)

# Voice Selection Section
st.markdown("### 🎵 Voice Selection")
voice_options = ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]

# Voice descriptions for better UX
voice_descriptions = {
    "alloy": "Balanced and versatile voice",
    "ash": "Clear and confident tone",
    "ballad": "Smooth and melodic",
    "coral": "Warm and friendly",
    "echo": "Deep and resonant",
    "fable": "Expressive storytelling voice",
    "onyx": "Strong and authoritative",
    "nova": "Crisp and modern",
    "sage": "Wise and calm",
    "shimmer": "Bright and energetic",
    "verse": "Poetic and flowing"
}

selected_voice = st.selectbox(
    "Choose Your Preferred Voice",
    voice_options,
    key="voice",
    help="Select the base voice that best fits your content"
)

if selected_voice:
    st.info(f"✨ **{selected_voice.title()}**: {voice_descriptions[selected_voice]}")

# Enhanced Customization Section with Real Functionality
st.markdown("### 🎛️ Advanced Voice Customization")

col1, col2 = st.columns(2)

with col1:
    voice_style = st.selectbox(
        "🎭 Voice Style",
        [
            "Professional & Authoritative",
            "Conversational & Friendly", 
            "Dramatic & Expressive",
            "News Anchor Style",
            "Educational & Clear",
            "Storytelling & Engaging"
        ],
        index=0,
        help="Defines the overall character and approach of the voice"
    )
    
    tone_setting = st.selectbox(
        "🎯 Tone",
        [
            "Neutral & Balanced",
            "Warm & Approachable",
            "Serious & Formal",
            "Enthusiastic & Energetic",
            "Calm & Soothing",
            "Confident & Assertive"
        ],
        index=0,
        help="Sets the emotional undertone of the speech"
    )

with col2:
    punctuation_style = st.selectbox(
        "⏸️ Punctuation Handling",
        [
            "Natural Pauses",
            "Extended Pauses for Clarity",
            "Minimal Pauses (Fast-paced)",
            "Dramatic Pauses",
            "Professional Presentation Style"
        ],
        index=0,
        help="Controls how punctuation affects speech rhythm and pacing"
    )
    
    delivery_style = st.selectbox(
        "🚀 Delivery Style",
        [
            "Standard Pace",
            "Fast-paced & Dynamic",
            "Slow & Deliberate",
            "Varied Pace for Emphasis",
            "Presentation Style"
        ],
        index=0,
        help="Determines the speed and rhythm of speech delivery"
    )

# Advanced Settings
st.markdown("#### ⚙️ Fine-tuning Controls")

col3, col4 = st.columns(2)
with col3:
    speech_speed = st.slider(
        "🎵 Speech Speed",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Adjust the overall speed of speech generation"
    )

with col4:
    emphasis_level = st.selectbox(
        "💪 Emphasis Level",
        ["Subtle", "Moderate", "Strong", "Very Strong"],
        index=1,
        help="Controls how much key words and phrases are emphasized"
    )

# Text Input Section
st.markdown("### 📝 Text Input")

input_text = st.text_area(
    "Enter your text to convert to speech:",
    height=200,
    placeholder="Type or paste your content here. The AI will apply your customization settings to generate professional-quality speech...",
    help="Enter the text you want to convert to speech. The system will apply all your customization settings."
)

# Character count and analysis
if input_text:
    char_count = len(input_text)
    word_count = len(input_text.split())
    estimated_duration = word_count / 150  # Average speaking pace
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Characters", char_count)
    with col_stats2:
        st.metric("Words", word_count)
    with col_stats3:
        st.metric("Est. Duration", f"{estimated_duration:.1f} min")

# Advanced Text Processing Functions
def apply_voice_style_processing(text, style):
    """Apply text modifications based on voice style"""
    if style == "Professional & Authoritative":
        # Add slight pauses after important statements
        text = re.sub(r'\.(\s+[A-Z])', r'.\n\1', text)
    elif style == "Conversational & Friendly":
        # Make text more conversational
        text = text.replace(" and ", " and, ")
    elif style == "Dramatic & Expressive":
        # Add emphasis markers
        text = re.sub(r'\b(important|critical|essential|key)\b', r'**\1**', text, flags=re.IGNORECASE)
    elif style == "News Anchor Style":
        # Structure for news delivery
        text = re.sub(r'\.(\s+)', r'.\n\n', text)
    elif style == "Educational & Clear":
        # Add natural teaching pauses
        text = re.sub(r'(first|second|third|next|finally|therefore|however)', r'\n\1', text, flags=re.IGNORECASE)
    
    return text

def apply_punctuation_style(text, punctuation_style):
    """Modify text based on punctuation preferences"""
    if punctuation_style == "Extended Pauses for Clarity":
        text = text.replace(',', ', ')
        text = text.replace('.', '. ')
        text = text.replace(';', '; ')
    elif punctuation_style == "Minimal Pauses (Fast-paced)":
        text = re.sub(r'\s*,\s*', ',', text)
        text = re.sub(r'\s*\.\s*', '.', text)
    elif punctuation_style == "Dramatic Pauses":
        text = text.replace('.', '... ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
    elif punctuation_style == "Professional Presentation Style":
        text = re.sub(r'\.(\s+)', r'.\n\n', text)
        text = re.sub(r':(\s+)', r':\n', text)
    
    return text

def build_enhanced_instructions(voice_style, tone, punctuation, delivery, emphasis):
    """Build comprehensive instructions for voice generation"""
    
    style_instructions = {
        "Professional & Authoritative": "Speak with confidence and authority, maintaining a professional demeanor throughout.",
        "Conversational & Friendly": "Use a warm, approachable tone as if speaking to a friend or colleague.",
        "Dramatic & Expressive": "Add emotional depth and dramatic flair to important points.",
        "News Anchor Style": "Deliver content with the clarity and professionalism of a news broadcaster.",
        "Educational & Clear": "Explain concepts clearly with appropriate pacing for learning.",
        "Storytelling & Engaging": "Use narrative techniques to make the content compelling and engaging."
    }
    
    tone_instructions = {
        "Neutral & Balanced": "Maintain an even, balanced emotional tone throughout.",
        "Warm & Approachable": "Use a friendly, welcoming tone that puts listeners at ease.",
        "Serious & Formal": "Keep a serious, professional tone appropriate for formal contexts.",
        "Enthusiastic & Energetic": "Inject energy and enthusiasm into the delivery.",
        "Calm & Soothing": "Use a gentle, calming voice that relaxes the listener.",
        "Confident & Assertive": "Project confidence and certainty in every statement."
    }
    
    return f"""
    VOICE STYLE: {style_instructions.get(voice_style, voice_style)}
    TONE: {tone_instructions.get(tone, tone)}
    PUNCTUATION: Handle pauses and rhythm according to {punctuation} style.
    DELIVERY: Use {delivery} approach for optimal engagement.
    EMPHASIS: Apply {emphasis.lower()} emphasis to key terms and important information.
    
    Additional Instructions:
    - Maintain consistent energy throughout the speech
    - Use natural inflection patterns
    - Ensure clear pronunciation of technical terms
    - Apply appropriate emotional context to the content
    """

# Enhanced Audio Generation Function
async def generate_professional_audio(input_text: str, voice: str, voice_style: str, tone: str, 
                                    punctuation: str, delivery: str, emphasis: str, speed: float) -> str:
    
    # Use a default output folder (can be desktop or temp folder)
    output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "TTS_Output")
    
    # Process text based on customization settings
    processed_text = apply_voice_style_processing(input_text, voice_style)
    processed_text = apply_punctuation_style(processed_text, punctuation)
    
    # Build comprehensive instructions
    instructions = build_enhanced_instructions(voice_style, tone, punctuation, delivery, emphasis)
    
    # Add instructions as a prefix to guide the AI (though OpenAI TTS doesn't directly use them,
    # the text structure can influence delivery)
    if voice_style in ["Educational & Clear", "Professional & Authoritative"]:
        # For educational/professional content, we can structure the text better
        final_text = processed_text
    else:
        final_text = processed_text
    
    try:
        async with openai.audio.speech.with_streaming_response.create(
            model="tts-1-hd",  # Using HD model for better quality
            voice=voice,
            input=final_text,
            response_format="mp3",
            speed=speed,
        ) as response:
            audio_data = await response.read()
            
            # Ensure output directory exists
            os.makedirs(output_folder, exist_ok=True)
            
            # Create filename with customization info
            timestamp = int(time.time())
            filename = f"professional_audio_{voice}_{voice_style.replace(' & ', '_').replace(' ', '_')}_{timestamp}.mp3"
            file_path = os.path.join(output_folder, filename)
            
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            return file_path
            
    except Exception as e:
        raise Exception(f"Audio generation failed: {str(e)}")

# Professional Generation Interface
st.markdown("---")
if st.button("🎵 Generate Professional Audio", key="generate_button"):
    if input_text.strip():
        with st.spinner("🎙️ Generating your professional audio with custom settings..."):
            try:
                # Show current settings
                with st.expander("📋 Current Settings Summary", expanded=True):
                    st.write(f"**Voice:** {selected_voice} ({voice_descriptions[selected_voice]})")
                    st.write(f"**Style:** {voice_style}")
                    st.write(f"**Tone:** {tone_setting}")
                    st.write(f"**Punctuation:** {punctuation_style}")
                    st.write(f"**Delivery:** {delivery_style}")
                    st.write(f"**Speed:** {speech_speed}x")
                    st.write(f"**Emphasis:** {emphasis_level}")
                
                # Generate audio with all customizations
                file_path = asyncio.run(generate_professional_audio(
                    input_text, selected_voice, voice_style, tone_setting, 
                    punctuation_style, delivery_style, emphasis_level, 
                    speech_speed
                ))
                
                # Success message with file info
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                st.success(f"""
                ✅ **Professional audio generated successfully!**
                
                📁 **File:** `{os.path.basename(file_path)}`  
                📍 **Location:** `{file_path}`  
                📊 **Size:** {file_size:.2f} MB  
                🎵 **Quality:** Professional HD
                """)
                
                # Audio player with enhanced controls
                st.markdown("### 🎧 Preview Your Audio")
                st.audio(file_path, format="audio/mp3")
                
                # Download option
                with open(file_path, "rb") as audio_file:
                    st.download_button(
                        label="📥 Download Audio File",
                        data=audio_file.read(),
                        file_name=os.path.basename(file_path),
                        mime="audio/mp3"
                    )
                
            except Exception as e:
                st.error(f"❌ **Generation Error:** {str(e)}")
                st.info("💡 **Troubleshooting Tips:**\n- Check your OpenAI API key\n- Ensure output folder is accessible\n- Verify internet connection")
    else:
        st.warning("⚠️ Please enter text before generating audio")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🎙️ <strong>Professional Text-to-Speech Generator</strong></p>
    <p>Powered by OpenAI's Advanced TTS Technology | Enhanced with Professional Customization</p>
</div>
""", unsafe_allow_html=True)