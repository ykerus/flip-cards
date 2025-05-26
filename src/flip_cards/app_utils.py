import os
import random
import time
from typing import Dict, List, Tuple, Union

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from flip_cards.config import Config

QuestionObjectType = Union[Dict, pd.Series]


def you_shall_not_password():
    if (
        os.getenv("APP_PASSWORD")
        and not st.session_state.get("password_correct")
        and not os.getenv("ENV") == "local"
    ):
        with st.form("password_form"):
            entered_password = st.text_input("🦤 Wachtwoord:", type="password")
            check_password = st.form_submit_button("Check")
        if check_password:
            if entered_password == os.environ["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.success("✅ Welkom!")
                time.sleep(2)
                st.rerun()
            else:
                time.sleep(3)
                st.error("✋ You shall not pass!")
                time.sleep(2)
        st.stop()


@st.cache_data
def load_data() -> Union[Dict, pd.DataFrame]:
    # To be customized per use case
    return {}


@st.cache_data
def prepare_question_answer_pairs(*args, **kwargs) -> Tuple[List[QuestionObjectType], List[str]]:
    # To be customized per use case
    question_objects: List[QuestionObjectType] = [
        {
            "question": "Welke vogel zingt als de Merel?",
            "info": "Tuututuu tudu tuu",
            "tags": ["veelvoorkomend"],
        },
        {
            "question": "Welke vogel zingt als de Roodborst?",
            "info": "Tiitidi tudiiti ti",
            "tags": ["klein"],
        },
        {
            "question": "Welke vogel zingt als de Koolmees?",
            "info": "Tii duu tii duu",
            "tags": ["klein", "mees", "veelvoorkomend"],
        },
        {
            "question": "Welke vogel zingt als de Pimpelmees?",
            "info": "Ti ti ti dududududu",
            "tags": ["klein", "mees"],
        },
        {
            "question": "Welke vogel zingt als de Houtduif?",
            "info": "Tu duuu du tudu",
            "tags": ["duif", "veelvoorkomend"],
        },
        {
            "question": "Welke vogel zingt als de Tortelduif?",
            "info": "Tu duuu du",
            "tags": ["duif"],
        },
        {
            "question": "Welke vogel zingt als de Scholekster?",
            "info": "Tepiet tepiet",
            "tags": ["steltloper", "veelvoorkomend"],
        },
        {
            "question": "Welke vogel zingt als de Grutto?",
            "info": "Grutto grutto",
            "tags": ["steltloper"],
        },
        {
            "question": "Welke vogel zingt als de Ijsvogel?",
            "info": "Twiit twiit",
            "tags": ["blauw"],
        },
        {
            "question": "Welke vogel zingt als de Tapuit?",
            "info": "Tju tju tju",
            "tags": [],
        },
    ]
    correct_answers: List[str] = [
        "Merel",
        "Roodborst",
        "Koolmees",
        "Pimpelmees",
        "Houtduif",
        "Tortelduif",
        "Scholekster",
        "Grutto",
        "Ijsvogel",
        "Tapuit",
    ]

    assert len(question_objects) == len(correct_answers)
    return question_objects, correct_answers


def welcome_message():
    st.subheader("👈 Start de overhoring")
    # st.snow()
    st.stop()


def initialize_session_state(
    question_objects: List[QuestionObjectType], correct_answers: List[str]
):
    st.session_state["counter"] = 0  # Used by focus_on_text_input()
    st.session_state["question_objects"] = question_objects
    st.session_state["correct_answers"] = correct_answers
    st.session_state["all_tags"] = {
        tag for tags in [q["tags"] for q in question_objects] for tag in tags
    }
    st.session_state["total_questions"] = len(question_objects)
    st.session_state["answer_submitted"] = False
    st.session_state["clear_answer_field"] = False
    st.session_state["next_question"] = False
    st.session_state["overhoring_started"] = False
    st.session_state["_config_default"] = Config().dict()  # Before starting overhoring
    st.session_state["_config"] = Config().dict()  # Before starting overhoring
    st.session_state["config"] = Config().dict()  # Actual config used in overhoring
    st.session_state["initialized"] = True


def _toggle_input_focus(state: str = "off"):
    if state == "off":
        st.session_state["focus_on_input"] = False
        st.session_state["focus_on_next_button"] = False
    elif state == "on" or state == "input_field":
        st.session_state["focus_on_input"] = True
        st.session_state["focus_on_next_button"] = False
    elif state == "next_button":
        st.session_state["focus_on_input"] = False
        st.session_state["focus_on_next_button"] = True
    else:
        raise NotImplementedError


def _set_config(config_key: str, widget_key: str):
    st.session_state["_config"][config_key] = st.session_state[widget_key]


def _set_config_default(config_key: str):
    try:
        st.session_state["_config_default"][config_key] = st.session_state["_config"][
            config_key
        ].copy()
    except AttributeError:
        st.session_state["_config_default"][config_key] = st.session_state["_config"][config_key]


def _sync_configs_and_defaults(key: str):
    set_config_default_keys = [
        "selected_questions",
        "included_tags",
        "excluded_tags",
        "n_random_questions",
        "question_start_index",
        "question_end_index",
    ]
    set_config_default_keys.remove(key)
    for k in set_config_default_keys:
        _set_config_default(k)

    _set_config(key, key + "_widget")


def _checkbox_answer_suggestions():
    def _on_change():
        _set_config("answer_suggestions", "answer_suggestions_widget")
        _toggle_input_focus("off")

    st.checkbox(
        "Antwoord suggesties",
        value=st.session_state["_config_default"]["answer_suggestions"],
        key="answer_suggestions_widget",
        on_change=_on_change,
    )


def _checkbox_infinite_practice():
    def _on_change():
        _set_config("infinite_practice", "infinite_practice_widget")
        _toggle_input_focus("off")

    st.checkbox(
        "Eindeloos oefenen",
        value=st.session_state["_config_default"]["infinite_practice"],
        key="infinite_practice_widget",
        on_change=_on_change,
    )


def _multiselect_selected_questions():
    def _on_change():
        _sync_configs_and_defaults("selected_questions")
        _toggle_input_focus("off")

    possible_indices = _get_possible_indices_from_selected_tags("_config")
    possible_questions = [st.session_state["correct_answers"][i] for i in possible_indices]
    st.multiselect(
        "Meegenomen vragen (mag leeg zijn)",
        possible_questions,
        default=st.session_state["_config_default"]["selected_questions"],
        key="selected_questions_widget",
        on_change=_on_change,
    )


def _multiselect_included_tags():
    def _on_change():
        _sync_configs_and_defaults("included_tags")
        _toggle_input_focus("off")

    possible_indices = _get_possible_indices_from_excluded_tags("_config")
    possible_question_objects = [st.session_state["question_objects"][i] for i in possible_indices]
    possible_tags = {tag for tags in [q["tags"] for q in possible_question_objects] for tag in tags}
    st.multiselect(
        "Meegenomen tags (mag leeg zijn)",
        list(possible_tags),
        default=st.session_state["_config_default"]["included_tags"],
        key="included_tags_widget",
        on_change=_on_change,
    )


def _multiselect_excluded_tags():
    def _on_change():
        _sync_configs_and_defaults("excluded_tags")
        _toggle_input_focus("off")

    if st.session_state["_config"]["selected_questions"]:
        return

    possible_tags = [
        tag
        for tag in st.session_state["all_tags"]
        if tag not in st.session_state["_config"]["included_tags"]
    ]

    st.multiselect(
        "Uitgesloten tags (mag leeg zijn)",
        possible_tags,
        default=st.session_state["_config_default"]["excluded_tags"],
        key="excluded_tags_widget",
        on_change=_on_change,
    )


def _checkbox_random_selection():
    def _on_change():
        _set_config("random_selection", "random_selection_widget")
        _toggle_input_focus("off")

    st.checkbox(
        "Willekeurige selectie",
        value=st.session_state["_config_default"]["random_selection"],
        key="random_selection_widget",
        on_change=_on_change,
    )


def _select_slider_n_random_questions():
    def _on_change():
        _set_config("n_random_questions", "n_random_questions_widget")
        _toggle_input_focus("off")

    possible_question_indices = _get_possible_question_indices("_config")
    st.select_slider(
        "Aantal vragen",
        range(1, len(possible_question_indices) + 1),
        key="n_random_questions_widget",
        value=min(
            len(possible_question_indices),
            st.session_state["_config_default"]["n_random_questions"],
        ),
        on_change=_on_change,
    )
    # This is done extra for the case that someone changes the filters. In that
    # case the values of the slider change, but it does not trigger a "change"
    _set_config("n_random_questions", "n_random_questions_widget")


def _select_slider_from_to_questions():
    def _set_config_from_to():
        start_index = st.session_state["questions_from_to_widget"][0]
        end_index = st.session_state["questions_from_to_widget"][1] + 1
        st.session_state["_config"]["question_start_index"] = start_index
        st.session_state["_config"]["question_end_index"] = end_index

    def _on_change():
        _set_config_from_to()
        _toggle_input_focus("off")

    possible_question_indices = _get_possible_question_indices("_config")

    def _format_func(i):
        indx = possible_question_indices[i]
        return f"{st.session_state['correct_answers'][indx]}"

    st.select_slider(
        "Selectie van-tot",
        range(len(possible_question_indices)),
        value=(
            min(
                st.session_state["_config_default"]["question_start_index"],
                len(possible_question_indices) - 2,
            ),
            min(
                st.session_state["_config_default"]["question_end_index"],
                len(possible_question_indices) - 1,
            ),
        ),
        format_func=lambda x: _format_func(x),
        on_change=_on_change,
        key="questions_from_to_widget",
    )
    # This is done extra for the case that someone changes the filters. In that
    # case the values of the slider change, but it does not trigger a "change"
    _set_config_from_to()


def config_form():
    # To be customized per use case

    with st.sidebar.container(border=True):
        st.subheader("**Configuratie**")

        st.write("**Algemene instellingen**")

        _checkbox_answer_suggestions()
        _checkbox_infinite_practice()

        _multiselect_selected_questions()

        if not st.session_state["_config"]["selected_questions"]:
            _multiselect_included_tags()
            _multiselect_excluded_tags()

        n_preselected_questions = len(_get_possible_question_indices("_config"))
        if n_preselected_questions == 0:
            st.write(
                "Oeps, er zijn niet genoeg vragen voor deze filters! Probeer opnieuw met andere filters."
            )
            st.stop()

        elif n_preselected_questions == 1:
            n_questions_selected = 1

        elif n_preselected_questions > 1:
            st.container(border=True).write(
                f"🐣 &nbsp; {n_preselected_questions} van {st.session_state['total_questions']} "
                + "vragen in voorselectie"
            )

            _checkbox_random_selection()

            if st.session_state["_config"]["random_selection"]:
                _select_slider_n_random_questions()
            else:
                _select_slider_from_to_questions()

            n_questions_selected = _get_n_questions_selected("_config")

        st.container(border=True).write(
            f"🐥 &nbsp; {n_questions_selected} van {st.session_state['total_questions']} "
            + "vragen in eindselectie"
        )

        def _on_click_start_overhoring():
            st.session_state["overhoring_started"] = True
            st.session_state["initialize_queue"] = True
            st.session_state["config"] = st.session_state["_config"].copy()
            _toggle_input_focus("on")

            if n_questions_selected == 1:
                st.session_state["config"]["random_selection"] = True
                st.session_state["config"]["n_random_questions"] = 1

        st.button("Start overhoring", on_click=_on_click_start_overhoring)


def _get_n_questions_selected(config: str = "config") -> int:
    return (
        st.session_state[config]["n_random_questions"]
        if st.session_state[config]["random_selection"]
        else st.session_state[config]["question_end_index"]
        - st.session_state[config]["question_start_index"]
    )


def reset_session_state():
    st.session_state["n_correct"] = 0
    st.session_state["next_question"] = False
    st.session_state["answer_checked"] = False
    st.session_state["answer_submitted"] = False
    st.session_state["n_questions"] = _get_n_questions_selected()
    infinite_practice = st.session_state["config"]["infinite_practice"]
    st.session_state["question_indices_seen"] = [] if infinite_practice else set()


def _get_possible_indices_from_selected_questions(config: str = "config"):
    possible_from_selected_questions = []
    for i, question_object in enumerate(st.session_state["question_objects"]):
        correct_answer = st.session_state["correct_answers"][i]

        if st.session_state[config]["selected_questions"]:
            if correct_answer in st.session_state[config]["selected_questions"]:
                possible_from_selected_questions.append(i)
        else:
            possible_from_selected_questions.append(i)
    return possible_from_selected_questions


def _get_possible_indices_from_included_tags(config: str = "config") -> List[int]:
    possible_from_included_tags = []
    for i, question_object in enumerate(st.session_state["question_objects"]):
        if st.session_state[config]["included_tags"]:
            for tag in question_object["tags"]:
                if tag in st.session_state[config]["included_tags"]:
                    possible_from_included_tags.append(i)
        else:
            possible_from_included_tags.append(i)
    return possible_from_included_tags


def _get_possible_indices_from_excluded_tags(config: str = "config") -> List[int]:
    possible_from_excluded_tags = []
    for i, question_object in enumerate(st.session_state["question_objects"]):
        if st.session_state[config]["excluded_tags"]:
            possible_from_excluded_tags.append(i)
            for tag in question_object["tags"]:
                if tag in st.session_state[config]["excluded_tags"]:
                    possible_from_excluded_tags.pop()
                    break
        else:
            possible_from_excluded_tags.append(i)
    return possible_from_excluded_tags


def _get_possible_indices_from_selected_tags(config: str = "config"):
    possible_from_included_tags = _get_possible_indices_from_included_tags(config)
    possible_from_excluded_tags = _get_possible_indices_from_excluded_tags(config)
    possible_indices = set(possible_from_included_tags).intersection(possible_from_excluded_tags)

    return sorted(list(possible_indices))


def _get_possible_question_indices(config: str = "config"):
    indices_from_selected_questions = _get_possible_indices_from_selected_questions(config)
    indices_from_selected_tags = _get_possible_indices_from_selected_tags(config)
    possible_question_indices = list(
        set(indices_from_selected_questions).intersection(indices_from_selected_tags)
    )
    return sorted(possible_question_indices)


def initialize_queue():
    possible_question_indices = _get_possible_question_indices()
    error_msg = (
        "Oeps, er zijn niet genoeg vragen voor deze filters!"
        + " Probeer opnieuw met andere filters."
    )

    if not possible_question_indices:
        st.write(error_msg)
        st.stop()

    if not st.session_state["config"]["random_selection"]:
        start_index = st.session_state["config"]["question_start_index"]
        end_index = st.session_state["config"]["question_end_index"]
        if end_index > len(possible_question_indices):
            st.write(error_msg)
            breakpoint()

            st.stop()

        queue = possible_question_indices[start_index:end_index]
    else:
        n_random_questions = st.session_state["config"]["n_random_questions"]
        if n_random_questions > len(possible_question_indices):
            st.write(error_msg)
            st.stop()
        queue = random.sample(possible_question_indices, n_random_questions)

    if st.session_state["config"]["infinite_practice"]:
        queue *= int(110000 / len(queue))
        random.shuffle(queue)
        queue = queue[:100000]

    st.session_state["question_indices"] = queue.copy()

    random.shuffle(queue)
    st.session_state["queue"] = queue
    st.session_state["initialize_queue"] = False


def define_answer_suggestions():
    correct_answers = st.session_state["correct_answers"]
    question_indices = st.session_state["question_indices"]
    st.session_state["suggestions"] = sorted(
        list(set([correct_answers[i] for i in question_indices]))
    )


def get_current_question_answer_pair():
    current_index = st.session_state["queue"][0]
    st.session_state["question_index"] = current_index
    st.session_state["question_object"] = st.session_state["question_objects"][current_index]
    st.session_state["correct_answer"] = st.session_state["correct_answers"][current_index]


def _get_feedback_emoji(correct_perc: float) -> str:
    if correct_perc == 1:
        return "😁"  # Perfect score
    elif correct_perc >= 0.9:
        return "😊"  # Excellent
    elif correct_perc >= 0.8:
        return "🙂"  # Very good
    elif correct_perc >= 0.7:
        return "😌"  # Good
    elif correct_perc >= 0.6:
        return "😐"  # Average
    elif correct_perc >= 0.5:
        return "😕"  # Below average
    elif correct_perc >= 0.4:
        return "🙁"  # Poor
    elif correct_perc >= 0.2:
        return "😢"  # Very poor
    else:
        return "😭"  # Extremely poor


def show_progress():
    infinite_practice = st.session_state["config"]["infinite_practice"]
    answer_submitted = st.session_state["answer_submitted"]
    queue = st.session_state["queue"]

    n_start = st.session_state["n_questions"] if not infinite_practice else 100000

    if infinite_practice:
        n_left = len(queue) - 1 if answer_submitted else len(queue)
    else:
        n_left = len(
            set(st.session_state["question_indices"])
            - set(st.session_state["question_indices_seen"])
        )
    n_done = n_start - n_left
    progress_perc = n_done / n_start
    progress_msg = f"**Voortgang**: {progress_perc:.0%} ({n_done}/{n_start})"

    n_correct = st.session_state["n_correct"]
    n_seen = len(st.session_state["question_indices_seen"])

    correct_perc = n_correct / n_seen if n_seen else 0
    emoji = _get_feedback_emoji(correct_perc) if n_seen else ""
    correct_msg = f"**Correct**: {correct_perc:.0%} ({n_correct}/{n_seen}) {emoji}"
    st.progress(progress_perc, f"{progress_msg} -- {correct_msg}")


def present_question():
    # To be customized per use case
    st.write(st.session_state["question_object"]["question"])


def answer_form(
    text: str,
):
    def _on_click_check():
        st.session_state["given_answer"] = st.session_state["answer_field"]
        if st.session_state["given_answer"]:
            st.session_state["answer_submitted"] = True
            _toggle_input_focus("next_button")
            if not st.session_state["answer_checked"]:
                check_answer()
                update_queue()

    def _on_click_volgende():
        st.session_state["answer_submitted"] = False
        st.session_state["queue"].pop(0)
        st.session_state["answer_checked"] = False
        st.session_state["clear_answer_field"] = True
        _toggle_input_focus("input_field")

    with st.form("answer_form"):
        if st.session_state["config"]["answer_suggestions"]:
            st.selectbox(text, options=[""] + st.session_state["suggestions"], key="answer_field")
        else:
            st.text_input(text, key="answer_field")

        if not st.session_state["answer_submitted"]:
            st.form_submit_button("Check", on_click=_on_click_check)
        else:
            st.form_submit_button("Volgende", on_click=_on_click_volgende)


def check_answer():
    given_answer = st.session_state["given_answer"].lower()
    correct_answer = st.session_state["correct_answer"].lower()
    correct = given_answer == correct_answer

    infinite_practice = st.session_state["config"]["infinite_practice"]

    question_index = st.session_state["question_index"]
    unseen_question = question_index not in st.session_state["question_indices_seen"]
    if correct and (infinite_practice or (not infinite_practice and unseen_question)):
        st.session_state["n_correct"] += 1

    st.session_state["answer_checked"] = True
    st.session_state["answer_correct"] = correct
    if infinite_practice:
        st.session_state["question_indices_seen"].append(question_index)
    else:
        st.session_state["question_indices_seen"].add(question_index)


def update_queue():
    if st.session_state["answer_correct"] or st.session_state["config"]["infinite_practice"]:
        return
    question_index = st.session_state["question_index"]
    insert_index = min(random.randint(3, 8), len(st.session_state["queue"]))
    st.session_state["queue"].insert(insert_index, question_index)


def show_feedback_message():
    if st.session_state["answer_correct"]:
        st.write(
            '<div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-bottom: 10px;">✅ Goed!</div>',
            unsafe_allow_html=True,
        )
    else:
        st.write(
            '<div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 10px;">❌ Fout!</div>',
            unsafe_allow_html=True,
        )


def show_tags():
    st.write(" ".join([f"`{t}`" for t in st.session_state["question_object"]["tags"]]))


def present_question_information():
    # To be customized per use case
    show_tags()
    st.write(st.session_state["question_object"]["info"])


def next_question():
    st.session_state["queue"].pop(0)
    st.session_state["next_question"] = False
    st.session_state["answer_checked"] = False
    st.session_state["clear_answer_field"] = True
    st.rerun()


def stop_overhoring():
    st.subheader("Dat was de laatste! 🎉")
    st.balloons()
    st.write("")
    if st.button("Volgende"):
        st.session_state["overhoring_started"] = False
        st.rerun()
    focus_on_next_button_in_form()
    st.stop()


def clear_answer_field():
    st.session_state["answer_field"] = ""
    st.session_state["clear_answer_field"] = False


def focus_on_input_in_form():
    st.session_state["counter"] += 1
    if st.session_state["config"]["answer_suggestions"]:
        components.html(
            f"""
                <div>some hidden container</div>
                <p>{st.session_state.counter}</p>
                <script>
                    // Focus on Streamlit selectbox elements
                    var selectBoxes = window.parent.document.querySelectorAll('[role="combobox"]');
                    if (selectBoxes.length > 0) {{
                        selectBoxes[3].focus();
                    }}
            </script>
            """,
            height=0,
        )
    else:
        components.html(
            f"""
                <div>some hidden container</div>
                <p>{st.session_state.counter}</p>
                <script>
                    // Focus on text input elements
                    var textInputs = window.parent.document.querySelectorAll("input[type=text]");
                    textInputs[0].focus();
            </script>
            """,
            height=0,
        )


def focus_on_next_button_in_form():
    components.html(
        """
        <script>
            // Focus on the "Volgende" button
            var buttons = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; ++i) {
                if (buttons[i].innerText === "Volgende") {
                    buttons[i].focus();
                    break;
                }
            }
        </script>
        """,
        height=0,
    )
