import os
import json

class SkillsManager:
    def __init__(self, skills_dir=".skills"):
        self.skills_dir = skills_dir
        os.makedirs(self.skills_dir, exist_ok=True)

    def save_skill(self, name, description, code):
        """Save a new skill to the catalog."""
        skill_data = {
            "name": name,
            "description": description,
            "code": code
        }
        filename = name.lower().replace(" ", "_") + ".json"
        path = os.path.join(self.skills_dir, filename)
        with open(path, 'w') as f:
            json.dump(skill_data, f, indent=2)
        return path

    def get_skill(self, name):
        """Retrieve a skill by name."""
        filename = name.lower().replace(" ", "_") + ".json"
        path = os.path.join(self.skills_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def list_skills(self):
        """List all available skills."""
        skills = []
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.skills_dir, filename), 'r') as f:
                    skills.append(json.load(f))
        return skills
