import streamlit as st
import hashlib
import sqlite3
import numpy as np
from keras.models import load_model
from PIL import Image


import base64


st.set_page_config(
    page_title="Fake Currency Detection",
    page_icon=":smiley:",
    layout="wide",
    initial_sidebar_state="expanded",
)

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('bbg.jpg')  


st.sidebar.title("Fake Currency Detection")
st.sidebar.image("s2.jpg")

# Create a connection to the database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create a table to store user information
c.execute('''CREATE TABLE IF NOT EXISTS users (username text, password text)''')

def fake_currency(imgg):
    IMAGE_SIZE = 64
    model = load_model('currency_modell.h5')
    img = Image.open(imgg)

    img = img.resize((IMAGE_SIZE,IMAGE_SIZE))
    img = np.array(img)

    img = img.reshape(1,IMAGE_SIZE,IMAGE_SIZE,3)

    img = img.astype('float32')
    img = img / 255.0
    prediction = model.predict(img)
    Fake=np.argmax(prediction)

    return Fake

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def signup():
    st.write("Create a new account")
    username = st.text_input("Enter a username")
    password = st.text_input("Enter a password", type="password")
    confirm_password = st.text_input("Confirm your password", type="password")
    
    
    signup_button = st.button("SignUp")
    st.info("Login if already have account")
    
    if signup_button:
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        st.success("You have successfully created an account. Go to login page")

def login():
    st.write("Login to your account")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")
    login_button = st.button("Login")
    
    if login_button:
        hashed_password = hash_password(password)
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = c.fetchone()
        if user:
            st.success("You have successfully logged in")
            session_id = user[0] # Use the username as the session ID
            st.session_state['session_id'] = session_id
        
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")
   
def get_image():
    img = st.file_uploader("Upload Image", type=["png","jpg","svg","jpeg"])
    if img:
        st.image(img, width=500)  
        result = fake_currency(img)
        
        
        if result == 0:
            st.markdown('<p style="color:lime; font-size: 30px;font-weight:bold">No Fake Currency detected</p>', unsafe_allow_html=True)
        elif result == 1:
            st.markdown('<p style="color:red; font-size: 30px;font-weight:bold">Fake Currency detected</p>', unsafe_allow_html=True)

def logout():
    st.session_state.pop('session_id', None)
    st.info("You have been logged out") 
    st.experimental_rerun() 
    
    
    
    
menu1 = ["Signup","Login"]
menu2 = ["Upload Image", "About", "Logout"]
if 'session_id' not in st.session_state:
    choice = st.sidebar.selectbox("Select an option", menu1)
else:
    choice = st.sidebar.selectbox("Select an option", menu2)
    
####    
st.sidebar.text("Created By : EBUKA")


if choice == "Login":
    login()
elif choice == "Signup":
    signup()
elif choice == "Logout":
    logout()
elif choice == "Upload Image":
    get_image()
elif choice == "About":
    about()
else:
    st.write("Welcome back, " + st.session_state['session_id'])
