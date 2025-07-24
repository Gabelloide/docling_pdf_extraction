# Installation

- Install python dependencies:

```bash
pip install docling
```

Docling installs a CPU compiled version of torch, if you have a GPU please install
a GPU compiled version here : https://pytorch.org/get-started/locally/

- Example:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

# Ollama

- Install Ollama to be able to run the file [`full_pipeline_ollama.py`](full_pipeline_ollama.py): https://ollama.com/

# Usage

## Ollama version

The program [`full_pipeline_ollama.py`](full_pipeline_ollama.py) uses the provided Ollama vision language model to evaluate each image encountered in the PDF.
The output is a markdown file with all the information about the images, including their description from the VLM and the text extracted from the PDF.

```python
python full_pipeline_ollama.py 
--input <PDF file path or URL> 
--output <output_directory_path> 
--vlm-prompt <optional: custom prompt for vision model>
--ollama-model <optional: name of Ollama multimodal model to use (default llava)>
```

## Huggingface version

Alternatively, you can use any docling compatible VLM with the docling library.
The program [`full_pipeline.py`](full_pipeline.py) uses the provided VLM to evaluate each image encountered in the PDF.
The results are the same as the ollama version.

```python
python full_pipeline_ollama.py 
--input <PDF file path or URL> 
--output <output_directory_path> 
--vlm-prompt <optional: custom prompt for vision model>
```

ℹ️ Note that Hugginface with download the VLM from Hugginface Hub, so make sure it is downloaded in the right place by setting the `HF_HOME` environment variable.

Also you can manage/download models with the hugginface-cli python module : `pip install -U "huggingface_hub[cli]"`

## Picture description

An experimental program to create a markdown file with only the images from a PDF and their VLM-generated descriptions.
To use [`picture_description.py`](picture_description.py), you may edit the variables DOC_SOURCE and SAVE_DIR to respectively point to your document and save directory.

