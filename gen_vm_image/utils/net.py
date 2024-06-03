import requests
import tqdm


def download_file(url, ouput_path, chunk_size=8192):
    with open(ouput_path, "wb") as _file:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))

            tqdm_params = {
                "desc": url,
                "total": total,
                "miniters": 1,
                "unit": "B",
                "unit_scale": True,
                "unit_divisor": 1024,
            }
            with tqdm.tqdm(**tqdm_params) as pb:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    pb.update(len(chunk))
                    _file.write(chunk)
