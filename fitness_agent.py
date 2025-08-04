import streamlit as st
import requests

# --- CONFIGURATION ---
API_KEY = "J9MXIvP6zEjpiCfX-CLobBX8TInVxFKJDPsP9PAbMpko"
PROJECT_ID = "100594a5-cdfe-40d5-94ca-47776f3feb16"
MODEL_ID = "ibm/granite-3-8b-instruct"
REGION = "au-syd"
GENERATION_URL = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

# --- TOKEN HANDLER ---
@st.cache_data(ttl=3000)
def get_bearer_token():
    IAM_URL = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "apikey": API_KEY,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }
    response = requests.post(IAM_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Failed to get token: " + response.text)
        return None

# --- FITNESS BUDDY QUERY ---
def query_fitness_buddy(user_input, bearer_token):
    structured_prompt = f"""
You are Fitness Buddy, an AI health assistant.

Based on the user’s information, provide:
1. A motivational message.
2. A simple vegetarian meal plan for the day.
3. A short home workout routine.
4. A weekly fitness tip.
5. A habit to track this week using a streak idea.

Input: {user_input}

Output:
"""
    body = {
        "input": structured_prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1000,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "moderations": {
            "hap": {"input": {"enabled": True, "threshold": 0.5}, "output": {"enabled": True, "threshold": 0.5}},
            "pii": {"input": {"enabled": True, "threshold": 0.5}, "output": {"enabled": True, "threshold": 0.5}},
            "granite_guardian": {"input": {"threshold": 1}}
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    response = requests.post(GENERATION_URL, headers=headers, json=body)

    if response.status_code != 200:
        return f"❌ API Error: {response.status_code}\n{response.text}"

    return response.json()["results"][0]["generated_text"]

# --- STYLING ---
st.set_page_config(page_title="Fitness Buddy", page_icon="💪")
st.markdown("""
    <style>
        .chat-scroll {
            max-height: 70vh;
            overflow-y: auto;
            padding-right: 10px;
        }
        .user-msg {
            background-color: #d2f8d2;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .bot-msg {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("fitness.png", width=250)  # Ensure image is in your working directory
    st.markdown("### 💪 Welcome to Fitness Buddy")
    st.markdown("Ask me anything about **fitness**, **meal plans**, or **healthy habits**.")
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# --- TITLE ---
st.title("🤖 Fitness Buddy – Your AI Health Assistant")

# --- INITIALIZE CHAT HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- DISPLAY CHAT HISTORY ---
with st.container():
    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    for user, bot in st.session_state.chat_history:
        st.markdown(f'<div class="user-msg"><strong>🧍 You:</strong><br>{user}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-msg"><strong>🤖 Fitness Buddy:</strong><br>{bot}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT BOX FIXED AT BOTTOM ---
# --- Input box at the bottom ---
with st.form(key="input_form", clear_on_submit=True):
    user_query = st.text_input(
        "💬 Type your question below",
        key="input_text",
        placeholder="e.g., Suggest a 20-minute workout plan"
    )
    submitted = st.form_submit_button("Send")

# --- Only process new query if submitted and not empty ---
if submitted and user_query.strip():
    with st.spinner("Fitness Buddy is preparing your response..."):
        token = get_bearer_token()
        if token:
            reply = query_fitness_buddy(user_query.strip(), token)
            st.session_state.chat_history.append((user_query.strip(), reply))
            st.rerun()
        else:
            st.error("Authorization failed. Please check your API key.")

