# File: app.py
# An enhanced Flask web application for tracking compliance tasks.
# Features a modern, accessible, and responsive design with Tailwind CSS.

import json
from flask import Flask, render_template_string, request, redirect, url_for
from pathlib import Path
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Define the file path for data storage
DATA_FILE = Path("data.json")

# --- DATA HANDLING FUNCTIONS ---
# These functions handle reading from and writing to the JSON file.
# This separates data logic from the application routes, demonstrating modular design.

def load_data():
    """Loads project data from the JSON file."""
    if not DATA_FILE.exists():
        return {"projects": []}
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """Saves project data to the JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- FLASK ROUTES ---
# Each route handles a specific part of the application's functionality.

@app.route("/", methods=["GET"])
def home():
    """Renders the home page, showing all projects."""
    data = load_data()
    return render_template_string(HTML_TEMPLATE, projects=data["projects"])

@app.route("/create_project", methods=["POST"])
def create_project():
    """Handles the creation of a new project."""
    project_title = request.form.get("title")
    if project_title:
        data = load_data()
        new_project_id = len(data["projects"]) + 1
        new_project = {
            "id": new_project_id,
            "title": project_title,
            "tasks": []
        }
        data["projects"].append(new_project)
        save_data(data)
    return redirect(url_for("home"))

@app.route("/project/<int:project_id>", methods=["GET"])
def project_detail(project_id):
    """Renders the detail page for a specific project."""
    data = load_data()
    project = next((p for p in data["projects"] if p["id"] == project_id), None)
    if not project:
        return "Project not found", 404
    return render_template_string(HTML_TEMPLATE, project=project, projects=data["projects"])

@app.route("/add_task/<int:project_id>", methods=["POST"])
def add_task(project_id):
    """Adds a new task to a specific project."""
    task_text = request.form.get("task_text")
    due_date = request.form.get("due_date")
    if task_text:
        data = load_data()
        project = next((p for p in data["projects"] if p["id"] == project_id), None)
        if project:
            new_task = {
                "id": len(project["tasks"]) + 1,
                "text": task_text,
                "completed": False,
                "due_date": due_date
            }
            project["tasks"].append(new_task)
            save_data(data)
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/toggle_task/<int:project_id>/<int:task_id>", methods=["POST"])
def toggle_task(project_id, task_id):
    """Toggles the completion status of a task."""
    data = load_data()
    project = next((p for p in data["projects"] if p["id"] == project_id), None)
    if project:
        task = next((t for t in project["tasks"] if t["id"] == task_id), None)
        if task:
            task["completed"] = not task["completed"]
            save_data(data)
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/edit_task/<int:project_id>/<int:task_id>", methods=["POST"])
def edit_task(project_id, task_id):
    """Edits the text of an existing task."""
    new_text = request.form.get("new_text")
    new_date = request.form.get("new_date")
    if new_text:
        data = load_data()
        project = next((p for p in data["projects"] if p["id"] == project_id), None)
        if project:
            task = next((t for t in project["tasks"] if t["id"] == task_id), None)
            if task:
                task["text"] = new_text
                task["due_date"] = new_date
                save_data(data)
    return redirect(url_for("project_detail", project_id=project_id))
    
@app.route("/delete_task/<int:project_id>/<int:task_id>", methods=["POST"])
def delete_task(project_id, task_id):
    """Deletes a task from a project."""
    data = load_data()
    project = next((p for p in data["projects"] if p["id"] == project_id), None)
    if project:
        project["tasks"] = [t for t in project["tasks"] if t["id"] != task_id]
        save_data(data)
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/delete_project/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    """Deletes an entire project."""
    data = load_data()
    data["projects"] = [p for p in data["projects"] if p["id"] != project_id]
    save_data(data)
    return redirect(url_for("home"))


# --- HTML TEMPLATE ---
# The entire HTML/CSS is stored as a multi-line string for a single-file solution.

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Documentation and Task Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
    <div class="container mx-auto p-4 md:p-8">
        <header class="flex justify-between items-center mb-6">
            <a href="/" class="text-3xl md:text-4xl font-extrabold flex items-center">
                <svg class="h-8 w-8 md:h-10 md:w-10 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2ZM8 17.5h8.5v-2H8v2Zm0-4.5h8.5v-2H8v2Zm0-4.5h8.5v-2H8v2Z"/>
                </svg>
                Compliance Documentation and Task Tracker
            </a>
            <button id="theme-toggle" aria-label="Toggle dark mode" class="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path class="moon-icon" d="M12 2.75a9.25 9.25 0 1 0 0 18.5 9.25 9.25 0 0 0 0-18.5ZM12 4.25a7.75 7.75 0 1 1 0 15.5 7.75 7.75 0 0 1 0-15.5Z"/>
                    <path class="sun-icon hidden" d="M12 18.25a6.25 6.25 0 1 0 0-12.5 6.25 6.25 0 0 0 0 12.5ZM12 2.75a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5a.75.75 0 0 1 .75-.75ZM12 19.25a.75.75 0 0 1-.75.75v1.5a.75.75 0 0 1 1.5 0v-1.5a.75.75 0 0 1-.75-.75ZM18.5 12a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75ZM3.5 12a.75.75 0 0 1-.75-.75h-1.5a.75.75 0 0 1 0 1.5h1.5a.75.75 0 0 1 .75-.75ZM16.326 7.674a.75.75 0 0 1-.53-.22L17.53 6.31a.75.75 0 0 1 1.06 1.06L16.856 8.41a.75.75 0 0 1-.53-.22ZM6.41 17.53a.75.75 0 0 1-1.06-1.06L6.31 16.856a.75.75 0 0 1 1.06 1.06L6.41 17.53ZM17.53 16.856a.75.75 0 0 1-1.06 1.06l-1.205-1.205a.75.75 0 0 1 1.06-1.06l1.205 1.205ZM6.31 6.31a.75.75 0 0 1-1.06-1.06L7.674 3.984a.75.75 0 0 1 .53.22L7.674 6.31a.75.75 0 0 1-.53.22Z"/>
                </svg>
            </button>
        </header>

        {% if project %}
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-2xl md:text-3xl font-semibold mb-2">{{ project.title }}</h2>
                <div class="flex space-x-2">
                    <a href="/" class="p-2 rounded-full text-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200" aria-label="Back to all projects">
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L2 12h3v8h6v-6h2v6h6v-8h3L12 2Z"/>
                        </svg>
                    </a>
                    <form action="{{ url_for('delete_project', project_id=project.id) }}" method="post" onsubmit="return confirm('Are you sure you want to delete this project?');">
                        <button type="submit" class="p-2 rounded-full text-red-500 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200" aria-label="Delete project">
                             <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12Zm-2-4v2h16v-2h-2V7h-3V5h-6v2H6v2H4Zm12-2h-2V9h2v2Z"/>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
            
            {% set completed_tasks = project.tasks | selectattr('completed') | list %}
            {% set progress = (completed_tasks | length) / (project.tasks | length) * 100 if project.tasks else 0 %}
            <div class="mb-6">
                <p class="text-sm font-semibold mb-1">Progress: {{ progress|int }}%</p>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                    <div class="bg-blue-500 h-2.5 rounded-full" style="width: {{ progress }}%"></div>
                </div>
            </div>

            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-4">
                <form action="{{ url_for('add_task', project_id=project.id) }}" method="post" class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                    <div class="flex-grow">
                        <label for="task-text" class="sr-only">New Task</label>
                        <input type="text" id="task-text" name="task_text" placeholder="Add a new compliance task" required aria-label="Add a new compliance task" class="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label for="due-date" class="sr-only">Due Date</label>
                        <input type="date" id="due-date" name="due_date" aria-label="Due date for the task" class="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <button type="submit" aria-label="Add Task" class="p-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 transition-colors duration-200">
                        Add Task
                    </button>
                </form>
                <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">The due date helps you prioritize tasks and meet important compliance deadlines.</p>
            </div>
            
            <ul class="space-y-4">
                {% for task in project.tasks %}
                <li class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 flex flex-col md:flex-row items-start md:items-center justify-between">
                    <div class="flex items-center space-x-3 w-full">
                        <form action="{{ url_for('toggle_task', project_id=project.id, task_id=task.id) }}" method="post" aria-label="Toggle task completion">
                            <input type="checkbox" class="h-5 w-5 rounded text-blue-500 focus:ring-blue-500" onchange="this.form.submit()" {% if task.completed %}checked{% endif %}>
                        </form>
                        <div class="flex-grow">
                            <span class="text-lg {% if task.completed %}line-through text-gray-500 dark:text-gray-400{% endif %}">{{ task.text }}</span>
                            {% if task.due_date %}
                                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">Due: {{ task.due_date }}</div>
                            {% endif %}
                        </div>
                    </div>
                    <div class="flex space-x-2 mt-2 md:mt-0">
                        <button onclick="editTask({{ project.id }}, {{ task.id }}, '{{ task.text }}', '{{ task.due_date }}')" class="p-2 text-yellow-500 hover:text-yellow-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-yellow-500" aria-label="Edit task">
                            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.06 9.06L15.94 10.94 9 17.88 7.12 16L14.06 9.06ZM17.66 4.34a.996.996 0 0 0-1.41 0L15.06 5.53l2.83 2.83 1.18-1.18a.996.996 0 0 0 0-1.41L17.66 4.34ZM14.06 7.47L16.53 10l-6.38 6.38-2.47-2.47 6.38-6.38Z"/>
                            </svg>
                        </button>
                        <form action="{{ url_for('delete_task', project_id=project.id, task_id=task.id) }}" method="post" onsubmit="return confirm('Are you sure you want to delete this task?');">
                            <button type="submit" class="p-2 text-red-500 hover:text-red-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500" aria-label="Delete task">
                                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12Zm-2-4v2h16v-2h-2V7h-3V5h-6v2H6v2H4Zm12-2h-2V9h2v2Z"/>
                                </svg>
                            </button>
                        </form>
                    </div>
                </li>
                {% endfor %}
            </ul>

        {% else %}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
                <form action="{{ url_for('create_project') }}" method="post" class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                    <label for="project-title" class="sr-only">New Project Title</label>
                    <input type="text" id="project-title" name="title" placeholder="e.g., Q3 Data Regulation Review" required aria-label="Enter new project title" class="flex-grow p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button type="submit" class="p-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 transition-colors duration-200">
                        Create Project
                    </button>
                </form>
            </div>
            
            <h2 class="text-2xl md:text-3xl font-semibold mb-4">All Projects</h2>
            <p class="text-gray-500 dark:text-gray-400 mb-4">Click on a project to view and manage its tasks.</p>
            <ul class="space-y-4">
                {% for project in projects %}
                <li class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 flex items-center justify-between">
                    <a href="{{ url_for('project_detail', project_id=project.id) }}" class="text-lg md:text-xl font-medium text-blue-500 hover:text-blue-600 transition-colors duration-200">{{ project.title }}</a>
                    <form action="{{ url_for('delete_project', project_id=project.id) }}" method="post" onsubmit="return confirm('Are you sure you want to delete this project?');">
                        <button type="submit" class="p-2 text-red-500 hover:text-red-600 transition-colors duration-200" aria-label="Delete project">
                            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12Zm-2-4v2h16v-2h-2V7h-3V5h-6v2H6v2H4Zm12-2h-2V9h2v2Z"/>
                            </svg>
                        </button>
                    </form>
                </li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>

    <script>
        // Theme toggle logic
        const toggleButton = document.getElementById('theme-toggle');
        const sunIcon = toggleButton.querySelector('.sun-icon');
        const moonIcon = toggleButton.querySelector('.moon-icon');

        const isDarkMode = localStorage.getItem('theme') === 'dark';
        if (isDarkMode) {
            document.documentElement.classList.add('dark');
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }

        toggleButton.addEventListener('click', () => {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.removeItem('theme');
                sunIcon.classList.add('hidden');
                moonIcon.classList.remove('hidden');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
                sunIcon.classList.remove('hidden');
                moonIcon.classList.add('hidden');
            }
        });

        // Edit task function (replaces old task text with an input field)
        function editTask(projectId, taskId, currentText, currentDate) {
            const listItem = event.target.closest('li');
            const originalDiv = listItem.querySelector('.flex-grow');
            const buttonContainer = listItem.querySelector('div.flex.space-x-2');
            
            const editForm = document.createElement('form');
            editForm.action = `/edit_task/${projectId}/${taskId}`;
            editForm.method = 'post';
            editForm.classList.add('flex', 'flex-col', 'md:flex-row', 'space-y-2', 'md:space-y-0', 'md:space-x-2', 'w-full');

            const editInput = document.createElement('input');
            editInput.type = 'text';
            editInput.name = 'new_text';
            editInput.value = currentText;
            editInput.required = true;
            editInput.className = 'p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-500';
            editInput.setAttribute('aria-label', 'Edit task text');

            const editDate = document.createElement('input');
            editDate.type = 'date';
            editDate.name = 'new_date';
            editDate.value = currentDate;
            editDate.className = 'p-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-500';
            editDate.setAttribute('aria-label', 'Edit task due date');

            const saveButton = document.createElement('button');
            saveButton.type = 'submit';
            saveButton.textContent = 'Save';
            saveButton.className = 'p-2 rounded-lg bg-yellow-500 text-white hover:bg-yellow-600 transition-colors duration-200';

            editForm.appendChild(editInput);
            editForm.appendChild(editDate);
            editForm.appendChild(saveButton);
            
            originalDiv.replaceWith(editForm);
            
            buttonContainer.classList.add('hidden');
            editInput.focus();
        }

        document.body.addEventListener('click', function(e) {
            const li = e.target.closest('li[role="checkbox"]');
            if (li && !e.target.closest('button, a, input')) {
                li.querySelector('input[type="checkbox"]').click();
            }
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
