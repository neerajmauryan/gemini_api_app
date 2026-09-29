import os

import requests
import streamlit as st


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "dots-studio/dots-3-note-preview:free"

st.set_page_config(
    page_title="OpenRouter Chat",
    page_icon="✳",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #18201d;
        --muted: #68736d;
        --paper: #f7f8f4;
        --green: #166b50;
        --line: #e2e7df;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%, rgba(194, 224, 203, .35), transparent 34rem),
            var(--paper);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3, [data-testid="stSidebar"] h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: 0 !important;
    }
    .main .block-container { max-width: 820px; padding-top: 3.25rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { background: #eef2ec; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
    .eyebrow {
        color: var(--green); font-size: .76rem; font-weight: 700;
        letter-spacing: .08em; text-transform: uppercase; margin-bottom: .65rem;
    }
    .intro { color: var(--muted); font-size: 1rem; margin-top: -.45rem; }
    div[data-testid="stChatMessage"] { border: 1px solid var(--line); border-radius: 12px; padding: .9rem 1rem; }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: #edf5ef; }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { background: #fff; }
    [data-testid="stChatInput"] { border-color: #cbd7cd; border-radius: 12px; }
    .stButton button { border-radius: 8px; }
    .small-note { color: var(--muted); font-size: .82rem; line-height: 1.5; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    try:
        saved_key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        saved_key = ""
    return os.getenv("OPENROUTER_API_KEY", "") or saved_key


def ask_openrouter(messages: list[dict[str, str]], model: str, api_key: str, temperature: float) -> str:
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "OpenRouter Chat",
        },
        json={"model": model, "messages": messages, "temperature": temperature},
        timeout=90,
    )
    if not response.ok:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except (ValueError, AttributeError):
            detail = response.text
        raise RuntimeError(f"OpenRouter returned {response.status_code}: {detail[:500]}")

    try:
        return response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("OpenRouter returned an unexpected response. Try again or choose another model.") from error


with st.sidebar:
    st.markdown("# ✳ OpenRouter Chat")
    st.caption("A simple chat interface for OpenRouter models")
    st.divider()

    api_key = get_api_key()
    if not api_key:
        api_key = st.text_input(
            "OpenRouter API key",
            type="password",
            placeholder="sk-or-v1-…",
            help="Your key is used only for this session and is not saved by the app.",
        )
    else:
        st.success("API key loaded from environment or Streamlit secrets")

    model = st.text_input(
        "Model",
        value=DEFAULT_MODEL,
        help="Use an OpenRouter model ID, for example: google/gemini-2.5-flash",
    ).strip()
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    system_prompt = st.text_area(
        "System instructions",
        value="You are a helpful, clear, and friendly assistant.",
        height=110,
    )
    st.divider()
    if st.button("Clear conversation", use_container_width=True, icon="🗑️"):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        '<p class="small-note">Model access and pricing are determined by your OpenRouter account.</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="eyebrow">Your AI, your choice of model</div>', unsafe_allow_html=True)
st.title("What can I help with?")
st.markdown('<p class="intro">Ask a question, explore an idea, or work through a problem.</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message the assistant…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Add your OpenRouter API key in the sidebar to start chatting.")
        elif not model:
            st.error("Enter an OpenRouter model ID in the sidebar.")
        else:
            with st.spinner("Thinking…"):
                try:
                    messages = [{"role": "system", "content": system_prompt}]
                    messages.extend(st.session_state.messages)
                    answer = ask_openrouter(messages, model, api_key, temperature)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except requests.RequestException as error:
                    st.error(f"Could not reach OpenRouter: {error}")
                except RuntimeError as error:
                    st.error(str(error))