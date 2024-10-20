from datetime import datetime
from env import Env

import logging
import requests
import traceback

NOTION_API_VERSION= "2022-06-28"

def get_notion_page_content(get_children):
    try:
        NOTION_API_KEY = Env.get("NOTION_API_TOKEN")
        NOTION_PAGE_ID = Env.get("NOTION_PAGE_ID")
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": f"{NOTION_API_VERSION}"
        }
        children = "children" if get_children else ""
        notion_api_url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/{children}"

        response = requests.get(notion_api_url, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
    
def retrieve_words():
    try:
        logging.info("Retrieving words")
        anki_page = get_notion_page_content(get_children=True)
        results = anki_page['results']
        # bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': 'lekker', 'link': None}, 'plain_text': 'lekker', 'href': None}]
        bullet_list_items = [result["bulleted_list_item"] for result in results if result["type"] == "bulleted_list_item"]

        words = []
        for bullet_list_item in bullet_list_items:
            rich_text_items = bullet_list_item.get('rich_text', [])
            word = rich_text_items[0].get('plain_text', None)
            if word:
                words.append(word)
            else:
                logging.error(f"ERROR: can't find plain_text in the Notion response")

        return words
    except:
        logging.error(f"ERROR:{traceback.format_exc()}\nThis program assumes that Notion page contains one bulled list. Either your Notion page looks differently or Notion API has changed.")

def get_remote_last_edit_time():
    anki_page = get_notion_page_content(get_children=False)
    return datetime.fromisoformat(anki_page['last_edited_time'])

def check_for_updates():
    logging.info("Checking status ...")

    remote_last_edit_date = get_remote_last_edit_time()
    local_last_edit_date = Env.get("LAST_EDIT_DATE")
    update_needed = local_last_edit_date == None or remote_last_edit_date > datetime.fromisoformat(local_last_edit_date)

    if update_needed:
        Env.export("LAST_EDIT_DATE", remote_last_edit_date)

    return update_needed