from typing import Union

class myField:
    """
    This class represents a REDCap field (i.e. variable).

    field : str
        The name or label of the field in REDCap
    event : Optional[Union[str, None]]
        Specifies if the field belongs in a different event or instrument.
    check : Optional[Union[str, None]]
        Specifies if the field refers to a value within a checkbox
    """
    def __init__(self, field: str, event: Union[str, None] = None, check: Union[str, None] = None) -> None:
        self.field: str = field
        self.event: Union[str, None] = event
        self.check: Union[str, None] = check
    
    def __str__(self) -> str:
        if self.event:
            event_string: str = f"[{self.event}]"
        else:
            event_string: str = ""
        if self.check:
            field_string: str = f"[{self.field}({self.check})]"
        else:
            field_string: str = f"[{self.field}]"

        return f"{event_string}{field_string}"

    def __repr__ (self) -> str:
        return f"myField({self.field}, event={self.event}, check={self.check})"