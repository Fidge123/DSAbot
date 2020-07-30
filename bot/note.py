import re
import random

from bot import persistence


def parse(message):
    return re.search(
        r"^note:(?P<id>[a-z]*)->(?P<number>(\+|-)?[0-9]*)$", message, re.IGNORECASE,
    )


def create_response(regex_result, number_notes):
    if regex_result:

        if not (regex_result.group("id") in number_notes):
            number_notes[regex_result.group("id")] = 0

        number_notes[regex_result.group("id")] += int(regex_result.group("number"))
        response = "{} is now {}".format(
            regex_result.group("id"), number_notes[regex_result.group("id")]
        )
        persistence.persist_note(
            regex_result.group("id"), number_notes[regex_result.group("id")]
        )
        return response
