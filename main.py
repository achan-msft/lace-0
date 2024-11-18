# to run it, execute streamlit run main.py 
import streamlit as st 

st.title('My First Streamlit App st.title')
st.write('Welcome to my Streamlit app! st.write')

user_input = st.text_input('Enter a custom message:', 'Hello, Streamlit!')
st.write('Customized Message:', user_input)

x = st.slider('x')
st.write(x, 'Squared is ...', x*x)
