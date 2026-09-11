import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. DYNAMIC DATABASE SETUP (Reading from GitHub)
# ----------------------------------------------------
#@st.cache_data(ttl=600)  # Caches the data for 10 minutes so it stays fast
#def load_profiles_from_github():
    # Replace 'YOUR_GITHUB_USERNAME' with kuthethurmuralidhar-art
    # Replace 'profile-finder-bot' if your repo name is different
#   username = "kuthethurmuralidhar-art"
#   repo_name = "profile-finder-bot"
    
#   url = f"https://githubusercontent.com{username}/{repo_name}/main/profiles.csv"
@st.cache_data(ttl=600)  # Caches the data for 10 minutes so it stays fast
def load_profiles_from_github():
    try:
        # Read the file directly from the local directory instead of a web URL link
        df = pd.read_csv("profiles.csv")
        return df
    except Exception as e:
        # Fallback tracking display
        st.error(f"Could not read local data asset. Error: {e}")
        fallback_data = {
            "Name": ["System Error Tracker"],
            "Email": ["admin@example.com"],
            "Skills": ["Error"]
        }
        return pd.DataFrame(fallback_data)

    try:
        # Streamlit reads the CSV file directly from your GitHub cloud link
        df = pd.read_csv(url)
        return df
    except Exception as e:
        # Fallback in case the GitHub file isn't uploaded yet or link is wrong
        st.error(f"Could not connect to GitHub database. Showing offline sample. Error: {e}")
        fallback_data = {
            "Name": ["System Error Tracker"],
            "Email": ["admin@example.com"],
            "Skills": ["Error"]
        }
        return pd.DataFrame(fallback_data)

profiles_df = load_profiles_from_github()

# ----------------------------------------------------
# 2. UI CONFIGURATION
# ----------------------------------------------------
st.set_page_config(page_title="Live Profile Finder Bot", page_icon="🔍")
st.title("🔍 Profile  Matcher")
#st.write("This bot scans our live GitHub database (`profiles.csv`) to match candidate skills.")

# ----------------------------------------------------
# 3. CHATBOT INTERFACE LOGIC
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Good morning! Enter a skill to search our cloud-hosted GitHub database."
        }
    ]

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to User Query
if user_input := st.chat_input("Enter skill (e.g., Oracle DBA)..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    search_skill = user_input.strip().lower()
    
    # Filter using pandas string matching
    matched_profiles = profiles_df[profiles_df["Skills"].str.lower().str.contains(search_skill, na=False)]
    
    if not matched_profiles.empty:
        response_text = f"### Found **{len(matched_profiles)}** live cloud match(es) for **'{user_input}'**:\n\n"
        for idx, row in matched_profiles.iterrows():
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:5px;'>👤 **Name:** {row['Name']}</span>"
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:5px;'>📧 **Email:** <a href='mailto:{row['Email']}'>{row['Email']}</a></span>"
            response_text += f"<span style='font-size:14px; display:block; margin-bottom:15px;'>🛠️ **Matched Skills:** *{row['Skills']}*</span>"
            response_text += "<hr style='margin: 10px 0; border: 0; border-top: 1px solid #eee;'>\n"
    else:
    else:
        response_text = f"No live profile matches found for **'{user_input}'**.\n\nTry searching for alternative skills listed in your repository."

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
