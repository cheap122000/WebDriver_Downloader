# WebDriver Downloader
from genericpath import exists
import platform
import os
import plistlib
import requests
import cpuinfo
import subprocess
import json
import re
import shutil
from selenium.webdriver import Chrome, Firefox, Edge, Safari
import time
import zipfile

def get_file_version(file_path):
    from win32com import client as wincom_client
    if not os.path.isfile(file_path):
        raise FileNotFoundError("{!r} is not found.".format(file_path))

    wincom_obj = wincom_client.Dispatch('Scripting.FileSystemObject')
    version = wincom_obj.GetFileVersion(file_path)
    return version.strip()

def download_driver(download_uri, save_dir, web_browser, wd_info, last_driver_ver):
    if wd_info.get(web_browser):
        if wd_info[web_browser] == last_driver_ver:
            return False, ""

    resp = requests.get(download_uri, stream=True, timeout=300)
    if resp.status_code == 200:
        file_name = download_uri.split("/")[-1]
        with open(os.path.join(save_dir, file_name), "wb") as f:
            f.write(resp.content)
        return True, os.path.join(save_dir, file_name)
    else:
        raise Exception("Download chrome driver failed")

def unzip_driver(current_os, file_path, file_dir):
    if current_os == "darwin":
        if file_path.endswith(".zip"):
            process = subprocess.Popen(['unzip', '-o', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
            
        elif file_path.endswith(".tar.gz"):
            process = subprocess.Popen(['tar', '-xvf', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
        os.remove(file_path)
        if file_path.find("edgedriver") != -1:
            shutil.rmtree(os.path.join(file_dir, "Driver_Notes"))
    elif current_os == "windows":
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(file_dir)
        os.remove(file_path)
        if file_path.find("edgedriver") != -1:
            shutil.rmtree(os.path.join(file_dir, "Driver_Notes"))

def save_wd_info(save_path, web_browser, version, wd_info):
    wd_info[web_browser] = version
    with open(save_path, "w", encoding="utf8") as f:
        f.write(json.dumps(wd_info))

def get_webdriver(web_browser, save_dir):
    current_os = platform.system().lower()
    cpu = 'arm' if 'm1' in cpuinfo.get_cpu_info().get('brand_raw').lower() else 'x86_64'
    wd_info = {}
    web_browser = web_browser.lower()

    wd_info_path = os.path.join(save_dir, "wd_info.json")
    if os.path.exists(wd_info_path):
        with open(wd_info_path, "r", encoding="utf8") as f:
            wd_info = json.loads(f.read())

    if web_browser == "chrome":
        if current_os == "darwin":
            if not os.path.exists("/Applications/Google Chrome.app"):
                raise FileNotFoundError("You haven't installed Chrome.")
            else:
                plistloc = "/Applications/Google Chrome.app/Contents/Info.plist"
                with open(plistloc, 'rb') as f:
                    wd_version = plistlib.load(f)["CFBundleShortVersionString"]
                driver_platform = "mac64" if cpu == "x86_64" else "mac64_m1"
                driver_name = "chromedriver"
        elif current_os == "windows":
            if not os.path.exists(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") and not os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
                raise FileNotFoundError("You haven't installed Chrome.")

            if os.path.exists(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
                wd_version = get_file_version(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
            elif os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
                wd_version = get_file_version(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            driver_platform = "win32"
            driver_name = "chromedriver.exe"

        last_driver_ver = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{wd_version.split('.')[0]}").text
        download_uri = f"https://chromedriver.storage.googleapis.com/{last_driver_ver}/chromedriver_{driver_platform}.zip"

    elif web_browser == "firefox":
        if current_os == "darwin":
            if not os.path.exists("/Applications/Firefox.app"):
                raise FileNotFoundError("You haven't installed Firefox.")
            else:
                driver_platform = "macos" if cpu == "x86_64" else "macos-aarch64"
                driver_name = "geckodriver"
            ext = "tar.gz"     
        elif current_os == "windows":
            if not os.path.exists(r"C:\Program Files\Mozilla Firefox\firefox.exe") and not os.path.exits(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"):
                raise FileNotFoundError("You haven't installed Firefox.")
            
            if os.path.exists(r"C:\Program Files\Mozilla Firefox\firefox.exe"):
                driver_platform = "win64"
            elif os.path.exits(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"):
                driver_platform = "win32"
            ext = "zip"
            driver_name = "geckodriver.exe"

        lines = requests.get("https://github.com/mozilla/geckodriver/releases").text.split('\n')
        line1, line2 = "", ""
        for line in lines:
            line1 = line2
            line2 = line
            if line.find("latest") != -1:
                break
            
        last_driver_ver = re.findall("\d+.\d+.\d+", line1)[0]
        download_uri = f"https://github.com/mozilla/geckodriver/releases/download/v{last_driver_ver}/geckodriver-v{last_driver_ver}-{driver_platform}.{ext}"

    elif web_browser == "edge":
        if current_os == "darwin":
            if not os.path.exists("/Applications/Microsoft Edge.app"):
                raise FileNotFoundError("You haven't installed Microsoft Edge.")
            else:
                plistloc = "/Applications/Microsoft Edge.app/Contents/Info.plist"
                with open(plistloc, 'rb') as f:
                    version = plistlib.load(f)["CFBundleShortVersionString"]
                last_driver_ver = version
                driver_platform = "mac64" if cpu == "x86_64" else "arm64"
                driver_name = "msedgedriver"
        elif current_os == "windows":
            if not os.path.exists(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") and not os.path.exits(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
                raise FileNotFoundError("You haven't installed Microsoft Edge.")
            
            if os.path.exists(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
                wd_version = get_file_version(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
            elif os.path.exists(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
                wd_version = get_file_version(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")

            driver_name = "msedgedriver.exe"
            driver_platform = "win64"
            last_driver_ver = wd_version

        download_uri = f"https://msedgedriver.azureedge.net/{last_driver_ver}/edgedriver_{driver_platform}.zip"

    elif web_browser == "safari":
        return

    success, zip_path = download_driver(download_uri, save_dir, web_browser, wd_info, last_driver_ver)
    if success:
        unzip_driver(current_os, zip_path, save_dir)
        save_wd_info(wd_info_path, web_browser, last_driver_ver, wd_info)

    return os.path.join(save_dir, driver_name)

def test_webdriver(web_browser, driver_path):
    web_browser = web_browser.lower()
    if web_browser == "chrome":
        wd_name = "chromedriver" 
        driver = Chrome(executable_path=driver_path)
    elif web_browser == "firefox":
        wd_name = "geckodriver" 
        driver = Firefox(executable_path=driver_path)
    elif web_browser == "edge":
        wd_name = "msedgedriver" 
        driver = Edge(executable_path=driver_path, capabilities={})
    elif web_browser == "safari":
        wd_name = None
        if platform.system().lower() == "darwin":
            try:
                driver = Safari().get("https://tw.yahoo.com")
                time.sleep(1)
                driver.quit()
                return
            except:
                raise FileNotFoundError("Please turn on Safari Remote Automation by the following guide: https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari")
        else:
            raise FileNotFoundError("This platform does not suppor safari browser.")
    else:
        wd_name = None

    if wd_name:
        driver.get("https://tw.yahoo.com")
        time.sleep(1)
        driver.quit()

if __name__ == "__main__":
    driver_save_dir = "./"
    browser = "chrome" # chrome, firefox, edge, safari
    driver_path = get_webdriver(browser, driver_save_dir)
    test_webdriver(browser, driver_path)