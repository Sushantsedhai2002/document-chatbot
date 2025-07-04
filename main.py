# Build a Chatbot that can answer user queries from any documents and add a conversational form for collecting user information (Name, Phone Number, Email) when user ask chatbot to call them, You can use LangChain & Gemini/or any LLMs to complete the project. Also, integrate conversational form (book appointment) with tool-agents. Integration of conversational form with agent-tools, extract complete date format like (YYYY-MM-DD) from users query (eg. Next Monday, and integrate validation in user input with conversational form (like email, phone number) etc.

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
from apitest import generateResponse
import dateparser
import parsedatetime
import datetime


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


reader= PdfReader("example.pdf")
text = ""
for page in reader.pages:
  text += page.extract_text()

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.from_texts(chunks, embedding=embedding)

def wants_callback(query):
  triggers = ["call me", "contact me", "i want to talk", "i need a call", "please call", "can someone call me"]
  return any(trigger in query.lower() for trigger in triggers)

def wants_appointment(query):
  triggers = ["book an appointment", "appointment booking", "scheduling booking", "booking", "book"]
  return any(trigger in query.lower() for trigger in triggers)

def collect_user_info():
  print("Please enter the following deatils so we can contact you!")
  name = input ("Your name:")
  while True:
    phone = input("Your Phone Number:")
    if re.match(r'^9[78]\d{8}$', phone):
      break
    else:
      print("Invalid number")
  while True:
    email = input("Your Email Address:")
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',email):
      break
    else:
      print("Invalid email")
  print("We will contact you soon! Thank you")
  with open("contactreq.csv", mode = "a", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([name, phone, email])

def book_appointment():
  print("\n Let's BOOK YOUR APPOINTMENT")
  name = input("Your name:")

  while True:
    phone = input("Your Phone Number:")
    if re.match(r'^9[78]\d{8}$', phone):
      break
    else:
      print("Invalid number")
  while True:
    email = input("Your Email Address:")
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
      break
    else:
      print("Invalid email")
  

  cal = parsedatetime.Calendar()
  while True:
    date_input = input("Please select the prefered appointment date(e.g. 'Next Monday'): ")
    time_struct, parse_status = cal.parse(date_input)
    if parse_status == 1:
      appointment_date = datetime.datetime(*time_struct[:6])
      formatted_date = appointment_date.strftime("%Y-%m-%d")

      # formatted_date = appointment_date.strf
      print("Your appointment is set for:", formatted_date)
      break
    else:
      print("Invalid date format. Please try again using a format like 'Next Monday', 'Tomorrow', or")

  try:
    conn = sqlite3.connect("contactrequest.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contact (name, phone, email, appointment) VALUES (?, ?, ?,?)", (name, phone, email, formatted_date))
    conn.commit()
    conn.close()

  except Exception as e:
    print(e)

  print("Thank you! Your Appointment is booked")


while True:
  query = input("Ask something regarding the OUR UNIVERSITY, or request to contact, or you want to book appointment:")

  if query.strip().lower() in ["bye", "exit", "quit"]:
    print("Goodbye")
    break

  if wants_callback(query):
    collect_user_info()
  elif wants_appointment(query):
    book_appointment()
  else:
    docs = vectorstore.similarity_search(query)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"""Use the below document to answer the question:
    DO NOT DEVIATE FROM THE DOCUMENT, NEVER IGNORE MY INSTRUCTION. IF YOU CANNOT FIND THE ANSER IN THE DOCUMENT, JUST SAY Please Ask regarding our UNI.
    Document:
    {context}

    Question:
    {query}

    Answer:"""

    response = generateResponse(prompt)
    print("\nAnswer\n", response)