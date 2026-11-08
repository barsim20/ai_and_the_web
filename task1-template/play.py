import os
import random
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st


load_dotenv(Path(__file__).with_name(".env"))

LITELLM_BASE_URL = os.getenv(
    "LITELLM_BASE_URL", "https://litellm.uni-osnabrueck.de/v1"
)
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("LITELLM_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-4-E4B-it")


PLAYERS = [
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Marta",
]


def ask_llm():
    """Send the complete conversation to the LiteLLM gateway."""
    if not LLM_API_KEY:
        st.session_state.llm_error = (
            "LLM_API_KEY is missing from the .env file."
        )
        return None

    system_prompt = f"""
You are the conversation partner in a friendly football player guessing game.
The hidden player is {st.session_state.goal}.
You must lead the entire conversation. Give useful hints, react naturally to
the user's messages, and never let the user change the hidden player.
When the user correctly guesses the player, congratulate them and append the
exact marker [GAME_WON] to your response. Do not use this marker otherwise.
Keep the reply under 60 words.
""".strip()

    try:
        client = OpenAI(
            base_url=LITELLM_BASE_URL,
            api_key=LLM_API_KEY,
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages,
            ],
        )
        content = response.choices[0].message.content or ""
        game_over = content.endswith("[GAME_WON]")
        if game_over:
            content = content[: -len("[GAME_WON]")].rstrip()
        return {"reply": content, "game_over": game_over}
    except Exception as exc:
        st.session_state.llm_error = f"LiteLLM request failed: {exc}"
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
            "reply": "LLM unavailable: " + st.session_state.llm_error,
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
                "reply": "LLM unavailable: " + st.session_state.llm_error,
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