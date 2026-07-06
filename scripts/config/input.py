# scripts/config/input.py

# -< IMPORTS
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError

# -< IMPORTS: LOCAL
import scripts.config.colors as color
import scripts.config.definitions as define
import scripts.config.utils as util

# -< IMPORTS: RICH
from rich.console import Console
console = Console()
cw = console.width



# =<< INPUT FIELD
# --- --- --- --- --- --- --- ---
def input_field(caller="", config_type="", input_page="", stock_type="", placeholder=""):
    # GUARDS
    if caller == "":
        message = "no caller defined"
        util.pause(reason="w", message=message, enter="c")
        return None
    if (config_type != "" and stock_type != "") or (config_type == "" and stock_type == ""):
        message = "cannot have both config type and stock type defined" if config_type != "" and stock_type != "" else "one of config type or stock type must be defined"
        util.pause(reason="w", message=message, enter="c")
        return None

    # DEFINE INPUT MODE
    mode = f"{caller}_{config_type}_{input_page}"

    # DEFINE PLACEHOLDER TEXT AND FIELD WIDTH
    if caller == "search" or caller == "s":
        if placeholder == "":
            placeholder_text = "Enter Ticker Symbol" if stock_type == "PUBLIC" else "Enter Ccompany Name"
            field_width = 20 if stock_type == "PUBLIC" else int(cw // 1.25)
        else:
            placeholder_text = placeholder
            field_width = int(cw // 1.6)
    elif caller == "config" or caller == "c":
        if config_type == "structure":
            placeholder_text = "Enter name of key" if input_page == "add" else placeholder
        elif config_type == "portfolio":
            placeholder_text = placeholder
        else:
            placeholder_text = placeholder
    else:
            placeholder_text = placeholder
    f_width = int(cw // 1.25) if caller != "search" and caller != "s" else field_width

    # DEFINE STYLE AND VALIDATION
    style = Style.from_dict({
        "input-field":             f"{color.DOS}",
        "input-field.placeholder": f"{color.mute}",
    })

    # VALIDATE INPUT FIELD WIDTH
    class MaxLenValidator(Validator):
        def validate(self, document):
            if len(document.text) > f_width:
                raise ValidationError(message=f"Max {f_width} chars")

    # CREATE SESSION
    session = PromptSession(style=style, multiline=False, wrap_lines=False)

    # FORCE CAMELCASE, LOWERCASE OR UPPERCASE AS USER TYPES DEPENDING ON INPUT FIELD TYPE 
    @session.default_buffer.on_text_changed.add_handler
    def _(buffer):
        if caller == "search" or caller == "s":
            buffer.text = buffer.text.upper()
        elif config_type == "structure":
            buffer.text = util.camel_case(buffer.text)
        else:
            buffer.text = buffer.text.lower()

    # DEFINE PROMPT STYLE
    prompt = define.prompt_xrxs

    # PROMPT LOOP
    while True:
        # Pass prompt as a styled tuple list to match our style dict
        prompt_message = [("class:input-field", f"{prompt}")]

        text = session.prompt(
            prompt_message,
            placeholder=placeholder_text,
            validator=MaxLenValidator(),
            validate_while_typing=True,
        ).strip()

        if text:
            break

    return text