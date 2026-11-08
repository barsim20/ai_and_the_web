import streamlit as st


st.title("Statistics")

games = st.session_state.get("games_played", 0)
guesses = st.session_state.get("guesses_per_game", [])

if guesses:
    average = sum(guesses) / len(guesses)
else:
    average = 0

first_column, second_column = st.columns(2)
first_column.metric("Games played", games)
second_column.metric("Average guesses", f"{average:.1f}")

if guesses:
    st.subheader("Guesses per game")
    st.bar_chart({"Guesses": guesses})
else:
    st.info("Finish one game to see your statistics.")