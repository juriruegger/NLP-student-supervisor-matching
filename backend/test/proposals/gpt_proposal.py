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
        model="gpt-4o",
        instructions = (
            "You will receive a research-project description originally written by a supervisor at a university.\n"
            "Rewrite it to sound like a master’s student pitching their own thesis idea.\n"
            "Write in first-person singular, using conversational and concise sentences. Contractions are welcome.\n"
            "Avoid formal academic jargon or supervisor-specific terminology.\n"
            "Summarise the main research question and planned approach but in an 'I want to', 'I would like to' or similar format.\n"
            "Feel free to reorder, merge, or split ideas for natural flow, while keeping the overall length similar to the original.\n"
            "Do not add section headings, citations, bullet points, lists, or technical footnotes.\n"
            "Paraphrase fully and avoid copying uncommon phrases or terms.\n"
            "Write one continuous paragraph, or two short paragraphs at most.\n"
            "Return only the rewritten proposal text with no explanation and no title."
            "Example: The current student-supervisor matching process at ITU is time-consuming, inefficient and unreliable in ensuring optimal matches for students and potential supervisors. This master thesis seeks to improve the current implementation by iterating on an already developed prototype, using BERT to match supervisors’ abstracts to a self-written text by the student. \n"
            "To guide the aforementioned iterative development, a survey will be distributed to the students indicating the major pain points they face in this process and to validate whether the issue of finding a compatible supervisor is a widespread problem.\n"
            "The most critical and challenging aspect of this project is evaluating the quality of the matches produced by the system. Since no objective function exists for determining the \"correct\" match, a proxy evaluation method must be developed. Potential approaches include:\n"
            "Asking students to rate the relevance of their recommended matches and refining the system based on their feedback.\n"
            "Measuring how well the model predicts a supervisor when students write texts specifically tailored for them.\n"
            "Assessing whether the system correctly identifies supervisors with singular expertise in a given area as the top recommendation for students interested in that area. If a professor is the clear authority on a niche topic, they should consistently rank as the best match for students focusing on that topic.\n"
            "Each of these evaluation methods has significant limitations, requiring further research into similar technical challenges and a clearer definition of what constitutes ‘the best match’ before settling on a final evaluation strategy.\n"
            "I propose the following problem statement:\n"
            "How can students be matched with supervisors based on their previous academic work and research interests to ensure relevance while reducing the time and effort required from students?\n"
            "While this research focuses on ITU, the findings could be applicable to other universities facing similar challenges in student-supervisor matching."
        ),
        input=text
    )

    print(response.output_text)
        
    gpt_proposals = pd.concat([gpt_proposals, pd.DataFrame([{
        "firstName": first_name,
        "lastName": last_name,
        "proposal": response.output_text
    }])], ignore_index=True)


gpt_proposals.to_csv("backend/test/proposals/gpt_proposals.csv", index=False)