import requests
from typing import Optional
import time
import urllib.parse

class MyMemoryTranslator:
    def __init__(self):
        self.api_url = "https://api.mymemory.translated.net/get"
        self.last_request = 0
        self.min_delay = 1.0  # Minimum delay between requests in seconds
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "es"
    ) -> str:
        """
        Translate text using MyMemory Translation API with rate limiting
        """
        try:
            if not text.strip():
                return text

            # Implement rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request
            if time_since_last < self.min_delay:
                time.sleep(self.min_delay - time_since_last)
            
            # Format language codes (MyMemory uses different format)
            lang_pair = f"{source_lang}|{target_lang}"
            
            # URL encode the text
            encoded_text = urllib.parse.quote(text)
            
            # Make request
            url = f"{self.api_url}?q={encoded_text}&langpair={lang_pair}"
            response = requests.get(url)
            self.last_request = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data["responseStatus"] == 200:
                    return data["responseData"]["translatedText"]
                else:
                    print(f"Translation error: {data['responseStatus']}")
                    return text
            else:
                print(f"Translation error: {response.status_code}")
                return text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text