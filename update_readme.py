import re
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import google.generativeai as genai
#from dotenv import load_dotenv
import random

# Load environment variables from .env file
# load_dotenv()
# Configure the Gemini API
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configure the Gemini API using the environment variable directly
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(
    history=[]
)

important_figures = [
    "Alan Turing",
    "Grace Hopper",
    "Ada Lovelace",
    "Donald Knuth",
    "Tim Berners-Lee",
    "Linus Torvalds",
    "John von Neumann",
    "Claude Shannon",
    "Barbara Liskov",
    "Dennis Ritchie",
    "Ken Thompson",
    "Margaret Hamilton",
    "Vint Cerf",
    "Robert Kahn",
    "James Gosling",
    "Guido van Rossum",
    "Bjarne Stroustrup",
    "Edsger Dijkstra",
    "Douglas Engelbart",
    "John McCarthy",
    "Seymour Cray",
    "Richard Stallman",
    "Steve Jobs",
    "Bill Gates",
    "Elon Musk",
    "Mark Zuckerberg",
    "Marissa Mayer",
    "Sheryl Sandberg",
    "Radia Perlman",
    "Jean Sammet",
    "Elizabeth Feinler",
    "Frances E. Allen",
    "Mary Lou Jepsen",
    "John Backus",
    "Larry Page",
    "Sergey Brin",
    "Jeff Dean",
    "Yukihiro Matsumoto",
    "Niklaus Wirth",
    "Brian Kernighan",
    "Anders Hejlsberg",
    "Tim Paterson",
    "Adele Goldberg",
    "Ivan Sutherland",
    "Andrew Ng",
    "Geoffrey Hinton",
    "Yann LeCun",
    "Fei-Fei Li",
    "Chris Lattner",
    "Hal Abelson",
    "Alan Kay",
    "Peter Norvig",
    "Michael Stonebraker",
    "Rosalind Picard",
    "Cynthia Breazeal",
    "Daphne Koller",
    "Martine Rothblatt",
    "Turing Award Recipients",
    "Computer History Museum Honorees"
]

figure = random.choice(important_figures)

prompt = (
    f"Please create a totally new motivational or inspirational phrase by {figure} that I can use in a Markdown link with the typing SVG format, and include the author and year. "
    "For the author citation, ensure that you only use a single dash (–) before the name, not a hyphen followed by a plus sign (-+), as this will not render correctly in the SVG.\n\n"
    "The 'lines' parameter should contain the phrase, with words separated by '+' to ensure proper URL encoding. "
    "Make sure the 'multiline' attribute is used to split the text into separate lines within the SVG, making it more readable in a README or similar document. "
    "Always adjust the 'width' parameter dynamically to fit the entire length of the phrase, ensuring no part of it is cut off, and make sure the value is never less than 750.\n\n"
    "Ensure that the text and the author citation are placed on separate lines within the 'lines' parameter to keep the formatting clear and readable. "
    "Make sure to enclose the phrase in double quotes for proper display.\n\n"
    "For example:\n"
    "[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=14&pause=1000&color=FFFFFF&multiline=true&width=435&lines=The+five+boxing+wizards+jump+quickly;How+vexingly+quick+daft+zebras+jump)](https://git.io/typing-svg)\n\n"
    "Ensure the phrase is formatted as follows:\n\n"
    "[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=14&pause=1000&color=FFFFFF&multiline=true&width=YOUR_WIDTH&lines=\"Your+motivational+phrase+here\";–+Author+Name,+Year)](https://git.io/typing-svg)\n\n"
    "Your response should only include the Markdown link with the formatted phrase."
)

# Send the prompt to the model
response = chat_session.send_message(prompt)

def update_badges_section(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    badges_section = re.search(r'<!--START_SECTION:badges-->(.*?)<!--END_SECTION:badges-->', content, re.DOTALL)
    
    if badges_section:
        badges = badges_section.group(1).strip().split('\n')
        updated_badges = []
        for badge in badges:
            badge = badge.strip()
            if badge.startswith('![') and '(' in badge and ')' in badge:
                url = badge[badge.find("(")+1:badge.find(")")]
                updated_badges.append(f'<img src="{url}" alt="{url}" />')
            elif badge:
                updated_badges.append(badge)
        updated_badges_content = '\n'.join(updated_badges)
    
        updated_content = content[:badges_section.start(1)] + '\n' + updated_badges_content + '\n' + content[badges_section.end(1):]
        with open(file_path, 'w') as file:
            file.write(updated_content)
            print("Badges Section Updated")

def update_up_time_section(file_path):
    start_date = datetime(2006, 3, 24)
    current_date = datetime.now()
    difference = relativedelta(current_date, start_date)

    years = difference.years
    months = difference.months
    days = difference.days

    up_time_text = f'Up time: {years} years, {months} months and {days} days'

    with open(file_path, 'r') as file:
        content = file.read()

    # Use regex to find the up time section
    up_time_section = re.search(r'<!--UP_TIME_START-->(.*?)<!--UP_TIME_END-->', content, re.DOTALL)

    if up_time_section:
        updated_content = content[:up_time_section.start(1)] + f'\n```text\n{up_time_text}\n```\n' + content[up_time_section.end(1):]

        with open(file_path, 'w') as file:
            file.write(updated_content)
            print("Up Time Section Done")

def update_model_response(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regex to find the model response section
    model_response_section = re.search(r'<!--MODEL_RESPONSE_START-->(.*?)<!--MODEL_RESPONSE_END-->', content, re.DOTALL)

    if model_response_section:
        # Replace the content between the markers with the new response
        updated_content = content[:model_response_section.start(1)] + f'\n{response.text}\n' + content[model_response_section.end(1):]

        with open(file_path, 'w') as file:
            file.write(updated_content)
            print("Model Response Section Done")
    else:
        # If the section is not found, print a message or handle as needed
        print("Model response section not found in the file.")

if __name__ == "__main__":
    file_path = 'README.md'
    update_badges_section(file_path)
    update_up_time_section(file_path)
    update_model_response(file_path)
