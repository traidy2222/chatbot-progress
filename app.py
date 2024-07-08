from flask import Flask, request, render_template
import requests
import git
import os

app = Flask(__name__)

# Set up the connection to the remotely hosted LLM
class ChatBot:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def send_message(self, message):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': message}
            ]
        }
        response = requests.post(f'{self.base_url}/v1/chat/completions', headers=headers, json=data)
        return response.json()

    def thought(self, question):
        return question

    def action(self, action_type, params):
        if action_type == "send_message":
            return self.send_message(params)
        elif action_type == "clone_repo":
            git_ops.clone_repo()
        elif action_type == "create_branch":
            git_ops.create_branch(params)
        elif action_type == "commit_and_push":
            git_ops.commit_and_push(params['commit_message'], params['branch_name'])
        return "PAUSE"

    def action_response(self, response):
        return response

# Git operations
class GitOperations:
    def __init__(self, repo_url, local_path):
        self.repo_url = repo_url
        self.local_path = local_path

    def clone_repo(self):
        if not os.path.exists(self.local_path):
            git.Repo.clone_from(self.repo_url, self.local_path)
        else:
            print("Repository already exists locally.")

    def create_branch(self, branch_name):
        repo = git.Repo(self.local_path)
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    def commit_and_push(self, commit_message, branch_name):
        repo = git.Repo(self.local_path)
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push(branch_name)

api_key = os.getenv("GITHUB_TOKEN")
chatbot = ChatBot(base_url="http://202.169.113.228:1234", api_key=api_key, model="QuantFactory/DeepSeek-Coder-V2-Lite-Instruct-GGUF")
git_ops = GitOperations(repo_url="https://github.com/e2b-dev/e2b-cookbook.git", local_path="./e2b-cookbook")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form["question"]

        # Thought
        thought = chatbot.thought(question)

        # Action
        if "introduce" in thought.lower():
            action_type = "send_message"
            params = "Introduce yourself."
        elif "clone" in thought.lower():
            action_type = "clone_repo"
            params = None
        elif "create branch" in thought.lower():
            action_type = "create_branch"
            params = "new-feature"
        elif "commit and push" in thought.lower():
            action_type = "commit_and_push"
            params = {'commit_message': "Initial commit", 'branch_name': "new-feature"}
        else:
            action_type = "send_message"
            params = thought

        response = chatbot.action(action_type, params)

        # PAUSE
        if response == "PAUSE":
            return render_template("index.html", question=question, answer="Action paused. Please continue.")

        # Action_Response
        final_response = chatbot.action_response(response)
        return render_template("index.html", question=question, answer=final_response)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000)

