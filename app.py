import streamlit as st
import sqlite3
import bcrypt
import logging
import os
import requests

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
        [data-baseweb="base-input"]::placeholder {
            color: #666 !important; 
        }
        [data-baseweb="base-input"]:focus {
            border-color: #7d0a91 !important;
            box-shadow: 0 0 5px rgba(125, 10, 145, 0.5) !important;
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

# Database connection
def create_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
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
def convert_file(file):
    url = "https://file.io/"
    response = requests.post(url, files={"file": file})

    if response.status_code == 200:
        return response.json().get("link")
    else:
        st.error("Couldn't upload file :(")
        return None

def show_dashboard():
    st.title(f"Welcome Back, {st.session_state.username}! 💜")

    with st.container():
        st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
        
        st.subheader("What would you like to do today?")

        if st.button("Add a Loved One", key="profile_btn"):
            st.session_state.show_add_family_form = True

        if "show_add_family_form" in st.session_state and st.session_state.show_add_family_form:
            with st.form(key="add_family"):
                name = st.text_input("Name")
                relation = st.text_input("Relation")
                favourite_memory = st.text_input(f"Favourite Memory with {st.session_state.username}")
                
                st.camera_input("Take a picture")
                
                # file uploader
                upload_picture = st.file_uploader("Or upload a picture", type=["jpg", "jpeg", "png"])

                submit_button = st.form_submit_button(label="Add Me!")

                if submit_button:
                    if name and relation and favourite_memory and upload_picture:
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

        if "show_members_form" in st.session_state and st.session_state.show_members_form:
             with st.form(key="add_story"):         
                # file uploader
                upload_picture = st.file_uploader(f"Share Your Day with {st.session_state.username}", type=["jpg", "jpeg", "png"])

                submit_button = st.form_submit_button(label="Generate")

                if submit_button:
                    if name and relation and favourite_memory and upload_picture:
                        st.session_state.add_member_status = (success, message)
                        st.session_state.show_members_form = False
                        st.rerun()
                    else:
                        st.session_state.add_member_status = (False, "Please upload one image")
                        st.session_state.show_members_form = False
                        st.rerun()
        
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