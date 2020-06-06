import os
import zipfile
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import random
load_dotenv(verbose=True)


PROXY_PORT = 29842  # port
PROXY_USER = os.getenv("PROXY_USER")  # username
PROXY_PASS = os.getenv("PROXY_PASS")  # password


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


def background(host):
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (host, PROXY_PORT, PROXY_USER, PROXY_PASS)
    return background_js


def get_proxy():
    path = 'proxy.txt'
    with open(file=path, encoding='utf-8', mode='r') as reader:
        rows = reader.readlines()
    proxies = []
    for r in rows:
        proxies.append(r.replace(':29842', '').strip())
    return proxies


def get_chromedriver(background_js="", use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
        # chrome_options.add_experimental_option("detach", True)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        options=chrome_options)
    return driver


def rand():
    return random.randint(200, 999)


def get_url():
    return 'https://www.fastpeoplesearch.com/%s-%s-%s' % (rand(), rand(), rand())


def main():
    proxies = get_proxy()
    for proxy in proxies:
        back = background(host=proxy)
        driver = get_chromedriver(background_js=back, use_proxy=True)
        # #driver.get('https://www.google.com/search?q=my+ip+address')
        driver.get(get_url())
        time.sleep(10)


if __name__ == '__main__':
    main()
