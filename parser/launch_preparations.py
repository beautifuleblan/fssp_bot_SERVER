from playwright.sync_api import Playwright
from playwright._impl._api_structures import ProxySettings
from pyuseragents import random as random_useragent
from configs.config import *


browser_args = ['--disable-background-networking',
                '--enable-automation',
                '--disable-back-forward-cache',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-component-extensions-with-background-pages',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-features=ImprovedCookieControls,'
                'LazyFrameLoading,GlobalMediaControls,'
                'DestroyProfileOnBrowserClose,'
                'MediaRouter,DialMediaRouteProvider,'
                'AcceptCHFrame,'
                'AutoExpandDetailsElement,'
                'CertificateTransparencyComponentUpdater,'
                'AvoidUnnecessaryBeforeUnloadCheckSync,'
                'Translate',
                '--disable-extensions',
                '--allow-pre-commit-input',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--disable-field-trial-config',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-default-apps',
                '--disable-dev-shm-usage',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--password-store=basic --use-mock-keychain',
                '--password-store=basic',
                '--use-mock-keychain',
                '--no-service-autorun',
                '--export-tagged-pdf',
                '--enable-use-zoom-for-dsf=false',
                '--proxy-bypass-list=<-loopback>']

def launch_firefox(playwright: Playwright, proxy_server: ProxySettings):
    browser = playwright.firefox.launch(headless=False, proxy={'server': 'per-context'},
                                       slow_mo=BETWEEN_ACTIONS_DELAY*1000)
    context = browser.new_context(user_agent=random_useragent(), proxy=proxy_server)
    page = context.new_page()
    page.set_default_timeout(SELECTOR_TIMEOUT*1000)
    page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return page, browser

def launch_chrome(playwright: Playwright, proxy_server: ProxySettings):
    browser = playwright.chromium.launch(channel="chrome", headless=False, proxy=proxy_server,
                                         slow_mo=BETWEEN_ACTIONS_DELAY * 1000, ignore_default_args=browser_args, args=[
            '--disable-blink-features=AutomationControlled'
        ])
    page = browser.new_page(user_agent=random_useragent())
    page.set_default_timeout(SELECTOR_TIMEOUT * 1000)
    return page, browser