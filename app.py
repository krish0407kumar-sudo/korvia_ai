# app.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import time
import base64
from io import BytesIO

# ==================== ENV & CLIENT ====================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== MEMORY FILE ====================
MEMORY_FILE = "korvia_memory.json"
NOTES_FILE = "korvia_notes.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Load previous memory
memory_data = load_json(MEMORY_FILE)
notes_data = load_json(NOTES_FILE)

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="Korvia AI", page_icon="🧠", layout="wide")

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(145deg, #0b0c10, #10151a, #0e1723);
            color: #e0e0e0;
        }
        [data-testid="stSidebar"] {
            background: rgba(20, 25, 30, 0.9);
            border-right: 1px solid rgba(0, 150, 200, 0.15);
        }
        h1, h2, h3, h4 {
            color: #4fd3c4;
            font-family: 'Poppins', sans-serif;
            text-shadow: 0px 0px 10px rgba(79, 211, 196, 0.4);
        }
        div.stButton > button {
            background: linear-gradient(90deg, #2a9d8f, #48cae4);
            color: white;
            border-radius: 10px;
            border: none;
            padding: 10px 22px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background: linear-gradient(90deg, #48cae4, #2a9d8f);
            box-shadow: 0px 0px 15px rgba(72, 202, 228, 0.4);
            transform: translateY(-2px);
        }
        .chat-bubble-user {
            background: rgba(72, 202, 228, 0.08);
            border-left: 3px solid #48cae4;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .chat-bubble-ai {
            background: rgba(42, 157, 143, 0.08);
            border-left: 3px solid #2a9d8f;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        textarea {
            background: rgba(18, 22, 28, 0.9) !important;
            color: #c9d6df !important;
            border: 1px solid rgba(72, 202, 228, 0.3) !important;
            border-radius: 8px !important;
        }
        .fade-in {
            animation: fadeIn 1.5s ease-in;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        .korvia-logo {
            text-align: center;
            margin-top: 60px;
            color: #48cae4;
            font-size: 36px;
            font-family: 'Poppins';
            text-shadow: 0px 0px 20px rgba(72,202,228,0.5);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% {text-shadow: 0 0 10px #48cae4;}
            50% {text-shadow: 0 0 25px #00eaff;}
            100% {text-shadow: 0 0 10px #48cae4;}
        }
        .small-muted { color: #a5b5c5; font-size:12px; }
    </style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
st.sidebar.title("🧠 Korvia AI Controls")
mode = st.sidebar.radio("Choose Mode", ["Summarizer", "Chat", "Image", "Notes"])
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#4fd3c4;'>✨ Where intelligence meets simplicity.</small>", unsafe_allow_html=True)
st.sidebar.markdown("<small style='color:#a5b5c5;'>Built with ❤️ by Krish</small>", unsafe_allow_html=True)
st.sidebar.markdown("")
st.sidebar.markdown("**Memory:**")
if st.sidebar.button("Export Memory JSON"):
    st.sidebar.download_button("Download memory", json.dumps(memory_data, indent=2), file_name="korvia_memory.json")
if st.sidebar.button("Export Notes JSON"):
    st.sidebar.download_button("Download notes", json.dumps(notes_data, indent=2), file_name="korvia_notes.json")

# ==================== LOADING SCREEN ====================
if "first_load" not in st.session_state:
    st.session_state.first_load = True
    st.markdown("<div class='korvia-logo fade-in'>🧠 Korvia AI<br><small>Activating Intelligence...</small></div>", unsafe_allow_html=True)
    time.sleep(1.2)
    st.session_state.first_load = False
    st.rerun()

# ==================== MAIN AREA ====================
st.markdown("<h1 style='text-align:center;'>💠 Korvia AI</h1>", unsafe_allow_html=True)
st.caption("Your intelligent companion — calm, elegant, and powerful.")

# Helper: call chat model
def ask_model(messages, model="gpt-4o-mini"):
    """
    messages: list of dicts with {"role": "system"/"user"/"assistant", "content": "..."}
    returns assistant text or raises exception
    """
    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content

# ==================== SUMMARIZER MODE ====================
if mode == "Summarizer":
    st.subheader("🧠 Text Summarizer")
    text_input = st.text_area("✍️ Enter text to summarize:", height=250)
    if st.button("⚡ Summarize"):
        if text_input.strip():
            with st.spinner("Korvia is analyzing your text... 💭"):
                try:
                    messages = [
                        {"role": "system", "content": "You are an intelligent AI that summarizes text clearly and concisely."},
                        {"role": "user", "content": f"Summarize this in 5 lines:\n\n{text_input}"}
                    ]
                    summary = ask_model(messages)
                    st.success("✅ Summary generated!")
                    st.markdown(f"<div style='background:rgba(72,202,228,0.08);padding:12px;border-radius:8px;border-left:3px solid #48cae4;'>{summary}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Please enter text.")

# ==================== CHAT MODE ====================
elif mode == "Chat":
    st.subheader("💬 Chat with Korvia AI")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = memory_data.get("history", [])

    # Show last 10 messages
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>🧑 You:</b> {chat['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'><b>🤖 Korvia AI:</b> {chat['content']}</div>", unsafe_allow_html=True)

    user_input = st.text_input("💭 Type your message and press Enter:")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send"):
            if user_input and user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.spinner("Korvia is thinking... 🤖"):
                    try:
                        # construct system + conversation
                        system_msg = {"role":"system","content":"You are Korvia AI, a calm and intelligent assistant created by Krish. Keep a friendly and helpful tone."}
                        messages = [system_msg] + st.session_state.chat_history
                        reply = ask_model(messages)
                        st.session_state.chat_history.append({"role":"assistant", "content": reply})
                        memory_data["history"] = st.session_state.chat_history
                        save_json(MEMORY_FILE, memory_data)
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a message first.")

    with col2:
        if st.button("🧹 Clear Memory"):
            st.session_state.chat_history = []
            if os.path.exists(MEMORY_FILE):
                os.remove(MEMORY_FILE)
            memory_data.clear()
            st.success("🧠 Memory cleared!")

# ==================== IMAGE MODE ====================
elif mode == "Image":
    st.subheader("📷 Image Assist — upload a screenshot or photo")
    st.markdown("Upload an image (photo, screenshot) and ask Korvia to help. You can also use the camera file on mobile to capture a photo.")
    img_file = st.file_uploader("Upload image (png/jpg)", type=["png","jpg","jpeg"], accept_multiple_files=False)
    analyze_caption = st.text_input("Add quick context / question for the image (optional)")
    if img_file:
        # display
        image_bytes = img_file.read()
        st.image(image_bytes, use_column_width=True)
        # Save a temporary copy (optional)
        tmp_path = os.path.join("uploads", img_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)

        # simple base64 preview (for logs or potential sending)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        # NOTE: most chat models cannot inspect raw binary in messages; we pass a note about the uploaded file
        st.markdown("<div class='small-muted'>Image saved locally to uploads/ (not sent to model as pixels). If you'd like image understanding, add context or ask Korvia to request clarifying details.</div>", unsafe_allow_html=True)

        if st.button("🔎 Analyze Image"):
            if analyze_caption.strip():
                prompt = f"User uploaded an image named '{img_file.name}'. User question/context: {analyze_caption}\n\nImportant: I have the filename saved but not pixel-level access in the model. Ask clarifying questions if needed or give best-effort troubleshooting steps based on the user's description."
            else:
                prompt = f"User uploaded an image named '{img_file.name}'. Ask the user to describe what they need from the image and then provide step-by-step help. If possible, propose probable causes and solutions."

            with st.spinner("Korvia analyzing..."):
                try:
                    system_msg = {"role":"system","content":"You are Korvia AI, helpful and calm. When given an image filename, ask clarifying questions and offer step-by-step diagnostics or recommendations. If you cannot see the pixels, ask the user for details."}
                    messages = [system_msg, {"role":"user","content":prompt}]
                    answer = ask_model(messages)
                    st.markdown(f"<div style='background:rgba(72,202,228,0.05);padding:12px;border-radius:8px;border-left:3px solid #48cae4;'>{answer}</div>", unsafe_allow_html=True)
                    # Save to memory history
                    mem_hist = memory_data.get("history", [])
                    mem_hist.append({"role":"user","content":f"Uploaded image: {img_file.name} -- {analyze_caption or '(no caption)'}"})
                    mem_hist.append({"role":"assistant","content":answer})
                    memory_data["history"] = mem_hist
                    save_json(MEMORY_FILE, memory_data)
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("**Tips:**\n- For accurate help, upload a close-up photo with good lighting.\n- Use the caption box to point the exact area or problem in the image.")

# ==================== NOTES MODE ====================
elif mode == "Notes":
    st.subheader("🗂️ Save & View Notes")
    note_title = st.text_input("📝 Note Title")
    note_text = st.text_area("📘 Write your note here:", height=200)

    coln1, coln2 = st.columns(2)
    with coln1:
        if st.button("💾 Save Note"):
            if note_title and note_text:
                notes_data[note_title] = note_text
                save_json(NOTES_FILE, notes_data)
                st.success(f"✅ Note '{note_title}' saved successfully!")
            else:
                st.warning("⚠️ Please enter both title and content.")
    with coln2:
        if st.button("📂 View All Notes"):
            if notes_data:
                for title, content in notes_data.items():
                    st.markdown(f"<div style='background:rgba(72,202,228,0.05);padding:10px;border-radius:8px;border-left:3px solid #48cae4;'><b>📘 {title}</b><br>{content}</div>", unsafe_allow_html=True)
            else:
                st.info("No notes saved yet.")

    st.markdown("---")
    st.markdown("**Export / Import Notes**")
    if st.button("Download Notes JSON"):
        st.download_button("Download notes", json.dumps(notes_data, indent=2), file_name="korvia_notes.json")
    uploaded_notes = st.file_uploader("Upload notes JSON to import", type=["json"])
    if uploaded_notes:
        try:
            imported = json.load(uploaded_notes)
            notes_data.update(imported)
            save_json(NOTES_FILE, notes_data)
            st.success("Imported notes.")
        except Exception as e:
            st.error(f"Failed to import: {e}")

# ==================== FOOTER ====================
st.markdown("<br><hr><center><span style='color:#48cae4;'>⚡ Built by Krish | Korvia AI © 2025</span></center>", unsafe_allow_html=True)
