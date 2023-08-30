import configparser

def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def get_language_term_pairs(config):
    language_term_section = config['LANGUAGE_TERM_PAIRS']
    return {
        language: [term.strip() for term in terms.split(',')]
        for language, terms in language_term_section.items()
    }
