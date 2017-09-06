"""Defines Entries (data model rows built from fields)."""

from __future__ import unicode_literals
import datetime as dt

from schematics.types import ListType, ModelType, StringType, FloatType, \
        DateType, IntType
from schematics.models import Model as SchematicsModel

from .config import CONFIG
DATE_FORMAT = CONFIG["DATABASE"]["date_format"]


NameItem = StringType
CategoryItem = StringType
ValueItem = FloatType
SumItem = FloatType
DateItem = DateType
DateItem.SERIALIZED_FORMAT = DATE_FORMAT


class Entry(SchematicsModel):
    """Base class storing the 'name' field in lowercase."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.lower()

class BaseEntry(Entry):
    """Innermost element of the Model, child of a CategoryEntry. Holds
    information on name, value and date."""
    name = NameItem(min_length=1)
    value = ValueItem()
    # support legacy format
    date = DateItem(formats=("%Y-%m-%d", DATE_FORMAT), default=dt.date.today())
    eid = IntType(default=0)

    ITEM_TYPES = ["name", "value", "date"]

    NAME_LENGTH = 16
    VALUE_LENGTH = 8 # 00000.00
    VALUE_DIGITS = 2
    DATE_LENGTH = 5 # mm-dd
    SHOW_EID = True
    EID_LENGTH = 3 if SHOW_EID else 0
    # add spaces separating name/value, value/date and date/eid
    TOTAL_LENGTH = NAME_LENGTH + VALUE_LENGTH + DATE_LENGTH + EID_LENGTH + \
            3 if SHOW_EID else 2

    @classmethod
    def from_tinydb(cls, element):
        """Create a BaseEntry from a TinyDB Element or a dict. In the first
        case, the entry eid is copied, otherwise it defaults to -1.
        """

        try:
            element.update({"eid": element.eid})
        except AttributeError:
            # element is dict, not tinydb.database.Element
            pass
        return cls(raw_data=element)

    def __str__(self):
        """Return a formatted string representing the entry. The value is
        rendered absolute."""
        capitalized_name = " ".join([s.capitalize() for s in self.name.split()])
        string = "{name:{0}.{0}} {value:>{1}.{2}f} {date}".format(
                self.NAME_LENGTH, self.VALUE_LENGTH, self.VALUE_DIGITS,
                name=capitalized_name,
                value=abs(self.value),
                date=self.date_str
                )
        if self.SHOW_EID:
            string += " {1:{0}d}".format(self.EID_LENGTH, self.eid)
        return string

    @property
    def date_str(self):
        """Convenience method to return formatted date."""
        return DateItem().to_primitive(self.date)


class CategoryEntry(Entry):
    """First child of the model, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""
    name = CategoryItem(min_length=1)
    value = SumItem(default=0.0)
    entries = ListType(ModelType(BaseEntry), default=[])

    ITEM_TYPES = ["name", "sum", "empty"]
    DEFAULT_NAME = CONFIG["DATABASE"]["default_category"]

    BASE_ENTRY_INDENT = 2
    NAME_LENGTH = BaseEntry.NAME_LENGTH + BASE_ENTRY_INDENT
    TOTAL_LENGTH = BaseEntry.TOTAL_LENGTH + BASE_ENTRY_INDENT

    def __str__(self):
        """Return a formatted string representing the entry including its
        children (i.e. BaseEntries). The category representation is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented. The value is rendered absolute.
        """

        capitalized_name = " ".join([s.capitalize() for s in self.name.split()])
        lines = [
                "{name:{0}.{0}} {value:>{1}.{2}f}".format(
                    self.NAME_LENGTH, BaseEntry.VALUE_LENGTH, BaseEntry.VALUE_DIGITS,
                    name=capitalized_name,
                    value=abs(self.value)
                    ).ljust(self.TOTAL_LENGTH)
                ]

        for entry in self.entries:
            lines.append("  " + str(entry))

        return '\n'.join(lines)


def create_base_entry(name, value, date=None):
    """Factory method for convenience."""
    data = {"name": name, "value": value}
    if date is not None:
        data["date"] = date
    return BaseEntry(data)
