import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Personal Knowledge Assistant",
    layout="wide"
)

# HEADER
st.title("Personal Knowledge Assistant")
st.markdown(
    """
Upload one or more PDF documents and ask questions about them.
"""
)

# SIDEBAR
with st.sidebar:
    st.header("📤 Upload Documents")

    uploaded_files = st.file_uploader(
        "Select PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button(
        "Upload Documents",
        use_container_width=True
    ):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_BASE_URL}/upload",
                    files=files
                )

                if response.status_code == 200:
                    st.success(
                        f"Uploaded {uploaded_file.name}"
                    )
                else:
                    st.error(
                        f"Failed to upload {uploaded_file.name}"
                    )

            st.rerun()
        else:
            st.warning(
                "Please select a PDF."
            )

    st.divider()

    st.header("📚 Knowledge Base")

    try:
        response = requests.get(
            f"{API_BASE_URL}/sources"
        )

        sources = response.json().get(
            "sources",
            []
        )

        if sources:
            st.caption(
                f"{len(sources)} document(s) indexed"
            )

            for source in sources:
                st.write(
                    f"📄 {source}"
                )
        else:
            st.info(
                "No documents uploaded."
            )
    except Exception:
        st.error(
            "Unable to load knowledge base."
        )

    st.divider()

    if st.button(
        "🗑️ Clear Knowledge Base",
        use_container_width=True
    ):
        response = requests.post(
            f"{API_BASE_URL}/clear"
        )

        if response.status_code == 200:
            st.success(
                "Knowledge base cleared."
            )

            st.rerun()

        else:
            st.error(
                "Failed to clear knowledge base."
            )

# QUESTION SECTION
st.divider()

question = st.text_input(
    "Ask a question",
    placeholder="Example: What certifications do I have?"
)

# ASK QUESTION
ask_button = st.button("Ask")

if ask_button:
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Searching documents and generating answer..."):
            response = requests.get(
                f"{API_BASE_URL}/ask",
                params={
                    "question": question
                }
            )

            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer")

                st.success(
                    data.get(
                        "answer",
                        "No answer returned."
                    )
                )

                sources = data.get("sources", [])

                if sources:
                    st.subheader("Sources")
                    for source in sources:
                        st.write(f"📄 {source}")

            else:
                st.error(
                    f"Request failed ({response.status_code})"
                )
