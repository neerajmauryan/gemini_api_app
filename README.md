# OpenRouter Chat

A small Python chat app that uses OpenRouter's OpenAI-compatible chat completions API.

## Run it

```powershell
& "C:/Program Files/Python314/python.exe" -m pip install -r requirements.txt
& "C:/Program Files/Python314/python.exe" -m streamlit run app.py
```

Open the local URL printed by Streamlit. Paste an OpenRouter API key into the sidebar, or set `OPENROUTER_API_KEY` in your environment before launching. The app does not save keys entered in the sidebar.

The model field accepts any chat model ID available to your OpenRouter account. The default is `dots-studio/dots-3-note-preview:free`. Embedding models cannot generate chat replies.