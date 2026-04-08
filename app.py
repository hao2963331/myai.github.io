import streamlit as st

# Title of the Streamlit app
st.title("Welcome to My Streamlit App!")

# Input field to get the user's name
name = st.text_input("Enter your name:")

# Display greeting message based on user input
if name:
    st.write(f"Hello, {name}! Welcome to the app.")
else:
    st.write("Please enter your name to receive a greeting.")