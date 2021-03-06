import requests

# url = 'http://localhost:5000'

url = "https://dev.kiwix.gamma.junior-entreprises.com/mail"

# addresses: List[List[str]]
#     content: str = ''
#     subject: str = ''
#     from_: str
#     template_name: Optional[str]

#     class Config:
#         fields = {
#             'from_': 'from'
#         }

#     data: Dict[str, Any] = {}

data = {
    "addresses": [
        ['paul.leveau@cnje.org'],
        ['paul.leveau@gmail.com', 'plawn.yay@gmail.com'],
    ],
    "subject": "test",
    "from": "Kiwi Auth",
    "content": "Coucou, petit test depuis l'api de mails"
}

r = requests.post(url + "/send/kiwi/plain", json=data)

print(r.status_code)
