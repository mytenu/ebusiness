import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Define scope
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
@st.cache_resource
def init_connection():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE
    )
    client = gspread.authorize(credentials)
    return client

# Initialize connection
CLIENT = init_connection()
SHEET = CLIENT.open("users101").sheet1

# ===== FUNCTIONS =====
def register_user(username, password, First_name, last_name, DoB, contact, email):
    users = SHEET.get_all_records()
    if any(user["username"] == username for user in users):
        return False, "Username already exists!"
    SHEET.append_row([First_name, last_name, DoB, contact, email, password, username])
    return True, "Registration successful!"

def login_user(username, password):
    users = SHEET.get_all_records()
    for user in users:
        if user["username"] == username and str(user["password"]) == str(password):
            return True
    return False

# ===== PRODUCT DISPLAY =====
def show_products():
    st.markdown("<h2 style='text-align: center;'>🛍️ Afa Exclusive Collection</h2>", unsafe_allow_html=True)

    search_query = st.text_input("🔍 Search products", "").lower()

    product_list = [
        {"name": "Italian Shirt", "price": 250, "image": "images/shirt1.jpeg"},
        {"name": "Versace Shirt", "price": 310, "image": "images/shirt2.jpeg"},
        {"name": "Versace Trousers", "price": 150, "image": "images/trouser1.jpeg"},
        {"name": "Italian Trousers 2", "price": 180, "image": "images/trouser2.jpeg"},
    ]

    if search_query:
        product_list = [p for p in product_list if search_query in p["name"].lower()]

    cols = st.columns(4)
    for i, product in enumerate(product_list):
        with cols[i % 4]:
            if os.path.exists(product["image"]):
                st.image(product["image"], width=180)
            else:
                st.write("Image not found")
            st.write(f"**{product['name']}**")
            st.write(f" Ghs{product['price']}")
            if st.button(f"Add to Cart", key=f"add_{i}"):
                st.session_state.cart.append(product)
                st.rerun()

# ===== CART PAGE =====
def show_cart():
    st.markdown("<h2 style='text-align:center;'>🛒 Your Cart</h2>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        st.session_state.page = "dashboard"
        st.rerun()
        return

    total = 0
    for i, item in enumerate(st.session_state.cart):
        st.write(f"**{item['name']}** - Ghs{item['price']}")
        total += item['price']
        if st.button(f"❌ Remove {item['name']}", key=f"remove_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    st.markdown("---")
    st.subheader(f"Total: Ghs{total}")

    if st.button("Proceed to Checkout"):
        st.session_state.page = "checkout"
        st.rerun()

# ===== CHECKOUT PAGE =====
def checkout_page():
    st.markdown("<h2 style='text-align:center;'>💳 Checkout</h2>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("Your cart is empty. Add some products first.")
        st.session_state.page = "dashboard"
        st.rerun()
        return

    payment_method = st.radio("Select Payment Method", ["PayPal", "Visa/Mastercard"])
    st.write(f"You selected: **{payment_method}**")

    if st.button("Confirm Payment"):
        st.success(f"Payment successful via {payment_method}! 🎉")
        st.session_state.cart.clear()
        # Show button to shop more products after payment success
        if st.button("🛍️ Shop More Products"):
            st.session_state.page = "dashboard"
            st.rerun()

# ===== LOGIN/REGISTER PAGE =====
def show_login_register():
    st.markdown("<h1 style='text-align:center;'>Welcome to Afa E-Business Hub</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])

    with tab1:
        with st.form("login_form"):
            login_user_input = st.text_input("Username", key="login_user")
            login_pass_input = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login_user(login_user_input, int(login_pass_input)):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user_input
                    st.session_state.page = "cart"  # Redirect to cart after login
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("register_form"):
            reg_user_input = st.text_input("Username", key="reg_user")
            reg_pass_input = st.text_input("Password", type="password", key="reg_pass")
            reg_passre_input = st.text_input("Repeat Password", type="password", key="reg_pass_re")
            reg_first_input = st.text_input("First name", key="reg_first")
            reg_last_input = st.text_input("Last name", key="reg_last")
            reg_email_input = st.text_input("Email", key="reg_email")
            reg_dob_input = st.text_input("Date of birth", key="reg_dob")
            reg_contact_input = st.text_input("Contact", key="reg_contact")
            submitted = st.form_submit_button("Register")
            if submitted:
                if reg_pass_input != reg_passre_input:
                    st.error("Passwords do not match")
                else:
                    success, msg = register_user(
                        reg_user_input, reg_pass_input, reg_first_input, reg_last_input,
                        reg_dob_input, reg_contact_input, reg_email_input
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# ===== STREAMLIT APP SETUP =====
st.set_page_config(page_title="E-Business App", page_icon="🛍️", layout="wide")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "cart" not in st.session_state:
    st.session_state.cart = []

# ===== TOP BAR =====
top_cols = st.columns([4, 1, 1])
with top_cols[0]:
    if st.session_state.logged_in:
        st.markdown(f"**👤 {st.session_state.username}**")
    else:
        st.markdown("**👤 Guest**")

with top_cols[1]:
    if st.button(f"🛒 {len(st.session_state.cart)}"):
        if st.session_state.logged_in:
            st.session_state.page = "cart"
        else:
            st.session_state.page = "login"
        st.rerun()

with top_cols[2]:
    if st.session_state.logged_in:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.cart = []
            st.session_state.page = "dashboard"
            st.rerun()

st.markdown("---")

# ===== PAGE ROUTING =====
if st.session_state.page == "dashboard":
    show_products()

elif st.session_state.page == "cart":
    show_cart()

elif st.session_state.page == "checkout":
    checkout_page()

elif st.session_state.page == "login":
    show_login_register()
