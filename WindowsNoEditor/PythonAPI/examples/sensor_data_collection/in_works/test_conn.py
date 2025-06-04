# import requests
# print(requests.get('https://api.openai.com').status_code)

import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

print(os.environ['SSL_CERT_FILE'])
# c:\WS\CARLA_0.9.13\.venv\lib\site-packages\certifi\cacert.pem