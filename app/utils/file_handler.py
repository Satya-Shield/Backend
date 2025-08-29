import logging

def read_prompt(prompt_name: str) -> str:
    try:
        path = f"app/prompts/{prompt_name}.txt"
        with open(path) as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error while reading prompt: {e}")

if __name__ == "__main__":
    prompt = read_prompt("test")
    print(prompt)
