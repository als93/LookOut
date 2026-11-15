#!/usr/bin/env python3
"""Tests the REAL lookoutV41Show in the REAL app page (real CSS), in Chromium only.
Usage: python3 real_page_tests.py <viewer.html> [--chromium /path/to/chrome]
A one-line hook is injected into a TEMP COPY so the closure-scoped function can be called; the input file is never modified.
Fixtures are synthetic. No archive / journal / controller is read or written.
These are Chromium results. They are NOT Firefox evidence (see REVIEW.md)."""
import asyncio,io,re,sys,time,tempfile,threading,functools,http.server,shutil
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.async_api import async_playwright
SRC=Path(sys.argv[1]).resolve()
CH=sys.argv[sys.argv.index('--chromium')+1] if '--chromium' in sys.argv else None
TMP=Path(tempfile.mkdtemp());PORT=8899
txt=SRC.read_text();assert txt.count('function lookoutV41Show(')==1
(TMP/'page.html').write_text(txt.replace('function lookoutV41Show(','window.__show=(...x)=>lookoutV41Show(...x);\nfunction lookoutV41Show(',1))
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',PORT),functools.partial(Quiet,directory=str(TMP)));threading.Thread(target=srv.serve_forever,daemon=True).start()
COL=[(222,110,105),(100,195,234),(250,193,90),(211,145,235),(102,225,142)]
def jpg(i,size=(720,405)):
    im=Image.new('RGB',size,COL[i%5]);d=ImageDraw.Draw(im);d.ellipse((size[0]*.3,size[1]*.2,size[0]*.7,size[1]*.8),fill=(255,255,255));d.text((20,15),f'FRAME {i}',fill=(10,10,10))
    b=io.BytesIO();im.save(b,format='JPEG',quality=88);return b.getvalue()
def dark(px):return max(px)<70 or sum(px)<300
res=[]
def rep(n,ok,d=''):res.append(ok);print(('PASS ' if ok else 'FAIL ')+n+(f'  [{d}]' if d else ''))
async def open_real(p,delay=lambda i:.07,sizes=lambda i:(720,405),same_origin=False,vp=(1280,900)):
    b=await p.chromium.launch(executable_path=CH,args=['--no-sandbox','--disable-dev-shm-usage'])
    pg=await b.new_page(viewport={'width':vp[0],'height':vp[1]},device_scale_factor=1);pg.errs=[];pg.reqs=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e)[:200]))
    async def route(r):
        u=r.request.url;m=re.search(r'/frame/(\d+)\.jpg',u)
        if m:
            i=int(m.group(1));pg.reqs.append(i);await asyncio.sleep(delay(i))
            return await r.fulfill(status=200,body=jpg(i,sizes(i)),content_type='image/jpeg')
        if u.startswith(f'http://127.0.0.1:{PORT}/') and '/fx/' not in u:return await r.continue_()
        await r.abort()
    await pg.route('**/*',route);await pg.goto(f'http://127.0.0.1:{PORT}/page.html',wait_until='domcontentloaded')
    await pg.wait_for_function('typeof window.__show==="function"',timeout=15000)
    pg.host=f'http://127.0.0.1:{PORT}/fx' if same_origin else 'https://cross-origin.example.invalid';return b,pg
async def start(pg,n=36,fps='12'):
    await pg.evaluate('''([h,n,f])=>{window.F=Array.from({length:n},(_,i)=>{const ms=Date.UTC(2026,10,1,0,i,0);return {url:`${h}/frame/${i}.jpg`,ms,timestamp:new Date(ms).toISOString().replace('.000Z','Z'),precision:'second_utc',verification:'fixture',source:'test'}});
      window.__show({name:'T'},{setMediaViewMode(){}},null,{id:'t',title:'t',provider:'nims',sourcePage:'x',completeness:'fixture'},window.F);document.querySelector('[data-fps]').value=f}''',[pg.host,n,fps])
    await pg.wait_for_function("!document.querySelector('[data-frame]').hidden",timeout=15000)
