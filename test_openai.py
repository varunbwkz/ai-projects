import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_embedding():
    """Test OpenAI embedding"""
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Create the OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test embedding generation
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input="Hello world"
            )
            
            embedding = response.data[0].embedding
            print(f"✅ Embedding works! Vector dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"❌ Embedding Error: {e}")
            
    except Exception as e:
        print(f"❌ General Error: {e}")
        
if __name__ == "__main__":
    test_embedding()
