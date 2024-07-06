import requests
import os
import re

waka_api_key = os.getenv('WAKATIME_API_KEY')
gh_token = os.getenv('GH_TOKEN')
readme_path = 'README.md'

def get_wakatime_data():
    url = f"https://wakatime.com/api/v1/users/current/stats/last_7_days?api_key={waka_api_key}"
    response = requests.get(url)
    return response.json()

def update_section(content, marker_start, marker_end, new_data):
    pattern = f"{re.escape(marker_start)}(.*?){re.escape(marker_end)}"
    return re.sub(pattern, f"{marker_start}\n{new_data}\n{marker_end}", content, flags=re.DOTALL)

def main():
    data = get_wakatime_data()
    
    with open(readme_path, 'r') as file:
        readme_content = file.read()

    # Update different sections
    stats = f"![Code Time](http://img.shields.io/badge/Code%20Time-{data['data']['total_seconds']}%20secs-blue)"
    readme_content = update_section(readme_content, "<!--START_SECTION:waka_stats-->", "<!--END_SECTION:waka_stats-->", stats)

    languages = '\n'.join([f"{lang['name']} - {lang['percent']}%" for lang in data['data']['languages']])
    readme_content = update_section(readme_content, "<!--START_SECTION:waka_languages-->", "<!--END_SECTION:waka_languages-->", f"```\n{languages}\n```")

    editors = '\n'.join([f"{editor['name']} - {editor['percent']}%" for editor in data['data']['editors']])
    readme_content = update_section(readme_content, "<!--START_SECTION:waka_editors-->", "<!--END_SECTION:waka_editors-->", f"```\n{editors}\n```")

    projects = '\n'.join([f"{project['name']} - {project['percent']}%" for project in data['data']['projects']])
    readme_content = update_section(readme_content, "<!--START_SECTION:waka_projects-->", "<!--END_SECTION:waka_projects-->", f"```\n{projects}\n```")

    with open(readme_path, 'w') as file:
        file.write(readme_content)

if __name__ == "__main__":
    main()
