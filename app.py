import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found.")
    st.info("Please check your .env file.")
    st.stop()

# Create Groq client
client = Groq(api_key=groq_api_key)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Notes Generator",
    page_icon="📚",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    /* Generate button */
    div.stButton > button {
        width: 180px;
        height: 42px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 600;
    }

    /* Main title */
    h1 {
        font-size: 42px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "selected" not in st.session_state:
    st.session_state.selected = None


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📚 Prompt History")

if st.session_state.history:

    # Newest first
    for i, item in enumerate(
        reversed(st.session_state.history)
    ):

        if st.sidebar.button(
            item["topic"],
            key=f"history_{i}"
        ):
            st.session_state.selected = item

else:

    st.sidebar.info("No history yet")


# Clear history

if st.sidebar.button("🗑️ Clear History"):

    st.session_state.history = []
    st.session_state.selected = None

    st.rerun()


# ==========================================
# MAIN PAGE
# ==========================================

st.title("📚 AI Notes Generator")

st.write(
    "Enter a topic and generate structured notes using AI."
)

st.divider()


# ==========================================
# TOPIC INPUT
# ==========================================

topic = st.text_input(
    "Enter Topic",
    placeholder="Example: Data Structures"
)


# ==========================================
# GENERATE BUTTON
# ==========================================

if st.button("✨ Generate Notes"):

    if not topic.strip():

        st.warning("⚠️ Please enter a topic first.")

    else:

        with st.spinner("🤖 Generating notes..."):

            try:

                # ======================================
                # FIND AVAILABLE GROQ MODELS
                # ======================================

                available_models = client.models.list()

                model_ids = [
                    model.id
                    for model in available_models.data
                ]


                # ======================================
                # PREFERRED MODELS
                # ======================================

                preferred_models = [

                    "openai/gpt-oss-120b",

                    "openai/gpt-oss-20b",

                    "llama-3.1-8b-instant",

                    "llama-3.3-70b-versatile",

                    "qwen/qwen3.6-27b",

                ]


                # Find first model available
                selected_model = None

                for model in preferred_models:

                    if model in model_ids:

                        selected_model = model
                        break


                # If none of the preferred models
                # are available

                if selected_model is None:

                    st.error(
                        "❌ No supported chat model is available "
                        "for your Groq API key."
                    )

                    st.write(
                        "Models available to your key:"
                    )

                    st.code(
                        "\n".join(model_ids)
                    )

                    st.stop()


                # ======================================
                # GENERATE NOTES
                # ======================================

                response = client.chat.completions.create(

                    model=selected_model,

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "You are an expert educational "
                                "assistant. Create clear, "
                                "accurate and well-structured "
                                "study notes for students."
                            )
                        },

                        {
                            "role": "user",
                            "content": (
                                f"Generate detailed and "
                                f"easy-to-understand study "
                                f"notes on: {topic}\n\n"

                                "Use the following structure:\n\n"

                                "## 1. Introduction\n"
                                "Explain the topic briefly.\n\n"

                                "## 2. Important Concepts\n"
                                "Explain the main concepts "
                                "clearly.\n\n"

                                "## 3. Key Points\n"
                                "Give important points "
                                "using bullet points.\n\n"

                                "## 4. Examples\n"
                                "Give simple practical "
                                "examples.\n\n"

                                "## 5. Advantages and "
                                "Disadvantages\n"
                                "Include them if applicable.\n\n"

                                "## 6. Conclusion\n"
                                "Give a short summary.\n\n"

                                "Use simple language suitable "
                                "for college students."
                            )
                        }

                    ],

                    temperature=0.7,

                    max_tokens=2000
                )


                # ======================================
                # GET NOTES
                # ======================================

                notes = response.choices[0].message.content


                # ======================================
                # SAVE TO HISTORY
                # ======================================

                new_item = {

                    "topic": topic,

                    "notes": notes

                }

                st.session_state.history.append(
                    new_item
                )

                st.session_state.selected = new_item


                # ======================================
                # SUCCESS MESSAGE
                # ======================================

                st.success(
                    f"✅ Notes generated successfully!"
                )


            except Exception as e:

                st.error(
                    "❌ Something went wrong while "
                    "generating the notes."
                )

                st.code(str(e))


# ==========================================
# DISPLAY NOTES
# ==========================================

if st.session_state.selected:

    selected = st.session_state.selected

    st.divider()

    st.subheader(
        f"📝 Notes on: {selected['topic']}"
    )

    st.markdown(
        selected["notes"]
    )

else:

    st.info(
        "Enter a topic above and click "
        "**✨ Generate Notes** to create your notes."
    )
