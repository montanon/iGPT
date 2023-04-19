import os
import PyPDF2
import openai
import re
import fitz

from tqdm import tqdm
from langchain.text_splitter import CharacterTextSplitter


with open('.env', 'r') as f:
    KEY = f.read().split('=')[-1].replace('\n', '')
openai.api_key = KEY


def process_strings(strings_list, available_tokens):
    string = '\n'.join(strings_list)
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=available_tokens, chunk_overlap=0)
    processed_strings = text_splitter.split_text(string)
    return processed_strings


def split_string_at_space(text, max_chars):
    if len(text) <= max_chars:
        return text

    split_index = max_chars
    while text[split_index] != ' ' and split_index > 0:
        split_index -= 1

    if split_index == 0:
        # If there's no space before the max_chars, split at the first space after max_chars
        split_index = text.find(' ', max_chars)

    return text[:split_index], text[split_index + 1:]


def load_counter(file_path='token_usage'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            counter = int(file.read().strip())
    else:
        counter = 0
    return counter


def save_counter(counter, file_path='token_usage'):
    with open(file_path, 'w') as file:
        file.write(str(counter))


def increment_counter(usage, file_path='token_usage'):
    counter = load_counter(file_path=file_path)
    counter += usage
    save_counter(counter, file_path=file_path)
    return counter


def select_pdf_file(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            return os.path.join(folder_path, file)
    return None


def extract_pdf_text(pdf_file_path):

    doc = fitz.open(pdf_file_path)

    paragraphs = []
    for page in doc:
        blocks = page.get_text('blocks')
        paragraph = ' '.join([bl[-3] for bl in blocks])
        paragraphs.append(paragraph)

    return paragraphs


def summarize_pdf_text(paragraphs, pre_prompt, max_tokens=4097, tokens_response=200):

    output_text = ''
#
    #adjusted_paragraphs = []
    #for paragraph in paragraphs:
    #    while len(paragraph) / 3 > max_tokens - tokens_response - 3750:
    #        max_chars = int(3 * (max_tokens - tokens_response - 3750))
    #        shortened_paragraph, paragraph = split_string_at_space(paragraph, max_chars)
    #        adjusted_paragraphs.append(shortened_paragraph)
    #    adjusted_paragraphs.append(paragraph)

    adjusted_paragraphs = process_strings(paragraphs, max_tokens - tokens_response - 1000)
    
    with open(pre_prompt, 'r') as f:
        prompt = f.read()

    for paragraph in tqdm(adjusted_paragraphs):

        prompt = f"{prompt}\n{paragraph}"
        
        response = openai.Completion.create(
            engine="text-davinci-003",#"gpt-3.5-turbo"
            prompt=prompt,
            max_tokens=tokens_response,
            n=1,
            stop=None,
            temperature=0.15,
        )

        increment_counter(response["usage"]["total_tokens"])

        output_text += response.choices[0].text.strip() + "\n\n"

    return output_text.strip()


def classify_pdf_text(summary):

    with open('pre-prompt_classification.txt', 'r') as f:
        pre_prompt = f.read()

    prompt = f"{pre_prompt}\n{summary}"
    
    response = openai.Completion.create(
        engine="text-davinci-003",#"gpt-3.5-turbo"
        prompt=prompt,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.15,
    )

    increment_counter(response["usage"]["total_tokens"])

    output_text = response.choices[0].text.strip() + "\n\n"

    return output_text.strip()


def main():
    folder_path = '/Users/sebastian/Desktop/TODAI/Yoshida-sensei/References/kajikawa2009.pdf'

    pdf_file_path = folder_path

    if pdf_file_path is None:
        print("No PDF file found in the specified folder.")
        return

    paragraphs = extract_pdf_text(pdf_file_path)

    summary = summarize_pdf_text(paragraphs)

    with open('summary.txt', 'w') as f:
        f.write(summary)

    print(f"Summarized PDF content:\n{summary}")

    classification = classify_pdf_text(summary)

    with open('classification.txt', 'w') as f:
        f.write(classification)

    print(f"Classified PDF content:\n{classification}")


if __name__ == "__main__":
    main()
