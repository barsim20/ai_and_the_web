import json
import os
import random
from urllib import error, request

from dotenv import load_dotenv
import streamlit as st


load_dotenv()

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")


PLAYERS = [
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Marta",
]


def ask_llm():
    """Send the complete conversation to the LiteLLM gateway."""
    if not LITELLM_BASE_URL or not LITELLM_API_KEY or not MODEL_NAME:
        return None

    endpoint = LITELLM_BASE_URL.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint += "/chat/completions"

    system_prompt = f"""
You are the conversation partner in a friendly football player guessing game.
The hidden player is {st.session_state.goal}.
You must lead the entire conversation. Give useful hints, react naturally to
the user's messages, and never let the user change the hidden player.
When the user correctly guesses the player, congratulate them and set game_over
to true. Otherwise set game_over to false.
Return only valid JSON with exactly these keys:
{{"reply": "your message to the user", "game_over": false}}
Keep the reply under 60 words.
""".strip()

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
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
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
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
    st.session_state.messages = []

    first_message = ask_llm()
    if first_message is None:
        first_message = {
            "reply": (
                "The LLM is not configured yet. Add the LiteLLM settings "
                "to your .env file."
            ),
            "game_over": False,
        }
    st.session_state.messages.append(
        {"role": "assistant", "content": first_message["reply"]}
    )


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
    if not guess.strip():
        st.warning("Please enter a name first.")
    else:
        st.session_state.guess_count += 1
        st.session_state.messages.append({"role": "user", "content": guess})

        response = ask_llm()
        if response is None:
            response = {
                "reply": "I could not reach the LLM. Please check your settings.",
                "game_over": False,
            }

        st.session_state.messages.append(
            {"role": "assistant", "content": response["reply"]}
        )
        if response.get("game_over", False):
            st.session_state.game_over = True
            st.session_state.games_played += 1
            st.session_state.guesses_per_game.append(
                st.session_state.guess_count
            )
        st.rerun()

if st.session_state.game_over and st.button("Start a new game"):
    start_game()
    st.rerun()

st.caption(f"Guesses in this game: {st.session_state.guess_count}")