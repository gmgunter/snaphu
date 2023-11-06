#!/usr/bin/env python
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SNAPHU_URL = "https://web.stanford.edu/group/radar/softwareandlinks/sw/snaphu/"


def fetch_stanford_version_url() -> str:
    """
    Find the link to the latest version of "snaphu-vXXX.tar.gz" from the given URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to search for the snaphu tarball.

    Returns
    -------
    str
        The URL to the latest version of snaphu tarball if found, otherwise an empty string.

    """
    response = requests.get(SNAPHU_URL)
    response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    # Find all .tar.gz files
    tarball_links = [link for link in links if link.get("href", "").endswith(".tar.gz")]

    # Filter out the links that match the pattern "snaphu-vXXX.tar.gz"
    snaphu_links = [
        link for link in tarball_links if "snaphu-v" in link.get("href", "")
    ]

    if not snaphu_links:
        return ""

    # Assuming the latest version is the one with the highest version number
    latest_version_tar_name = sorted(
        snaphu_links, key=lambda x: x.get("href"), reverse=True
    )[0].get("href")

    latest_version = re.match(
        r"snaphu-v(\d+\.\d+\.\d+)", latest_version_tar_name
    ).group(1)
    # Join the relative URL with the base URL to form an absolute URL
    full_code_url = urljoin(SNAPHU_URL, latest_version_tar_name)

    return latest_version, full_code_url


def get_current_version_from_github_readme() -> str:
    """
    Get the current version of the code from the README file in the given GitHub repository.


    Returns
    -------
    str
        The current version of the code as mentioned in the README, or an empty string if not found.

    """
    # Convert the GitHub repo URL to the raw README URL
    readme_file = Path(__file__).parent.parent.parent / "README"
    readme = readme_file.read_text()

    # Use regular expression to find version patterns like 'vX.X.X' or 'X.X.X'
    for line in readme.splitlines():
        if version_match := re.match(r"Version\s+(\d+\.\d+\.\d+)", line):
            return version_match.group(1)
    else:
        raise ValueError(f"Failed to parse version from readme: {readme}")


if __name__ == "__main__":
    # Find and print the latest version URL
    remote_version, code_url = fetch_stanford_version_url()
    current_version = get_current_version_from_github_readme()

    if remote_version != current_version:
        print("::set-output name=new_version_available::true")
        print("::set-output name=remote_version::{remote_version}")
        print("TODO: Update local code...")
    else:
        print("::set-output name=new_version_available::false")
        print("Local version matches remote: nothing to do")
