import os
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables
load_dotenv()

# Initialize Notion Client
notion = Client(auth=os.environ.get("NOTION_TOKEN"))
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

def load_report(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()




def create_notion_page(report_text):
    print("Connecting to Notion API...")
    
    # Defensive programming: Notion limits text blocks to 2000 characters.
    # We split the report by paragraphs to ensure no single block exceeds the limit.
    paragraphs = report_text.split('\n\n')
    children_blocks = []
    

    for p in paragraphs:
        if p.strip():
            # Truncate just in case a single paragraph is abnormally long
            text_content = p.strip()[:2000] 
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text_content}}]
                }
            })


    # Generate a dynamic title with the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    page_title = f"Clinical AI Report - {timestamp}"

    try:
        # Create the new entry in the database
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                # "Reports" matches the exact title property in your database
                "Reports": {
                    "title": [
                        {
                            "text": {
                                "content": page_title
                            }
                        }
                    ]
                }
            },
            # Notion API allows a maximum of 100 blocks per request
            children=children_blocks[:100] 
        )
        print("="*50)
        print(f"SUCCESS! Report successfully published to Notion.")
        print(f"View your page here: {new_page['url']}")
        print("="*50)
    except Exception as e:
        print(f"Failed to create page in Notion: {e}")


if __name__ == "__main__":
    print("Initiating Step 5: Notion Integration...")
    
    report_path = "report.txt"
    report_content = load_report(report_path)
    
    if report_content:
        if not DATABASE_ID:
            print("Error: NOTION_DATABASE_ID is missing in your .env file.")
        else:
            create_notion_page(report_content)