import streamlit as st
from openai import OpenAI
import os


client = OpenAI(api_key=api_key)

# Define personality categories
categories = [
    "big_five",
    "mbti",
    "enneagram",
    "love_languages"
]

# Function to generate questions using the OpenAI GPT-4o model
def generate_questions(num_questions, prompt_text):
    generated_questions = []
    for _ in range(num_questions):
        messages = [
            {"role": "system", "content": "You are a creative assistant tasked with devising insightful personality test questions."},
            {"role": "user", "content": prompt_text}
        ]
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=50,
            stop=None
        )
        question = completion.choices[0].message.content.strip()
        generated_questions.append(question)
    return generated_questions

# Function to generate the prompt for personality analysis
def generate_prompt(responses):
    prompt_text = "Given the following responses, analyze and provide a comprehensive personality profile:\n"
    for category, answer_list in responses.items():
        prompt_text += f"\n{category}:\n"
        for question, answer in zip(answer_list["questions"], answer_list["responses"]):
            prompt_text += f"- {question} Response: {answer}\n"
    return prompt_text

# Function to get the analysis from the OpenAI GPT-4o model
def get_analysis(prompt_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in psychology and personality analysis."},
        {"role": "user", "content": prompt_text}
    ]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=800
    )
    return completion.choices[0].message.content

# Function to generate a report based on the responses
def generate_report(responses):
    report = "## Personality Analysis Report\n\n"
    for category, answer_list in responses.items():
        report += f"### {category.capitalize()}\n"
        for question, answer in zip(answer_list["questions"], answer_list["responses"]):
            report += f"**{question}**\n- {answer}\n\n"
    return report

st.title("Comprehensive Personality Type Analyzer")

if 'selected_questions' not in st.session_state or st.button("Regenerate Questions"):
    initial_prompt = "Generate a single general question to help understand someone's personality."
    follow_up_prompt = "Generate a single follow-up question to further refine understanding of someone's personality."
    
    st.session_state.selected_questions = generate_questions(10, initial_prompt)
    st.session_state.follow_up_questions = generate_questions(5, follow_up_prompt)
    st.session_state.responses = {category: {"questions": [], "responses": []} for category in categories}
    st.session_state.current_phase = 'initial'
    st.session_state.current_question_index = 0

responses = st.session_state.responses
current_phase = st.session_state.current_phase
current_question_index = st.session_state.current_question_index

if current_phase == 'initial' and current_question_index < 10:
    question = st.session_state.selected_questions[current_question_index]
    user_response = st.text_input(f"Question {current_question_index + 1}: {question}", key=f"question_{current_question_index}")
    if st.button("Next Question"):
        if user_response:
            responses[categories[current_question_index % len(categories)]]["questions"].append(question)
            responses[categories[current_question_index % len(categories)]]["responses"].append(user_response)
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index == 10:
                st.session_state.current_phase = 'follow_up'
                st.session_state.current_question_index = 0

elif current_phase == 'follow_up' and current_question_index < 5:
    question = st.session_state.follow_up_questions[current_question_index]
    user_response = st.text_input(f"Follow-up Question {current_question_index + 1}: {question}", key=f"follow_up_question_{current_question_index}")
    if st.button("Next Follow-up Question"):
        if user_response:
            responses[categories[current_question_index % len(categories)]]["questions"].append(question)
            responses[categories[current_question_index % len(categories)]]["responses"].append(user_response)
            st.session_state.current_question_index += 1

if len([q for cat in responses.values() for q in cat["questions"]]) == 15:
    prompt_text = generate_prompt(responses)
    result = get_analysis(prompt_text)
    st.write("Analysis complete! Here is the personality profile based on your responses:")
    st.write(result)
    report = generate_report(responses)
    st.write(report)

st.sidebar.header("About the Application")
st.sidebar.info("This application uses OpenAI's GPT-4o to dynamically generate and analyze responses across multiple personality frameworks.")
