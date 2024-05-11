import streamlit as st
import random
import json
from thefuzz import fuzz
from thefuzz import process
from pathlib import Path
import pandas as pd

path = Path(__file__).parent

with open(path / 'data/civics2024-05-08.json') as fi:
    civics_final = json.load(fi)


if 'stage' not in st.session_state:
    st.session_state.stage = 0

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0

if 'answer_score' not in st.session_state:
    st.session_state.answer_score = []

if 'chosen_questions' not in st.session_state:
    st.session_state.chosen_questions = []

if 'answer_table' not in st.session_state:
    st.session_state.answer_table = pd.DataFrame(columns=['Question', 'Your Answer', 'Closest Answer'])


def setup_questions(max_q):
    # select random  questions
    chosen_q = random.sample(range(1,101), max_q)
    st.session_state.chosen_questions = chosen_q
    update_stage(1)

def check_answer(your_answer, correct_answer):
    # take only the closest match
    st.session_state.answer_score = process.extract(your_answer, correct_answer, scorer=fuzz.token_sort_ratio)[0]
    q_num = str(st.session_state.chosen_questions[st.session_state.current_question - 1])

    question = list(civics_final[q_num].keys())[0]
    st.session_state.answer_table = pd.DataFrame({'Question':question,
                                                  'Your Answer':your_answer,
                                                  'Closest Answer':st.session_state.answer_score[0]}, index=[0])
    update_stage(2)


def update_stage(stage): #cur_q, chosen_q

    # to get to the end one
    if (st.session_state.stage == 2 
        and st.session_state.current_question == len(st.session_state.chosen_questions)):
        st.session_state.stage = 3
    else:
        st.session_state.stage = stage

    if stage == 0:
        st.session_state.current_question = 0
    elif stage == 1:
        st.session_state.current_question += 1

    

st.title('🇺🇸 Practice Civics Test 🗽')

if st.session_state.stage == 0:
    max_q = st.slider('How many questions would you like to answer?', 1, 100, 10)
    st.button('Start Quiz!', on_click=setup_questions, args=(max_q,))

if st.session_state.stage == 1:
    #st.write('current q', st.session_state.current_question)
    # extract the right question number based on the index
    q_num = str(st.session_state.chosen_questions[st.session_state.current_question - 1])
    question = list(civics_final[q_num].keys())[0]
    correct_answer = list(civics_final[q_num].values())[0]
    st.write(question)

    your_answer = st.text_input('Your answer:', '')
    st.button('Submit', on_click=check_answer, args=(your_answer, correct_answer))#, st.session_state.chosen_questions))
    st.progress((st.session_state.current_question-1)/len(st.session_state.chosen_questions), text='Quiz Progress')
    
if st.session_state.stage == 2:
    #st.write('current q', st.session_state.current_question)
    q_num = str(st.session_state.chosen_questions[st.session_state.current_question - 1])
    #question = list(civics_final[q_num].keys())[0]
    correct_answer = list(civics_final[q_num].values())[0]
    
    st.dataframe(st.session_state.answer_table, use_container_width=True, hide_index=True)

    # this is the score; can be adjusted
    if st.session_state.answer_score[1] >= 75:
        st.success(f'Good job! Your answer was a {st.session_state.answer_score[1]}% match')
    elif st.session_state.answer_score[1] >= 50:
        st.warning(f'Uh oh, your answer was a {st.session_state.answer_score[1]}% match')
    else: 
        st.error(f'Oh no! Your answer was only a {st.session_state.answer_score[1]}% match')


    with st.expander('Show list of all possible answers'):
        # this is just to format it more nicely
        for ca in correct_answer:
            st.write('- '+ ca)
    st.button('Next Question', on_click=update_stage, args=(1,))
    st.progress(st.session_state.current_question/len(st.session_state.chosen_questions), text='Quiz Progress')

if st.session_state.stage == 3:
    st.write('You done it all. The end')
    st.balloons()

if st.session_state.stage != 0: 
    st.divider() 
    st.button('Reset Quiz', on_click=update_stage, args=(0,))