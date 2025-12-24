import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
import warnings
import json

class PageOwnerNotFoundError(Exception):
    """Raised when the central user (page owner) cannot be identified."""

    def __init__(self, username=None):
        self.username = username
        message = "Page owner is not in the list"
        if username:
            message = f"User '{username}' is not in the subscription list"

        super().__init__(message)


class PageOwnerNotFoundWarning(Warning):
    """Warning raised when the page owner is not found in the data."""
    def __init__(self, username, message=None):
        self.username = username
        if message is None:
            message = f"Page owner '{username}' is not in the list. You may want to check how you wrote the username."
        self.message = message
        super().__init__(self.message)

working_dir = os.getcwd()
all_files = os.listdir(f"{working_dir}/insta_follow")
current_nodes = [Path(nick).stem for nick in all_files]


def get_all_subscribers(html_path):
    with open(html_path) as f:
        raw_html = f.read()

    soup = BeautifulSoup(raw_html, 'html.parser')
    raw_nicks = soup.find_all('span', class_='_ap3a _aaco _aacw _aacx _aad7 _aade')
    nickname = Path(html_path).stem
    nicks = [nick.text for nick in raw_nicks if nick.text != 'chanelofficial']
    if nickname not in nicks:
        warnings.warn(PageOwnerNotFoundWarning(nickname))
    else:
        nicks.remove(nickname)

    return nicks

graph_dict = dict()
for html_file in all_files:
    html_path = f"{working_dir}/insta_follow/{html_file}"
    nickname = Path(html_path).stem
    subscriptions = get_all_subscribers(html_path)
    graph_dict[nickname] = subscriptions


with open('fs_inst_following.json', 'w') as file:
    json.dump(graph_dict, file, indent=2, ensure_ascii=False)
