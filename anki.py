import json
import urllib.request
import logging

# Taken from https://foosoft.net/projects/anki-connect/
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    try:
        requestJson = json.dumps(request(action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    except Exception as e:
        logging.error(f"Error ocurred while sending request to anki: {e}")

def verify_connection():
    pass
    #TODO: check if anki client is running and if anki-connect is installed

def update_deck(deck_name: str, words: list):
    if not exist(deck_name):
        create_deck(deck_name)
    add_words_to_deck(deck_name, words)

def exist(deck_name):
   decks = invoke("deckNames")
   return deck_name in decks

def create_deck(deck_name):
    invoke('createDeck', deck=deck_name)

def generate_note(deck_name, front, back):
    # TODO: create your own model
    return {
        "deckName" : f"{deck_name}",
        "modelName" : "Basic",
        "fields": {
            "Front": f"{front}",
            "Back": f"{back}"
        },
        "options" : {
            "allowDuplicate": False
        }
    }

def add_words_to_deck(deck_name, words):
    # TODO: query LLM for translation and example
    notes = [generate_note("test_dutch_words", word, "not_implemented") for word in words]
    notes_status = invoke("canAddNotesWithErrorDetail", notes = notes)
    
    # TODO: What is better sending one big request or a lot of small requests??? Mb "addNotes" is better
    for (note_index, note) in enumerate(notes):
        if notes_status[note_index]['canAdd']:
            logging.info(f"Adding word: `{words[note_index]}` to anki deck")
            invoke("addNote", note = note)
        else:
            error_description = notes_status[note_index]['error']
            if "cannot create note because it is a duplicate" in error_description:
                logging.info(f"Skip word `{words[note_index]}` because it's already in the deck")
            else:
                logging.info(f"Word `{words[note_index]}` was not added, error: `{error_description}`")
