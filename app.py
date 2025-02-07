from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

class WebMapper:
    def __init__(self):
        self.visited_urls = set()
        self.page_data = {
            "title": "",
            "internal_links": [],
            "external_links": [],
            "images_count": 0,
            "tables_count": 0,
            "forms_count": 0
        }
    
    def analyze_page(self, url):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                base_domain = urlparse(url).netloc
                
                # Réinitialiser les données
                self.page_data = {
                    "title": soup.title.string if soup.title else "Sans titre",
                    "internal_links": [],
                    "external_links": [],
                    "images_count": len(soup.find_all('img')),
                    "tables_count": len(soup.find_all('table')),
                    "forms_count": len(soup.find_all('form'))
                }
                
                # Analyser les liens
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(url, href)
                    link_domain = urlparse(full_url).netloc
                    
                    if link_domain == base_domain:
                        self.page_data["internal_links"].append({
                            "url": full_url,
                            "text": link.get_text(strip=True) or "Sans texte"
                        })
                    else:
                        self.page_data["external_links"].append({
                            "url": full_url,
                            "text": link.get_text(strip=True) or "Sans texte"
                        })
                
                return self.page_data
                
        except Exception as e:
            return {"error": str(e)}

mapper = WebMapper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url', '')
    results = mapper.analyze_page(url)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)