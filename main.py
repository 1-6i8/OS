import time
import json
import sys
import ollama
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

# Get API keys for cloud AI...
load_dotenv(Path(__file__).resolve().parent / ".env")

gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

gemini_client = None
groq_client = None

if gemini_key:
    gemini_client = OpenAI(
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

if groq_key:
    groq_client = Groq(api_key=groq_key)

#ข้อมูล AI
def validateAi(ai):
    required_fields = {"id", "name", "description","type" ,"model"}

    if not isinstance(ai, dict):
        raise ValueError("Each AI entry must be a JSON object")

    missingfields = required_fields - ai.keys()

    if missingfields:
        raise ValueError(f"Missing fields: {missingfields}")

    for field in required_fields:
        if not isinstance(ai[field], str) or not ai[field].strip():
            raise ValueError(f"Invalid or empty field: {field}")

#Lacal ai method
def chatWithLocalAi(ai, message):
    try:
        response = ollama.chat(
            model=ai["model"],
            messages=[
                {"role": "user", "content": message}
            ]
        )

        return response['message']['content']
    except Exception as e:
        print(f"\nChat error: {e}")
        return None

#Cloud ai method
def chatWithCloudAi(ai, message):
    try:
        if ai["id"] == "groq":
            if groq_client is None:
                print("Groq API key is missing.")
                return None

            response = groq_client.chat.completions.create(
                model=ai["model"],
                messages=[
                    {"role": "user", "content": message}
                ],
                timeout=180
            )

        elif ai["id"] == "gemini":
            if gemini_client is None:
                print("Gemini API key is missing.")
                return None

            response = gemini_client.chat.completions.create(
                model=ai["model"],
                messages=[
                    {"role": "user", "content": message}
                ],
                timeout=180
            )

        else:
            print(f"Unsupported Cloud AI: {ai['id']}")
            return None

        return response.choices[0].message.content

    except Exception as e:
        print(f"Cloud AI error: {type(e).__name__}: {e}")
        return None

#Chat with Ai
def chatWithAi(ai, message):
    start = time.perf_counter()
    if not ai.get("model"):
        print("This AI has not been configured yet.")
        return None
    elif ai.get("type") == "cloud":
        answer = chatWithCloudAi(ai, message)
    elif ai.get("type") == "local":
        answer = chatWithLocalAi(ai, message)
    else:
        print(f"Unsupported AI type: {ai.get('type')}")
        return None

    if answer is not None:
     end = time.perf_counter()
     print(f"\n[Response time : {end - start:.3f} s]")
     print(f"\033[1;36m\n{ai['name']} : \033[0m{answer}")


#ค้ณหา AI edit
def loadRegistry():
    with open("aiRegistry.json", "r", encoding="utf-8") as file:
        registry = json.load(file)

    if not isinstance(registry, list):
        raise ValueError("Registry must be a JSON array")

    seen_ids = set()

    for ai in registry:
        validateAi(ai)

        if ai["id"] in seen_ids:
            raise ValueError(f"Duplicate AI ID: {ai['id']}")

        seen_ids.add(ai["id"])

    return registry

#แสดงหน้า start
def startMenu():
    print("==============================================")
    print("===                                        ===")
    print("===      Welcome to Rasberry pi Project    ===")
    print("===                 AI HUB                 ===")
    print("===                                        ===")
    print("===             Sec 04 Group 5             ===")
    print("===                                        ===")
    print("==============================================\n")

#แสดง หน้า menu
def menu():
    print("\033[1;32m\nCommands list.\033[0m")
    print("/1 change model AI.")
    print("/2 see detail of AI.")
    print("/3 list of AI.")
    print("/4 menu.")
    print("/5 clear screen")
    print("/6 exit program.\n")

#เปลี่ยน ai
def changeModel():
    print("Enter number (1-4) : 1")
    listAi()
    while(True):
        userInput = input("\nSelect AI: ")

        try:
            index = int(userInput) - 1
            if 0 <= index < len(registry):
                return registry[index]
        except ValueError:
            print("Invalid AI selection.Please enter (1-4).")
            pass

#input
def systemInput(ai):
    while True:
        #print("\033[90mEnter your message\033[0m")
        userInput = input("\033[31mUser\033[0m: ")

        if userInput == "/1":
            newAi = changeModel()
            if newAi is not None:
                ai = newAi
                print(f"Changed AI to {ai['name']}\n")

        elif userInput == "/2":
            detailAi(ai)
        elif userInput == "/3":
            listAi()
        elif userInput == "/4":
            menu()
        elif userInput == "/5":
            os.system("clear")
            print("Clear screen is succeed.")
        elif userInput == "/6":
            print("exit...")
            break

        elif userInput:
            chatWithAi(ai, userInput)

#แสดงลิส
def listAi():
    for i, ai in enumerate(registry, start=1):
        print(f"{i}. {ai['name']} ")

#แสดง detail
def detailAi(ai):
    print(f"\nModel : {ai['model']}")
    print(f"Type  : {ai['type']}")
    print(f"detail: {ai['description']}\n")

#main
if __name__ == "__main__":
    os.system("clear")
    registry = loadRegistry()
    startMenu()

    model = changeModel()
    menu()
    systemInput(model)