async def seek(pg,i):
    await pg.evaluate("i=>{const v=document.querySelector('[data-scrub]');v.value=String(window.F[i].ms);v.dispatchEvent(new Event('input',{bubbles:true}))}",i)
    await pg.wait_for_function("i=>document.querySelector('[data-counter]').textContent===(i+1)+'/36'&&document.querySelector('[data-frame]').style.opacity===''",arg=i,timeout=6000);await asyncio.sleep(.1)
async def px(pg,fx,fy):
    im=Image.open(io.BytesIO(await pg.locator('[data-frame]').screenshot())).convert('RGB');return im.getpixel((int(im.width*fx),int(im.height*fy)))
async def t_sync(p):
    b,pg=await open_real(p,delay=lambda i:.16 if i%3==0 else .04,same_origin=True);await start(pg)
    await pg.evaluate('''()=>{window.S={n:0,bad:[],dark:0};const C=[[222,110,105],[100,195,234],[250,193,90],[211,145,235],[102,225,142]];const c=document.querySelector('[data-frame]'),x=c.getContext('2d');
      const f=()=>{if(!c.hidden&&c.style.opacity===''){const m=document.querySelector('[data-counter]').textContent.match(/^(\\d+)\\//);if(m){const i=+m[1]-1,p=x.getImageData(5,5,1,1).data,e=C[i%5];window.S.n++;
        if(Math.abs(p[0]-e[0])+Math.abs(p[1]-e[1])+Math.abs(p[2]-e[2])>40)window.S.bad.push([i+1,[p[0],p[1],p[2]]]);if(p[0]+p[1]+p[2]<300)window.S.dark++}}requestAnimationFrame(f)};requestAnimationFrame(f)}''')
    await pg.evaluate("document.querySelector('[data-play]').click()");await asyncio.sleep(7);S=await pg.evaluate('window.S')
    rep('T1 counter/timestamp always matches the pixels on screen, 12 FPS autoplay (rAF sampler, same-origin)',not S['bad'] and S['dark']==0 and S['n']>100,f"{S['n']} samples, {len(S['bad'])} mismatches, {S['dark']} dark");await b.close()
async def t_drawfail(p):
    b,pg=await open_real(p,delay=lambda i:.05,same_origin=True);await start(pg)
    await pg.evaluate('''()=>{const o=CanvasRenderingContext2D.prototype.drawImage;window.T={armed:false,snap:null};CanvasRenderingContext2D.prototype.drawImage=function(...a){
      if(window.T.armed&&a[0] instanceof HTMLImageElement){window.T.armed=false;const c=this.canvas;setTimeout(()=>{const q=this.getImageData(c.width/2|0,c.height/2|0,1,1).data;window.T.snap=[q[0],q[1],q[2]];window.T.hidden=c.hidden},0);throw new Error('injected')}return o.apply(this,a)}}''')
    await pg.evaluate("document.querySelector('[data-play]').click()");await asyncio.sleep(.9);await pg.evaluate("window.T.armed=true");await asyncio.sleep(.6)
    T=await pg.evaluate('window.T');rep('T2 injected drawImage failure during autoplay leaves the previous frame intact',T['snap'] is not None and sum(T['snap'])>=300 and not T['hidden'],f"centre pixel after failure={T['snap']}");await b.close()
async def t_pause(p):
    b,pg=await open_real(p,delay=lambda i:.16 if i%3==0 else .05);await start(pg)
    await pg.evaluate("document.querySelector('[data-apply]').click()");await pg.wait_for_function("document.querySelector('[data-counter]').textContent==='36/36'&&!document.querySelector('[data-frame]').hidden")
    await pg.evaluate("()=>{const p=document.querySelector('[data-play]');p.click();setTimeout(()=>p.click(),15)}");await asyncio.sleep(.6)
    c=await pg.evaluate("document.querySelector('[data-counter]').textContent");rep('T3 pause 15 ms after play displays nothing afterwards (timing driven inside the page)',c=='36/36',c);await b.close()
