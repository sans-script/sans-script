import re
import os
import subprocess
import json
import urllib.request
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

def get_github_activity(username='sans-script'):
    """Get recent GitHub activity from the GitHub API"""
    try:
        url = f'https://api.github.com/users/{username}/events?per_page=100'
        req = urllib.request.Request(url)
        
        # Recommended headers from GitHub API docs
        req.add_header('Accept', 'application/vnd.github+json')
        req.add_header('X-GitHub-Api-Version', '2022-11-28')
        req.add_header('User-Agent', 'sans-script-readme-updater')
        
        # Add token if available (increases rate limit and may show private events)
        github_token = os.environ.get('GH_TOKEN') or os.environ.get('ACCESS_TOKEN')
        if github_token:
            req.add_header('Authorization', f'Bearer {github_token}')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            events = json.loads(response.read().decode())
        
        # Analyze recent activity (last 30 days, up to 300 events)
        repos = set()
        event_types = []
        commits_count = 0
        languages_in_commits = set()
        
        for event in events[:50]:  # Analyze last 50 events
            event_type = event.get('type', '')
            repo_name = event.get('repo', {}).get('name', '')
            
            # Collect all active repositories
            if repo_name:
                repos.add(repo_name)
            
            if event_type == 'PushEvent':
                commits_count += len(event.get('payload', {}).get('commits', []))
                event_types.append('coding')
            elif event_type == 'PullRequestEvent':
                event_types.append('PR')
            elif event_type == 'IssuesEvent':
                event_types.append('issue')
            elif event_type == 'CreateEvent':
                event_types.append('created')
            elif event_type == 'WatchEvent':
                event_types.append('starred')
        
        print(f"✓ GitHub activity: {len(repos)} repos, {commits_count} commits, {len(event_types)} events")
        return {
            'repos': list(repos)[:3],  # Top 3 active repos
            'commits_count': commits_count,
            'activity_types': list(set(event_types))
        }
    except urllib.error.HTTPError as e:
        print(f"GitHub API HTTP Error {e.code}: {e.reason}")
        return {'repos': [], 'commits_count': 0, 'activity_types': []}
    except Exception as e:
        print(f"Could not fetch GitHub activity: {e}")
        return {'repos': [], 'commits_count': 0, 'activity_types': []}

def get_wakatime_data(file_path):
    """Extract real programming data from WakaTime section"""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        waka_section = re.search(r'<!--START_SECTION:waka-->(.*?)<!--END_SECTION:waka-->', content, re.DOTALL)
        if waka_section:
            waka_content = waka_section.group(1)
            
            # Extract languages with percentages
            languages = re.findall(r'([\w\s+#]+?)\s+(\d+\s+(?:hrs?|mins?).*?)\s+([\d.]+)\s*%', waka_content)
            
            # Extract editors
            editors = re.findall(r'🔥 Editors:.*?(\w+(?:\s+\w+)*)\s+\d+\s+(?:hrs?|mins?)', waka_content, re.DOTALL)
            
            # Extract OS
            os_match = re.findall(r'💻 Operating System:.*?(\w+)', waka_content, re.DOTALL)
            
            return {
                'languages': languages[:3] if languages else [],  # Top 3 languages
                'editor': editors[0].strip() if editors else 'VS Code',
                'os': os_match[0].strip() if os_match else 'WSL'
            }
    except Exception as e:
        print(f"Could not extract WakaTime data: {e}")
    
    return {'languages': [], 'editor': 'VS Code', 'os': 'WSL'}

# Get real data
github_activity = get_github_activity()
wakatime_data = get_wakatime_data('README.md')

# Build context from real data
languages_text = ", ".join([lang[0].strip() for lang in wakatime_data['languages']]) if wakatime_data['languages'] else "Angular, TypeScript, HTML"
repos_text = ", ".join([repo.split('/')[-1] for repo in github_activity['repos']]) if github_activity['repos'] else ""
activity_context = f" Active repositories: {repos_text}." if repos_text else ""
commits_info = f" Made {github_activity['commits_count']} commits recently." if github_activity['commits_count'] > 0 else ""

tech_topics = [
    "TypeScript advanced patterns",
    "Angular performance optimization",
    "RxJS operators",
    "Component architecture",
    "State management",
    "Responsive design patterns",
    "Accessibility best practices",
    "Web performance",
    "Testing strategies",
    "Clean code principles"
]

topic = random.choice(tech_topics)

prompt = f"""
Generate a compact "Dev Status Report" for a Frontend Developer's GitHub README profile based on REAL data from their GitHub activity.

Real data from this week:
- Programming languages used: {languages_text}
- Editor: {wakatime_data['editor']}
- OS: {wakatime_data['os']}{activity_context}{commits_info}

Format your response EXACTLY like this (3-4 lines total):

### 🚀 Current Focus
**This week:** [Describe activity based on the languages/tools and repositories they actually worked on] • Exploring {topic} • [1-2 relevant emoji]

**Quick insight:** [One practical technical tip related to their actual work - something actionable and specific]

Requirements:
- Base the "This week" section on the REAL languages/tools/repos they used
- Keep it professional but friendly
- Use 1-2 emoji that represent mood/status (🔥💡🎯⚡️🚀✨🎨🧪🔧etc)
- The insight should be practical and related to their actual tech stack
- Total length: 3-4 lines maximum
- Make it sound natural, like a real developer writing it
- Return ONLY the markdown text, nothing else

Example output:
### 🚀 Current Focus
**This week:** Working with JavaScript & HTML across multiple projects
### 🚀 Current Focus
**This week:** Working with JavaScript & HTML • Exploring Component architecture • 🔥💡

**Quick insight:** Using semantic HTML improves accessibility and SEO - always prefer <button> over <div> for clickable elements!
"""

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
