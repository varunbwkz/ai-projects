import os
import logging
from typing import List, Dict, Any, Optional, Union
import base64
try:
    from openai import OpenAI
except ImportError:
    raise ImportError("The 'openai' package is not installed. Please run 'pip install openai==1.14.0' to install it.")
import json
import re
import numpy as np
import chromadb
from src.analytics import analytics

from config.config import (
    OPENAI_API_KEY, 
    PROCESS_INSTRUCTIONS, 
    PROCESS_EMBEDDINGS, 
    get_formatted_process_guide, 
    get_process_keywords, 
    generate_embedding,
    search_processes_vector,
    USE_VECTOR_STORE
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEngine:
    """Engine for handling AI capabilities using OpenAI."""
    
    def __init__(self, api_key: str = OPENAI_API_KEY):
        """Initialize the AI engine with API key."""
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
        
        # Get process keywords mapping from config
        self.process_keywords = get_process_keywords()
        
        # Initialize chromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        
    def _match_process(self, query: str) -> Optional[str]:
        """
        Match a user query to a predefined process.
        
        Args:
            query: User query
            
        Returns:
            Process name if matched, None otherwise
        """
        query_lower = query.lower()
        
        # Clean up the query by removing common filler words
        filler_words = [
            "thanks", "thank you", "please", "any", "idea", "on", "how", "do", "we", "can", "you", "tell", "me",
            "about", "the", "way", "to", "process", "of", "steps", "for", "help", "with"
        ]
        clean_query = " ".join([word for word in query_lower.split() if word not in filler_words])
        
        # Try vector similarity search first with adjusted thresholds
        try:
            # Use both original and cleaned query for better matching
            vector_results_original = search_processes_vector(query, top_k=3)
            vector_results_clean = search_processes_vector(clean_query, top_k=3)
            
            # Combine and deduplicate results
            vector_results = []
            seen_processes = set()
            
            for results in [vector_results_original, vector_results_clean]:
                if results and len(results) > 0:
                    for result in results:
                        process_id = result['process_id']
                        if process_id not in seen_processes:
                            seen_processes.add(process_id)
                            vector_results.append(result)
            
            if vector_results:
                best_match = vector_results[0]['process_id']
                similarity = vector_results[0]['similarity']
                
                # Lower threshold for better semantic matching
                threshold = 0.65
                
                if similarity > threshold:
                    logger.info(f"Vector similarity match found: {best_match} with similarity {similarity}")
                    # Track successful match in analytics
                    analytics.track_process_request(query, best_match)
                    return best_match
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
        
        # Try keyword matching with both original and cleaned query
        best_match = None
        highest_score = 0
        
        for process_name, keywords in self.process_keywords.items():
            score = 0
            
            # Check both original and cleaned query
            for test_query in [query_lower, clean_query]:
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in test_query:
                        # Higher score for exact matches
                        if keyword_lower == test_query:
                            score += 10
                        # Higher score for multi-word matches
                        else:
                            score += len(keyword.split())
                    # Also check if query terms appear in keyword
                    elif any(term in keyword_lower for term in test_query.split()):
                        score += 0.5  # Partial match score
            
            if score > highest_score:
                highest_score = score
                best_match = process_name
        
        if highest_score > 2:  # Keep threshold for keyword matches
            logger.info(f"Keyword match found: {best_match} with score {highest_score}")
            # Track successful match in analytics
            analytics.track_process_request(query, best_match)
            return best_match
            
        # Track unmatched query in analytics
        analytics.track_process_request(query, None)
        return None
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm_a * norm_b)
        
    def generate_response(self, query: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            query: User query
            context: Optional context information (e.g., search results)
            
        Returns:
            Generated response
        """
        try:
            # Add user query to conversation history
            self.add_message("user", query)
            
            # Check if query matches any process
            matched_process = self._match_process(query)
            
            # If we have a direct match to any process, use direct response method to ensure exact steps
            if matched_process:
                logger.info(f"Using direct response for {matched_process} process")
                
                try:
                    # Get the processes directory
                    processes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processes')
                    process_data = None

                    # Search for the process file in all subdirectories
                    for root, dirs, files in os.walk(processes_dir):
                        process_file_path = os.path.join(root, f"{matched_process}.json")
                        if os.path.exists(process_file_path):
                            try:
                                with open(process_file_path, 'r') as f:
                                    process_data = json.load(f)
                                logger.info(f"Found process file at {process_file_path}")
                                break
                            except Exception as e:
                                logger.error(f"Error reading process file {process_file_path}: {e}")
                                continue
                    
                    # If we found and loaded the process file, use it
                    if process_data:
                        return self._format_direct_process_response(matched_process, process_data)
                    
                except Exception as e:
                    logger.error(f"Error creating direct response for {matched_process}: {str(e)}")
            
            # If we get here, we either didn't match a process or couldn't load the process file
            return """I apologize, but I can only provide accurate information based on the documented processes in Brandworkz. 
            
Could you please rephrase your question? For example:
- "How do I [specific task]?"
- "What are the steps to [specific action]?"
- "Can you show me how to [specific process]?"

This helps me find the exact process documentation you need."""
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error while generating a response: {str(e)}"
    
    def _detect_uncertainty(self, query: str) -> bool:
        """
        Detect if user query indicates uncertainty or need for guidance.
        
        Args:
            query: User query
            
        Returns:
            Boolean indicating whether user seems uncertain
        """
        uncertainty_indicators = [
            "help", "not sure", "don't know", "confused", "where do i", "how do i", 
            "what can you", "what do you", "options", "suggestions", "recommend", 
            "unclear", "guide", "guidance", "start", "beginner", "new to", "first time",
            "?", "advice", "tutorial", "where to begin", "capabilities", "functions"
        ]
        
        # If query is very short, treat as potentially uncertain
        if len(query.split()) < 4:
            return True
            
        # Check for uncertainty indicators
        query_lower = query.lower()
        for indicator in uncertainty_indicators:
            if indicator in query_lower:
                return True
                
        return False
    
    def _format_response(self, text: str) -> str:
        """
        Improves the formatting of the response text for better readability.
        
        Args:
            text: The response text from the OpenAI API
            
        Returns:
            Formatted response text with improved spacing
        """
        # First, normalize line endings
        text = text.replace('\r\n', '\n')
        
        # Fix formats where the number and content are separated by a newline
        # This regex matches patterns like "1.\nText" and changes them to "1. Text"
        text = re.sub(r'(\d+\.)\s*\n\s*([A-Z])', r'\1 \2', text)
        
        # Fix bolded numbers that got split
        text = re.sub(r'(\*\*\d+\.\*\*|\*\*\d+\.\b)\s*\n\s*([A-Z])', r'\1 \2', text)
        
        # Make sure list markers aren't lost
        text = re.sub(r'^(\d+\.\s)', r'\1', text, flags=re.MULTILINE)
        text = re.sub(r'^([•\-]\s)', r'\1', text, flags=re.MULTILINE)
        
        # Find natural paragraph breaks (sentences ending with punctuation followed by newline)
        # This adds proper spacing between paragraphs that don't have enough spacing
        text = re.sub(r'([.!?])\s*\n(?!\d+\.|\-|•|>|\*)(?=[A-Z])', r'\1\n\n', text)
        
        # Replace single newlines with double newlines for paragraph separation
        # But don't break up list items
        text = re.sub(r'(?<!\n)(?<!\d\.)(?<!•)(?<!-)(?<!>)\n(?!\n)(?!\d+\.)(?!•)(?!-)(?!>)', r'\n\n', text)
        
        # Ensure proper spacing after section titles (lines ending with a colon)
        text = re.sub(r'(:\n)(?!\n)(?!\d+\.)(?!•)(?!-)(?!>)', r':\n\n', text)
        
        # Ensure proper spacing between list items but not within the same item
        text = re.sub(r'((?:\d+\.|•|-)[^\n]+)\n(?!\n)(?!\d+\.|•|-)', r'\1\n\n', text)
        
        # Special handling for sections like "Helpful Tips:" to add spacing after the header
        text = re.sub(r'((?:^|\n)(?:[A-Z][a-z]+ )+:)\s*', r'\1\n\n', text)
        
        # Remove excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _process_id_to_question(self, process_id: str) -> str:
        """
        Convert a process ID to a natural language question.
        
        Args:
            process_id: The process ID to convert
            
        Returns:
            A natural language phrasing of the process
        """
        # Map of process IDs to natural language questions
        question_map = {
            "metadata_management": "manage metadata",
            "asset_workflow": "set up an asset workflow",
            "search_asset": "search for assets",
            "upload_asset": "upload assets",
            "create_collection": "create a collection",
            "share_assets": "share assets",
            "download_assets": "download assets"
        }
        
        # Return the mapped question or a default transformation
        return question_map.get(process_id, process_id.replace('_', ' '))
        
    def _format_direct_process_response(self, process_id: str, process_data: Dict[str, Any]) -> str:
        """
        Format a response using process data from a JSON file.
        
        Args:
            process_id: The ID of the process
            process_data: The process data from the JSON file
            
        Returns:
            Formatted response string
        """
        # Start with the title and description
        response_parts = []
        
        if "title" in process_data:
            response_parts.append(f"# {process_data['title']}\n")
        
        if "description" in process_data:
            response_parts.append(f"{process_data['description']}\n")
        
        # Add steps section
        if "steps" in process_data and process_data["steps"]:
            response_parts.append("\n## Steps\n")
            for i, step in enumerate(process_data["steps"], 1):
                response_parts.append(f"{i}. {step}")
        
        # Add troubleshooting section if present
        if "troubleshooting" in process_data and process_data["troubleshooting"]:
            response_parts.append("\n## Troubleshooting\n")
            for issue in process_data["troubleshooting"]:
                response_parts.append(f"- {issue}")
        
        # Add tips section if present
        if "tips" in process_data and process_data["tips"]:
            response_parts.append("\n## Tips\n")
            for tip in process_data["tips"]:
                response_parts.append(f"- {tip}")
        
        # Join all parts with newlines
        return "\n".join(response_parts)
    
    def get_process_instructions(self, process_name: str) -> Optional[List[str]]:
        """
        Get step-by-step instructions for a specified process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            List of instructions or None if process not found
        """
        return PROCESS_INSTRUCTIONS.get(process_name)
    
    def search_answer(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate an answer based on search results.
        
        Args:
            query: User query
            search_results: List of search results
            
        Returns:
            Generated answer
        """
        try:
            # Format search results for context
            context = []
            
            for result in search_results[:5]:  # Limit to first 5 results for context
                result_info = {
                    "id": result.get("id", "Unknown"),
                    "title": result.get("title", "Unknown"),
                    "fileType": result.get("fileType", "Unknown"),
                    "description": result.get("description", ""),
                    "url": result.get("url", "")
                }
                context.append(result_info)
            
            prompt = f"""
Based on the user's query: "{query}"
And these search results from Brandworkz:
{json.dumps(context, indent=2)}

Please provide a helpful response that:
1. Summarizes the most relevant results
2. Explains how these results relate to the user's query
3. Suggests next steps (e.g., viewing specific documents)
            """
            
            # Call OpenAI API without updating conversation history
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # using a widely available model
                messages=[
                    {"role": "system", "content": "You are an AI assistant for the Brandworkz platform. You help users search for documents and provide guidance on using the system."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Format the response for better readability
            response_text = self._format_response(response.choices[0].message.content)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating search answer: {str(e)}")
            return f"I encountered an error while processing the search results: {str(e)}"
    
    def guide_process(self, process_name: str) -> str:
        """
        Guide the user through a specific process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            Step-by-step instructions
        """
        # Get formatted process guide using the new helper function
        formatted_guide = get_formatted_process_guide(process_name)
        
        if not formatted_guide:
            return f"I'm sorry, but I don't have specific information about the '{process_name}' process in my knowledge base. Would you like to try a different process? Or perhaps I can help you with general questions about Brandworkz instead."
        
        friendly_process_name = process_name.replace('_', ' ')
        
        # Format the guide with proper markdown for a numbered list
        return f"""## How to {friendly_process_name.title()}

I'd be happy to guide you through the process of {friendly_process_name}! Follow these steps:

{formatted_guide}

**Need more help?** If you have questions about any of these steps, please ask and I'll provide more detailed guidance. I'm here to help make your experience with Brandworkz as smooth as possible!"""

    def _suggest_next_steps(self, query: str, matched_process: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Suggest next steps for the user based on their query and matched process.
        
        Args:
            query: The user's query
            matched_process: The process that was matched (if any)
            
        Returns:
            List of suggested next steps
        """
        suggestions = []
        
        # If we have a matched process, use process_relationships
        if matched_process:
            try:
                from config.process_relationships import get_related_processes
                return get_related_processes(matched_process)
            except Exception as e:
                logger.error(f"Error getting related processes: {e}")
        
        # If no matched process or error with relationships, use vector search to find related processes
        try:
            # Use a modified query that asks "what's next after X"
            next_step_query = f"what to do after {query}"
            vector_results = search_processes_vector(next_step_query, top_k=2)
            
            if vector_results:
                for result in vector_results:
                    process_id = result.get('process_id')
                    if process_id and process_id != matched_process:
                        # Get process title for better suggestion text
                        process_title = process_id.replace('_', ' ').title()
                        
                        # Create a simple transition text based on the process
                        if "upload" in process_id:
                            transition = f"You might want to upload content to the platform."
                        elif "search" in process_id:
                            transition = f"You could search for content in the system."
                        elif "metadata" in process_id:
                            transition = f"You could manage metadata for better organization."
                        elif "collection" in process_id:
                            transition = f"Creating collections could help organize your content."
                        elif "share" in process_id:
                            transition = f"You might want to share content with others."
                        elif "workflow" in process_id:
                            transition = f"Setting up workflows could streamline your processes."
                        else:
                            transition = f"You might be interested in learning about {process_title}."
                        
                        suggestions.append({
                            "process_id": process_id,
                            "transition": transition,
                            "reason": f"Related to your query about {query}"
                        })
        except Exception as e:
            logger.error(f"Error in vector-based next step suggestions: {e}")
        
        # If we still don't have suggestions, add default ones
        if not suggestions:
            suggestions = [
                {
                    "process_id": "search_asset",
                    "transition": "You might want to learn how to search for assets in the system.",
                    "reason": "Searching is a fundamental operation in Brandworkz."
                },
                {
                    "process_id": "upload_asset",
                    "transition": "You could learn how to upload new content to the platform.",
                    "reason": "Uploading is a fundamental operation in Brandworkz."
                }
            ]
            
            # If the matched process is one of our defaults, replace it
            if matched_process == "search_asset":
                suggestions[0] = {
                    "process_id": "metadata_management",
                    "transition": "You might want to learn how to manage metadata for your assets.",
                    "reason": "Metadata helps with organization and searching."
                }
            elif matched_process == "upload_asset":
                suggestions[1] = {
                    "process_id": "share_assets",
                    "transition": "You could learn how to share assets with your team.",
                    "reason": "Sharing is a common operation after uploading."
                }
                
        return suggestions[:2]  # Return up to 2 suggestions
