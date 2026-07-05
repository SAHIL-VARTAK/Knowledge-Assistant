import os

import requests
import streamlit as st

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(page_title="Personal Knowledge Assistant", layout="wide")

st.markdown(
    """
<style>

/* User message */
div[data-testid="stChatMessage"]:has(
    div[data-testid="stChatMessageAvatarUser"]
){
    margin-left: 20%;
    width: 80%;
}

/* Assistant message */
div[data-testid="stChatMessage"]:has(
    div[data-testid="stChatMessageAvatarAssistant"]
){
    margin-right: 20%;
    width: 80%;
}

</style>
""",
    unsafe_allow_html=True,
)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

# HEADER
st.title("📚 Personal Knowledge Assistant")
st.markdown(
    """
Upload one or more documents and ask questions about them.
"""
)

# SIDEBAR
with st.sidebar:
    # Model Selection
    st.header("Model Selector")

    response = requests.get(f"{API_BASE_URL}/providers")

    providers = response.json()

    selected_provider = st.selectbox("Provider", list(providers.keys()))

    selected_model = st.selectbox("Model", providers[selected_provider])

    api_key = st.text_input("API Key", type="password")

    if st.button("Use Model", use_container_width=True):
        requests.post(
            f"{API_BASE_URL}/model-config",
            json={"provider": selected_provider, "model": selected_model, "api_key": api_key},
        )

        st.success("Model configuration updated.")

    st.divider()

    st.header("📤 Upload Documents")

    uploaded_files = st.file_uploader(
        "Select Documents",
        type=["pdf", "docx", "txt", "md", "py", "java", "js", "ts", "html", "css", "sql", "cpp", "c", "cs"],
        accept_multiple_files=True,
    )

    if st.button("Upload Documents", use_container_width=True):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

                response = requests.post(f"{API_BASE_URL}/upload", files=files)

                if response.status_code == 200:
                    st.success(f"Uploaded {uploaded_file.name}")
                else:
                    st.error(f"Failed to upload {uploaded_file.name}")

            st.rerun()
        else:
            st.warning("Please select a valid file.")

    st.divider()

    st.header("📚 Knowledge Base")

    try:
        response = requests.get(f"{API_BASE_URL}/sources")

        sources = response.json().get("sources", [])

        if sources:
            st.caption(f"{len(sources)} document(s) indexed")

            for source in sources:
                st.write(f"📄 {source}")
        else:
            st.info("No documents uploaded.")
    except Exception:
        st.error("Unable to load knowledge base.")

    st.divider()

    if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
        response = requests.post(f"{API_BASE_URL}/clear")

        if response.status_code == 200:
            st.success("Knowledge base cleared.")

            st.session_state.messages = []
            st.rerun()

        else:
            st.error("Failed to clear knowledge base.")

    if st.button("🧹 Clear Chat", use_container_width=True):
        requests.post(f"{API_BASE_URL}/clear-chat")

        st.session_state.messages = []
        st.rerun()

# CHAT AREA
st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            st.caption("Sources")

            for source in message["sources"]:
                st.caption(f"📄 {source}")

# CHAT INPUT
question = st.chat_input("Ask a question about your documents...")

if question:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                response = requests.get(f"{API_BASE_URL}/ask", params={"question": question})

                if response.status_code == 200:
                    data = response.json()

                    answer = data.get("answer", "No answer returned.")

                    sources = data.get("sources", [])

                    st.markdown(answer.replace("\n", "<br>"), unsafe_allow_html=True)

                    if sources:
                        st.caption("Sources")

                        for source in sources:
                            st.caption(f"📄 {source}")

                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                else:
                    st.error(f"Request failed ({response.status_code})")
            except Exception as e:
                st.error(f"Error: {str(e)}")
