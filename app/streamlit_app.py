import streamlit as st
from game_logic import TicTacToeBoard
from nlp_utils import apply_move_from_text

st.title("Tic-Tac-Toe LLM Controller 🎮🤖")

if "board" not in st.session_state:
    st.session_state.board = TicTacToeBoard()

user_input = st.text_input("Wpisz polecenie (np. 'Zagraj X w lewym górnym rogu planszy.'):")

if st.button("Wykonaj ruch"):
    result = apply_move_from_text(st.session_state.board, user_input)
    st.session_state.last_result = result

if "last_result" in st.session_state:
    st.markdown(
        f"<b>Komunikat:</b> <span style='color:#fff09c'>{st.session_state.last_result['message']}</span>",
        unsafe_allow_html=True
    )
    st.markdown("**Stan planszy:**")
    board_display = st.session_state.last_result["board_display"]
    st.markdown(f"```\n{board_display}\n```")
    if st.session_state.last_result["winner"]:
        st.success(f"Wygrywa: {st.session_state.last_result['winner']}")

if st.button("Resetuj grę"):
    st.session_state.board = TicTacToeBoard()
    st.session_state.last_result = None