# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Utility classes to provide a graphical interface to paperfetcher handsearch and snowballsearch classes.
"""
import ipywidgets
from IPython.display import display
import os

from paperfetcher import handsearch, parsers, snowballsearch


class CrossrefHandSearchDOIWidget:
    def __init__(self, default_save_location="./"):
        self.name = ipywidgets.Text(
            value='untitled',
            disabled=False
        )
        self.issn_list = ipywidgets.Textarea(
            placeholder='Comma-separated ISSNs',
            disabled=False
        )
        self.keyword_list = ipywidgets.Textarea(
            placeholder='Comma-separated keywords',
            disabled=False
        )
        self.from_date = ipywidgets.DatePicker(
            disabled=False
        )
        self.until_date = ipywidgets.DatePicker(
            disabled=False
        )
        self.save_location = ipywidgets.Text(
            value=default_save_location,
            disabled=False
        )
        self.output_format = ipywidgets.ToggleButtons(
            options=[('Plain text (.txt)', 'txt'),
                     ('CSV (.csv)', 'csv'),
                     ('Excel (.xlsx)', 'excel')],
            disabled=False,
            button_style='',
        )
        self.search_button = ipywidgets.Button(
            description='Search',
            disabled=False,
            button_style='',
            icon='check'  # (FontAwesome names without the `fa-` prefix)
        )

    def execute_search(self, b):
        # Disable click while search is being performed
        self.search_button._click_handlers.callbacks = []

        ISSNs = list(self.issn_list.value.strip().split(","))
        if self.keyword_list.value is not None and self.keyword_list.value != "":
            keywords = list(self.keyword_list.value.strip().split(","))
        else:
            keywords = None
        fromd = self.from_date.value
        untild = self.until_date.value

        for issn in ISSNs:
            print("Searching ISSN: %s" % issn)
            search = handsearch.CrossrefSearch(ISSN=issn,
                                               keyword_list=keywords,
                                               from_date=fromd,
                                               until_date=untild)
            search(select=True, select_fields=["DOI"])
            doi_ds = search.get_DOIDataset()

            # Check if save location exists, if not, create it
            if not os.path.exists(self.save_location.value):
                os.makedirs(self.save_location.value)

            if self.output_format.value == 'txt':
                doi_ds.save_txt(self.save_location.value + "/{}_{}.txt".format(self.name.value, issn))
            elif self.output_format.value == 'csv':
                doi_ds.save_csv(self.save_location.value + "/{}_{}.csv".format(self.name.value, issn))
            elif self.output_format.value == 'excel':
                doi_ds.save_excel(self.save_location.value + "/{}_{}.xlsx".format(self.name.value, issn))
            else:
                raise ValueError("Undefined output format.")

        # Enable click again
        self.search_button.on_click(self.execute_search)

    def __call__(self):
        items = [ipywidgets.Label('Name of search (A-Za-z0-9):'), self.name,
                 ipywidgets.Label('ISSNs:'), self.issn_list,
                 ipywidgets.Label('Search keywords:'), self.keyword_list,
                 ipywidgets.Label('Fetch from this date onwards:'), self.from_date,
                 ipywidgets.Label('Fetch until this date:'), self.until_date,
                 ipywidgets.Label('Location to save DOIs:'), self.save_location,
                 ipywidgets.Label('Output format for DOIs:'), self.output_format,
                 self.search_button, ipywidgets.Label('')]
        self.search_button.on_click(self.execute_search)
        display(ipywidgets.GridBox(items, layout=ipywidgets.Layout(grid_template_columns="400px 600px")))


class CrossrefHandSearchCitationsWidget:
    def __init__(self, default_save_location="./"):
        self.name = ipywidgets.Text(
            value='untitled',
            disabled=False
        )
        self.issn_list = ipywidgets.Textarea(
            placeholder='Comma-separated ISSNs',
            disabled=False
        )
        self.keyword_list = ipywidgets.Textarea(
            placeholder='Comma-separated keywords',
            disabled=False
        )
        self.from_date = ipywidgets.DatePicker(
            disabled=False
        )
        self.until_date = ipywidgets.DatePicker(
            disabled=False
        )
        self.fields = ipywidgets.SelectMultiple(
            options=[('DOI', 'DOI'),
                     ('URL', 'URL'),
                     ('Title', 'title'),
                     ('Authors', 'author'),
                     ('Publication Date', 'issued')],
            value=['DOI', 'URL', 'title', 'author', 'issued'],
            disabled=False
        )
        self.save_location = ipywidgets.Text(
            value=default_save_location,
            disabled=False
        )
        self.output_format = ipywidgets.ToggleButtons(
            options=[('Plain text (.txt)', 'txt'),
                     ('CSV (.csv)', 'csv'),
                     ('Excel (.xlsx)', 'excel')],
            disabled=False,
            button_style='',
        )
        self.search_button = ipywidgets.Button(
            description='Search',
            disabled=False,
            button_style='',
            icon='check'  # (FontAwesome names without the `fa-` prefix)
        )

    def execute_search(self, b):
        # Disable click while search is being performed
        self.search_button._click_handlers.callbacks = []

        ISSNs = list(self.issn_list.value.strip().split(","))
        if self.keyword_list.value is not None and self.keyword_list.value != "":
            keywords = list(self.keyword_list.value.strip().split(","))
        else:
            keywords = None
        fromd = self.from_date.value
        untild = self.until_date.value

        field_list = []
        field_parsers = []

        for field in self.fields.value:
            field_list.append(field)
            if field == "DOI":
                field_parsers.append(None)
            elif field == "URL":
                field_parsers.append(None)
            elif field == "title":
                field_parsers.append(parsers.crossref_title_parser)
            elif field == "author":
                field_parsers.append(parsers.crossref_authors_parser)
            elif field == "issued":
                field_parsers.append(parsers.crossref_date_parser)
            else:
                raise NotImplementedError("Cannot parse field {}.".format(field))

        for issn in ISSNs:
            print("Searching ISSN: %s" % issn)
            search = handsearch.CrossrefSearch(ISSN=issn,
                                               keyword_list=keywords,
                                               from_date=fromd,
                                               until_date=untild)
            search(select=True, select_fields=field_list)
            cit_ds = search.get_CitationsDataset(field_list=field_list,
                                                 field_parsers_list=field_parsers)
            if self.output_format.value == 'txt':
                cit_ds.save_txt(self.save_location.value + "/{}_{}.txt".format(self.name.value, issn))
            elif self.output_format.value == 'csv':
                cit_ds.save_csv(self.save_location.value + "/{}_{}.csv".format(self.name.value, issn))
            elif self.output_format.value == 'excel':
                cit_ds.save_excel(self.save_location.value + "/{}_{}.xlsx".format(self.name.value, issn))
            else:
                raise ValueError("Undefined output format.")

        # Enable click again
        self.search_button.on_click(self.execute_search)

    def __call__(self):
        items = [ipywidgets.Label('Name of search (A-Za-z0-9):'), self.name,
                 ipywidgets.Label('ISSNs:'), self.issn_list,
                 ipywidgets.Label('Search keywords:'), self.keyword_list,
                 ipywidgets.Label('Fetch from this date onwards:'), self.from_date,
                 ipywidgets.Label('Fetch until this date:'), self.until_date,
                 ipywidgets.Label('Fields to fetch (Shift + click to select multiple):'), self.fields,
                 ipywidgets.Label('Location to save DOIs:'), self.save_location,
                 ipywidgets.Label('Output format for DOIs:'), self.output_format,
                 self.search_button, ipywidgets.Label('')]
        self.search_button.on_click(self.execute_search)
        display(ipywidgets.GridBox(items, layout=ipywidgets.Layout(grid_template_columns="400px 600px")))


class CrossrefSnowballSearchDOIWidget:
    def __init__(self, default_save_location="./"):
        self.name = ipywidgets.Text(
            value='untitled_snowball',
            disabled=False
        )
        self.doi_list = ipywidgets.Textarea(
            placeholder='Comma-separated DOIs',
            disabled=False
        )
        self.save_location = ipywidgets.Text(
            value=default_save_location,
            disabled=False
        )
        self.search_button = ipywidgets.Button(
            description='Search',
            disabled=False,
            button_style='',
            icon='check'  # (FontAwesome names without the `fa-` prefix)
        )

    def execute_search(self, b):
        # Disable click while search is being performed
        self.search_button._click_handlers.callbacks = []

        DOIs = list(self.doi_list.value.strip().split(","))

        search = snowballsearch.CrossrefSearch(DOIs)
        search()
        doi_ds = search.get_DOIDataset()

        # Check if save location exists, if not, create it
        if not os.path.exists(self.save_location.value):
            os.makedirs(self.save_location.value)

        doi_ds.save_txt(self.save_location.value + "/{}.txt".format(self.name.value))

        # Enable click again
        self.search_button.on_click(self.execute_search)

    def __call__(self):
        items = [ipywidgets.Label('Name of search (A-Za-z0-9):'), self.name,
                 ipywidgets.Label('Search DOIs:'), self.doi_list,
                 ipywidgets.Label('Location to save result DOIs:'), self.save_location,
                 self.search_button, ipywidgets.Label('')]
        self.search_button.on_click(self.execute_search)
        display(ipywidgets.GridBox(items, layout=ipywidgets.Layout(grid_template_columns="400px 600px")))
