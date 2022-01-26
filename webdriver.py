import platform
import subprocess
import os
import plistlib
import cpuinfo
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver import Chrome, Firefox, Edge, Safari
import re
import time

def testwebdriver(app):
    if app == "chromedriver":
        driver = Chrome(executable_path="./chromedriver")
    elif app == "geckodriver":
        driver = Firefox(executable_path="./geckodriver")
    elif app == "edgedriver":
        driver = Edge(executable_path="./msedgedriver", capabilities={})
    elif app == "safaridriver":
        driver = Safari()
    driver.get("https://www.google.com")
    time.sleep(1)
    driver.quit()

class WebDriverDownloader:
    class webdriver(object):
        chromedriver = "chromedriver"
        geckodriver = "geckodriver"
        edgedriver = "edgedriver"
        safaridriver = "safaridriver"

    def __init__(self, app:webdriver) -> None:
        self.os = platform.system()
        self.app = app

        manufacturer = cpuinfo.get_cpu_info().get('brand_raw')
        self.cpu = 'arm' if 'm1' in manufacturer.lower() else 'x86_64'

    def getDriver(self, save_path):
        if self.os == "Darwin":
            self.__getDriverMacOS(save_path)
        elif self.os == "Windows":
            self.__getDriverWindows(save_path)
        

    def __getDriverMacOS(self, save_path):
        if self.app == self.webdriver.chromedriver:
            if not os.path.exists("/Applications/Google Chrome.app"):
                raise FileNotFoundError("You haven't installed Chrome.")
            else:
                plistloc = "/Applications/Google Chrome.app/Contents/Info.plist"
                with open(plistloc, 'rb') as f:
                    self.version = plistlib.load(f)["CFBundleShortVersionString"]
                last_driver_ver = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{self.version.split('.')[0]}").text
                driver_platform = "mac64" if self.cpu == "x86_64" else "mac64_m1"
                download_uri = f"https://chromedriver.storage.googleapis.com/{last_driver_ver}/chromedriver_{driver_platform}.zip"
                
                resp = requests.get(download_uri, stream=True, timeout=300)

                if resp.status_code == 200:
                    file_name = download_uri.split("/")[-1]
                    with open(os.path.join(save_path, file_name), "wb") as f:
                        f.write(resp.content)
                    print("Download driver completed")
                else:
                    raise Exception("Download chrome driver failed")

                process = subprocess.Popen(['unzip', '-o', os.path.join(save_path, file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate() 

        elif self.app == self.webdriver.edgedriver:
            if not os.path.exists("/Applications/Microsoft Edge.app"):
                raise FileNotFoundError("You haven't installed Microsoft Edge.")
            else:
                plistloc = "/Applications/Microsoft Edge.app/Contents/Info.plist"
                with open(plistloc, 'rb') as f:
                    self.version = plistlib.load(f)["CFBundleShortVersionString"]
                driver_platform = "mac64" if self.cpu == "x86_64" else "mac64" #"arm64"
                download_uri = f"https://msedgedriver.azureedge.net/{self.version}/edgedriver_{driver_platform}.zip"
                resp = requests.get(download_uri, stream=True, timeout=300)

                if resp.status_code == 200:
                    file_name = download_uri.split("/")[-1]
                    with open(os.path.join(save_path, file_name), "wb") as f:
                        f.write(resp.content)
                    print("Download driver completed")
                else:
                    raise Exception("Download chrome driver failed")

                process = subprocess.Popen(['unzip', '-o', os.path.join(save_path, file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate() 
        elif self.app == self.webdriver.safaridriver:
            pass
        elif self.app == self.webdriver.geckodriver:
            if not os.path.exists("/Applications/Firefox.app"):
                raise FileNotFoundError("You haven't installed Firefox.")
            else:
                lines = requests.get("https://github.com/mozilla/geckodriver/releases").text.split('\n')
                line1, line2 = "", ""
                for line in lines:
                    line1 = line2
                    line2 = line
                    if line.find("latest") != -1:
                        break
                last_driver_ver = re.findall("\d+.\d+.\d+", line1)[0]
                driver_platform = "macos" if self.cpu == "x86_64" else "macos-aarch64"
                download_uri = f"https://github.com/mozilla/geckodriver/releases/download/v{last_driver_ver}/geckodriver-v{last_driver_ver}-{driver_platform}.tar.gz"
                
                resp = requests.get(download_uri, stream=True, timeout=300)
                if resp.status_code == 200:
                    file_name = download_uri.split("/")[-1]
                    with open(os.path.join(save_path, file_name), "wb") as f:
                        f.write(resp.content)
                    print("Download driver completed")
                else:
                    raise Exception("Download chrome driver failed")
                process = subprocess.Popen(['tar', '-xvf', os.path.join(save_path, file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate() 

    def __getDriverWindows(self, save_path):
        if self.app == self.webdriver.chromedriver:
            pass
        elif self.app == self.webdriver.edgedriver:
            pass
        elif self.app == self.webdriver.safaridriver:
            pass
        elif self.app == self.webdriver.geckodriver:
            pass    

if __name__ == "__main__":
    app = WebDriverDownloader.webdriver.edgedriver
    driver_save_path = "./"
    WebDriverDownloader(app=app).getDriver(driver_save_path)
    testwebdriver(app)