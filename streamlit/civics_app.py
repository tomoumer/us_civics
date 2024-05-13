import streamlit as st
import random
import json
from thefuzz import fuzz
from thefuzz import process
from pathlib import Path

path = Path(__file__).parent

with open(path / 'data/civics2024-05-08.json') as fi:
    civics_final = json.load(fi)


if 'stage' not in st.session_state:
    st.session_state.stage = 0

if 'question_count' not in st.session_state:
    st.session_state.question_count = 0

if 'answer_score' not in st.session_state:
    st.session_state.answer_score = []

if 'chosen_questions' not in st.session_state:
    st.session_state.chosen_questions = []

if 'total_score' not in st.session_state:
    st.session_state.total_score = [0, 0, 0]



def setup_questions(max_q):
    # select random  questions
    st.session_state.chosen_questions = random.sample(range(1,101), max_q)
    # reset score
    st.session_state.total_score = [0, 0, 0]
    update_stage(1)

def check_answer(your_answers, correct_answers):
    
    # to construct, it's going to have: your answer, best actual answer and score
    # for each answer (if more than one)
    st.session_state.answer_score = []

    # copy the answers for displaying later
    st.session_state.your_last_answer = your_answers

    # I'll have to remove elements after matching when the question asks for more than 1 answer
    tmp_answers = correct_answers.copy()

    # for each of the answers, find the closest match
    for your_answer in your_answers:
        tmp_answer_score = [your_answer]
        # take only the closest match
        tmp_answer_score.extend(process.extract(your_answer, tmp_answers, scorer=fuzz.token_sort_ratio)[0])
        # remove from other matching
        tmp_answers.remove(tmp_answer_score[1])
        
        st.session_state.answer_score.append(tmp_answer_score)
    update_stage(2)


def update_stage(stage): #cur_q, chosen_q

    # to get to the end one
    if (st.session_state.stage == 2 
        and st.session_state.question_count == len(st.session_state.chosen_questions)):
        st.session_state.stage = 3
    else:
        st.session_state.stage = stage

    if stage == 0:
        st.session_state.question_count = 0
    elif stage == 1:
        st.session_state.question_count += 1

    

st.title('🇺🇸 Practice Civics Test 🗽')


if st.session_state.stage == 0:
    st.write('Welcome to the U.S. civics test that I made for fun! The questions and answers are completely based on [the USCIS civics test](https://www.uscis.gov/sites/default/files/document/questions-and-answers/OoC_100_Questions_2008_Civics_Test_V1.pdf).')
    with st.expander('Show instructions'):
            st.markdown("""
                        - Select number of questions you want to answer and 'Start Quiz'
                        - You can 'Reset Quiz' at any point for any reason and start again
                        - Write the answer(s) and press 'Submit'
                        - The resulting page will show you which of the possible answer(s) most closly matched your answer
                        - You can also review additional possible answers
                        - Please note that there are a few questions specific to the State and (at least for right now), I decided to fill it with the one where I was so warmly welcomed - 4th congressional district of [Tennessee](https://en.wikipedia.org/wiki/Tennessee), the volunteer state!
                        - Special thanks to [Nashville Software School](https://nashvillesoftwareschool.com) who helped me gain the skills necessary to do this!
            """)
    max_q = st.slider('How many questions would you like to answer?', 1, 100, 10)
    st.button('Start Quiz!', on_click=setup_questions, args=(max_q,))

if st.session_state.stage == 1:
    quiz_progress = (st.session_state.question_count-1)/len(st.session_state.chosen_questions)
    # extract the right question number based on the index
    q_num = str(st.session_state.chosen_questions[st.session_state.question_count - 1])
    question = list(civics_final[q_num].keys())[0]
    correct_answers = list(civics_final[q_num].values())[0]
    #st.write(question)
    #make question fancy in blue
    st.info(f'{question}')

    your_answers = []
    your_answers.append(st.text_input('Your answer:', ''))

    if 'two' in question and 'one of the two' not in question:
        your_answers.append(st.text_input('Second answer:', ''))
    elif 'Name three ' in question:
        your_answers.append(st.text_input('Second answer:', ''))
        your_answers.append(st.text_input('Third answer:', ''))

    st.button('Submit', on_click=check_answer, args=(your_answers, correct_answers))#, st.session_state.chosen_questions))
    
if st.session_state.stage == 2:
    quiz_progress = st.session_state.question_count/len(st.session_state.chosen_questions)
    #st.write('current q', st.session_state.question_count)
    q_num = str(st.session_state.chosen_questions[st.session_state.question_count - 1])
    question = list(civics_final[q_num].keys())[0]
    correct_answers = list(civics_final[q_num].values())[0]

    printout = '| Question    | Your Answer | Correct Answer |\n| ----------- | ----------- | -------------- |\n'
    tmp_score = 0

    # there will be 1 on more depending on how many answers
    for i, answer_score in enumerate(st.session_state.answer_score):
        # note question is the same here, might have multiple answers
        printout += f'| {question} | {answer_score[0]} | {answer_score[1]} |\n'
        tmp_score += answer_score[2]

    # to get the avg. and then turn it to int
    tmp_score = int(tmp_score / (i+1))

    # this is the score; can be adjusted
    if tmp_score >= 75:
        st.success(f'Good job! Your answer was a {tmp_score}% match')
        st.session_state.total_score[0] += 1
    elif tmp_score >= 50:
        st.warning(f'Uh oh, your answer was a {tmp_score}% match')
        st.session_state.total_score[1] += 1
    else: 
        st.error(f'Oh no! Your answer was only a {tmp_score}% match')
        st.session_state.total_score[2] += 1

    st.write(printout)

    st.write('')

    #st.write(st.session_state.answer_score)


    # st.write('- Question:', question)
    # st.write('- Your Answer:', st.session_state.your_last_answer[0])
    # st.write('- Correct Answer:', st.session_state.answer_score[0])

    # st.write(f"""
    #             | Question    | Your Answer | Correct Answer |
    #             | ----------- | ----------- | -------------- | 
    #             | {question}     | {st.session_state.your_last_answer[0]}      | {st.session_state.answer_score[0]}               |
                
    #             """)

    # st.dataframe({'Question': question,
    #           'Your Answer': st.session_state.your_last_answer[0],
    #           'Correct Answer': st.session_state.answer_score[0]},
    #           use_container_width=True)

    with st.expander('Show list of all possible answers'):
        # this is just to format it more nicely
        for ca in correct_answers:
            st.write('- '+ ca)
    st.button('Next Question', on_click=update_stage, args=(1,))

if st.session_state.stage == 3:
    quiz_progress = 1.
    st.write('You have finished the quiz! Here are your final results:')
    st.write('- Correct answers:', st.session_state.total_score[0])
    st.write('- Partially Correct answers:', st.session_state.total_score[1])
    st.write('- Wrong Answers:', st.session_state.total_score[2])

    if st.session_state.total_score[0]/ (st.session_state.total_score[0] + st.session_state.total_score[1] + st.session_state.total_score[2]) >= 0.6:
        st.success("Congrats, you've gotten 60% or more answers correct, passing the USCIS test for naturalization!")
        st.balloons()
    else:
        st.error("Oh no! Your scored less than 60% answers correctly!")
        st.write("Maybe review the [USCIS 100 questions on Civics](https://www.uscis.gov/sites/default/files/document/questions-and-answers/OoC_100_Questions_2008_Civics_Test_V1.pdf) before retaking the quiz!") 

if st.session_state.stage != 0: 
    st.divider()
    st.progress(quiz_progress, 'quiz progress')
    st.button('Reset Quiz', on_click=update_stage, args=(0,))