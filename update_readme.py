import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

def update_badges_section(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regex to find the badges section
    badges_section = re.search(r'<!--START_SECTION:badges-->(.*?)<!--END_SECTION:badges-->', content, re.DOTALL)
    
    if badges_section:
        # Split the badges into a list, strip leading/trailing whitespace, and join with newline
        badges = badges_section.group(1).strip().split('\n')
        updated_badges = '\n'.join(badge.strip() for badge in badges if badge.strip())
        
        updated_content = content[:badges_section.start(1)] + '\n' + updated_badges + '\n' + content[badges_section.end(1):]

        with open(file_path, 'w') as file:
            file.write(updated_content)
            print("Badges Section Done")

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
        updated_content = content[:up_time_section.start(1)] + f'\n```python\n{up_time_text}\n```\n' + content[up_time_section.end(1):]

        with open(file_path, 'w') as file:
            file.write(updated_content)
            print("Up Time Section Done")

if __name__ == "__main__":
    file_path = 'README.md'
    update_badges_section(file_path)
    update_up_time_section(file_path)
