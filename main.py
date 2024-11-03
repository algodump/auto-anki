from env import Env
import anki
import logging
import notion
import ai
import json

def main():
    Env.init()
    logging.basicConfig(level=logging.DEBUG)

    # TODO: make anki deck name command line argument 
    # TODO: make word list as command line argument as well (choose from file or notion)
    anki_deck_name = "test_words"
    Env.export("CURRENT_ANKI_DECK_NAME", anki_deck_name)

    if notion.check_for_updates():
        words_to_learn = notion.retrieve_words()

        ai_model = ai.Gpt4All(prompt_name="translate_dutch_words_and_generate_example.txt", words=words_to_learn)
        ai_response = ai_model.generate_response()
        json_response = ai_response[ai_response.index("{"):]
        words_with_examples = json.loads(json_response)["words"]

        anki_client = anki.Anki()
        anki_client.add_words_to_deck(
            anki_client.create_deck(anki_deck_name),
            anki_client.create_model("my_super_dutch_deck_model"),
            words_with_examples)
    else:
        logging.info("Everything is up to date, no new words were added to the Notion page.")

if __name__ == "__main__":
    main()