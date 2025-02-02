from audiobookdl import Source, logging, args, output, __version__
from audiobookdl.exceptions import AudiobookDLException
from .utils import dependencies
from .output.download import download
from .sources import find_compatible_source
from .config import load_config, Config

import os
import sys
from rich.prompt import Prompt
from typing import Optional
import traceback

def get_cookie_path(options) -> Optional[str]:
    """Find path to cookie file"""
    if options.cookie_file is not None and os.path.exists(options.cookie_file):
        return options.cookie_file
    if os.path.exists("./cookies.txt"):
        return "./cookies.txt"
    return None

def get_or_ask(attr: str, hidden: bool, source_name: str, options, config: Config) -> str:
    """Return `value` if it exists else asks for a value"""
    config_value = getattr(config.sources.get(source_name), attr, None)
    value: Optional[str] = getattr(options, attr, None) or config_value
    if value is None:
        return Prompt.ask(attr.capitalize(), password=hidden)
    return value

def login(source: Source, options, config: Config):
    login_data = {}
    for name in source.login_data:
        hidden = name == "password"
        login_data[name] = get_or_ask(name, hidden, source.name, options, config)
    source.login(**login_data)

def get_urls(options) -> list[str]:
    urls = []
    # Args
    urls.extend(options.urls)
    # File
    if options.input_file:
        with open(options.input_file, "r") as f:
            urls.extend(f.read().split())
    return urls

def run() -> None:
    """Main function"""
    # Parsing arguments
    options = args.parse_arguments()
    config = load_config()
    options.output_template = options.output_template or config.output_template
    # Applying arguments as global constants
    logging.debug_mode = options.debug
    logging.quiet_mode = options.quiet
    logging.ffmpeg_output = options.ffmpeg_output or options.debug
    logging.debug(f"audiobook-dl {__version__}", remove_styling=True)
    logging.debug(f"python {sys.version}", remove_styling=True)
    urls = get_urls(options)
    if not urls:
        logging.simple_help()
        exit()
    try:
        dependencies.check_dependencies(options)
        for url in urls:
            run_on_url(url, options, config)
    except AudiobookDLException as e:
        e.print()
        traceback.print_exc()
        exit(1)

def run_on_url(url: str, options, config: Config):
    logging.log("Finding compatible source")
    s = find_compatible_source(url)
    # Load cookie file
    cookie_path = get_cookie_path(options)
    if cookie_path is not None:
        s.load_cookie_file(cookie_path)
    # Adding username and password
    if s.supports_login and not s.authenticated:
        login(s, options, config)
    # Running program
    if options.print_output:
        print_output(s, options)
    elif options.cover:
        download_cover(s)
    else:
        download(s, options)


def print_output(source: Source, options):
    """Prints output location"""
    source.prepare()
    meta = source.get_metadata()
    location = output.gen_output_location(options.template, meta, options.remove_chars)
    print(location)


def download_cover(source: Source):
    source.prepare()
    cover = source.get_cover()
    if cover:
        with open(f"cover.{cover.extension}", "wb") as f:
            f.write(cover.image)

if __name__ == "__main__":
    run()
