

```shell
curl -X POST http://localhost:3000/ecommerce/products/validate \
     -H "Content-Type: application/json" \
     -d '{
            "products": [
                {
                    "id": "product1",
                    "name": "Product 1",
                    "price": 19.99,
                    "quantity": 2
                },
                {
                    "id": "product2",
                    "name": "Product 2",
                    "price": 5.99
                }
            ]
        }'
```