A conversational AI chatbot that answers user queries from uploaded documents (PDFs) and handles appointment bookings/callbacks. Built with LangChain, Gemini/LLMs, and Python.

Features::

Document-based Q&A: Extract answers from PDFs using RAG (Retrieval-Augmented Generation).

Conversational Forms:

Callback Request: Collects user info (Name, Phone, Email) with validation.

Appointment Booking: Parses natural language dates (e.g., "Next Monday") into YYYY-MM-DD.

Tool-Agent Integration: Uses LangChain Agents for dynamic form handling.

Data Storage: Saves user data to SQLite (appointments) and CSV (callbacks).

now image also !!!!!!!
