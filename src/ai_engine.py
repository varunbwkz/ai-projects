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
        
        # Check for direct process mentions (e.g., "show me the asset workflow process")
        for process_name in PROCESS_INSTRUCTIONS.keys():
            process_pattern = re.compile(r'\b' + re.escape(process_name.replace('_', ' ')) + r'\b')
            if process_pattern.search(query_lower):
                logger.info(f"Direct process match found: {process_name}")
                return process_name
        
        # Try vector similarity search
        try:
            # Get top matches from vector search
            vector_results = search_processes_vector(query, top_k=1)
            
            if vector_results and len(vector_results) > 0:
                best_match = vector_results[0]['process_id']
                similarity = vector_results[0]['similarity']
                
                # Only return match if similarity is above threshold
                if similarity > 0.75:  # Adjust threshold as needed
                    logger.info(f"Vector similarity match found: {best_match} with similarity {similarity}")
                    return best_match
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            # Fall back to keyword matching if vector search fails
        
        # Fall back to keyword matches
        best_match = None
        highest_score = 0
        
        for process_name, keywords in self.process_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    # Higher score for multi-word matches
                    score += len(keyword.split()) 
            
            if score > highest_score:
                highest_score = score
                best_match = process_name
        
        if highest_score > 0:
            logger.info(f"Keyword match found: {best_match} with score {highest_score}")
            return best_match
            
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
            
            # Check if user seems uncertain or needs guidance
            is_uncertain = self._detect_uncertainty(query)
            
            # Check if query matches any process
            matched_process = self._match_process(query)
            process_guide = None
            
            # If we have a direct match to any process, use direct response method to ensure exact steps
            if matched_process:
                logger.info(f"Using direct response for {matched_process} process")
                
                try:
                    # Get the raw process steps
                    process_steps = PROCESS_INSTRUCTIONS.get(matched_process, [])
                    
                    # Try to get the original file to access additional fields like troubleshooting
                    # First determine which subdirectory it might be in
                    process_dirs = ["asset_management", "collection_management", "sharing_collaboration", "workflow_management"]
                    process_data = None
                    
                    for subdir in process_dirs:
                        try:
                            process_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                           'processes', subdir, f"{matched_process}.json")
                            if os.path.exists(process_file_path):
                                with open(process_file_path, 'r') as f:
                                    process_data = json.load(f)
                                break
                        except Exception:
                            continue
                    
                    # If we couldn't find or load the file, use just the steps
                    if not process_data and isinstance(process_steps, list):
                        process_data = {"steps": process_steps}
                    
                    # Format response based on the process data
                    return self._format_direct_process_response(matched_process, process_data)
                    
                except Exception as e:
                    logger.error(f"Error creating direct response for {matched_process}: {str(e)}")
                    # Fall back to the normal response method
                    process_guide = get_formatted_process_guide(matched_process)
            
            # Continue with normal processing if direct response failed or if no process matched
            if matched_process and not process_guide:
                process_guide = get_formatted_process_guide(matched_process)
                logger.info(f"Found matching process: {matched_process}")
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": """You are a friendly and helpful Brandworkz platform assistant named BrandwizAI. 
                
Your tone should be:
- Warm and conversational, addressing the user as if you're having a friendly chat
- Professional but not overly formal
- Enthusiastic about helping users master the Brandworkz platform
- Patient and encouraging, especially with new users

Your responses should be:
- Detailed and comprehensive, providing thorough explanations
- Well-structured with clear sections when appropriate
- Practical with real-world examples where possible
- Empathetic to user challenges and frustrations

When explaining processes:
- Break down complex tasks into manageable steps
- Explain the reasoning behind each step
- Mention potential pitfalls to avoid
- Acknowledge when something might be challenging

When users seem uncertain or don't know what to ask:
- Proactively offer suggestions based on common Brandworkz tasks
- Ask clarifying questions to understand their needs better
- Provide a menu of options related to their area of interest
- Suggest specific topics they might want to explore

Always conclude your responses with 1-2 suggestions for what the user might want to do next. 
Base these suggestions on what would naturally follow the user's current task. For example:
- After explaining searching, suggest downloading or creating collections
- After explaining uploading, suggest adding metadata or sharing
- After explaining metadata, suggest searching using those metadata terms

Available processes you can guide users through include:
- upload_asset: How to upload assets to Brandworkz
- search_asset: How to effectively search for assets
- create_collection: How to create and manage collections
- share_assets: How to share assets with others
- download_assets: How to download assets from the platform
- asset_workflow: How to set up and manage asset workflows
- metadata_management: How to create and manage metadata for assets

Your main goal is to guide users through Brandworkz processes with clarity and encouragement, making them feel supported and confident in using the platform."""}
            ]
            
            # Add context if provided
            if context:
                context_text = json.dumps(context, indent=2)
                messages.append({"role": "system", "content": f"Here is some context that might help with the query: {context_text}"})
            
            # If we matched a process, provide the guide
            if process_guide:
                friendly_process_name = matched_process.replace('_', ' ')
                messages.append({"role": "system", "content": f"""The user is asking about the {friendly_process_name} process. 
                
Here is a detailed guide for this process. You MUST COPY THE STEPS VERBATIM without ANY changes:

{process_guide}