async def t_mixed(p):
    b,pg=await open_real(p,sizes=lambda i:(720,405) if i>=34 else (640,480));await start(pg)
    await seek(pg,10);bar=await px(pg,.02,.5);mid=await px(pg,.5,.9)
    rep('T4a 4:3 frame on 16:9 surface: side bar = stage colour, picture centred',bar[0]<40 and abs(mid[0]-COL[0][0])<30,f'bar={bar} mid={mid}')
    await seek(pg,34);bar2=await px(pg,.02,.5);rep('T4b following 16:9 frame leaves no stale bar pixels',abs(bar2[0]-COL[4][0])<30,f'bar={bar2}')
    await seek(pg,10);await seek(pg,34);await seek(pg,10);c=await px(pg,.5,.5);rep('T4c repeated aspect changes stay clean',min(c)>240,f'centre={c}');await b.close()
async def t_full(p):
    b,pg=await open_real(p);await start(pg);await pg.click('[data-fullscreen]');await asyncio.sleep(.8)
    fs=await pg.evaluate('!!document.fullscreenElement');im=Image.open(io.BytesIO(await pg.screenshot())).convert('RGB');q=im.load();xs=[];ys=[]
    for y in range(0,int(im.height*.72),2):
        for x in range(0,im.width,2):
            if min(q[x,y])>245:xs.append(x);ys.append(y)
    a=(max(xs)-min(xs))/(max(ys)-min(ys)) if xs else 0;rep('T5 real fullscreen CSS: picture not distorted',fs and abs(a-1.185)<.06,f'aspect={a:.3f} (undistorted 1.185)');await b.close()
async def t_close(p):
    b,pg=await open_real(p,delay=lambda i:.12);await start(pg);await pg.evaluate("document.querySelector('[data-play]').click()");await asyncio.sleep(1)
    await pg.evaluate("document.querySelector('[data-close]').click()");await asyncio.sleep(.5);n1=len(pg.reqs);await asyncio.sleep(1.5)
    gone=await pg.evaluate("document.querySelectorAll('.lookout-v41-history').length===0");rep('T6 close during autoplay: panel removed, no further requests, no page errors',gone and len(pg.reqs)==n1 and not pg.errs,pg.errs);await b.close()
async def info_fps(p):
    b,pg=await open_real(p,delay=lambda i:.02);await start(pg,n=120);await pg.evaluate("document.querySelector('[data-limit]').value='120';document.querySelector('[data-apply]').click()")
    await pg.wait_for_function("document.querySelector('[data-counter]').textContent==='120/120'&&!document.querySelector('[data-frame]').hidden",timeout=15000)
    await pg.evaluate("window.__c=[];new MutationObserver(()=>window.__c.push(performance.now())).observe(document.querySelector('[data-counter]'),{childList:true,characterData:true,subtree:true})")
    await pg.evaluate("document.querySelector('[data-play]').click()");await asyncio.sleep(5);c=await pg.evaluate('window.__c');print(f'INFO  measured playback with 12 FPS selected and 20 ms fixture latency: {(len(c)-1)/((c[-1]-c[0])/1000):.2f} fps');await b.close()
async def info_lock(p):
    b,pg=await open_real(p,sizes=lambda i:(320,180) if i==35 else (1280,720));await start(pg);await seek(pg,5)
    print('INFO  surface size after a 320x180 first frame then a 1280x720 frame:',await pg.evaluate("[document.querySelector('[data-frame]').width,document.querySelector('[data-frame]').height]"));await b.close()
async def main():
    async with async_playwright() as p:
        for t in (t_sync,t_drawfail,t_pause,t_mixed,t_full,t_close,info_fps,info_lock):await t(p)
    print(f'RESULT: {sum(res)}/{len(res)} passed');srv.shutdown();shutil.rmtree(TMP,ignore_errors=True);sys.exit(0 if all(res) else 1)
asyncio.run(main())
