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


# SESSION STATE
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# SIDEBAR

with st.sidebar:
    st.header("Upload Documents 📂")

    uploaded_files = st.file_uploader(
        "Select PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Upload Documents"):
        if not uploaded_files:
            st.warning("Please select at least one PDF.")
        else:
            progress_bar = st.progress(0)

            for index, uploaded_file in enumerate(uploaded_files):
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
                    data = response.json()

                    st.success(
                        f"Uploaded: {data['filename']}"
                    )

                    if uploaded_file.name not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(
                            uploaded_file.name
                        )

                else:
                    st.error(
                        f"Failed to upload {uploaded_file.name}"
                    )

                progress_bar.progress(
                    (index + 1) / len(uploaded_files)
                )

# SHOW UPLOADED FILES
if st.session_state.uploaded_files:
    st.subheader("Uploaded Documents")

    for file_name in st.session_state.uploaded_files:
        st.write(f"📄 {file_name}")

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
