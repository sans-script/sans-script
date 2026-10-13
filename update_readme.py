import re
import os
import json
import urllib.request
import urllib.parse
import random
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import google.generativeai as genai

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

# WakaTime "languages" that say nothing about what is being built
NON_CODE_LANGUAGES = {'markdown', 'json', 'yaml', 'text', 'toml', 'ini', 'xml', 'csv', 'git config', 'gitignore file', 'other'}

def github_get(path):
    """GET a GitHub API path and return the decoded JSON"""
    req = urllib.request.Request(f'https://api.github.com{path}')

    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    req.add_header('User-Agent', 'sans-script-readme-updater')

    github_token = os.environ.get('GH_TOKEN') or os.environ.get('ACCESS_TOKEN')
    if github_token:
        req.add_header('Authorization', f'Bearer {github_token}')

    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())

def get_github_activity(username='sans-script'):
    """Get recent GitHub activity and commit messages from the GitHub API"""
    try:
        events = github_get(f'/users/{username}/events?per_page=100')

        # Authenticated requests also return private events; never expose those
        events = [e for e in events if e.get('public')]

        repos = []  # most recent first; only repos actually worked on (not starred)
        event_types = []

        for event in events[:50]:
            event_type = event.get('type', '')
            repo_name = event.get('repo', {}).get('name', '')

            # The profile repo only gets automated README commits
            if (repo_name and repo_name != f'{username}/{username}' and repo_name not in repos
                    and event_type in ('PushEvent', 'PullRequestEvent', 'CreateEvent')):
                repos.append(repo_name)

            if event_type == 'PushEvent':
                event_types.append('coding')
            elif event_type == 'PullRequestEvent':
                event_types.append('PR')
            elif event_type == 'IssuesEvent':
                event_types.append('issue')
            elif event_type == 'CreateEvent':
                event_types.append('created')
            elif event_type == 'WatchEvent':
                event_types.append('starred')

        repos = repos[:3]

        # PushEvent payloads no longer carry commits, so read them from each repo
        since = (datetime.now(timezone.utc) - relativedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
        commits_count = 0
        commit_messages = []
        for repo_name in repos:
            try:
                commits = github_get(f'/repos/{repo_name}/commits?author={username}&since={since}&per_page=100')
            except Exception as e:
                print(f"Could not fetch commits for {repo_name}: {e}")
                continue
            commits_count += len(commits)
            messages = [c['commit']['message'].split('\n')[0] for c in commits]
            short_name = repo_name.split('/')[-1]
            commit_messages += [f"[{short_name}]: {msg}" for msg in messages if not msg.startswith('Merge ')][:2]

        print(f"✓ GitHub activity: {len(repos)} repos, {commits_count} commits, {len(event_types)} events")
        return {
            'repos': repos,
            'commits_count': commits_count,
            'activity_types': list(set(event_types)),
            'recent_commits': commit_messages[:6]
        }
    except urllib.error.HTTPError as e:
        print(f"GitHub API HTTP Error {e.code}: {e.reason}")
        return {'repos': [], 'commits_count': 0, 'activity_types': [], 'recent_commits': []}
    except Exception as e:
        print(f"Could not fetch GitHub activity: {e}")
        return {'repos': [], 'commits_count': 0, 'activity_types': [], 'recent_commits': []}

def parse_minutes(text):
    """'1 hr 38 mins' -> 98"""
    hrs = re.search(r'(\d+)\s*hrs?', text)
    mins = re.search(r'(\d+)\s*mins?', text)
    return (int(hrs.group(1)) * 60 if hrs else 0) + (int(mins.group(1)) if mins else 0)

def parse_waka_block(waka_content, header):
    """Return [(name, minutes)] for the rows listed under a WakaTime header"""
    block = re.search(re.escape(header) + r'.*?\n(.*?)(?:\n\s*\n|$)', waka_content, re.DOTALL)
    if not block:
        return []
    rows = re.findall(r'^(\S.*?)\s{2,}(.+?)\s{2,}[█░]', block.group(1), re.MULTILINE)
    return [(name.strip(), parse_minutes(time)) for name, time in rows]

def get_wakatime_data(file_path):
    """Extract real programming data from WakaTime section"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        waka_section = re.search(r'<!--START_SECTION:waka-->(.*?)<!--END_SECTION:waka-->', content, re.DOTALL)
        if waka_section:
            waka_content = waka_section.group(1)
            languages = [name for name, _ in parse_waka_block(waka_content, 'Programming Languages:')
                         if name.lower() not in NON_CODE_LANGUAGES]
            editors = parse_waka_block(waka_content, 'Editors:')
            os_rows = parse_waka_block(waka_content, 'Operating System:')

            return {
                'languages': languages[:3],
                'editor': editors[0][0] if editors else 'VS Code',
                'os': os_rows[0][0] if os_rows else 'WSL',
                # Each editor row is a slice of the week, so their sum is the weekly total
                'total_minutes': sum(minutes for _, minutes in editors)
            }
    except Exception as e:
        print(f"Could not extract WakaTime data: {e}")

    return {'languages': [], 'editor': 'VS Code', 'os': 'WSL', 'total_minutes': 0}

# Fetch metrics from active APIs and files
def get_profile_views(username='sans-script'):
    try:
        url = f'https://komarev.com/ghpvc/?username={username}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            svg_content = response.read().decode('utf-8')
        match = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
        if match:
            for text in reversed(match):
                if re.match(r'^[\d,]+$', text.strip()):
                    return text.strip()
    except Exception as e:
        print(f"Could not fetch profile views: {e}")
    return "0"

def add_repo_links(text, repos, username='sans-script'):
    """Add GitHub links to repository names mentioned in the text"""
    for repo in repos:
        repo_short = repo.split('/')[-1]
        text = re.sub(r'`' + re.escape(repo_short) + r'`', repo_short, text, flags=re.IGNORECASE)
        pattern = r'(?<!\[)\b' + re.escape(repo_short) + r'\b(?!\])'
        replacement = f'[{repo_short}](https://github.com/{repo})'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE, count=1)

    return text

def generate_model_response(file_path):
    """Ask Gemini for the focus and tip, render the section; None if anything fails"""
    github_activity = get_github_activity()
    wakatime_data = get_wakatime_data(file_path)
    # profile_views = get_profile_views()

    # Build context from tracked metrics
    top_langs = wakatime_data['languages']
    languages_text = ", ".join(top_langs) if top_langs else "TypeScript, Node.js"
    repos_text = ", ".join([repo.split('/')[-1] for repo in github_activity['repos']]) if github_activity['repos'] else ""
    total_minutes = wakatime_data.get('total_minutes', 0)

    if total_minutes < 60:
        activity_level = "light"
        activity_prefix = "Quick coding session with"
    elif total_minutes < 180:
        activity_level = "moderate"
        activity_prefix = "Working with"
    else:
        activity_level = "active"
        activity_prefix = "Deep diving into"

    if repos_text and github_activity['commits_count'] > 0:
        activity_context = f" Active repositories: {repos_text}."
        commits_info = f" Made {github_activity['commits_count']} commits recently."
    elif repos_text:
        activity_context = f" Active repositories: {repos_text}."
        commits_info = ""
    else:
        no_activity_messages = [
            " Taking a break from public repos this week.",
            " Focusing on local development.",
            " Working on private projects.",
            " Experimenting offline."
        ]
        activity_context = random.choice(no_activity_messages)
        commits_info = ""

    recent_commits_list = github_activity['recent_commits']
    commits_context = "\n".join(recent_commits_list) if recent_commits_list else "No recent public commit messages available."

    prompt = f"""
Generate a compact, highly specific "Dev Status Report" for a Software Developer's GitHub README profile based on REAL data.

Real data from this week:
- Programming languages used: {languages_text}
- Total coding time: {total_minutes} minutes (Activity level: {activity_level})
- Editor: {wakatime_data['editor']}
- OS: {wakatime_data['os']}{activity_context}{commits_info}
- Recent Commit Messages for deep context:
{commits_context}

CRITICAL INSTRUCTIONS:
1. Focus ONLY on the actual languages used: {languages_text}
2. Be HONEST about activity level based on the total minutes provided. If time is low, keep descriptions lightweight.
3. Analyze the provided commit messages to deduce WHAT specific features, architectures, or integrations the user is actually building. Do not hallucinate topics outside this technical scope.
4. For the RPG tip: It MUST be an advanced engineering pro-tip tailored directly to the architecture implied by the languages ({languages_text}) or commits.
5. CRITICAL: Strictly AVOID basic, cliché tutorial advice (e.g., "use const instead of let", "use semantic HTML", "remember to write tests"). Focus on clean code architecture, performance optimization, concurrency, or advanced type mechanics.
6. Write the tip like an RPG loading screen hint - just a single impactful sentence with no prefix, no list format, and no emoji.
7. Only mention repositories from the data above, by their exact name, without markdown links.

Respond with ONLY a JSON object with exactly these keys:
- "focus": one short phrase (max 15 words) with the highly specific technical action or focus area deduced from the commits. It is shown right after "{activity_prefix} {languages_text} •", so do not repeat the languages or start with a similar verb.
- "emoji": 1-2 relevant emoji.
- "tip": the advanced RPG loading screen programming tip.
"""

    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
        )
        data = json.loads(model.generate_content(prompt).text)
        focus, emoji, tip = (" ".join(str(data[key]).split()) for key in ('focus', 'emoji', 'tip'))
        if not (focus and tip):
            raise ValueError(f"empty fields in {data}")
    except Exception as e:
        print(f"Could not generate model response, keeping the previous one: {e}")
        return None

    focus = add_repo_links(focus.rstrip('.'), github_activity['repos'])
    return (
        f"### 🎯 Current Focus\n"
        f"{activity_prefix} {languages_text} • {focus} • {emoji}\n\n"
        f'<div align="center"><strong>{tip}</strong></div>'
    )


def update_overall_stats_section(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    hidden_section = re.search(r'<!--START_SECTION:hidden_badges-->(.*?)<!--END_SECTION:hidden_badges-->', content, re.DOTALL)

    code_time = "Unknown"
    lines_of_code = "Unknown"

    if hidden_section:
        badges = hidden_section.group(1).strip().split('\n')
        for badge in badges:
            badge = badge.strip()
            # Match both old 'Code%20Time' and new 'AI%20Code%20Time' label from WakaTime
            if 'Code%20Time' in badge:
                match = re.search(r'(?:AI%20)?Code%20Time-(.*?)-blue', badge)
                if match:
                    code_time = urllib.parse.unquote(match.group(1)).replace('--', '-')
            elif 'From%20Hello%20World' in badge:
                match = re.search(r'Written-(.*?)-blue', badge)
                if match:
                    lines_of_code = urllib.parse.unquote(match.group(1)).replace('--', '-')

    if code_time == "Unknown" or lines_of_code == "Unknown":
        overall_section_text = re.search(r'<!--OVERALL_STATS_START-->(.*?)<!--OVERALL_STATS_END-->', content, re.DOTALL)
        if overall_section_text:
            existing_text = overall_section_text.group(1)
            code_time_match = re.search(r'\*\*Code Time:\*\* (.*?)\s*\|', existing_text)
            if code_time_match:
                code_time = code_time_match.group(1).strip()
            lines_match = re.search(r'\*\*From Hello World I\'ve Written:\*\* (.*?)(?:\s*\||$)', existing_text)
            if lines_match:
                lines_of_code = lines_match.group(1).strip()

    # bot_views_match = re.search(r'<!--BOT_VIEWS:\s*(\d+)\s*-->', content)
    # bot_views = int(bot_views_match.group(1)) if bot_views_match else 0
    # bot_views += 1

    # try:
    #     raw_views = int(str(profile_views).replace(',', ''))
    #     real_profile_views = str(max(0, raw_views - bot_views))
    # except ValueError:
    #     real_profile_views = profile_views

    if code_time != "Unknown" and lines_of_code != "Unknown":
        overall_stats_text = f"**Code Time:** {code_time} | **From Hello World I've Written:** {lines_of_code}" # | **Profile Views:** {real_profile_views}"

        # if bot_views_match:
        #     content = content[:bot_views_match.start()] + f"<!--BOT_VIEWS:{bot_views}-->" + content[bot_views_match.end():]
        # else:
        #     content = re.sub(r'(<!--OVERALL_STATS_END-->)', r'\1\n<!--BOT_VIEWS:' + str(bot_views) + r'-->', content, count=1)

        # Update the plain text section
        overall_section = re.search(r'<!--OVERALL_STATS_START-->(.*?)<!--OVERALL_STATS_END-->', content, re.DOTALL)
        if overall_section:
            content = content[:overall_section.start(1)] + "\n" + overall_stats_text + "\n" + content[overall_section.end(1):]

        # Empty the hidden badges section so they don't show up on GitHub
        hidden_section = re.search(r'<!--START_SECTION:hidden_badges-->(.*?)<!--END_SECTION:hidden_badges-->', content, re.DOTALL)
        if hidden_section:
            content = content[:hidden_section.start(1)] + "\n" + content[hidden_section.end(1):]

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            print("Overall Stats Section Updated and Hidden Badges Cleared")
    else:
        print("No new stats found, leaving existing Overall Stats intact.")

def update_up_time_section(file_path):
    start_date = datetime(2006, 3, 24)
    current_date = datetime.now()
    difference = relativedelta(current_date, start_date)

    years = difference.years
    months = difference.months
    days = difference.days

    up_time_text = f'Up time: {years} years, {months} months and {days} days'

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    up_time_section = re.search(r'<!--UP_TIME_START-->(.*?)<!--UP_TIME_END-->', content, re.DOTALL)

    if up_time_section:
        prefix = content[:up_time_section.start(1)]
        suffix = content[up_time_section.end(1):]
        middle = "\n```text\n" + up_time_text + "\n```\n"
        updated_content = prefix + middle + suffix

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            print("Up Time Section Done")

def strip_waka_badges(file_path):
    """Remove badge lines (e.g. AI Code Time) injected by WakaTime into the waka section"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    waka_section = re.search(r'(<!--START_SECTION:waka-->)(.*?)(<!--END_SECTION:waka-->)', content, re.DOTALL)
    if waka_section:
        inner = waka_section.group(2)
        # Remove any markdown badge lines: ![...](http://img.shields.io/badge/...)
        cleaned = re.sub(r'!\[.*?\]\(https?://img\.shields\.io/badge/.*?\)\s*\n?', '', inner)
        if cleaned != inner:
            content = content[:waka_section.start(2)] + cleaned + content[waka_section.end(2):]
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print("WakaTime badges stripped from waka section")
        else:
            print("No WakaTime badges found in waka section")


def update_model_response(file_path, response_text):
    if response_text is None:
        print("Model Response Section left unchanged")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    model_response_section = re.search(r'<!--MODEL_RESPONSE_START-->(.*?)<!--MODEL_RESPONSE_END-->', content, re.DOTALL)

    if model_response_section:
        prefix = content[:model_response_section.start(1)]
        suffix = content[model_response_section.end(1):]
        middle = '\n' + response_text + '\n'
        updated_content = prefix + middle + suffix

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            print("Model Response Section Done")
    else:
        print("Model response section not found in the file.")

if __name__ == "__main__":
    target_readme = 'README.md'
    update_overall_stats_section(target_readme)
    strip_waka_badges(target_readme)
    update_up_time_section(target_readme)
    update_model_response(target_readme, generate_model_response(target_readme))
