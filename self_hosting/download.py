import asyncio
import os
import shutil


def generate_caddy_file(pairs, path):
    headers = "\n".join([pair.generate_caddy_style_headers() for pair in pairs])
    return f"""http://localhost:80 {{
    root * {path}
    file_server

{headers}
}}"""


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
            caddy_headers += f"\theader /{self.path} {key} {value}\n"
        return caddy_headers


def parse_responses(root_path):
    pairs = []
    for file in os.listdir(root_path):
        path = f"{root_path}/{file}"
        pair = HeadersResponsePair(path)
        pairs.append(pair)
    return pairs


def write_files_to_serve(root_path, pairs):
    for pair in pairs:
        with open(f"{root_path}/{pair.path}", "wb") as f:
            f.write(pair.body)


async def main():
    # downloader = AsyncWget(".")
    # directory = await downloader.download("https://www.varzesh3.com")
    directory = "varzesh3"
    pairs = parse_responses(directory)
    caddyfile = generate_caddy_file(pairs, "/home/divar/websites")
    if os.path.exists("/home/divar/websites/varzesh3"):
        shutil.rmtree(f"/home/divar/websites/{directory}")
    os.mkdir(f"/home/divar/websites/{directory}")
    write_files_to_serve("/home/divar/websites", pairs)
    print(caddyfile)


if __name__ == '__main__':
    asyncio.run(main())
