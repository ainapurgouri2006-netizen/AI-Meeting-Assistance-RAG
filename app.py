import streamlit as st
import tempfile
import os

from main import run_pipeline
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #777;
    margin-bottom: 30px;
}

.card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

.chat-user {
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
}

.chat-assistant {
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 AI Meeting Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Transform meetings and videos into summaries, decisions, action items and an interactive AI chat.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Input")

    input_type = st.radio(
        "Choose input type",
        ["YouTube URL", "Local File"]
    )

    source = None

    if input_type == "YouTube URL":

        source = st.text_input(
            "Enter YouTube URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )

    else:

        uploaded_file = st.file_uploader(
            "Upload audio/video",
            type=[
                "mp3",
                "wav",
                "m4a",
                "mp4",
                "mov",
                "avi",
                "mkv"
            ]
        )

        if uploaded_file:

            suffix = os.path.splitext(uploaded_file.name)[1]

            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            )

            temp_file.write(uploaded_file.read())
            temp_file.close()

            source = temp_file.name

    st.divider()

    process_button = st.button(
        "🚀 Process Meeting",
        use_container_width=True
    )


# --------------------------------------------------
# Process pipeline
# --------------------------------------------------

if process_button:

    if not source:

        st.warning("Please provide a YouTube URL or upload a file.")

    else:

        with st.status(
            "Processing your meeting...",
            expanded=True
        ) as status:

            st.write("🎵 Downloading / processing audio...")
            
            try:

                result = run_pipeline(source)

                st.write("🧠 Generating meeting insights...")

                st.session_state.result = result
                st.session_state.rag_chain = result["rag_chain"]
                st.session_state.chat_history = []

                status.update(
                    label="✅ Meeting processed successfully!",
                    state="complete"
                )

            except Exception as e:

                status.update(
                    label="❌ Processing failed",
                    state="error"
                )

                st.error(f"Error: {e}")


# --------------------------------------------------
# Display result
# --------------------------------------------------

result = st.session_state.result


if result:

    st.success("Meeting analysis completed successfully!")

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    st.header("📌 Meeting Title")

    st.subheader(result["title"])

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    st.header("📝 Meeting Summary")

    st.markdown(result["summary"])

    # ----------------------------------------------
    # Insights
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Action Items")

        st.markdown(result["action_items"])

    with col2:

        st.subheader("🔑 Key Decisions")

        st.markdown(result["key_decisions"])

    # ----------------------------------------------
    # Questions
    # ----------------------------------------------

    st.subheader("❓ Open Questions")

    st.markdown(result["open_questions"])

    # ----------------------------------------------
    # Transcript
    # ----------------------------------------------

    with st.expander("📄 View Full Transcript"):

        st.text_area(
            "Transcript",
            result["transcript"],
            height=400
        )

    # ----------------------------------------------
    # RAG Chat
    # ----------------------------------------------

    st.divider()

    st.header("🤖 Chat with your Meeting")

    st.caption(
        "Ask questions about the uploaded meeting or YouTube video."
    )

    # Display previous messages

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.write(message["content"])

        else:

            with st.chat_message("assistant"):
                st.write(message["content"])

    # Chat input

    question = st.chat_input(
        "Ask something about the meeting..."
    )

    if question:

        # Show user question

        with st.chat_message("user"):
            st.write(question)

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Get answer

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    answer = ask_question(
                        st.session_state.rag_chain,
                        question
                    )

                    st.write(answer)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                except Exception as e:

                    st.error(f"Error: {e}")


else:

    # Initial screen

    st.info(
        "👈 Add a YouTube URL or upload a meeting file "
        "from the sidebar to get started."
    )