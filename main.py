import openai
from fastapi import FastAPI, Form, Request
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def load_input_file():
    try:
        with open("input.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "File not found. Please ensure input.txt is in the same directory"

input_file_content = load_input_file()

chat_log = [
    {
        'role': 'assistant',
        'content': input_file_content
    },
    {
        'role': 'system',
        'content': 'You are Aniket Bakre. You should respond as yourself in the first person based on the details in input.txt. For unrelated questions, respond with "This question is out of my scope or not related to Aniket. Please ask me again."'
    }
]

chat_responses = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses":[]})

@app.post("/", response_class=HTMLResponse)
async def chat(request:Request, user_input: Annotated[str, Form()]):
    try:
        chat_log.append({'role':'user', 'content':user_input})
        chat_responses.append(f"You: {user_input}")
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=chat_log,
            temperature=0.6,
            max_completion_tokens=30
        )
        logging.debug(f"OpenAI API Response: {response}")

        bot_response = response.choices[0].message.content
        
        chat_log.append({'role':'assistant', 'content': bot_response})
        chat_responses.append(f"Aniket: {bot_response}")

    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        bot_response = f"Error: {str(e)}"
        chat_responses.append(f"Error: {bot_response}")

    return templates.TemplateResponse('home.html', {"request":request, "chat_responses": chat_responses})