import platform
import subprocess
import os
import plistlib
import cpuinfo
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver import Chrome

def testwebdriver():
    driver = Chrome("./chromedriver")
    driver.get("https://www.google.com")

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

                process = subprocess.Popen(['unzip', '-o', os.path.join(save_path, file_name)],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
                stdout, stderr = process.communicate() 

        elif self.app == self.webdriver.edgedriver:
            pass
        elif self.app == self.webdriver.safaridriver:
            pass
        elif self.app == self.webdriver.geckodriver:
            pass

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
    app = WebDriverDownloader.webdriver.chromedriver
    driver_save_path = "./"
    WebDriverDownloader(app=app).getDriver(driver_save_path)
    testwebdriver()