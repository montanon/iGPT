import os
import tkinter as tk
import pickle

from tkinter import filedialog, ttk

from basic_functions import *


def display_files(folder_path, file_listbox):
    file_listbox.delete(0, tk.END)
    if not folder_path:
        return
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_listbox.insert(tk.END, file)
    save_last_folder_path(folder_path)


def save_last_folder_path(folder_path):
    with open("last_folder_path.pkl", "wb") as file:
        pickle.dump(folder_path, file)


def load_last_folder_path():
    try:
        with open("last_folder_path.pkl", "rb") as file:
            folder_path = pickle.load(file)
    except FileNotFoundError:
        folder_path = ""
    return folder_path


def main():
    root = tk.Tk()
    root.title("PDF Selector")

    # Folder path input
    folder_path_label = tk.Label(root, text="Enter folder path:")
    folder_path_label.grid(row=0, column=0, sticky="W", padx=10, pady=(10, 0))

    last_folder_path = load_last_folder_path()
    folder_path_entry = tk.Entry(root, width=50)
    folder_path_entry.insert(0, last_folder_path)
    folder_path_entry.grid(row=1, column=0, padx=10, pady=(5, 0))

    # Listbox to display available files
    file_listbox_label = tk.Label(root, text="Available PDF files:")
    file_listbox_label.grid(row=2, column=0, sticky="W", padx=10, pady=(10, 0))

    file_listbox = tk.Listbox(root, width=50, height=10, exportselection=False)
    file_listbox.grid(row=3, column=0, padx=10, pady=(5, 0))

    # Button to display files in the folder
    display_files_button = tk.Button(
        root,
        text="Display Files",
        command=lambda: display_files(folder_path_entry.get(), file_listbox),
    )
    display_files_button.grid(row=1, column=1, padx=(0, 10), pady=(5, 0))

    # Button to select the chosen PDF file
    def select_pdf(folder_path_entry, file_listbox, gpt_response):
        folder_path = folder_path_entry.get()
        selected_file = file_listbox.get(file_listbox.curselection())
        pdf_file_path = os.path.join(folder_path, selected_file)

        paragraphs = extract_pdf_text(pdf_file_path)

        summary_folder = os.path.join(folder_path, 'summaries')
        if not os.path.exists(summary_folder):
            os.mkdir(summary_folder)
        summary_path = os.path.join(summary_folder,
                                    selected_file.replace('.pdf', '.txt'))
  
        if not os.path.exists(summary_path):
            paragraphs_summary, doc_summary, summ_cost = summarize_pdf_text(paragraphs, pre_prompt='pre-prompt_summary.txt')
            with open(summary_path, 'w') as f:
                f.write(doc_summary)
            with open(summary_path.replace('.txt', '_intermediate.txt'), 'w') as f:
                f.write(paragraphs_summary)
        else:
            with open(summary_path, 'r') as f:
                doc_summary = f.read()
            with open(summary_path.replace('.txt', '_intermediate.txt'), 'r') as f:
                paragraphs_summary = f.read()

        gpt_response.delete(1.0, tk.END)  # Clear previous GPT response

        gpt_response.insert(tk.END, 'PARAGRAPHS SUMMARY:\n' + paragraphs_summary + '\n\n' + '='*20)
        gpt_response.insert(tk.END, 'DOCUMENT SUMMARY:\n' + doc_summary + '\n\n'+ '='*20)
        gpt_response.see(tk.END) 

        keywords_folder = os.path.join(folder_path, 'keywords')
        if not os.path.exists(keywords_folder):
            os.mkdir(keywords_folder)
        keywords_path = os.path.join(keywords_folder,
                                    selected_file.replace('.pdf', '.txt'))
  
        if not os.path.exists(keywords_path):
            paragraphs_keywords, doc_keywords, kw_cost = summarize_pdf_text(paragraphs, pre_prompt='pre-prompt_keywords.txt')
            with open(keywords_path, 'w') as f:
                f.write(doc_keywords)
            with open(keywords_path.replace('.txt', '_intermediate.txt'), 'w') as f:
                f.write(paragraphs_keywords)
        else:
            with open(keywords_path, 'r') as f:
                doc_keywords = f.read()
            with open(keywords_path.replace('.txt', '_intermediate.txt'), 'r') as f:
                paragraphs_keywords = f.read()

        #gpt_response.insert(tk.END, 'PARAGRAPHS KEYWORDS:\n' + paragraphs_keywords + '\n\n')
        gpt_response.insert(tk.END, 'DOCUMENT KEYWORDS:\n' + doc_keywords + '\n\n' + '='*20)
        gpt_response.see(tk.END) 

        classification_folder = os.path.join(folder_path, 'classifications')
        if not os.path.exists(classification_folder):
            os.mkdir(classification_folder)
        classification_path = os.path.join(classification_folder,
                                    selected_file.replace('.pdf', '.txt'))
        if not os.path.exists(classification_path):
            paragraphs_classification, doc_classification, topic_cost = summarize_pdf_text(paragraphs, pre_prompt='pre-prompt_classification.txt')
            with open(classification_path, 'w') as f:
                f.write(doc_classification)
            with open(classification_path.replace('.txt', '_intermediate.txt'), 'w') as f:
                f.write(paragraphs_classification)
        else:
            with open(classification_path, 'r') as f:
                doc_classification = f.read()
            with open(classification_path.replace('.txt', '_intermediate.txt'), 'r') as f:
                paragraphs_classification = f.read()

        gpt_response.insert(tk.END, "TOPIC:\n" + doc_classification + '\n\n')
        gpt_response.insert(tk.END, "TOTAL COST OF ANALYSIS: $" + str(summ_cost + kw_cost + topic_cost) + '\n\n')
        gpt_response.insert(tk.END, f"INDIVIDUAL COSTS: SUMMARY:${summ_cost}, KEYWORDS:${kw_cost}, TOPIC:${topic_cost}\n\n")
        gpt_response.see(tk.END)  # Scroll to the end of the GPT response text
        gpt_response.update_idletasks()  # Update the GUI to display the new text

    select_pdf_button = tk.Button(root, text="Select PDF", command=lambda: select_pdf(folder_path_entry, file_listbox, gpt_response))
    select_pdf_button.grid(row=3, column=1, padx=(0, 10), pady=(5, 0))

    # Text widget to display GPT-4 response
    gpt_response_label = tk.Label(root, text="GPT-4 Response:")
    gpt_response_label.grid(row=4, column=0, sticky="W", padx=10, pady=(10, 0))

    gpt_response = tk.Text(root, width=100, height=20, wrap=tk.WORD)
    gpt_response.grid(row=5, column=0, columnspan=2, padx=10, pady=(5, 10))

    display_files(last_folder_path, file_listbox)

    root.mainloop()


if __name__ == "__main__":
    main()
