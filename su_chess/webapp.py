from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
if __name__=='__main__':
 root=Path(__file__).parent/'web'; import os; os.chdir(root); print('http://127.0.0.1:8000'); ThreadingHTTPServer(('127.0.0.1',8000),SimpleHTTPRequestHandler).serve_forever()
