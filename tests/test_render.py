import requests

url = 'http://localhost:5000'

# url = "https://dev.kiwix.gamma.junior-entreprises.com/mail"

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


# class NotificationFragment(BaseModel):
#     body: Optional[Dict[str, Any]]
#     type: str
#     to: List[str]


# class SendTemplateMailBody(BaseModel):
#     # from: str
#     template_name: str
#     fragments: List[NotificationFragment]
#     base_data: Dict[str, Any]


data = {
    "from": "Kiwi Auth",
    "template_name": "junior/new-logo",
    "base_data": {
        "junior": {
            "name": "JISEP"
        }
    },
    "fragments": [
        {
            "to": ["paul.leveau@gmail.com"],
            "type": "email",
            "body": {
                "junior": {"name": "beb"},
                "user": "Paul",
            },
        },
        {
            "to": ["paul.leveau@cnje.org"],
            "type": "email",
            "body": {
                "junior_name": "JISEP",
                "user": "Jack",
            },
        }
    ]

}

r = requests.post(url + "/send/kiwi/html", json=data)

print(r.status_code)
print(r.text)
