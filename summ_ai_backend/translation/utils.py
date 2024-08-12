import os
import deepl
from bs4 import BeautifulSoup, NavigableString
from concurrent.futures import ThreadPoolExecutor
import logging
from retrying import retry

# Get the DeepL API key from the environment variable
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def translate_chunk(chunk, dest_language='EN-US'):
    """
    Translates a chunk of text into the specified language using DeepL API.
    
    Args:
        chunk (str): The text chunk to translate.
        dest_language (str): The target language for translation.
    
    Returns:
        str: The translated text, or the original chunk if an error occurs.
    
    Retries the translation up to 3 times in case of failure.
    """
    translator = deepl.Translator(DEEPL_API_KEY)
    try:
        translation = translator.translate_text(chunk, target_lang=dest_language.upper())
        return translation.text
    except Exception as e:
        logger.error(f"Error during translation: {e}")
        return chunk

def chunk_text_by_tokens(text, tokens_per_chunk=200):
    """
    Splits text into smaller chunks based on a specified number of tokens.
    
    Args:
        text (str): The text to split.
        tokens_per_chunk (int): The maximum number of tokens (words) per chunk.
    
    Returns:
        list: A list of text chunks, each with a maximum of `tokens_per_chunk` tokens.
    """
    words = text.split()
    chunks = [' '.join(words[i:i + tokens_per_chunk]) for i in range(0, len(words), tokens_per_chunk)]
    return chunks

def translate_text(text, dest_language='EN-US'):
    """
    Translates a large body of text by splitting it into chunks and translating each chunk.
    
    Args:
        text (str): The text to translate.
        dest_language (str): The target language for translation.
    
    Returns:
        str: The translated text, recombined from translated chunks.
    """
    chunks = chunk_text_by_tokens(text)
    with ThreadPoolExecutor() as executor:
        translated_chunks = list(executor.map(lambda chunk: translate_chunk(chunk, dest_language), chunks))
    return ' '.join(translated_chunks)

def translate_text_node(node, dest_language='EN-US'):
    """
    Translates a text node within an HTML document.
    
    Args:
        node (str): The text node to translate.
        dest_language (str): The target language for translation.
    
    Returns:
        str: The translated text, or the original node if an error occurs.
    
    Handles translation errors gracefully, logging them and returning the original text.
    """
    try:
        if node.strip():
            translated_text = translate_text(node, dest_language)
            return translated_text
        return node
    except Exception as e:
        logger.error(f"Error translating node: {e}")
        return node

def translate_html(html, dest_language='EN-US'):
    """
    Translates all text within an HTML document while preserving the structure.
    
    Args:
        html (str): The HTML content to translate.
        dest_language (str): The target language for translation.
    
    Returns:
        str: The HTML document with all translatable text translated into the target language.
    
    Translates only the inner text of tags and preserves the HTML structure.
    Replaces double quotes with single quotes in the final HTML output for consistency.
    """
    soup = BeautifulSoup(html, 'html.parser')
    text_nodes = [node for node in soup.find_all(string=True) if isinstance(node, NavigableString) and node.strip()]

    with ThreadPoolExecutor() as executor:
        translated_texts = list(executor.map(lambda node: translate_text_node(node, dest_language), text_nodes))

    for original, translated in zip(text_nodes, translated_texts):
        original.replace_with(f'{translated.strip()} ')

    translated_html = str(soup)
    translated_html = translated_html.replace('"', "'").replace(" >", ">").replace(" </", "</")

    return translated_html
