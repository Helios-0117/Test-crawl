from openai import OpenAI
import os

def chat(message,key):
    client = OpenAI(api_key = key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="gpt-3.5-turbo",
    )

    response = chat_completion.choices[0].message.content
    return response if response else 'Error'

if __name__ == '__main__':
    message = "Hello my name is Helios :-)"
    key = os.getenv('Chat_key',None)

    if message and key:
        reponse = chat(message,key)
        print(reponse)