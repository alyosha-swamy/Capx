import streamlit as st
from openai import OpenAI
import os

# Setup the OpenAI client
api_key = st.secrets["api_key"]
client = OpenAI(api_key=api_key)

# Define personality categories
categories = ["big_five", "mbti", "enneagram", "love_languages"]

# Function to generate questions
def generate_questions(num_questions, prompt_text):
    questions = []
    for _ in range(num_questions):
        try:
            messages = [
                {"role": "system", "content": "You are a creative assistant tasked with devising insightful personality test questions."},
                {"role": "user", "content": prompt_text}
            ]
            completion = client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=50
            )
            question = completion.choices[0].message.content.strip()
            questions.append(question)
        except Exception as e:
            st.error(f"Failed to generate questions: {e}")
            break
    return questions

# Handler for user responses
def handle_response(question, response, category):
    if response:
        responses[category]["questions"].append(question)
        responses[category]["responses"].append(response)

# Display questions and manage transitions
def display_questions(questions, phase):
    if questions:
        question = questions[current_question_index]
        user_response = st.text_input(f"{phase} Question {current_question_index + 1}: {question}", key=f"{phase}_{current_question_index}")
        if st.button("Next Question", key=f"next_{phase}_{current_question_index}"):
            handle_response(question, user_response, categories[current_question_index % len(categories)])
            next_question()

# Cycle to the next question
def next_question():
    if current_question_index + 1 < len(st.session_state.questions):
        st.session_state.current_question_index += 1
    else:
        st.session_state.phase = 'follow_up' if st.session_state.phase == 'initial' else 'completed'
        st.session_state.current_question_index = 0

# Initialize or reset the session
if 'phase' not in st.session_state or st.button("Restart Analysis"):
    st.session_state.questions = generate_questions(10, "Generate a single general question to help understand someone's personality.")
    st.session_state.follow_up_questions = generate_questions(5, "Generate a single follow-up question to further refine understanding of someone's personality.")
    st.session_state.responses = {category: {"questions": [], "responses": []} for category in categories}
    st.session_state.phase = 'initial'
    st.session_state.current_question_index = 0

responses = st.session_state.responses
current_phase = st.session_state.phase
current_question_index = st.session_state.current_question_index

if current_phase in ['initial', 'follow_up']:
    questions = st.session_state.questions if current_phase == 'initial' else st.session_state.follow_up_questions
    display_questions(questions, current_phase)
elif current_phase == 'completed':
    prompt_text = generate_prompt(responses)
    result = get_analysis(prompt_text)
    st.write("Analysis complete! Here is the personality profile based on your responses:")
    st.write(result)
    report = generate_report(responses)
    st.write(report)

st.sidebar.header("About the Application")
st.sidebar.info("This application uses OpenAI's GPT-4o to dynamically generate and analyze responses across multiple personality frameworks.")
