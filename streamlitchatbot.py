import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import google.generativeai as genai
import os
import csv
import sqlite3
import re
import parsedatetime
import datetime
from apitest import generateResponse

# Load environment
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load and process PDF
# @st.cache_data
def load_pdf_and_create_vectorstore():
    reader = PdfReader("example.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return FAISS.from_texts(chunks, embedding=embedding)

vectorstore = load_pdf_and_create_vectorstore()

# Title
st.title("📚 University Chatbot")

# User Input
query = st.text_input("Ask something about the university, or type 'call me' / 'book an appointment'")

def wants_callback(query):
    triggers = ["call me", "contact me", "i want to talk", "i need a call", "please call"]
    return any(trigger in query.lower() for trigger in triggers)

def wants_appointment(query):
    triggers = ["book an appointment", "book","appointment", "booking", "schedule"]
    return any(trigger in query.lower() for trigger in triggers)

# Contact Form
def collect_user_info():
    with st.form("contact_form"):
        st.subheader("📞 Contact Request Form")
        name = st.text_input("Your Name")
        phone = st.text_input("Phone Number (e.g. 98XXXXXXXX)")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not re.match(r'^9[78]\d{8}$', phone):
                st.error("Invalid phone number format")
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.error("Invalid email format")
            else:
                with open("contactreq.csv", mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([name, phone, email])
                st.success("We will contact you soon!")

# Appointment Booking
def book_appointment():
    with st.form("appointment_form"):
        st.subheader("📅 Book an Appointment")
        name = st.text_input("Your Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        date_input = st.text_input("Preferred Date (e.g. 'Next Monday')")
        submitted = st.form_submit_button("Book Appointment")

        if submitted:
            if not re.match(r'^9[78]\d{8}$', phone):
                st.error("Invalid phone number")
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.error("Invalid email")
            else:
                cal = parsedatetime.Calendar()
                time_struct, parse_status = cal.parse(date_input)
                if parse_status == 1:
                    appointment_date = datetime.datetime(*time_struct[:6])
                    formatted_date = appointment_date.strftime("%Y-%m-%d")
                    try:
                        conn = sqlite3.connect("contactrequest.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO contact (name, phone, email, appointment) VALUES (?, ?, ?, ?)",
                                       (name, phone, email, formatted_date))
                        conn.commit()
                        conn.close()
                        st.success(f"Appointment booked for {formatted_date}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Could not parse the date. Try phrases like 'Next Monday' or 'Tomorrow'.")


if query:
    if wants_callback(query):
        collect_user_info()
    elif wants_appointment(query):
        book_appointment()
    else:
        docs = vectorstore.similarity_search(query)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"""Use the below document to answer the question:
        DO NOT DEVIATE FROM THE DOCUMENT. If the answer isn't found, just say 'Please Ask regarding our UNI'.

        Document:
        {context}

        Question:
        {query}

        Answer:"""
        response = generateResponse(prompt)
        st.markdown("### 🤖 Chatbot Answer")
        st.write(response)
