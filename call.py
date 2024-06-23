import requests

key = "HediUact7BuuTzp4KWJnzclfvaZ8"
res = requests.get(
    "https://sms.ru/sms/send?api_id=0F9113E2-B4ED-8975-4BEA-B47ACCC656C6&to=79086007430&msg=hello+world&json=1"
    "https://email:api_key@gate.smsaero.ru/v2/sms/send?number=79990000000&text=your+text&sign=SMS Aero"
)
print(res.json())
