import streamlit as st
import sqlite3
import bcrypt
import logging
import os
import requests
from groq import Groq
import base64
import pyttsx3
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Create photos directory if it doesn't exist
if not os.path.exists('photos'):
    os.makedirs('photos')

# CSS for styling
st.markdown("""
    <style>
        body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(-45deg, #9667E0, #592da1, #862da1);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        [data-testid="stHeadingWithActionElements"]{
            color: #420a52 !important;
            text-align: center;
            font-style: italic;
        }
        [data-testid="stSidebar"] {
            background-color: #450c5c !important;  
        }
        [data-testid="stRadio"] {
            background-color: #7d0a91 !important;  
            padding: 20px;
            border-radius: 15px;
        }
        [data-testid="stForm"] {
            background-color: #1F193D !important;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        [data-testid="stTextInputRootElement"] {
            background-color: #fff !important; 
            border: none !important;
        }
        [data-testid="InputInstructions"] {
            color: black !important; 
        }
        [data-baseweb="base-input"] {
            background-color: #fff !important;  
            color: black !important;               
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 16px !important;
        }
        [data-baseweb="icon"] {
            color: black !important;
        }
        [data-testid="stMarkdownContainer"] {
            color: white !important;              
        }

        [data-testid="stFormSubmitButton"] > button {
            background-color: #5B2DA1 !important; 
            color: black !important;
        }
        .main {
            background: #F0F0FF;
            padding: 2rem;
            border-radius: 15px;
        }
        .stButton>button {
            width: 100%;
            background-color: #1F193D !important; 
            color: black !important;
            font-size: 18px;
            border-radius: 12px;
            padding: 10px;
            margin-top: 10px;
        }
        h1, h2, h3 {
            color: #fff !important;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 8px;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 2rem;
        }
        [data-baseweb="input"] {
            color: black !important;
        }
        [data-baseweb="base-input"] input {
            color: black !important;
        }
        input, textarea {
            color: black !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .story-container {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .story-text {
            font-size: 18px;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "signup_message" not in st.session_state:
    st.session_state.signup_message = None
if "add_member_status" not in st.session_state:
    st.session_state.add_member_status = None
if "show_add_family_form" not in st.session_state:
    st.session_state.show_add_family_form = False
if "show_members_form" not in st.session_state:
    st.session_state.show_members_form = False
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

# Groq client initialization
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def text_to_speech(text):
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            temp_path = temp_audio.name
        
        # Initialize the TTS engine
        engine = pyttsx3.init()
        
        # Optional: Adjust voice properties
        # engine.setProperty('rate', 150)  # Speed
        # engine.setProperty('volume', 0.9)  # Volume (0 to 1)
        
        # Get available voices and set a more natural one if available
        voices = engine.getProperty('voices')
        if len(voices) > 0:
            # Try to find a female voice for more warmth
            female_voices = [v for v in voices if 'female' in v.name.lower()]
            if female_voices:
                engine.setProperty('voice', female_voices[0].id)
        
        # Save to the temporary file
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        
        # Read the file and encode to base64
        with open(temp_path, 'rb') as f:
            audio_bytes = f.read()
        
        # Remove the temporary file
        os.unlink(temp_path)
        
        # Encode to base64 for embedding in HTML
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio controls autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        
        return True, audio_html
    
    except Exception as e:
        logging.error(f"Error in text_to_speech: {str(e)}")
        return False, str(e)

def get_memory_response(name, relation, memory):
    messages = [
        {"role": "assistant", "content": "You're a friendly assistant helping an elder with Alzheimers remember people in their life. Given the format of someone from their life: name| their relation to the elder | their favourite memory, help the elder remember who they are. Be specific but keep it around 5 sentences. Be more confident in your answer"},
        {"role": "user", "content": f"{name}|{relation}|{memory}"}
    ]
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        max_tokens=300
    )
    return completion.choices[0].message.content.strip()

def generate_story(people, image_data):
    try:
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create the data URL
        data_url = f"data:image/jpeg;base64,{base64_image}"
        
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Pretend you are {people}, tell the user a story what you did throughout the day. Pretend you are telling an elder loved one who has alzheiemer what you did through your day based on the image. Keep it under 10 sentences."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )
        return True, completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating story: {str(e)}")
        return False, f"Error generating story: {str(e)}"

# Database connection
def create_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, relation TEXT, favourite_memory TEXT)")
    conn.commit()
    return conn, cursor

# User creation
def create_user(username, password):
    conn, cursor = create_connection()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True, "Account created successfully! Please log in."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists."

# Authentication
def authenticate_user(username, password):
    conn, cursor = create_connection()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
        return True
    return False

# Navigation functions
def go_to_login():
    st.session_state.page = "login"
    # Clear audio and story when logging out
    st.session_state.generated_story = None
    st.session_state.audio_file = None

def go_to_signup():
    st.session_state.page = "signup"

def go_to_dashboard():
    st.session_state.page = "dashboard"

# Login page
def show_login():
    st.title("[ Memora :purple_heart: ]")
    st.subheader(" Don't let Alzheimers put a time limit on :rainbow[Memories] ")
    
    # Successful signup message
    if st.session_state.signup_message:
        st.success(st.session_state.signup_message)
        st.session_state.signup_message = None  
    
    with st.form(key="login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button(label="Login")
    
    if submit_button:
        logging.debug("Login form submitted")
        if username and password:
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success(f"✨ Welcome back, {username}!")
                go_to_dashboard()
                logging.debug("Navigating to dashboard")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
        else:
            st.warning("⚠ Please fill in all fields.")
    
    st.write("Don't have an account?")
    if st.button("Sign Up Here"):
        go_to_signup()
        st.rerun()

# Signup page
def show_signup():
    st.title("[ Memora :purple_heart: ]")
    st.subheader(" Don't let Alzheimers put a time limit on :rainbow[Memories] ")    
    
    with st.form(key="signup"):
        new_username = st.text_input("Choose a Username", key="signup_username")
        new_password = st.text_input("Choose a Password", type="password", key="signup_password")
        submit_button = st.form_submit_button(label="Sign Up")
    
    if submit_button:
        logging.debug("Signup form submitted")
        if new_username and new_password:
            success, message = create_user(new_username, new_password)
            if success:
                st.session_state.signup_message = message
                go_to_login()
                logging.debug("Navigating to login")
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("⚠ Please fill in all fields.")
    
    st.write("Already have an account?")
    if st.button("Login Here"):
        go_to_login()
        st.rerun()

# Create member function
def create_member(name, relation, favourite_memory):
    conn, cursor = create_connection()
    try:
        cursor.execute("INSERT INTO members (name, relation, favourite_memory) VALUES (?, ?, ?)", (name, relation, favourite_memory))
        conn.commit()
        conn.close()
        return True, "Member added successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Error adding member."

def show_dashboard():
    st.title(f"Welcome Back, {st.session_state.username}! 💜")

    with st.container():
        st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
        
        st.subheader("What would you like to do today?")

        if st.button("Add a Loved One", key="profile_btn"):
            st.session_state.show_add_family_form = True

        if st.session_state.show_add_family_form:
            with st.form(key="add_family"):
                name = st.text_input("Name")
                relation = st.text_input("Relation")
                favourite_memory = st.text_input(f"Favourite Memory with {st.session_state.username}")
                
                camera_pic = st.camera_input("Take a picture")
                
                # file uploader
                upload_picture = st.file_uploader("Or upload a picture", type=["jpg", "jpeg", "png"])

                submit_button = st.form_submit_button(label="Add Me!")

                if submit_button:
                    if name and relation and favourite_memory and (upload_picture or camera_pic):
                        success, message = create_member(name, relation, favourite_memory)
                        st.session_state.add_member_status = (success, message)
                        st.session_state.show_add_family_form = False
                        st.rerun()
                    else:
                        st.session_state.add_member_status = (False, "Please fill in all fields and upload an image.")
                        st.session_state.show_add_family_form = False
                        st.rerun()
        
        if st.session_state.add_member_status:
            success, message = st.session_state.add_member_status
            if success:
                st.success(message)
            else:
                st.error(message)
            st.session_state.add_member_status = None
        
        if st.button("What is my family up to?", key="note_btn"):
            st.session_state.show_members_form = True

        if st.session_state.show_members_form:
            with st.form(key="add_story"):         
                # Camera input
                camera_pic = st.camera_input(f"Take a picture to share with {st.session_state.username}")
                
                # File uploader
                upload_picture = st.file_uploader(f"Or upload a picture to share with {st.session_state.username}", 
                                                 type=["jpg", "jpeg", "png"])

                submit_button = st.form_submit_button(label="Generate Story")

                if submit_button:
                    image_file = camera_pic if camera_pic is not None else upload_picture
                    if image_file is not None:
                        # Get image data
                        image_data = image_file.getvalue()
                        
                        # Generate story directly from image data
                        success, story = generate_story(st.session_state.username, image_data)
                        
                        if success:
                            st.session_state.generated_story = story
                            # Clear previous audio when generating new story
                            st.session_state.audio_file = None
                        else:
                            st.session_state.add_member_status = (False, story)  # story contains error message
                        
                        st.session_state.show_members_form = False
                        st.rerun()
                    else:
                        st.session_state.add_member_status = (False, "Please take or upload an image")
                        st.session_state.show_members_form = False
                        st.rerun()
        
        # Display generated story if available
        if st.session_state.generated_story:
            st.markdown('<div class="story-container">', unsafe_allow_html=True)
            st.subheader("Your family member's day:")
            st.markdown(f'<div class="story-text">{st.session_state.generated_story}</div>', 
                        unsafe_allow_html=True)
            
            # Text-to-speech button
            if st.button("Read Story Aloud"):
                success, audio_html = text_to_speech(st.session_state.generated_story)
                if success:
                    st.session_state.audio_file = audio_html
                else:
                    st.error(f"Could not generate audio: {audio_html}")
                st.rerun()
            
            # Display audio player if available
            if st.session_state.audio_file:
                st.markdown(st.session_state.audio_file, unsafe_allow_html=True)
            
            # Add a button to clear the story
            if st.button("Clear Story"):
                st.session_state.generated_story = None
                st.session_state.audio_file = None
                st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.add_member_status:
            success, message = st.session_state.add_member_status
            if success:
                st.success(message)
            else:
                st.error(message)
            st.session_state.add_member_status = None

    # Logout button
    if st.button("Logout", key="logout_btn"):
        del st.session_state.username
        st.session_state.page = "login"
        # Clear audio and story when logging out
        st.session_state.generated_story = None
        st.session_state.audio_file = None
        logging.debug("Logging out and navigating to login")
        st.rerun()

def main():
    logging.debug(f"Current page: {st.session_state.page}")
    if st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "signup":
        show_signup()
    elif st.session_state.page == "dashboard":
        show_dashboard()

if __name__ == "__main__":
    main()