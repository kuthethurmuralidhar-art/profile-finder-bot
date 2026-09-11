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
# 2. APPLICATION LAYOUT UI
# ----------------------------------------------------
st.set_page_config(page_title="Live Profile Finder Bot", page_icon="🔍")
st.title("🔍 Live Profile Recruiter Matcher")
st.write("This bot matches candidate profiles and lets you download resumes directly from the server storage.")

# ----------------------------------------------------
# 3. CONVERSATION STATE INTERFACE
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Good morning! Enter a skill (e.g., DBA/OCI/AWS/Oracle/Python) to search candidate profiles."}
    ]

# Display history loops
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
        # 1. First print the text message header
        st.markdown(f"### Found **{len(matched_profiles)}** live cloud match(es) for **'{user_input}'**:")
        
        # 2. Loop through profiles to print information and render a native download button below each profile
        for idx, row in matched_profiles.iterrows():
            original_name = str(row['Name']).strip()
            target_file = str(row['Filename']).strip()
            
            # Print profile data using clean HTML containers
            profile_html = (
                f"<span style='font-size:14px; display:block; margin-top:10px; margin-bottom:5px;'>👤 **Name:** {original_name}</span>"
                f"<span style='font-size:14px; display:block; margin-bottom:5px;'>📧 **Email:** <a href='mailto:{row['Email']}'>{row['Email']}</a></span>"
                f"<span style='font-size:14px; display:block; margin-bottom:5px;'>🛠️ **Matched Skills:** *{row['Skills']}*</span>"
            )
            st.markdown(profile_html, unsafe_allow_html=True)
            
            # Use Streamlit's native button layout to fetch the binary asset directly from server space
            try:
                with open(target_file, "rb") as file_asset:
                    bytes_data = file_asset.read()
                
                st.download_button(
                    label=f"📥 Download {original_name}'s Profile",
                    data=bytes_data,
                    file_name=target_file,
                    mime="application/pdf",
                    key=f"dl_btn_{idx}_{target_file}" # Avoids duplicate widget key conflicts
                )
            except FileNotFoundError:
                st.warning(f"📄 File '{target_file}' is missing from the repository directory.")
                
            st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
            
        # Append confirmation log string to message logs state history tracking list
        st.session_state.messages.append({"role": "assistant", "content": f"Displayed profile matching loops for query: '{user_input}'"})
    else:
        no_match_text = f"No live profile matches found for **'{user_input}'**."
        with st.chat_message("assistant"):
            st.markdown(no_match_text)
        st.session_state.messages.append({"role": "assistant", "content": no_match_text})
