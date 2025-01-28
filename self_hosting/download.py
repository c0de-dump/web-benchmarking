import asyncio
import os
import shutil
import pathlib
from typing import List

from wget import Wget


def generate_caddy_file(pairs, path):
    headers = "\n".join([pair.generate_caddy_style_headers() for pair in pairs])
    return f"""{{
    auto_https off
}}
    http://*:80 {{
    root * {path}
    file_server
    bind 0.0.0.0
    {headers}
}}

"""


class HeadersResponsePair:
    def __init__(self, path):
        with open(path, "rb", encoding=None) as f:
            file_content = f.read()
        file_content.split(b"\r\n\r\n")
        headers, body = file_content.split(b'\r\n\r\n', 1)
        self.headers = headers.decode().split("\r\n")[1:]
        self.body = body
        self.path = path.split("?")[0]

    def generate_caddy_style_headers(self):
        caddy_headers = ""
        for header in self.headers:
            key, value = header.split(": ", 1)
            if key.lower() != "cache-control":
                continue
            caddy_headers += f"\theader {self.path} {key.lower()} {value.replace(' ', '')}\n"
        return caddy_headers


def parse_responses(root_path):
    pairs = []
    for file in os.listdir(root_path):
        if os.path.isdir(root_path + "/" + file):
            pairs = pairs + parse_responses(root_path + "/" + file)
            continue
        path = f"{root_path}/{file}"
        pair = HeadersResponsePair(path)
        pairs.append(pair)
    return pairs


def write_files_to_serve(root_path, pairs):
    for pair in pairs:
        with open(concat_paths(root_path, pair.path), "wb+") as f:
            f.write(pair.body)


def normalize_pair_paths(pairs: List[HeadersResponsePair], root_dir):
    for pair in pairs:
        pair.path = pair.path.replace(root_dir, "")


def write_output_file(content: str, path: str):
    with open(path, "w+") as f:
        f.write(content)


def concat_paths(p1, p2):
    if p1.endswith("/"):
        p1 = p1[:-1]
    if p2.startswith("/"):
        p2 = p2[1:]

    return f"{p1}/{p2}"


def self_host(website: str, caddy_serve_dir: str, caddyfile_path="./Caddyfile"):
    download_dir = "downloads"

    downloader = Wget(download_dir)
    directory = downloader.download(website)
    pairs = parse_responses(directory)
    normalize_pair_paths(pairs, download_dir)

    caddyfile = generate_caddy_file(pairs, caddy_serve_dir)
    write_output_file(caddyfile, caddyfile_path)

    website_files_path = concat_paths(caddy_serve_dir, directory.replace(download_dir, ""))
    pathlib.Path(website_files_path).mkdir(parents=True, exist_ok=True)

    write_files_to_serve(caddy_serve_dir, pairs)

    shutil.rmtree(directory)

    return directory.replace(download_dir, "")



async def main():
    downloader = Wget("downloads")
    directory = downloader.download("https://google.com/")
    pairs = parse_responses(directory)
    caddyfile = generate_caddy_file(pairs, "/home/divar/websites")

    # if os.path.exists(f"/home/divar/websites/{directory}"):
    #     shutil.rmtree(f"/home/divar/websites/{directory}")
    # os.mkdir(f"/home/divar/websites/{directory}")
    # write_files_to_serve("/home/divar/websites", pairs)
    # shutil.copy("./sw.js", f"/home/divar/websites/{directory}")
    print(caddyfile)


if __name__ == '__main__':
    asyncio.run(main())
