import requests

def get_ddg_html():
    url = "https://html.duckduckgo.com/html/?q=site:linkedin.com/in/+Property+Developer+Kuala+Lumpur"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        with open("ddg_html_dump.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Dumped HTML to ddg_html_dump.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_ddg_html()
