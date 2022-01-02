# Global configuration


class GlobalConfig:
    # Change this to True if using paperfetcher from strealit
    # This is required for strealit to display progress (by switching from tqdm to stqdm)
    streamlit = False

    # Crossref settings
    crossref_useragent = "paperfetcher/0.0.1 (https://github.com/paperfetcher/paperfetcher; mailto:pallathakash@gmail.com)"
    # Set this to True if you wish to use Crossref Plus
    crossref_plus = False
    # Enter your Crossref Plus API auth token here
    crossref_plus_auth_token = ""
