import os
from google import genai
from google.genai import types

def analyze_content(client, prompt_text, media_path=None):
    # Define the configuration properly beforehand
    types_config = types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
    )
    
    # Pass the config variable cleanly into the call
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt_text, media_path] if media_path else prompt_text,
        config=types_config
    )
    
    return response.text
