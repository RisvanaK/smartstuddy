FOCUSMATE — CHIIKAWA THEME + GROQ AI

1. Extract this ZIP to a folder on your computer.
2. Open the extracted FocusMate_Chiikawa folder in VS Code.
3. Open Terminal > New Terminal.
4. Run: python -m pip install -r requirements.txt
5. In .streamlit, copy secrets.toml.example to a new file named secrets.toml.
6. In secrets.toml, replace PASTE_YOUR_GROQ_API_KEY_HERE with your actual Groq API key.
7. Run: python -m streamlit run app.py
8. Open the local URL shown in your terminal, then click AI Smart Planner.

Do not share secrets.toml or commit it to GitHub.
The original user-supplied Chiikawa image is in images/chiikawa.png.
Study tasks and timer progress are stored only in Streamlit session state and reset on new sessions.
AI requires internet and is subject to Groq API limits.
For Streamlit Community Cloud deployment, put GROQ_API_KEY in the app's Secrets settings.

ILLUSTRATED EDITION
Includes additional character illustrations cropped from the approved pastel dashboard preview.
The original character label was removed from the sidebar artwork; no CHIIKAWA wordmark is shown in the new artwork.
All illustrations are bundled in images/, so no separate downloads are required.


Design update: page headings and sidebar navigation use clean text labels without emoji icons. The characters_no_label.png artwork has been removed.
