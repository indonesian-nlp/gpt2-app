import streamlit as st
import SessionState
from mtranslate import translate
from prompts import PROMPT_LIST
import random
import time
from transformers import pipeline, set_seed
import psutil
import codecs
import streamlit.components.v1 as stc
import pathlib

# st.set_page_config(page_title="Indonesian GPT-2")

MODELS = {
    "Indonesian GPT-2 Small": {
        "group": "Indonesian GPT-2",
        "name": "flax-community/gpt2-small-indonesian",
        "description": "The original Indonesian GPT-2 small model.",
        "text_generator": None
    },
    "Indonesian GPT-2 Medium": {
        "group": "Indonesian GPT-2",
        "name": "flax-community/gpt2-medium-indonesian",
        "description": "The original Indonesian GPT-2 medium model.",
        "text_generator": None
    },
    "Indonesian Literature - GPT-2 Small": {
        "group": "Indonesian Literature",
        "name": "cahya/gpt2-small-indonesian-story",
        "description": "The Indonesian Literature Generator using fine-tuned GPT-2 small model.",
        "text_generator": None
    },
    "Indonesian Literature - GPT-2 Medium": {
        "group": "Indonesian Literature",
        "name": "cahya/gpt2-medium-indonesian-story",
        "description": "The Indonesian Literature Generator using fine-tuned GPT-2 medium model.",
        "text_generator": None
    },
    "Indonesian Academic Journal - GPT-2 Small": {
        "group": "Indonesian Journal",
        "name": "Galuh/id-journal-gpt2",
        "description": "The Indonesian Journal Generator using fine-tuned GPT-2 small model.",
        "text_generator": None
    },
    "Indonesian Persona Chatbot - GPT-2 Small": {
        "group": "Indonesian Persona Chatbot",
        "name": "cahya/gpt2-small-indonesian-personachat",
        "description": "The Indonesian Persona Chatbot using fine-tuned GPT-2 small model.",
        "text_generator": None
    },
}


def stc_chatbot(root_dir, width=700, height=900):
    html_file = root_dir/"app/chatbot.html"
    css_file = root_dir/"app/css/main.css"
    js_file = root_dir/"app/js/main.js"
    if css_file.exists() and js_file.exists():
        html = codecs.open(html_file, "r").read()
        css = codecs.open(css_file, "r").read()
        js = codecs.open(js_file, "r").read()
        html = html.replace('<link rel="stylesheet" href="css/main.css">', "<style>\n" + css + "\n</style>")
        html = html.replace('<script src="js/main.js"></script>', "<script>\n" + js + "\n</script>")
        stc.html(html, width=width, height=height, scrolling=True)

st.sidebar.markdown("""
<style>
.centeralign {
    text-align: center;
}
</style>
<p class="centeralign">
    <img src="https://huggingface.co/spaces/flax-community/gpt2-indonesian/resolve/main/huggingwayang.png"/>
</p>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
___
<p class="centeralign">
This is a collection of applications that generates sentences using Indonesian GPT-2 models!
</p>
<p class="centeralign">
Created by <a href="https://huggingface.co/indonesian-nlp">Indonesian NLP</a> team @2021
<br/>
<a href="https://github.com/indonesian-nlp/gpt2-app" target="_blank">GitHub</a> | <a href="https://github.com/indonesian-nlp/gpt2-app" target="_blank">Project Report</a>
<br/>
A mirror is available at <a href="https://gpt2-app.ai-research.id/" target="_blank">ai-research.id</a>
</p>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
___
        """, unsafe_allow_html=True)

model = st.sidebar.selectbox('Model', (MODELS.keys()))


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_generator(model_name: str):
    st.write(f"Loading the GPT2 model {model_name}, please wait...")
    text_generator = pipeline('text-generation', model=model_name)
    return text_generator


# Disable the st.cache for this function due to issue on newer version of streamlit
# @st.cache(suppress_st_warning=True, hash_funcs={tokenizers.Tokenizer: id})
def process(text_generator, text: str, max_length: int = 100, do_sample: bool = True, top_k: int = 50, top_p: float = 0.95,
            temperature: float = 1.0, max_time: float = 120.0, seed=42):
    # st.write("Cache miss: process")
    set_seed(seed)
    result = text_generator(text, max_length=max_length, do_sample=do_sample,
                            top_k=top_k, top_p=top_p, temperature=temperature,
                            max_time=max_time)
    return result


