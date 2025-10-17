import os
import google.generativeai as genai
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
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
    model_name="gemini-1.5-flash",
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
    f"Please provide a motivational or inspirational quote by {figure} that I can use in a Markdown link with the typing SVG format, and include the author and year. "
    "For the author citation, ensure that you only use a single dash (–) before the name, not a hyphen followed by a plus sign (-+), as this will not render correctly in the SVG.\n\n"
    "The 'lines' parameter should contain the quote, with words separated by '+' to ensure proper URL encoding. "
    "Make sure the 'multiline' attribute is used to split the text into separate lines within the SVG, making it more readable in a README or similar document. "
    "Always adjust the 'width' parameter dynamically to fit the entire length of the quote, ensuring no part of it is cut off, and make sure the value is never less than 750.\n\n"
    "Ensure that the text and the author citation are placed on separate lines within the 'lines' parameter to keep the formatting clear and readable. "
    "Make sure to enclose the quote in double quotes for proper display.\n\n"
    "For example:\n"
    "[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=14&pause=1000&color=FFFFFF&multiline=true&width=435&lines=The+five+boxing+wizards+jump+quickly;How+vexingly+quick+daft+zebras+jump)](https://git.io/typing-svg)\n\n"
    "Ensure the quote is formatted as follows:\n\n"
    "[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=14&pause=1000&color=FFFFFF&multiline=true&width=YOUR_WIDTH&lines=\"Your+motivational+quote+here\";–+Author+Name,+Year)](https://git.io/typing-svg)\n\n"
    "Your response should only include the Markdown link with the formatted phrase."
)

# Send the prompt to the model
response = chat_session.send_message(prompt)

# Display the response
print(response.text)

# Save the quote to a file for future reference
with open("RESPONSE.md", "a") as file:
    file.write(f"{response.text}\n")
