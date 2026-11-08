import json
import random
from urllib import error, request

import streamlit as st


# Fill these values with the credentials and gateway information from Keyosk.
LITELLM_BASE_URL = ""
LITELLM_API_KEY = ""
MODEL_NAME = ""


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


def ask_llm(guess):
    """Ask the LiteLLM gateway for the next game response."""
    if not LITELLM_BASE_URL or not LITELLM_API_KEY or not MODEL_NAME:
        return None

    endpoint = LITELLM_BASE_URL.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint += "/chat/completions"

    prompt = f"""
You are a friendly football player guessing game assistant.
The hidden player is {st.session_state.goal['name']}.
The player has guessed: {guess}
The guess is {'correct' if guess.casefold() == st.session_state.goal['name'].casefold() else 'incorrect'}.
If the guess is incorrect, give one short useful hint without revealing the answer.
If it is correct, congratulate the player. Keep your answer under 50 words.
""".strip()

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        http_request = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {LITELLM_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(http_request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except (
        error.HTTPError,
        error.URLError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
        OSError,
        TypeError,
        UnicodeDecodeError,
    ):
        return None


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
        correct_guess = clean_guess == goal_name.casefold()
        feedback = ask_llm(clean_guess)

        if correct_guess:
            if feedback is None:
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
            if feedback is None:
                hint_number = min(
                    st.session_state.guess_count,
                    len(st.session_state.goal["hints"]) - 1,
                )
                feedback = (
                    "That is not correct. Here is another hint: "
                    + st.session_state.goal["hints"][hint_number]
                )

        if st.session_state.guess_count == 4 and not correct_guess:
            feedback = (
                "You have used all your guesses. The correct answer was "
                + goal_name
            )
            st.session_state.game_over = True
            st.session_state.games_played += 1
            st.session_state.guesses_per_game.append(
                st.session_state.guess_count
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": feedback}
        )
        st.rerun()

if st.session_state.guess_count == 4:
    st.warning("The game is over. Start a new game to play again.")

if st.session_state.game_over and st.button("Start a new game"):
    start_game()
    st.rerun()

st.caption(f"Guesses in this game: {st.session_state.guess_count}")