from datetime import datetime
import logging
import requests
import traceback

def get_notion_page_content(env, get_children):
    try:
        NOTION_API_KEY = env["NOTION_API_TOKEN"]
        NOTION_PAGE_ID = env["NOTION_PAGE_ID"]
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        children = "children" if get_children else ""
        notion_api_url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/{children}"

        response = requests.get(notion_api_url, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")

def retrieve_words(env):
    try:
        anki_page = get_notion_page_content(env, get_children=True)
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

def get_remote_last_edit_time(env):
    anki_page = get_notion_page_content(env, get_children=False)
    return datetime.fromisoformat(anki_page['last_edited_time'])

def check_for_updates(env):
    logging.info("Checking status ...")
    local_last_edit_date = datetime.fromisoformat(env["LAST_EDIT_DATE"])
    remote_last_edit_date = get_remote_last_edit_time(env)

    update_needed = remote_last_edit_date > local_last_edit_date
    if update_needed:
        write_env(env, "LAST_EDIT_DATE", remote_last_edit_date)
    return update_needed

def read_env():
    env_vars = [line.strip().split('=') for line in open(".env").readlines()]
    env_vars_dict = {line[0] : line[1] for line in env_vars}
    
    return env_vars_dict

def write_env(current_env, key, value):
    logging.debug(f"Updating env file with {key} = {value}")
    current_env[key] = value
    
    with open('.env', 'w') as file:
        for (key, value) in current_env.items():
            file.write(f"{key}={value}\n")

def main():
    logging.basicConfig(level=logging.INFO)

    env = read_env()
    if check_for_updates(env):
        words_to_learn = retrieve_words(env)
        logging.info(f"Words fetched: {words_to_learn}")
    else:
        logging.info("Everything is up to date, no new words were added to the Notion page.")

if __name__ == "__main__":
    main()
