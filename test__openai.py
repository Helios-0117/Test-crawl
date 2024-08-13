from openai import OpenAI
from pprint import pprint
import os

chat_history = dict()

def chat(message,key,userID):
    client = OpenAI(api_key = key)

    # 把使用者的對話訊息加到紀錄中
    if userID in chat_history:
        chat_history[userID].append({"role": "user","content": message})
    else:
        chat_history[userID] = [{"role":"user","content": message}]

    message = message + '' # 可以改變ChatGPT的語氣
    chat_completion = client.chat.completions.create(
        messages = chat_history[userID][:-1] + [{"role": "user", "content": message}],
        model = "gpt-3.5-turbo",
    )

    response = chat_completion.choices[0].message.content

    # 把ChatGPT的對話訊息加到紀錄中
    chat_history[userID].append(
        {
            "role": "system",
            "content": response,
        }
    )
    return response if response else 'Error'

if __name__ == '__main__':
    key = os.getenv('Chat_key',None)

    while True:
        message = input("Enter something: ")
        userID = 'Helios'

        if message == 'Quit':
            print("Chat ended.")
            break

        if message and key:
            reponse = chat(message,key,userID)
            print("ChatGPT say: ", reponse)
        else:
            print("API key error, ", key)

        print("History: ")
        pprint(chat_history)