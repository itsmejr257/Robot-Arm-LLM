import os

def set_openai_api_key():
    api_key = input("Please enter your OpenAI API key: ")
    bashrc_path = os.path.expanduser("~/.bashrc")
    
    with open(bashrc_path, "a") as file:
        file.write(f'\nexport OPENAI_API_KEY="{api_key}"\n')
    
    print("API key has been set successfully.")

if __name__ == "__main__":
    set_openai_api_key()