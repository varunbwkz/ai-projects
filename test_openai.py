import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_embedding():
    """Test OpenAI embedding"""
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Removed the proxies setup that might be causing issues
        # Set the API key directly
        openai.api_key = api_key
        
        # Option 1: Using the new client approach
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input="Hello world"
            )
            
            embedding = response.data[0].embedding
            print(f"✅ Option 1 works! Vector dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"❌ Option 1 Error: {e}")
            
        # Option 2: Using the older API style (if available)
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input="Hello world"
            )
            
            embedding = response['data'][0]['embedding']
            print(f"✅ Option 2 works! Vector dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"❌ Option 2 Error: {e}")
            
    except Exception as e:
        print(f"❌ General Error: {e}")
        
if __name__ == "__main__":
    test_embedding()
