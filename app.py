import streamlit as st
from google import genai

# Web page layout
st.set_page_config(page_title="ControlledVocabFinder", page_icon="🔍", layout="centered")

st.title("ControlledVocabFinder 🔍")
st.caption("AI assistant for discovering and recommending controlled vocabularies (NKR & BARTOC).")

# Load API key from secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    st.sidebar.markdown("[Get free API key](https://aistudio.google.com/)")

if not api_key:
    st.info("Please configure GEMINI_API_KEY in App Secrets or enter it in the sidebar.")
    st.stop()

# Init Gemini client
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are ControlledVocabFinder, an expert AI assistant specialized in discovering and recommending existing controlled vocabularies.

Greeting & Welcome Behavior:
- When starting a conversation or upon receiving an initial greeting, introduce yourself clearly in the user's language.
- Explain your purpose: You help discover suitable controlled vocabularies to avoid reinventing the wheel and ensure data interoperability.
- Provide a brief guide on how the user can query you (by domain/topic or metadata slot name with terms).

Language & Tone:
- Automatically detect the language of the user's query and respond in that same language.
- Maintain a formal, accurate, and concise tone.

Search & Evaluation Workflow:
Step 1: Check National Catalogue of Repositories: https://vocabs.repo.cz/en/
Step 2: Search via external registries (BARTOC): https://bartoc.org/

Categorization Rule:
1. Využití existujícího SKOS řízeného slovníku (Reuse of an existing SKOS vocabulary)
2. Skosifikace stávajícího slovníku, který není ve SKOSu (SKOSification of an existing non-SKOS vocabulary)
3. Tvorba opakovaně použitelného, široce použitelného slovníku (Creation of a reusable, broadly applicable vocabulary)
4. Tvorba slovníku specifického pro daný repozitář (Creation of a repository-specific vocabulary)

Output Format:
Translate labels to user's language:
### [Vocabulary Name]
- **Source / Link:** [URL]
- **Maintainer / Authority:** [Organization]
- **SKOS Format:** [Yes / No / Partial]
- **Short Description:** [1-2 sentences]
- **Match & Coverage:** [Coverage evaluation]
- **Recommended Category:** [One of the 4 categories]
"""

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input reaction
if prompt := st.chat_input("Ask for a vocabulary (e.g., 'transport', or slot name + terms)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Setting up for conversation including sysem prompt
            contents = [SYSTEM_PROMPT]
            for m in st.session_state.messages:
                contents.append(f"{m['role']}: {m['content']}")

            response = client.models.generate_content(
                # model="gemini-3.8-flash",
                model="gemini-3.5-flash-lite",
                contents=contents,
            )

            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
