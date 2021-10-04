---
title: Indonesian GPT-2 
emoji: 🦀
colorFrom: green
colorTo: indigo
sdk: streamlit
app_file: app/app.py
pinned: false
---

# Configuration

`title`: _string_  
Display title for the Space

`emoji`: _string_  
Space emoji (emoji-only character allowed)

`colorFrom`: _string_  
Color for Thumbnail gradient (red, yellow, green, blue, indigo, purple, pink, gray)

`colorTo`: _string_  
Color for Thumbnail gradient (red, yellow, green, blue, indigo, purple, pink, gray)

`sdk`: _string_  
Can be either `gradio` or `streamlit`

`app_file`: _string_  
Path to your main application file (which contains either `gradio` or `streamlit` Python code).  
Path is relative to the root of the repository.

`pinned`: _boolean_  
Whether the Space stays on top of your list.
