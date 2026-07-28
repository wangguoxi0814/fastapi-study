from fastapi import FastAPI, Path

app = FastAPI()

@app.get('/book/{id}')
def get_book(id: int = Path(...)):
    return f'id:{id}的数据已找到'