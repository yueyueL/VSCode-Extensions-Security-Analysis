import openai
import pandas as pd
import os
import time

api_key = "sk-..."

def get_chatgpt_response(messages, model='gpt-3.5-turbo', temperature=0):
    """
    Returns the response from ChatGPT for a given prompt
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response


def labeling():
    openai.api_key = api_key

    data_path = "PATH/TO/MetaData.csv"
    saved_path = "PATH/TO/LabelResult.csv"
    saved_text = ""
    data = pd.read_csv(data_path)

    if os.path.exists(saved_path):
        with open(saved_path, "r") as f:
            saved_text = f.read()
    
    current_indexs = []
    for line in saved_text.split("\n"):
        if line:
            current_indexs.append(int(line.split(",")[0]))


    for index, ext in data.iterrows():
        extension_id = ext["extensionID"]
        type_ext = ext["type"]
        data_ext = ext["data"]
        
        if index in current_indexs:
            continue

        # prompt = "Given a text feature extracted from a VSCode extension, such as a command label, a configuration description, or a global state key, classify it into credentials or not credentials. Credentials include things like API keys, passwords, access tokens, etc. Not credentials include non-sensitive texts like code snippets, configuration options, etc. Assign a label of 1 for credentials and 0 for not credentials."
        prompt = "Assign a label of 1 for credentials-related text and 0 for not credentials. "
        prompt += f"The text is: {data_ext}"
        message = [{"role": "system", "content": "Your task is to label the following text as credentials or not credentials."}]
        message = [{"role": "user", "content": prompt}]

        try:
            response = get_chatgpt_response(message)
            label = response.choices[0].message.content
            saved_text += f"{index},{label}\n"
        except Exception as e:
            saved_text += f"{index},-1\n"
        
        if index % 50 == 0:
            # print time
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            with open(saved_path, "w") as f:
                f.write(saved_text)

    with open(saved_path, "w") as f:
        f.write(saved_text)


if __name__ == "__main__":
    revise_label()