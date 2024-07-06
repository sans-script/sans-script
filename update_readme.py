import re

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

if __name__ == "__main__":
    update_badges_section('README.md')