DO NOT REWRITE OR REINTERPRET ANY STEPS. When presenting these steps to the user:
1. Use the EXACT same words, phrases, and sentences as written above for each step
2. Maintain the exact same step numbering
3. Do not add any of your own steps
4. Do not combine or split steps
5. Do not add additional explanations within the steps themselves
6. You can add a title and intro, but the steps themselves MUST BE COPIED EXACTLY."""})
            
            # For uncertain users, add a specific instruction
            if is_uncertain:
                messages.append({"role": "system", "content": """The user seems uncertain about what to ask or how to proceed. 
                
In your response:
1. Acknowledge their uncertainty
2. Offer 3-5 specific suggestions for common Brandworkz tasks they might want to explore
3. Provide a brief menu of general topics (e.g., asset management, searching, collections, sharing)
4. Ask a follow-up question to help narrow down their interests
                
Make your suggestions specific rather than generic, and frame them as actionable options."""})
            
            # Add next step suggestions if not a direct process match
            if not matched_process:
                try:
                    next_steps = self._suggest_next_steps(query)
                    if next_steps:
                        suggestions_text = []
                        for step in next_steps:
                            process_id = step['process_id']
                            transition = step['transition']
                            
                            # Format process_id into a natural language question
                            question = self._process_id_to_question(process_id)
                                
                            suggestions_text.append(f"- {process_id.replace('_', ' ').title()}: {transition} The user can ask \"How do I {question}?\"")
                        
                        formatted_suggestions = "\n".join(suggestions_text)
                        
                        messages.append({"role": "system", "content": f"""Based on the user's query, these might be good next steps to suggest:
                        
{formatted_suggestions}

Include these suggestions towards the end of your response in a "What You Might Want to Try Next" section, phrasing them in a natural, conversational way."""})
                except Exception as e:
                    logger.error(f"Error adding next step suggestions to LLM prompt: {e}")
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # using a widely available model
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            
            # Format the response for better readability
            response_text = self._format_response(response_text)
            
            # Add assistant response to history
            self.add_message("assistant", response_text)
            
            return response_text
            
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
        
    def _format_direct_process_response(self, process_name: str, process_data: Dict[str, Any]) -> str:
        """
        Format a direct response for a process without using the LLM.
        
        Args:
            process_name: The name of the process
            process_data: The process data from the JSON file
            
        Returns:
            Formatted response text
        """
        # Get friendly process name
        friendly_process_name = process_name.replace('_', ' ').title()
        
        # Format the response
        response_text = f"# How to {friendly_process_name}\n\n"
        
        # Add description if available
        if 'description' in process_data:
            response_text += f"{process_data['description']}\n\n"
        else:
            response_text += f"I'm happy to guide you through the process of {process_name.replace('_', ' ')}. Follow these steps exactly:\n\n"
        
        # Add steps
        steps = process_data.get('steps', [])
        for i, step in enumerate(steps):
            # Check if step is a dictionary with 'step' and 'detail' fields
            if isinstance(step, dict) and 'step' in step:
                step_text = step['step']
                detail_text = step.get('detail', '')
                response_text += f"**Step {i+1}:** {step_text}\n\n"
                if detail_text:
                    response_text += f"{detail_text}\n\n"
            else:
                # Handle simple string steps
                response_text += f"**Step {i+1}:** {step}\n\n"
        
        # Add additional sections based on available data
        
        # Add troubleshooting if available
        if 'troubleshooting' in process_data and process_data['troubleshooting']:
            response_text += "## Potential Pitfalls to Avoid:\n\n"
            for issue in process_data['troubleshooting']:
                response_text += f"- {issue}\n"
            response_text += "\n"
        
        # Add prerequisites if available
        if 'prerequisites' in process_data and process_data['prerequisites']:
            response_text += "## Prerequisites:\n\n"
            for prereq in process_data['prerequisites']:
                response_text += f"- {prereq}\n"
            response_text += "\n"
        
        # Add notes if available
        if 'notes' in process_data and process_data['notes']:
            response_text += "## Notes:\n\n"
            if isinstance(process_data['notes'], list):
                for note in process_data['notes']:
                    response_text += f"- {note}\n"
            else:
                response_text += f"{process_data['notes']}\n"
            response_text += "\n"
        
        # Add concluding text
        response_text += "I hope this helps! Let me know if you have any questions about any of these steps.\n\n"
        
        # Add suggestions for next steps
        try:
            related_processes = self._suggest_next_steps(process_name, matched_process=process_name)
            
            if related_processes:
                response_text += "## What You Might Want to Do Next:\n\n"
                
                for related in related_processes[:2]:  # Limit to 2 suggestions
                    process_id = related["process_id"]
                    transition = related["transition"]
                    friendly_related_name = process_id.replace('_', ' ').title()
                    
                    # Format process_id into a natural language question
                    question = self._process_id_to_question(process_id)
                    
                    response_text += f"- **{friendly_related_name}**: {transition} Just ask me \"How do I {question}?\"\n"
                
                response_text += "\n"
        except Exception as e:
            logger.error(f"Error suggesting next steps: {e}")
            # Continue without suggestions if there's an error
        
        # Add to conversation history
        self.add_message("assistant", response_text)
        
        return response_text
    
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
