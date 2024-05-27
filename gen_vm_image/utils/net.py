import requests
import tqdm
import shutil


def download_file(url, ouput_path):
    with requests.get(url, stream=True) as r:
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            # Save the output
            with open(ouput_path, "wb") as output:
                shutil.copyfileobj(raw, output)
