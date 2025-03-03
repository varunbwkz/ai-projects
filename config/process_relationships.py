"""
Process relationships define natural progressions between different processes.
This allows the AI to suggest relevant next steps after a user completes a process.
"""

# Define which processes naturally follow from other processes
PROCESS_RELATIONSHIPS = {
    # Asset Management
    "upload_asset": [
        {
            "process_id": "metadata_management",
            "reason": "After uploading an asset, you typically need to add or edit its metadata.",
            "transition": "Now that you've uploaded your asset, you might want to add metadata to make it easier to find and organize."
        },
        {
            "process_id": "share_assets",
            "reason": "After uploading assets, sharing them with team members is a common next step.",
            "transition": "Once your asset is uploaded, you might want to share it with your team or external stakeholders."
        }
    ],
    "search_asset": [
        {
            "process_id": "download_assets",
            "reason": "After finding assets through search, downloading them is a common next action.",
            "transition": "Now that you've found the assets you were looking for, you might want to download them."
        },
        {
            "process_id": "create_collection",
            "reason": "Organizing search results into collections helps with project organization.",
            "transition": "If you need to organize the assets you've found, you could create a collection to group them together."
        }
    ],
    "metadata_management": [
        {
            "process_id": "search_asset",
            "reason": "After adding metadata, users often want to verify assets are searchable.",
            "transition": "With your metadata in place, you can now search for your assets using these terms."
        }
    ],
    
    # Collection Management
    "create_collection": [
        {
            "process_id": "share_assets",
            "reason": "After creating a collection, sharing it with team members is common.",
            "transition": "Now that you've created your collection, you might want to share it with your colleagues."
        }
    ],
    
    # Sharing & Collaboration
    "share_assets": [
        {
            "process_id": "asset_workflow",
            "reason": "After sharing assets, setting up a workflow for review/approval might be next.",
            "transition": "If these assets need approval or review, you could set up a workflow process for them."
        }
    ],
    
    # Workflow Management
    "asset_workflow": [
        {
            "process_id": "metadata_management",
            "reason": "After workflow completion, updating asset metadata with approval status is common.",
            "transition": "Once your workflow is complete, you may want to update the metadata to reflect the new status."
        }
    ],
    
    # Default suggestions for any process
    "default": [
        {
            "process_id": "search_asset",
            "reason": "Searching is a fundamental operation in Brandworkz.",
            "transition": "You might also be interested in learning how to effectively search for assets in the system."
        },
        {
            "process_id": "upload_asset",
            "reason": "Uploading is a fundamental operation in Brandworkz.",
            "transition": "If you need to add new content to the system, you might want to learn about uploading assets."
        }
    ]
}

def get_related_processes(process_id):
    """
    Get processes that naturally follow the given process.
    
    Args:
        process_id: ID of the current process
        
    Returns:
        List of related process suggestions
    """
    related = PROCESS_RELATIONSHIPS.get(process_id, [])
    
    # If we have fewer than 2 specific recommendations, add some default ones
    if len(related) < 2:
        defaults = PROCESS_RELATIONSHIPS.get("default", [])
        # Filter out any that are already in the related list
        existing_ids = {r["process_id"] for r in related}
        defaults = [d for d in defaults if d["process_id"] not in existing_ids and d["process_id"] != process_id]
        # Add defaults until we have at least 2 recommendations
        related.extend(defaults[:max(0, 2 - len(related))])
        
    return related
