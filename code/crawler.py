import urllib2
import zipfile
from os import path, pardir

from config import top1m_path


def get_top_1million_websites():
    filepath = path.join(pardir, "data", "top-1m.csv.zip")
    # download the file from the web if there is no local file
    if not path.exists(filepath):
        url = top1m_path
        download = urllib2.urlopen(url).read()
        with open(filepath, "wb") as output:
            output.write(download)
    # unzip the file
    with zipfile.ZipFile(filepath, "r") as top1m_file:
        # parse the file (append "http://www" to every entry and only pass
        # the url)
        top1mCSV = top1m_file.read(top1m_file.namelist()[0], "r")
        return ["http://www." + row.split(",")[1] for row
                in top1mCSV.split("\n")if row != ""]


if __name__ == "__main__":
    get_top_1million_websites()
