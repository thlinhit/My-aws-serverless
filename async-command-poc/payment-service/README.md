

```shell
curl -X POST http://localhost:3000/ecommerce/payments/validate \
     -H "Content-Type: application/json" \
     -d '{
            "orderId": "abafc3c4-6c64-41f1-99df-aed2f44d87ef",
            "userId": "992345678901",
            "total": 100.00
        }'
```