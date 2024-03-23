import urllib.request
import os
import json
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
# Download all module.json files from the list
lines = open('modulelist.txt').readlines()
result = []
names = set()
for url in lines:
  try:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    mydata = urllib.request.urlopen(req).read()

    module = json.loads(mydata.decode('utf-8'))
    if 'name' not in module:
        print('No name specified:', url)
    else:
        if module['name'].lower() in names:
            print('WARNING: Duplicate module name:', url)

        names.add(module['name'].lower())

        # Upgrade legacy fields
        if 'options' in module:
            if 'niceName' in module['options']:
                module['options']['cliName'] = module['options']['niceName']
                del module['options']['niceName']

        if 'category' in module:
            if 'keywords' not in module:
                module['keywords'] = [module['category']]
            else:
                module['keywords'].append(module['category'])
            del module['category']
        else:
            if 'keywords' not in module:
                module['keywords'] = ['network']

        print('Add:', url)
        result.append(module)
  except Exception as e:
    print(url, e)

# Sort by name
def guiname(x):
    if 'options' in x:
        if 'guiName' in x['options']:
            return strip_tags(x['options']['guiName'])
        if 'cliName' in x['options']:
            return strip_tags(x['options']['cliName'])
    return x['name']
    
result = sorted(result, key = lambda x: guiname(x).lower())

with open('modulelist.json', 'w') as fh:
    json.dump(result, fh)

print(len(result), 'mods listed!')
print(sum(1 for x in result if 'network' in x['keywords']), 'network mods listed!')
print(sum(1 for x in result if 'client' in x['keywords']), 'client mods listed!')
