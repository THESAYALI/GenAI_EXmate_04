from fastapi import FastAPI

app = FastAPI()
@app.get("/products")
def get_products():
    filtered_products = []

    for product in products:
        if product["price"] < 50000:
            filtered_products.append(product)

    return filtered_products

products = [
    {
        "name": "Samsung Galaxy S24",
        "price": 74999,
        "rating": "⭐⭐⭐⭐⭐",
        "description": "Premium smartphone"
    },
    {
        "name": "Apple iPhone 15",
        "price": 69900,
        "rating": "⭐⭐⭐⭐",
        "description": "Powerful smartphone"
    },
    {
        "name": "Sony WH-1000XM5",
        "price": 29990,
        "rating": "⭐⭐⭐⭐⭐",
        "description": "Wireless headphones"
    },
    {
        "name": "Dell Inspiron 15",
        "price": 55990,
        "rating": "⭐⭐⭐⭐",
        "description": "Laptop"
    },
    {
        "name": "boAt Airdopes 141",
        "price": 1299,
        "rating": "⭐⭐⭐",
        "description": "Wireless earbuds"
    }
]

