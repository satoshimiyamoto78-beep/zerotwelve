import asyncio, sys
from playwright.async_api import async_playwright
svg, pdf, png = sys.argv[1:4]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1123, "height": 1587}, device_scale_factor=3)
        html = f'<html><head><style>@page{{size:297mm 420mm;margin:0}}html,body{{margin:0}}svg{{display:block;width:297mm;height:420mm}}</style></head><body>{open(svg).read()}</body></html>'
        await pg.set_content(html); await pg.wait_for_timeout(500)
        await pg.pdf(path=pdf, width="297mm", height="420mm", print_background=True)
        await pg.screenshot(path=png, full_page=True)
        await b.close()
asyncio.run(main())
