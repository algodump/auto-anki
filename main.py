from env import Env
import anki
import logging
import notion

def main():
    Env.init()
    logging.basicConfig(level=logging.INFO)
    anki.verify_connection()

    # TODO: make this command line argument
    anki_deck_name = "test_words"
    Env.export("CURRENT_ANKI_DECK_NAME", anki_deck_name)

    if notion.check_for_updates():
        words_to_learn = notion.retrieve_words()
        logging.debug(f"Words fetched: {words_to_learn}")
        anki.update_deck(anki_deck_name, words_to_learn)
    else:
        logging.info("Everything is up to date, no new words were added to the Notion page.")

if __name__ == "__main__":
    main()