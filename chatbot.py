import requests
import git
import os

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

if __name__ == "__main__":
    # Example usage
    api_key = os.getenv("GITHUB_TOKEN")
    chatbot = ChatBot(base_url="http://202.169.113.228:1234", api_key=api_key, model="QuantFactory/DeepSeek-Coder-V2-Lite-Instruct-GGUF")
    response = chatbot.send_message("Introduce yourself.")
    print(response)

    git_ops = GitOperations(repo_url="https://github.com/e2b-dev/e2b-cookbook.git", local_path="./e2b-cookbook")
    git_ops.clone_repo()
    git_ops.create_branch("new-feature")
    git_ops.commit_and_push("Initial commit", "new-feature")

