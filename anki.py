import json
import urllib.request
import logging

# Taken from https://foosoft.net/projects/anki-connect/
def request(action, **params):
    if not params:
        return {'action': action, 'version': 6}

    params_provided = params.get('params', None)
    if params_provided:
        return {'action': action, 'params': params_provided, 'version': 6}
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

class Deck():
    def __init__(self, deck_name):
        self.deck_name = deck_name

    def name(self):
        return self.deck_name

    def exist(self):
        decks = invoke("deckNames")
        return self.deck_name in decks

    def create_anki_deck(self):
        if self.exist():
            logging.debug(f"Deck: {self.deck_name}, already exists")
        else:
            logging.debug(f"Creating anki deck: {self.deck_name}")
            invoke('createDeck', deck=self.deck_name)

# TODO: make it more customizable 
class DutchDeckModel():
    def __init__(self, model_name):
        self.model_name = model_name
        self.fields = ["Word", "Word_Translation", "Example", "Example_Translation"]
    
    def fields(self):
        return self.fields

    def template(self):
        return {
            "modelName" : f"{self.model_name}",
            "inOrderFields" : self.fields,
            "cardTemplates" : [
                {
                    "Name": "Card",
                    "Front": "{{Word}}<br>\n{{Word_Translation}}\n{{tts nl_NL voices=AwesomeTTS:Word}}",
                    "Back": "{{FrontSide}}\n<hr id=answer>\n{{Example}}\n{{tts nl_NL voices=AwesomeTTS:Example}}<hr id=answer>\n{{Example_Translation}}"
                }
            ]
        };

    def create_anki_model(self):
        model_names = invoke("modelNames")
        if self.model_name in model_names:
            logging.debug(f"Skip model creating, since it's already created")
        else:
            logging.debug(f"Creating model: `{self.model_name}`")
            invoke("createModel", params=self.template())

    def generate_note(self, deck_name, **given_fields):
        actual_fields = {field : given_fields[field] for field in self.fields}
        return {
            "deckName" : f"{deck_name}",
            "modelName" : f"{self.model_name}",
            "fields": actual_fields,
            "options" : {
                "allowDuplicate": False
            }
        }

class Anki():
    def __init__(self):
        pass

    def create_deck(self, deck_name):
        deck = Deck(deck_name)
        deck.create_anki_deck()
        return deck
    
    def create_model(self, model_name):
        model = DutchDeckModel(model_name)
        model.create_anki_model()
        return model

    def add_words_to_deck(self, deck, model, words_with_examples):
        notes = []
        for example in words_with_examples:
            note = model.generate_note(deck.name(), 
                                       Word = example["word"],
                                       Word_Translation = example["word_translation"],
                                       Example = example["example_in_dutch"],
                                       Example_Translation = example["translation_of_example"])
            notes.append(note)
        notes_status = invoke("canAddNotesWithErrorDetail", notes = notes)
        
        # TODO: What is better sending one big request or a lot of small requests??? Mb "addNotes" is better
        for (note_index, note) in enumerate(notes):
            word = words_with_examples[note_index]["word"]
            if notes_status[note_index]['canAdd']:
                logging.info(f"Adding word: `{word}` to anki deck")
                invoke("addNote", note = note)
            else:
                error_description = notes_status[note_index]['error']
                if "cannot create note because it is a duplicate" in error_description:
                    logging.info(f"Skip word `{word}` because it's already in the deck")
                else:
                    logging.info(f"Word `{word}` was not added, error: `{error_description}`")

    def verify_connection(self):
        #TODO: check if anki client is running and if anki-connect is installed
        pass