import dotenv
import streamlit as st

from flip_cards import app_utils

dotenv.load_dotenv()

st.set_page_config(
    page_title="Vogeltjes",
    page_icon="🦉",
    initial_sidebar_state=st.session_state.get("sidebar_state", "expanded"),
)

app_utils.you_shall_not_password()

data = app_utils.load_data()
question_objects, correct_answers = app_utils.prepare_question_answer_pairs(data)

if not st.session_state.get("initialized"):
    app_utils.initialize_session_state(question_objects, correct_answers)

app_utils.config_form()

if not st.session_state.get("overhoring_started"):
    app_utils.welcome_message()

if st.session_state["initialize_queue"]:
    app_utils.initialize_queue()
    app_utils.define_answer_suggestions()
    app_utils.reset_session_state()
    app_utils.clear_answer_field()

app_utils.show_progress()

if not st.session_state["queue"]:
    app_utils.stop_overhoring()

app_utils.get_current_question_answer_pair()

if st.session_state["clear_answer_field"]:
    app_utils.clear_answer_field()

app_utils.present_question()

app_utils.answer_form("Antwoord:")

if st.session_state["answer_submitted"]:
    # app_utils.show_feedback_message()
    app_utils.present_question_information()

# Keep at the end of the script
if st.session_state["focus_on_input"]:
    app_utils.focus_on_input_in_form()
elif st.session_state["focus_on_next_button"]:
    app_utils.focus_on_next_button_in_form()
