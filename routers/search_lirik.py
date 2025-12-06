from fastapi import APIRouter, HTTPException
import httpx
from bs4 import BeautifulSoup
import re
import json

router = APIRouter(tags=["search"])

def find_genius(q, headers):
    url = httpx.URL(f"https://duckduckgo.com/html/?q={q}+site:genius.com")
    response = httpx.get(str(url), headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if not href:
            continue
        
        if 'genius.com' in href:
            return href
        elif href.startswith('/l/?') and 'uddg=' in href:
            match = re.search(r'uddg=([^&]+)', href)
            if match:
                decoded = httpx.URL(match.group(1)).decode()
                if 'genius.com' in decoded:
                    return decoded
    return None

def extract_lyrics(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup.find_all(['script', 'style', 'noscript']):
        tag.decompose()
    
    def clean_text(text):
        if not text:
            return ''
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</(div|p|li|section|article|header|footer)[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<img[^>]*>', '', text)
        text = re.sub(r'</?[^>]+>', '', text)
        soup2 = BeautifulSoup(f'<div>{text}</div>', 'html.parser')
        text = soup2.div.get_text()
        lines = [l.replace('\s+', ' ').strip() for l in text.splitlines()]
        return '\n'.join(filter(None, lines)).strip()
    
    selectors = [
        {'data-lyrics-container': 'true'},
        {'class': re.compile(r'.*Lyrics__Container.*')},
        {'class': 'lyrics'},
        {'class': 'song_body-lyrics'},
        {'class': 'lyrics__root'}
    ]
    
    for selector in selectors:
        elements = soup.find_all(attrs=selector) if isinstance(selector, dict) else soup.select(selector)
        if not elements:
            continue
        
        parts = []
        for element in elements:
            txt = clean_text(str(element))
            if txt:
                parts.append(txt)
        
        if not parts:
            continue
        
        text = '\n\n'.join(parts)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        
        junk_patterns = [
            r'Read\s*More', r'Translations?', r'(?:فارسی|Español)',
            r'\b[\w\s]*Lyrics\b', r'https?://images\.genius\.com/\S+',
            r'SizedImage__NoScript[-\w]*', r'The lyrics are about[\s\S]*'
        ]
        
        for pattern in junk_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        lines = []
        for line in text.splitlines():
            l = line.strip()
            if not l or len(l) < 2:
                continue
            low = l.lower()
            if re.match(r'^share|^songfacts|^embed', low):
                continue
            if re.match(r'^(farsi|فارسی|español|translation)', low, re.IGNORECASE):
                continue
            if re.match(r'^https?://', l):
                continue
            if re.match(r'^(album|artist|writer|producer):', low):
                continue
            if len(l.split()) == 1 and len(l) < 10:
                continue
            lines.append(l)
        
        uniq = []
        last = None
        for x in lines:
            if x == last:
                continue
            last = x
            uniq.append(x)
        
        result = '\n'.join(uniq).strip()
        if result and len(result) > 50 and len(result.splitlines()) >= 2:
            return result
    
    ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    for script in ld_scripts:
        try:
            obj = json.loads(script.string)
            ly = obj.get('lyrics')
            if isinstance(ly, str):
                t = re.sub(r'\s+', ' ', ly).strip()
                if len(t) > 50:
                    return t
            elif isinstance(ly, dict):
                t = ly.get('text', '')
                t = re.sub(r'\s+', ' ', t).strip()
                if len(t) > 50:
                    return t
        except:
            continue
    
    pre_script = soup.find('script', string=re.compile(r'window\.__PRELOADED_STATE__\s*='))
    if pre_script:
        try:
            match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({[\s\S]*?});', pre_script.string)
            if match:
                o = json.loads(match.group(1))
                str_json = json.dumps(o)
                m = re.search(r'"lyrics"\s*:\s*"([^"]{50,})"', str_json)
                if m:
                    t = m.group(1).replace('\\n', '\n').replace('\\"', '"')
                    if len(t) > 50:
                        return t
        except:
            pass
    
    meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
    if meta_desc:
        desc = meta_desc.get('content', '')
        if desc:
            t = re.sub(r'\s+', ' ', desc).strip()
            if len(t) > 30 and not re.search(r'translation|read more|lyrics', t, re.IGNORECASE):
                return t
    
    return None

def ddg_extract(q, headers):
    url = f"https://duckduckgo.com/html/?q={q}+site:genius.com"
    response = httpx.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    page_url = None
    snippet = None
    
    for link in soup.find_all('a', href=True):
        if page_url:
            break
        
        href = link.get('href')
        
        def grab_snippet():
            nonlocal snippet
            parent = link.find_parent(['div', 'span'], class_=re.compile(r'result|result__body|result__snippet|c-result'))
            if parent:
                snip_elem = parent.find(class_=re.compile(r'result__snippet|result__excerpt|c-abstract|snippet'))
                if snip_elem:
                    snippet = snip_elem.get_text().strip()
            if not snippet:
                parent_text = link.parent.get_text()
                link_text = link.get_text()
                snippet = parent_text.replace(link_text, '').strip()
        
        if 'genius.com' in href:
            page_url = href
            grab_snippet()
        elif href.startswith('/l/?') and 'uddg=' in href:
            match = re.search(r'uddg=([^&]+)', href)
            if match:
                decoded = httpx.URL(match.group(1)).decode()
                if 'genius.com' in decoded:
                    page_url = decoded
                    grab_snippet()
    
    return {'pageUrl': page_url, 'snippet': snippet}

@router.get("/lyrics")
async def search_lyrics(q: str):
    api_url = f"https://genius.com/api/search/multi?q={q}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json,text/plain,*/*'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            data = response.json()
            
            sections = data.get('response', {}).get('sections', [])
            song_section = next((s for s in sections if s.get('type') == 'song'), None)
            
            if not song_section or not song_section.get('hits'):
                raise HTTPException(status_code=404, detail="Not found")
            
            song = song_section['hits'][0]['result']
            url = song.get('url')
            
            page_response = await client.get(url, headers={'User-Agent': headers['User-Agent']})
            lyrics = extract_lyrics(page_response.text)
            
            return {
                'title': song.get('full_title'),
                'thumbnail': song.get('song_art_image_url'),
                'url': url,
                'lyrics': lyrics
            }
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            ddg_result = ddg_extract(q, headers)
            genius_link = find_genius(q, headers)
            link = ddg_result.get('pageUrl') or genius_link
            
            if not link and not ddg_result.get('snippet'):
                raise HTTPException(status_code=404, detail="Fallback gagal")
            
            text = ddg_result.get('snippet', '').strip()
            return {
                'title': q,
                'thumbnail': None,
                'url': link,
                'lyrics': text or f"Preview mati, buka {link}"
            }
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))