st.title("Indonesian GPT-2 Applications")
prompt_group_name = MODELS[model]["group"]
st.header(prompt_group_name)
description = f"This application is a demo for {MODELS[model]['description']}"
st.markdown(description)
model_name = f"Model name: [{MODELS[model]['name']}](https://huggingface.co/{MODELS[model]['name']})"
st.markdown(model_name)
if prompt_group_name in ["Indonesian GPT-2", "Indonesian Literature", "Indonesian Journal"]:
    session_state = SessionState.get(prompt=None, prompt_box=None, text=None)
    ALL_PROMPTS = list(PROMPT_LIST[prompt_group_name].keys())+["Custom"]

    prompt = st.selectbox('Prompt', ALL_PROMPTS, index=len(ALL_PROMPTS)-1)

    # Update prompt
    if session_state.prompt is None:
        session_state.prompt = prompt
    elif session_state.prompt is not None and (prompt != session_state.prompt):
        session_state.prompt = prompt
        session_state.prompt_box = None
        session_state.text = None
    else:
        session_state.prompt = prompt

    # Update prompt box
    if session_state.prompt == "Custom":
        session_state.prompt_box = "Enter your text here"
    else:
        print(f"# prompt: {session_state.prompt}")
        print(f"# prompt_box: {session_state.prompt_box}")
        if session_state.prompt is not None and session_state.prompt_box is None:
            session_state.prompt_box = random.choice(PROMPT_LIST[prompt_group_name][session_state.prompt])

    session_state.text = st.text_area("Enter text", session_state.prompt_box)

    max_length = st.sidebar.number_input(
        "Maximum length",
        value=100,
        max_value=512,
        help="The maximum length of the sequence to be generated."
    )

    temperature = st.sidebar.slider(
        "Temperature",
        value=1.0,
        min_value=0.0,
        max_value=10.0
    )

    do_sample = st.sidebar.checkbox(
        "Use sampling",
        value=True
    )

    top_k = 30
    top_p = 0.95

    if do_sample:
        top_k = st.sidebar.number_input(
            "Top k",
            value=top_k,
            help="The number of highest probability vocabulary tokens to keep for top-k-filtering."
        )
        top_p = st.sidebar.number_input(
            "Top p",
            value=top_p,
            help="If set to float < 1, only the most probable tokens with probabilities that add up to top_p or higher "
                 "are kept for generation."
        )

    seed = st.sidebar.number_input(
        "Random Seed",
        value=25,
        help="The number used to initialize a pseudorandom number generator"
    )

    for group_name in MODELS:
        if MODELS[group_name]["group"] in ["Indonesian GPT-2", "Indonesian Literature", "Indonesian Journal"]:
            MODELS[group_name]["text_generator"] = get_generator(MODELS[group_name]["name"])
    # text_generator = get_generator()
    if st.button("Run"):
        with st.spinner(text="Getting results..."):
            memory = psutil.virtual_memory()
            st.subheader("Result")
            time_start = time.time()
            # text_generator = MODELS[model]["text_generator"]
            result = process(MODELS[model]["text_generator"], text=session_state.text, max_length=int(max_length),
                             temperature=temperature, do_sample=do_sample,
                             top_k=int(top_k), top_p=float(top_p), seed=seed)
            time_end = time.time()
            time_diff = time_end-time_start
            result = result[0]["generated_text"]
            st.write(result.replace("\n", "  \n"))
            st.text("Translation")
            translation = translate(result, "en", "id")
            st.write(translation.replace("\n", "  \n"))
            # st.write(f"*do_sample: {do_sample}, top_k: {top_k}, top_p: {top_p}, seed: {seed}*")
            info = f"""
            *Memory: {memory.total/(1024*1024*1024):.2f}GB, used: {memory.percent}%, available: {memory.available/(1024*1024*1024):.2f}GB*        
            *Text generated in {time_diff:.5} seconds*
            """
            st.write(info)

            # Reset state
            session_state.prompt = None
            session_state.prompt_box = None
            session_state.text = None
elif model.startswith("Indonesian Persona Chatbot"):
    root_dir = pathlib.Path(".")
    stc_chatbot(root_dir)
