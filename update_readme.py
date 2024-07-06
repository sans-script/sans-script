import os
import re
import requests

# Obtenha as variáveis de ambiente necessárias
wakatime_api_key = os.getenv('WAKATIME_API_KEY')
github_token = os.getenv('GH_TOKEN')

# URLs e headers necessários
stats_url = 'https://wakatime.com/api/v1/users/current/stats/last_7_days'
headers = {
    'Authorization': f'Bearer {wakatime_api_key}'
}

# Faça a solicitação para obter os dados do Wakatime
response = requests.get(stats_url, headers=headers)
data = response.json()

# Função para formatar a seção de linguagens
def format_languages(languages):
    formatted = "\n".join([f"{lang['name']} - {lang['percent']}%" for lang in languages])
    return f"**Languages:**\n```\n{formatted}\n```"

# Função para formatar a seção de projetos
def format_projects(projects):
    formatted = "\n".join([f"{proj['name']} - {proj['percent']}%" for proj in projects])
    return f"**Projects:**\n```\n{formatted}\n```"

# Função para formatar a seção de editores
def format_editors(editors):
    formatted = "\n".join([f"{editor['name']} - {editor['percent']}%" for editor in editors])
    return f"**Editors:**\n```\n{formatted}\n```"

# Função para formatar a seção de tempo de código
def format_code_time(data):
    total_seconds = data['cummulative_total']['seconds']
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"![Code Time](http://img.shields.io/badge/Code%20Time-{hours}%20hrs%20{minutes}%20mins-blue)"

# Dados formatados para cada seção
languages_section = format_languages(data['data']['languages'])
projects_section = format_projects(data['data']['projects'])
editors_section = format_editors(data['data']['editors'])
code_time_section = format_code_time(data)

# Leia o conteúdo atual do README.md
with open('README.md', 'r') as file:
    readme_contents = file.read()

# Atualize o conteúdo entre as seções definidas
readme_contents = re.sub(
    r'<!--START_SECTION:waka_stats-->.*<!--END_SECTION:waka_stats-->',
    f'<!--START_SECTION:waka_stats-->\n{code_time_section}\n<!--END_SECTION:waka_stats-->',
    readme_contents,
    flags=re.DOTALL
)

readme_contents = re.sub(
    r'<!--START_SECTION:waka_languages-->.*<!--END_SECTION:waka_languages-->',
    f'<!--START_SECTION:waka_languages-->\n{languages_section}\n<!--END_SECTION:waka_languages-->',
    readme_contents,
    flags=re.DOTALL
)

readme_contents = re.sub(
    r'<!--START_SECTION:waka_projects-->.*<!--END_SECTION:waka_projects-->',
    f'<!--START_SECTION:waka_projects-->\n{projects_section}\n<!--END_SECTION:waka_projects-->',
    readme_contents,
    flags=re.DOTALL
)

readme_contents = re.sub(
    r'<!--START_SECTION:waka_editors-->.*<!--END_SECTION:waka_editors-->',
    f'<!--START_SECTION:waka_editors-->\n{editors_section}\n<!--END_SECTION:waka_editors-->',
    readme_contents,
    flags=re.DOTALL
)

# Escreva o conteúdo atualizado de volta no README.md
with open('README.md', 'w') as file:
    file.write(readme_contents)
