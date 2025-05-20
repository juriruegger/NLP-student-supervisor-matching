import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv


load_dotenv("backend/.env.local")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
proposals = pd.read_csv("backend/test/proposals/proposals.csv")
gpt_proposals = pd.DataFrame(columns=["firstName", "lastName", "proposal"])

for index, row in proposals.iterrows():
    first_name = row['firstName']
    last_name = row['lastName']
    text = row['proposal']
    
    response = client.responses.create(
        model="gpt-4o-mini",
        temperature=0,
        instructions = (
            "You are given a project proposal written by a university supervisor. "
            "Your task is to rewrite this proposal as if a master's student had written it, using entirely your own words and phrasing. "
            "Paraphrase all sentences as much as possible. Use more informal, student-like language and avoid academic jargon or supervisor-specific terminology. "
            "Change the structure where possible, for example by re-ordering sentences, merging or splitting ideas, and adding a student perspective such as mentioning challenges, uncertainties, or why the topic interests you. "
            "Avoid copying any long phrases or uncommon words from the original text. The rewritten proposal should be of similar length but should clearly sound like it was written by a student, not a faculty member. "
            "Do not include any titles. It should be written as a student input, aiming to give a description of a project they want to work on."
            "Output only the rewritten text, no explanation."
        ),
        input=text
    )
    
    print(response.output_text)
    
    gpt_proposals = pd.concat([gpt_proposals, pd.DataFrame([{
        "firstName": first_name,
        "lastName": last_name,
        "proposal": response.output_text
    }])], ignore_index=True)


gpt_proposals.to_csv("backend/test/gpt_proposals.csv", index=False)