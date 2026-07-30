# SQLAlchemy study note

## 第一章 SQLAlchemy集成
### SQLAlchemy集成
- 安装：`pip install "sqlalchemy[asyncio]" aiomysql`
- 代码：[sql_alchemy_init.py](../orm/sql_alchemy_init.py)
  - 创建异步数据库引擎
  - 创建数据模型（继承`DeclarativeBase`类）
  - 在FastAPI的`lifescan`中建库、建表(只有当表不存在时才会创建)
  - 基于异步引擎创建异步会话(`AsyncSession`)
  - 在router中依赖异步会话，通过`AsyncSession`对象执行SQL
- 问题：
  - 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？

### 增删改查
#### 增
- 示例：[sql_alchemy_init.py:insert_books](../orm/sql_alchemy_init.py)
- 使用:
  - 批量添加：`AsyncSession.add_all()`
  - 添加单个：`AsyncSession.add()`
  - 提交事务

#### 删
- 示例：[sql_alchemy_init.py:delete_orm & delete_by](../orm/sql_alchemy_init.py)
- 删除分为两种方式：
  - ORM思维：通过`AsyncSession.delete()`删除，在执行删除前，必须先查询出对象，再删除对象,如果不先查，执行删除会报错，视角是对象
  - SQL思维：通过`select().where()`封装查询语句，再通过`AsyncSession.execute()`执行，视角是SQL本身
  > ORM思维更方便处理级联删除，如果存在级联关系，查询出对象时，对象里已经包含了级联对象，Alchmemy底层会级联删除.
  > 而SQL思维只关注当前数据，不会级联删除，会出现数据不一致情况 

#### 改
- 示例：[sql_alchemy_init.py:update_book](../orm/sql_alchemy_init.py)
- 查询出来，直接操作ORM对象即可，在提交事务时自动更新到数据库
- 原理：**脏标记追踪**
  - 修改的对象标记为dirty
  - 提交事务时，检查所有dirty对象，生成update语句更新

#### 查
- 示例：[sql_alchemy_init.py:search_book](../orm/sql_alchemy_init.py)
- 关键点:
  - `select().where()`封装查询语句，由`AsyncSession.execute()`执行
  - 执行后的结果，再通过`ScalarResult.scalars()`转为模型对象
- 按主键查询
  - `AsyncSession.get(DelarativeMode, primary_key)`: 按主键查询，快速获取详情信息
  - `AsyncSession.query(DelarativeMode).filter(DelarativeMode.id == primary_key)`: 按主键查询，返回查询结果对象
- 条件查询
  - `==`,`!=`,`>`,`>=`,`<`,`<=`,`like`,`in_`,`not_in_`
  - `&`, `|`,`~`,逻辑运算符优先级高于`==`,`!=`,`>`等，因此在连接多个条件时，需要使用括号进行括号运算
  - `like`模糊查询通配符：`%`匹配任意字符，`_`匹配任意一个字符
- 聚合查询
  - `func.count()`,`func.sum()`,`func.avg()`,`func.max()`,`func.min()`
  - 示例: [sql_alchemy_init.py:book_statistics](../orm/sql_alchemy_init.py)
- 分页查询
  - 关键参数：`offset`,`limit`, 和mysql的limit offset语法一致
  - `offset`计算：(page - 1) * page_size
  - 示例：[sql_alchemy_init.py:search_book](../orm/sql_alchemy_init.py)
