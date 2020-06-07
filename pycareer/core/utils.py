import datetime
from dateutil import parser


class XLSXSheet:
    """A custom implementation class that takes an xslx sheet and provides some
    functionality around it.
    """

    def __init__(self, xlrd_sheet):
        """Custom initialization that passes things on to the super constructor
        and adds some custom data to be used with other things
        """
        self.sheet = xlrd_sheet
        self.column_names = [c.value for c in self.sheet.row(0)]

    def zip_row_with_cols(self, row):
        return dict(
            zip(
                self.column_names,
                [c.value for c in row]
            )
        )

    def get_column_names(self):
        return self.column_names

    def __iter__(self):
        """Creates an iterator for the data, initializing the idx of the
        iterator to 1 (the row after the column titles)
        """
        self.iter_idx = 1
        return self

    def __len__(self):
        return self.sheet.nrows

    def __getitem__(self, index):
        start = max(index.start, 1)
        stop = min(self.sheet.nrows, index.stop)

        rows = [
            self.sheet.row(idx)
            for idx in range(start, stop)
        ]

        return [self.zip_row_with_cols(r) for r in rows]

    def next(self):  # Python 3: def __next__(self)
        """Returns the next item while iterating, the iterators index is kept
        track of using self.iter_idx.

        :rtype: dict
        :returns: mapping of column name to value for row at self.iter_idx
        """
        if self.iter_idx < self.sheet.nrows:
            self.iter_idx += 1
            return self.zip_row_with_cols(
                self.sheet.row(self.iter_idx-1)
            )

        raise StopIteration


def xlsx_date_reader(value):
    """Because xlsx converts dates to an integer that is the number of days
    since a given time we must convert it to an appropriate format
    """
    if isinstance(value, basestring):
        return parser.parse(str(value)).date()

    try:
        days = int(float(value))
    except:
        return None

    return (
        datetime.datetime(1899, 12, 30) + datetime.timedelta(days=days)
    ).date()


def xlsx_str_reader(value):
    if isinstance(value, basestring):
        return value.strip()
    try:
        return str(int(value))
    except:
        return ''


def xlsx_empty_int_reader(value):
    if not value:
        return None
    try:
        return int(value)
    except:
        return None
