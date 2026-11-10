import os
import re
import random
from playwright.sync_api import sync_playwright

PATH_TO_VIDEO_FOLDER = "./video"

SIZE = {"width": 1280, "height": 720}
SEARCH_BOX = 'textarea[name="q"]'
SEARCH_BUTTON = 'button[type="submit"]'
FIRST_RESULT = 'a[data-testid="result-title-a"]'

CURSOR_JS = r"""
(() => {
  const mk = (css) => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;left:0;top:0;pointer-events:none;' + css;
    return d;
  };
  const halo = mk('width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;background:rgba(255,230,0,.35);z-index:2147483646');
  const arrow = mk('width:32px;height:32px;z-index:2147483647');
  arrow.innerHTML = '<svg width="32" height="32" viewBox="0 0 32 32"><path d="M1 1 L1 23 L7 18 L11 28 L15 26 L11 17 L19 17 Z" fill="white" stroke="black" stroke-width="2" stroke-linejoin="round"/></svg>';

  window.addEventListener('mousemove', (e) => {
    if (!halo.isConnected) document.documentElement.append(halo, arrow);
    halo.style.transform = arrow.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
  }, true);

  window.addEventListener('mousedown', (e) => {
    const r = mk('width:32px;height:32px;margin:-16px 0 0 -16px;border-radius:50%;border:3px solid orange;box-sizing:border-box;z-index:2147483646');
    document.documentElement.append(r);
    const t = `translate(${e.clientX}px,${e.clientY}px)`;
    r.animate([{transform: t + ' scale(.2)', opacity: 1}, {transform: t + ' scale(1)', opacity: 0}], 600).onfinish = () => r.remove();
  }, true);
})();
"""


def find(page, selector):
    for _ in range(45):
        try:
            return page.wait_for_selector(selector + ":visible", timeout=2000)
        except Exception:
            pass
    raise TimeoutError("Не найден элемент: " + selector)


def click(page, pos, selector):
    box = find(page, selector).bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    steps = 40
    for i in range(1, steps + 1):                      
        page.mouse.move(pos[0] + (x - pos[0]) * i / steps,
                        pos[1] + (y - pos[1]) * i / steps)
        page.wait_for_timeout(15)
    pos[0], pos[1] = x, y
    page.wait_for_timeout(200)
    page.mouse.click(x, y)


def CaptureVideo_Magento(url, company_name, language, country,
                         postcode, city, street, house_no):
    folder = os.path.abspath(PATH_TO_VIDEO_FOLDER)
    os.makedirs(folder, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|]', "_", company_name)   
    dst = os.path.join(folder, name + ".webm")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(viewport=SIZE,
                                          record_video_dir=folder,
                                          record_video_size=SIZE)
            context.add_init_script(CURSOR_JS)
            page = context.new_page()
            video = page.video
            pos = [100, 100]

            page.goto(url)
            page.mouse.move(100, 100)                    

            click(page, pos, SEARCH_BOX)                 
            for ch in f"Magento developer in {city}":    
                page.keyboard.type(ch)
                page.wait_for_timeout(random.randint(60, 180))

            click(page, pos, SEARCH_BUTTON)             
            find(page, FIRST_RESULT)                     
            page.mouse.move(pos[0] + 1, pos[1] + 1)      
            click(page, pos, FIRST_RESULT)               
            page.wait_for_timeout(4000)

            context.close()                              
            if os.path.exists(dst):
                os.remove(dst)
            video.save_as(dst)
            video.delete()
            browser.close()
        return dst
    except Exception as e:
        print("Ошибка:", e)
        return None