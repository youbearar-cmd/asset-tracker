import requests
import urllib.parse

query = "sol 금"
encoded_query = urllib.parse.quote(query)
url = f"https://ac.finance.naver.com/ac?q={encoded_query}&q_enc=utf-8&st=1&frm=stock&r_format=json&r_enc=utf-8&r_unicode=1&t_koreng=1&ans=2&run=2&rev=4&con=1"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(r.json())
