import os
import sys

import click
import sqlite3
from .errors import ConfigFileError
from .utils import fetch_word, save_api_key, load_api_key, save_word, get_words, check_initialization, tabulate_words, initialize_db, initialize_application, has_api_key, has_db, format_words

HOME_DIR = os.path.expanduser('~') # User's Home Directory
# Base Directory to store all data related to the application.
BASE_DIR = os.path.join(HOME_DIR, '.lexico')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
WORDS_FILE = os.path.join(BASE_DIR, 'words.json')
DB_FILE = os.path.join(BASE_DIR, 'vocabulary.db')

@click.group()
def lexico():
    '''Your personal glossarist to help you expand your English vocabulary.'''
    #TODO: Add option for debugging.
    pass

@lexico.command()
@click.argument('word', required=False, default=None)
def add(word):
    '''Finds the dictionary data about a word.'''
    #TODO: raise error
    if word is None:
        word = click.prompt('Enter the word', type=str)
        word = word.lower()
    try:
        word_data = fetch_word(word)
    except ConfigFileError:
        click.echo('You need to initialize the application.')
        click.echo('Run:\n\t\t $ lexico init')
    else:
        click.echo_via_pager(word_data.stringify())


@lexico.command()
def init():
    '''Helps you get started with using "lexico".

    Save your Wordnik API Key.
    '''

    # Step 01: Check if application folder exists.
    # Step 02: Create it if necessary.
    # Step 03: Check if API Key is already provided.
    # Step 04: If API Key is not provided, prompt for input.
    # Step 05: Check if DB_FILE exists
    # Step 06: If not, then create necessary tables.

    is_initialized = check_initialization()
    if not is_initialized:
        initialize_application()

    is_key_present = has_api_key()
    if not is_key_present:
        # TODO: Move the instructions for registration to README and link them here.
        click.echo('In order to fetch information, this services requires you' \
               ' to provide a Wordnik API key.\n' \
               'Visit http://www.wordnik.com/signup to SignUp.')

        # Step 01: Save the API Key
        api_key = click.prompt('Enter your Wordnik API key').strip()
        save_status = save_api_key(api_key)
        if save_status:
            click.echo('Your API Key has been saved successfully\n')
        else:
            click.echo('There is some issue with saving your API key. Kindly retry.')

    is_db_initialized = has_db()
    if not is_db_initialized:
        is_init = initialize_db()
        if not is_init:
            click.echo('There is some issue with initializing your dictionary. Kindly retry.')
            sys.exit(1)

    click.echo('Your personal dictionary has been initialised.\n' \
               'In order to learn how to use it, try:\n\n$ lexico --help\n')


@lexico.command()
@click.option('--extra', default='meaning',help='Displays an additional column with information of your choice')
def view(extra):
    '''Lists all the words present in your dictionary.'''
    #TODO: Option for file output
    #TODO: More information/table columns
    words = get_words()
    words1=[]
    for x in words:
     x=list(x)
     id1=int(x[0])
     selectq="SELECT text FROM Vocabulary WHERE word_id =(?) AND type=(?)"
     with sqlite3.connect(DB_FILE) as connection:
      cursor = connection.cursor()
      cursor.execute(selectq,[id1,extra])
      info=cursor.fetchone()
      x.append(info)
      x=tuple(x)
      words1.append(x)
    formatted_words = format_words(words1)
    display_words = tabulate_words(formatted_words,extra)
    click.echo_via_pager(display_words)
