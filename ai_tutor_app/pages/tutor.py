import streamlit as st
from google import genai
from styles import TUTOR_STYLES
from dotenv import load_dotenv
import os
import time
import asyncio

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
CLIENT = genai.Client(api_key=GOOGLE_API_KEY)

# Retrieve selected tutor from session state
selected_tutor = st.session_state.get("selected_tutor", "Genius Professor")
style = TUTOR_STYLES[selected_tutor]

# Create a unique prefix for this tutor's session state variables
tutor_prefix = f"{selected_tutor}_"

# Apply the theme
st.set_page_config(
    page_title=f"{selected_tutor} AI Tutor",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {style["theme_color"]};
            color: {style["text_color"]};
        }}
        .stButton>button {{
            color: {style["theme_color"]};
            background-color: {style["text_color"]};
        }}
    </style>
""", unsafe_allow_html=True)


st.title(f"{selected_tutor} AI Tutor")
st.write(style["greeting"])

# 📝 Topic input
topic = st.text_input("Enter a topic you want to learn about:")

def call_gemini(prompt):
    """Call Google Gemini API with a prompt"""
    response = CLIENT.models.generate_content(
                model="gemini-2.0-flash-lite", contents=prompt
            )
    return response.text.strip()

def chat_stream(message):
    for word in message.split():
        yield word + " "
        time.sleep(0.05)  # Adjust the delay between words as needed

# Initialize tutor-specific session state variables
if f"{tutor_prefix}current_section" not in st.session_state:
    st.session_state[f"{tutor_prefix}current_section"] = 0
if f"{tutor_prefix}current_topic" not in st.session_state:
    st.session_state[f"{tutor_prefix}current_topic"] = ""
if f"{tutor_prefix}subtopic_selected" not in st.session_state:
    st.session_state[f"{tutor_prefix}subtopic_selected"] = False
if f"{tutor_prefix}typed_sections" not in st.session_state:
    st.session_state[f"{tutor_prefix}typed_sections"] = set()
if f"{tutor_prefix}section_chat_history" not in st.session_state:
    st.session_state[f"{tutor_prefix}section_chat_history"] = []

# 🚀 Learning Path
if topic:
    # Check if topic has changed for this tutor
    if topic != st.session_state[f"{tutor_prefix}current_topic"]:
        # Clear tutor-specific subtopics when topic changes
        if f"{tutor_prefix}subtopics" in st.session_state:
            del st.session_state[f"{tutor_prefix}subtopics"]
        # Update current topic for this tutor
        st.session_state[f"{tutor_prefix}current_topic"] = topic
        # Reset subtopic selection for this tutor
        st.session_state[f"{tutor_prefix}subtopic_selected"] = False
    
    st.subheader(f"📖 Learning: {topic}")

    # Step 1: Get subtopics
    if f"{tutor_prefix}subtopics" not in st.session_state:
        subtopics_raw = call_gemini(f"List key subtopics for {topic} as a numbered list. Format each subtopic on its own line with just the subtopic text (no descriptions or additional information). do not use numbering or bullets.")
        st.session_state[f"{tutor_prefix}subtopics"] = subtopics_raw.split("\n")

    # Step 2: Choose a subtopic
    subtopic_choice = st.selectbox("Pick a subtopic:", st.session_state[f"{tutor_prefix}subtopics"])
    
    # Check if user wants to learn a new subtopic
    learn_button = st.button("Learn this subtopic")
    
    # If user clicks learn button for a new subtopic
    if learn_button:
        # Reset state for new subtopic selection
        st.session_state[f"{tutor_prefix}current_subtopic"] = subtopic_choice
        st.session_state[f"{tutor_prefix}current_section"] = 0
        if f"{tutor_prefix}explanation_sections" in st.session_state:
            del st.session_state[f"{tutor_prefix}explanation_sections"]
        if f"{tutor_prefix}section_chat_history" in st.session_state:
            st.session_state[f"{tutor_prefix}section_chat_history"] = []
        if f"{tutor_prefix}typed_sections" in st.session_state:
            st.session_state[f"{tutor_prefix}typed_sections"] = set()
        st.session_state[f"{tutor_prefix}subtopic_selected"] = True
        st.rerun()  # Rerun to refresh with new selection
        
    # Only proceed with teaching if a subtopic has been selected
    if st.session_state[f"{tutor_prefix}subtopic_selected"]:
        current_subtopic = st.session_state[f"{tutor_prefix}current_subtopic"]
        st.subheader(f"📚 Teaching: {current_subtopic}")
        
        # Generate explanation in tutor's style (only once per subtopic)
        if f"{tutor_prefix}explanation_sections" not in st.session_state:
            explanation = call_gemini(f"Explain {current_subtopic} in {selected_tutor}'s style, breaking it into 3 short sections.")
            st.session_state[f"{tutor_prefix}explanation_sections"] = explanation.split("\n\n")
        
        sections = st.session_state[f"{tutor_prefix}explanation_sections"]
        current_section = st.session_state[f"{tutor_prefix}current_section"]
        
        # Display all sections up to the current one
        for i in range(current_section + 1):
            if i < len(sections):
                with st.chat_message("assistant", avatar=f"assets/{selected_tutor}_avatar.png"):
                    # If this section has already been displayed with typing effect before
                    # or it's not the current section, display it statically
                    if i in st.session_state[f"{tutor_prefix}typed_sections"] or i < current_section:
                        st.markdown(sections[i])
                    else:
                        # Only apply typing effect to the current section if it hasn't been typed before
                        st.write_stream(chat_stream(sections[i]))
                        # Mark this section as having been displayed with typing effect
                        st.session_state[f"{tutor_prefix}typed_sections"].add(i)
        
        # Display chat history for questions and answers
        for message in st.session_state[f"{tutor_prefix}section_chat_history"]:
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else f"assets/{selected_tutor}_avatar.png"):
                st.markdown(message["content"])
        
        # Chat input for questions about this section
        if question := st.chat_input("Ask a question about this topic..."):
            # Add user question to chat history
            st.session_state[f"{tutor_prefix}section_chat_history"].append({"role": "user", "content": question})
            
            # Generate answer to the question
            current_section_content = sections[min(current_section, len(sections)-1)]
            answer = call_gemini(f"Answer in {selected_tutor}'s style this question about {current_subtopic}: '{question}'. Base your answer on this content: {current_section_content}. If the question is not related to the {topic}, then tell the user it is not possible to answer.")
            
            # Add assistant answer to chat history with a flag indicating it should be typed out
            st.session_state[f"{tutor_prefix}section_chat_history"].append(
                {"role": "assistant", "content": answer, "should_type": True}
            )
            
            # Rerun to display the updated chat
            st.rerun()

        # Display chat history for questions and answers
        for i, message in enumerate(st.session_state[f"{tutor_prefix}section_chat_history"]):
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else f"assets/{selected_tutor}_avatar.png"):
                # If it's an assistant message that should be typed out
                if message["role"] == "assistant" and message.get("should_type", False):
                    st.write_stream(chat_stream(message["content"]))
                    # After displaying with typing effect, mark it as already typed
                    st.session_state[f"{tutor_prefix}section_chat_history"][i]["should_type"] = False
                else:
                    st.markdown(message["content"])

        
        # Only show Next button if not at the end of all sections
        if current_section < len(sections):
            # Create a container for the Next button at the bottom right
            button_container = st.container()
            with button_container:
                # Use columns to position the button on the right
                _, _, right_col = st.columns([5, 2, 1])
                with right_col:
                    if st.button("Next ➡️", key=f"next_{current_section}"):
                        st.session_state[f"{tutor_prefix}current_section"] += 1
                        st.rerun()
        else:
            st.success("🎉 You've completed all sections for this subtopic!")
