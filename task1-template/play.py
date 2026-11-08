import random

import streamlit as st


PLAYERS = [
    {
        "name": "Lionel Messi",
        "hints": [
            "He is from Argentina.",
            "He won the World Cup in 2022.",
            "He played for Barcelona for many years.",
        ],
    },
    {
        "name": "Cristiano Ronaldo",
        "hints": [
            "He is from Portugal.",
            "He is famous for wearing number 7.",
            "He played for Manchester United and Real Madrid.",
        ],
    },
    {
        "name": "Marta",
        "hints": [
            "She is from Brazil.",
            "She is one of the most famous female football players.",
            "She played for Brazil at many World Cups.",
        ],
    },
]


def start_game():
    player = random.choice(PLAYERS)
    st.session_state.goal = player
    st.session_state.guess_count = 0
    st.session_state.game_over = False
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Guess the football player. Here is your first hint: "
            + player["hints"][0],
        }
    ]


if "goal" not in st.session_state:
    start_game()

if "games_played" not in st.session_state:
    st.session_state.games_played = 0

if "guesses_per_game" not in st.session_state:
    st.session_state.guesses_per_game = []


st.title("Football Player Guessing Game")
st.write("Guess the player using the hints in the chat.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

guess = st.chat_input("Type your guess", disabled=st.session_state.game_over)

if guess:
    clean_guess = guess.strip().casefold()

    if not clean_guess:
        st.warning("Please enter a name first.")
    else:
        st.session_state.guess_count += 1
        st.session_state.messages.append({"role": "user", "content": guess})

        goal_name = st.session_state.goal["name"]
        if clean_guess == goal_name.casefold():
            feedback = (
                f"Correct! It was {goal_name}. You needed "
                f"{st.session_state.guess_count} guesses."
            )
            st.session_state.game_over = True
            st.session_state.games_played += 1
            st.session_state.guesses_per_game.append(
                st.session_state.guess_count
            )
        else:
            hint_number = min(
                st.session_state.guess_count,
                len(st.session_state.goal["hints"]) - 1,
            )
            feedback = (
                "That is not correct. Here is another hint: "
                + st.session_state.goal["hints"][hint_number]
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": feedback}
        )
        st.rerun()

if st.session_state.guess_count == 3:
    st.warning(
        "You have used all your guesses. The correct answer was "
        f"{st.session_state.goal['name']}."
    )
    st.session_state.game_over = True
    st.session_state.games_played += 1
    st.session_state.guesses_per_game.append(st.session_state.guess_count)

if st.session_state.game_over and st.button("Start a new game"):
    start_game()
    st.rerun()

st.caption(f"Guesses in this game: {st.session_state.guess_count}")