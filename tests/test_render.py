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
    "subject": "test2",
    "from": "Kiwi Auth",
    "template_name": "junior/new-logo",
    "base_data": {
        "junior": {
            "name": "JISEP"
        }
    },
    "data": {
        # "0": {
        #     "user": "Paul"
        # },
        "1": {
            "user": "Jeb"
        }
    }
}

r = requests.post(url + "/send/kiwi/html", json=data)

print(r.status_code)
