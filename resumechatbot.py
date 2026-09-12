import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. DATABASE CONFIGURATION (Reading CSV)
# ----------------------------------------------------
@st.cache_data(ttl=1)
def load_profiles_from_github():
    try:
        df = pd.read_csv("profiles.csv")
        return df
    except Exception as e:
        st.error(f"Could not read local data asset. Error: {e}")
        fallback_data = {"Name": ["Error"], "Email": ["error@example.com"], "Skills": ["Error"], "Filename": ["error.pdf"]}
        return pd.DataFrame(fallback_data)

profiles_df = load_profiles_from_github()

# ----------------------------------------------------
# 2. APPLICATION LAYOUT & STYLING UI
# ----------------------------------------------------
st.set_page_config(page_title="Advanced Profile Finder", page_icon="🔍", layout="wide")
st.title("🔍 Advanced Profile Recruiter Grid Portal")

# Custom CSS for modern visual grid cards and colored metric tags
st.markdown("""
<style>
    .candidate-card {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        height: 100%;
    }
    .skill-tag-matched {
        display: inline-block;
        background-color: #2e7d32;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        margin: 2px;
        font-size: 12px;
        font-weight: bold;
    }
    .skill-tag-normal {
        display: inline-block;
        background-color: #e0e0e0;
        color: #333333;
        padding: 3px 8px;
        border-radius: 4px;
        margin: 2px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. SIDEBAR: INTERACTIVE SKILL CHECKLIST
# ----------------------------------------------------
with st.sidebar:
    st.header("🎯 Interactive Filters")
    st.write("Check boxes below to instantly filter matching profiles in the grid view.")
    
    # Define a clean list of all unique skills present in your profiles database
    available_skills = ["Oracle DBA", "OCI", "Oracle Designer", "Python Basics", "Streamlit", "AWS", "Cloud Security", "Linux", "PL/SQL", "Git"]
    available_skills.sort()
    
    # Create the checkbox group list
    selected_sidebar_skills = []
    st.write("**Filter by Skill Matrix:**")
    for skill in available_skills:
        if st.checkbox(skill, key=f"cb_{skill}"):
            selected_sidebar_skills.append(skill.lower())

# ----------------------------------------------------
# 4. CHAT HISTORY INITIALIZATION
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Good morning! You can search using the input box below or click the skill checkboxes in the sidebar."}
    ]

# Display history loops
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# ----------------------------------------------------
# 5. DATA MATCHING ENGINE & QUERY PROCESSING
# ----------------------------------------------------
user_input = st.chat_input("Or type skills here (e.g., OCI, Python)...")

# Track active keywords from either source (Chat box input takes priority, otherwise uses sidebar checkmarks)
search_keywords = []
display_query_text = ""

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    search_keywords = [kw.strip().lower() for kw in user_input.split(",") if kw.strip()]
    display_query_text = user_input
elif selected_sidebar_skills:
    search_keywords = selected_sidebar_skills
    display_query_text = ", ".join([s.title() for s in selected_sidebar_skills])

# Filter profiles based on selected/typed criteria
if search_keywords:
    def match_row(skills_str):
        if pd.isna(skills_str):
            return False
        return any(kw in str(skills_str).lower() for kw in search_keywords)
    
    matched_profiles = profiles_df[profiles_df["Skills"].apply(match_row)]
    
    if not matched_profiles.empty:
        st.markdown(f"### 🎯 Found **{len(matched_profiles)}** matching candidate(s) for **'{display_query_text}'**:")
        
        # Grid creation (3 columns maximum per row display)
        cols = st.columns(3)
        
        for idx, (_, row) in enumerate(matched_profiles.iterrows()):
            original_name = str(row['Name']).strip()
            target_file = str(row['Filename']).strip()
            all_skills = [s.strip() for s in str(row['Skills']).split(",") if s.strip()]
            
            # Highlight matched skills in green tags
            tags_html = ""
            for skill in all_skills:
                is_matched = any(kw in skill.lower() for kw in search_keywords)
                tag_class = "skill-tag-matched" if is_matched else "skill-tag-normal"
                tags_html += f'<span class="{tag_class}">{skill}</span> '
            
            col_target = cols[idx % 3]
            
            with col_target:
                card_html = f"""
                <div class="candidate-card">
                    <h4 style="margin-top:0; color:#1f77b4; font-size:16px;">👤 {original_name}</h4>
                    <p style="font-size:13px; margin-bottom:8px;">📧 <b>Email:</b> <a href="mailto:{row['Email']}">{row['Email']}</a></p>
                    <p style="font-size:13px; margin-bottom:10px;"><b>Expertise Matrix:</b></p>
                    <div style="margin-bottom:15px;">{tags_html}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Fetch binary asset directly from server directory workspace safely
                try:
                    with open(target_file, "rb") as file_asset:
                        bytes_data = file_asset.read()
                    st.download_button(
                        label="📥 Download Profile File",
                        data=bytes_data,
                        file_name=target_file,
                        mime="application/pdf",
                        key=f"dl_grid_{idx}_{target_file}"
                    )
                except FileNotFoundError:
                    st.warning(f"📄 File '{target_file}' missing.")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
        if user_input:
            st.session_state.messages.append({"role": "assistant", "content": f"Displayed advanced grid matrix for query: '{user_input}'"})
    else:
        st.markdown(f"No profile matches found for **'{display_query_text}'**.")
