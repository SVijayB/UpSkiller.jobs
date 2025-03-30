import streamlit as st

st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="centered")

title_alignment = """
<style>
#the-title {
    text-align: center;
}
</style>
"""
st.markdown(title_alignment, unsafe_allow_html=True)
st.title("Choose your AI Tutor")

# Custom CSS for image styling
st.markdown("""
    <style>
    .tutor-image {
        width: 100%;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Display tutor choices as images with buttons below
col1, col2, col3 = st.columns(3)

with col1:
    try:
        st.image("assets/Iron Man_avatar.png", )
    except:
        st.write("Iron Man Image")
        
    if st.button("🦾 Iron Man", use_container_width=True):
        st.session_state.selected_tutor = "Iron Man"
        st.switch_page("pages/tutor.py")

with col2:
    try:
        st.image("assets/Kai Cenat_avatar.png", use_container_width=True)
    except:
        st.write("Kai Cenat Image")
        
    if st.button("🎮 Kai Cenat", use_container_width=True):
        st.session_state.selected_tutor = "Kai Cenat"
        st.switch_page("pages/tutor.py")

with col3:
    try:
        st.image("assets/Genius Professor_avatar.png", use_container_width=True)
    except:
        st.write("Genius Professor Image")
        
    if st.button("📚 Genius Professor", use_container_width=True):
        st.session_state.selected_tutor = "Genius Professor"
        st.switch_page("pages/tutor.py")
