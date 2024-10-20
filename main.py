from env import Env
import logging
import notion

def main():
    Env.init()
    logging.basicConfig(level=logging.INFO)

    if notion.check_for_updates():
        words_to_learn = notion.retrieve_words()
        logging.info(f"Words fetched: {words_to_learn}")
    else:
        logging.info("Everything is up to date, no new words were added to the Notion page.")

if __name__ == "__main__":
    main()