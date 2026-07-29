from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

from main import app


# 自定义响应格式
class RoleModel(BaseModel):
    role_id: int
    role_name: str


# 固定路径放在通配路由前面，避免被 /role/{role_id} 拦截
@app.get("/role/info", response_model=RoleModel)
def role_info():
    return {
        "role_id": 1,
        "role_name": 'admin'
    }


@app.get("/role/{role_id}", response_class=JSONResponse)
def role_detail(role_id: int):
    return {"role_id": role_id}

@app.get("/role/html_info/{role_id}", response_class=HTMLResponse)
def role_html(role_id: int):
    return "<h1>当前角色描述信息</h1>"

@app.get("/role/img/{role_id}")
def role_img(role_id: int):
    path = './files/liudehua.jpg'
    return FileResponse(path)