# Global configuration
import logging


class GlobalConfig:
    ############################################################################
    # Streamlit config
    ############################################################################

    # Change this to True if using paperfetcher from streamlit
    # This is required for streamlit to display progress (by switching from tqdm to stqdm)
    streamlit = False

    ############################################################################
    # Crossref API config
    ############################################################################

    # Crossref settings
    crossref_useragent = "paperfetcher/0.0.1 (https://github.com/paperfetcher/paperfetcher; mailto:pallathakash@gmail.com)"
    # Set this to True if you wish to use Crossref Plus
    crossref_plus = False
    # Enter your Crossref Plus API auth token here
    crossref_plus_auth_token = ""

    ############################################################################
    # Logging config
    ############################################################################

    loglevel = logging.INFO
