import requests
url="https://jsonplaceholder.typicode.com/posts"
params={
    "id":1
}
response=requests.get(url,params=params)
print(response.json())
print(response.status_code)