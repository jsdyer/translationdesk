"""Verify review UI and Translator integration with a clearly isolated contract double."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil,tempfile,threading,json
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def main():
 screenshots=ROOT/'browser-checks';screenshots.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory() as temporary:
  shutil.copytree(ROOT/'dist',Path(temporary)/'example-tool')
  server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temporary));threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.add_init_script("""window.Translator={create:async options=>({translate:async text=>{if(text==='FAIL')throw Error('Controlled engine failure');return 'Reviewed: '+text;},destroy(){}})};""")
    page.goto(f'http://127.0.0.1:{server.server_port}/example-tool/')
    expect(page.locator('#capability')).to_contain_text('available in this browser')
    page.locator('#source').fill('First passage.\n\nSecond passage.')
    page.locator('#prepare').click();expect(page.locator('#status')).to_contain_text('Language pair ready')
    page.locator('#translate').click();expect(page.locator('#status')).to_contain_text('Translation ready')
    assert page.locator('#target').input_value()=='Reviewed: First passage.\n\nReviewed: Second passage.'
    assert page.locator('.pair').count()==2
    previous=page.locator('#target').input_value();page.locator('#source').fill('FAIL');page.locator('#translate').click()
    expect(page.locator('#status')).to_contain_text('previous translation is unchanged')
    assert page.locator('#target').input_value()==previous
    page.locator('#source').fill('<img src=x onerror=alert(1)>');page.locator('#target').fill('Une traduction à vérifier.')
    assert page.locator('img').count()==0
    page.locator('#engine').select_option('libretranslate');page.locator('#endpoint').fill('https://private.example');page.locator('#key').fill('DO-NOT-EXPORT')
    page.locator('#translate').click();expect(page.locator('#status')).to_contain_text('Allow the source text')
    with page.expect_download() as download:page.locator('#save-project').click()
    raw=Path(download.value.path()).read_bytes();assert b'DO-NOT-EXPORT' not in raw and b'private.example' not in raw
    assert json.loads(raw)['source'].startswith('<img')
    page.locator('#clear').click();page.locator('#file').set_input_files({'name':'project.json','mimeType':'application/json','buffer':raw})
    expect(page.locator('#status')).to_contain_text('File opened locally')
    assert page.locator('#target').input_value()=='Une traduction à vérifier.'
    page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
    assert not errors,errors
    browser.close()
  finally:server.shutdown()
 print('Browser checks passed: review, controlled translator contract, error preservation, privacy exports and mobile width')
if __name__=='__main__':main()
