from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Rahul Kashyap"
        reader = PdfReader("Rahul Kashyap-DS-Resume.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("rk_summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."

        # Safety and content policy guardrails to prevent disallowed content
        system_prompt += (
            "\n\n## Safety and Content Policy (Strictly Enforce)\n"
            "You must not ask for, generate, or engage with any content that is sexual, harassing, abusive, hateful, violent, extremist, self-harm related, or otherwise harmful.\n"
            "Explicitly refuse and redirect if the user requests or steers the conversation toward any of the following:\n"
            "- Sexual content of any kind, including erotic content, sexual acts, fetish content, sexual content involving minors, incest, or sexual violence.\n"
            "- Harassment, bullying, threats, or targeted abuse; slurs or demeaning epithets; encouragement of violence or discrimination toward protected classes or individuals.\n"
            "- Hate or extremist content, praise or support for extremist ideologies or organizations.\n"
            "- Graphic violence, gore, or instructions to plan or commit violence or harm.\n"
            "- Self-harm or suicide instructions, encouragement, or facilitation.\n"
            "- Illegal activities guidance: instructions to commit crimes, procure illegal goods, or evade law enforcement.\n"
            "- Weapons construction or procurement instructions (e.g., bombs, firearms, 3D-printed weapons).\n"
            "- Malware creation, hacking, unauthorized access, or exploitation content.\n"
            "- Sensitive personal data requests or exchanges (PII) beyond what is explicitly and safely provided by the user for contact purposes.\n"
            "- Medical, legal, or financial advice presented as professional instruction; if asked, provide general, non-specific information with a clear disclaimer to consult a qualified professional.\n"
            "- Any content involving minors in a sexual or exploitative context (always strictly refuse).\n\n"
            "If the user requests disallowed content:\n"
            "1) Briefly refuse (one or two sentences),\n"
            "2) Provide a safe, professional alternative or offer to discuss {self.name}'s experience, projects, or services,\n"
            "3) Do not call tools with disallowed content.\n"
            "Stay polite and redirect the conversation to appropriate professional topics."
        )
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        max_calls = 15
        call_count = 0
        while not done:
            if call_count >= max_calls:
                return (
                    "Let's pause here to avoid an excessively long automated loop. "
                    "Please refine your request or ask a new question."
                )
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            call_count += 1
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(
        fn=me.chat,
        type="messages",
        title=f"Chat with {me.name}",
        description=(
            "Ask about Rahul's background, projects, and experience. "
            "To reach out directly, send: \n"
            "'Need to contact Rahul Kashyap, my email id: <your email>, note: <optional note>'"
        ),
        examples=[
            "What are your strongest data science skills?",
            "Can you summarize your experience with machine learning projects?",
            "Tell me about a challenging project and how you solved it.",
            "Which tools and frameworks do you use most often?",
            "How can your experience help my team/company?",
            "Need to contact Rahul Kashyap, my email id: your@email.com, note: Interested in a quick intro call"
        ],
        theme=gr.themes.Soft(),
        textbox=gr.Textbox(placeholder="Type a question or use the contact template above...")
    ).launch()
    