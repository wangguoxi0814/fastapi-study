from fastapi import HTTPException

from main import app

@app.get("/product/{product_id}")
def product_detail(product_id: int):
    ids = [1, 2, 3, 4, 5, 6]
    if product_id not in ids:
        raise HTTPException(status_code=404, detail="Product not found")
    return f'product:{product_id}正在备货中'