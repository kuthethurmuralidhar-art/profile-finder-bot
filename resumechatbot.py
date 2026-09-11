import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. DATABASE CONFIGURATION (Reading CSV)
# ----------------------------------------------------
@st.cache_data(ttl=1)  # Keeps data extraction synchronized
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
# 2. APPLICATION LAYOUT UI
# ----------------------------------------------------
st.set_page_config(page_title="Live Profile Finder Bot", page_icon="🔍")
st.title("🔍 Live Profile Recruiter Matcher")
st.write("This bot scans our live GitHub database (`profiles.csv`) to match candidate skills.")

# ----------------------------------------------------
# 3. CONVERSATION STATE HISTORY INTERFACE
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Good morning! Enter a skill to search our database."}
    ]

# Display history with explicit HTML parsing parameter
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# React to User Query Search Input
if user_input := st.chat_input("Enter skill (e.g., DBA)..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    search_skill = user_input.strip().lower()
    matched_profiles = profiles_df[profiles_df["Skills"].str.lower().str.contains(search_skill, na=False)]
    
    if not matched_profiles.empty:
        response_text = f"### Found **{len(matched_profiles)}** live cloud match(es) for **'{user_input}'**:\n\n"
        
        for idx, row in matched_profiles.iterrows():
            original_name = str(row['Name']).strip()
            # Explicitly pulls the case-sensitive filename directly from the CSV column
            target_file = str(row['Filename']).strip()
            
            # Formulates the absolute download link path directly with no variable generation gaps
            profile_url = f"https://githubusercontent.com{target_file}"
            
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:5px;'>👤 **Name:** {original_name}</span>"
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:5px;'>📧 **Email:** <a href='mailto:{row['Email']}'>{row['Email']}</a></span>"
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:5px;'>🛠️ **Matched Skills:** *{row['Skills']}*</span>"
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:15px;'>📄 **Profile Document:** <a href='{profile_url}' target='_blank' style='text-decoration:none; color:#1f77b4; font-weight:bold;'>📥 Download Profile File</a></span>"
            response_text += "<hr style='margin: 10px 0; border: 0; border-top: 1px solid #eee;'>\n"
    else:
        response_text = f"No live profile matches found for **'{user_input}'**."

    with st.chat_message("assistant"):
        st.markdown(response_text, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
