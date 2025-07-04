from google import genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load your GOOGLE_API_KEY from .env

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generateResponse(userQuery):
  response = client.models.generate_content(
      model="gemini-2.0-flash", contents=userQuery
  )
  return (response.text)


