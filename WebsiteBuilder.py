#Imports required libraries
import os
import re
from datetime import datetime

#Assigns folder and file paths
input_folder = r"C:\Users\jayse\Documents\jaysehughes.com\website builder\projects"
output_folder = r"C:\Users\jayse\Documents\jaysehughes.com\website builder\jaysehughes.com"
main_file = r"C:\Users\jayse\Documents\jaysehughes.com\website builder\projects\main.txt"

#Creates the output folder if it does not exist
os.makedirs(output_folder, exist_ok=True)

#Reads main.txt and generates a list of projects and the respective data
projects = []
with open(main_file, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            title, path, description = [x.strip() for x in line.split("|")]
            projects.append({"title": title, "path": path, "description": description})

#Reads project#.txt and generates a list of data for each file
for p in projects:
    project_file = os.path.join(input_folder, p["path"] + ".txt")
    if not os.path.exists(project_file):
        print(f"\n{project_file} does not exist, moving to next\n")
        p["latest_date"] = datetime.min
        continue

    with open(project_file, "r", encoding="utf-8") as f:
        content = f.read()
    updates_raw = re.split(r"\[UPDATE DATE\]", content)[1:]
    updates = []

    for u in updates_raw:
        lines = u.strip().splitlines()
        date = lines[0].strip()
        text = ""
        video = ""
        subtitle = ""
        collecting_text = False
        text_lines = []

        for line in lines[1:]:
            if line.startswith("[UPDATE TEXT]"):
                collecting_text = True
                text_lines.append(line.split("]",1)[1].strip())
            elif line.startswith("[UPDATE VIDEO]"):
                collecting_text = False
                video = line.split("]",1)[1].strip()
            elif line.startswith("[UPDATE SUBTITLE]"):
                subtitle = line.split("]",1)[1].strip()
            elif collecting_text:
                text_lines.append(line.strip())

        text = "\n".join(text_lines).strip()
        updates.append({"date": date, "subtitle": subtitle, "text": text, "video": video})

#Reads [UPDATE DATE] and finds the latest update 
    def parse_date(d):
        try:
            return datetime.strptime(d, "%b %Y")
        except ValueError:
            return datetime.min
        
    if updates:
        latest_date = max(parse_date(u["date"]) for u in updates)
    else:
        latest_date = datetime.min

    p["latest_date"] = latest_date
    p["updates"] = updates

#Sorts project cards by update date
projects.sort(key=lambda x: x["latest_date"], reverse=True)

#Begins homepage HTML
home_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Projects</title>
    <link rel="stylesheet" href="index.css">
</head>
<h1>My Projects</h1>
<div id="sort-options">
    <label for="sort-select">Sort Projects:</label>
    <select id="sort-select" onchange="sortProjects()">
        <option value="newest" selected>Newest First</option>
        <option value="oldest">Oldest First</option>
    </select>
</div>
<div class="projects-container" id="projects-container">
"""

#Generates a new project card for each project
for p in projects:
    home_html += f'<a href="{p["path"]}.html" class="project-card"><h3>{p["title"]}</h3><p>{p["description"]}</p></a>'

#Finishes homepage HTML
home_html += """
<script>
    const container = document.getElementById("projects-container");
    const cards = Array.from(container.children);
    function sortProjects() {
        const order = document.getElementById("sort-select").value;
        let sorted;

        if (order === "newest") {
            sorted = [...cards];
        } else {
            sorted = [...cards].reverse();
        }
        sorted.forEach(card => container.appendChild(card));
    }
</script>    
</div></body></html>
"""

#Writes index.html to the ouput folder
with open(os.path.join(output_folder, "index.html"), "w", encoding="utf-8") as f:
    f.write(home_html)

#Retrieves update data from earlier
for p in projects:
    updates = p["updates"]

#Begins project page HTML
    project_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{p["title"]}</title>
        <link rel="stylesheet" href="project.css">
    </head>
    <body>
    <div id="timeline">
    """

#Creates timeline buttons for each update
    for u in updates:
        project_html += f'<button onclick="document.getElementById(\'{p["path"]}-{u["date"]}\').scrollIntoView({{behavior:\'smooth\'}})">{u["date"]}</button>'

    project_html += f'<a href="index.html"><button id="back-button">Back to Projects</button></a>'
    project_html += "</div><div id='content'>"

#Parses update date and assigns it to the proper place on the project page
    for u in updates:
        paragraphs = [f"<p>{p.strip()}</p>" for p in u["text"].split("\n\n") if p.strip()]
        text_html = "\n".join(paragraphs)
        project_html += f"""
        <div id="{p['path']}-{u['date']}" class="update">
            <h4>{u['date']} Update -- {u['subtitle']}</h4>
            {text_html}
            <iframe src="{u['video']}" allowfullscreen></iframe>
        </div>
        """

#Finished project page HTML
    project_html += """
    <script>
        function scrollToUpdate(id){
            document.getElementById(id).scrollIntoView({behavior:'smooth'});
        }
    </script>
    </div></body></html>
    """

#Writes project#.html to output folder
    with open(os.path.join(output_folder, p["path"] + ".html"), "w", encoding="utf-8") as f:
        f.write(project_html)

#Reports that the program was successful
print(f"Homepage and {len(projects)} project pages generated in {output_folder}")
