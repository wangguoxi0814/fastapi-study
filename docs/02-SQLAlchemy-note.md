from sqlalchemy import UniqueConstraint

# SQLAlchemy study note

## 第一章 SQLAlchemy集成
### SQLAlchemy集成
- 前置：安装MySQL8.0+
- 安装：`pip install "sqlalchemy[asyncio]" aiomysql`
- 代码：[sql_alchemy_init.py](../basic_study/orm/sql_alchemy_init.py)
  - 创建异步数据库引擎
  - 创建数据模型（继承`DeclarativeBase`类）
  - 在FastAPI的`lifescan`中建库、建表(只有当表不存在时才会创建)
  - 基于异步引擎创建异步会话(`AsyncSession`)
  - 在router中依赖异步会话，通过`AsyncSession`对象执行SQL
- 问题：
  - 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？

### SQLAlchemy建模
- 继承`DeclarativeBase`的类
- 表名定义: `__tablename__`
- 索引和唯一约束定义
  ```python
  __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        Index('fk_news_category_idx', 'category_id'), 
        Index('idx_publish_time', 'publish_time')  
    )
  ```
  - UniqueConstraint参数分别为：字段名，约束名称
  - Index参数分别为：索引名称，索引字段

- 字段定义
  - `Mapped[T]`作为模型字段类型注解，告诉SQLAlchemy这是数据库字段，否则会报错。如果字段不需要映射到数据库，使用`ClassVar[]` 
    - 字段类型对应关系(Python->SQLAlchemy->MySQL)
      - int -> INTEGER -> int
      - str -> String() -> varchar()
      - xxx -> Enum(xxx, xxx) -> enum(xxx, xxx). xxx可以是任意类型，和枚举项类型匹配即可
  - 如果允许字段为空，使用`Mapped[Optional[str]]`，这样在操作ORM对象时，可以赋值为None，但数据库字段是否允许为`None`，由`mapped_column()`的`nullable`的bool值决定
  - 外键字段由`mapped_column(ForeignKey(f'{table_name}.{key}'))`指定
  - 
### 增删改查
#### 增
- 示例：[sql_alchemy_init.py:insert_books](../basic_study/orm/sql_alchemy_init.py)
- 使用:
  - 批量添加：`AsyncSession.add_all()`
  - 添加单个：`AsyncSession.add()`
  - 提交事务

#### 删
- 示例：[sql_alchemy_init.py:delete_orm & delete_by](../basic_study/orm/sql_alchemy_init.py)
- 删除分为两种方式：
  - ORM思维：通过`AsyncSession.delete()`删除，在执行删除前，必须先查询出对象，再删除对象,如果不先查，执行删除会报错，视角是对象
  - SQL思维：通过`select().where()`封装查询语句，再通过`AsyncSession.execute()`执行，视角是SQL本身
  > ORM思维更方便处理级联删除，如果存在级联关系，查询出对象时，对象里已经包含了级联对象，Alchmemy底层会级联删除.
  > 而SQL思维只关注当前数据，不会级联删除，会出现数据不一致情况 

#### 改
- 示例：[sql_alchemy_init.py:update_book](../basic_study/orm/sql_alchemy_init.py)
- 使用：
  - 查询出来，直接操作ORM对象即可，在提交事务时自动更新到数据库
  - `update(ORM_MODEL).where().values(field1=value1, field2=value2)` 按条件修改指定字段，由`db_session.execute()`执行。`values`的字段名如果不存在于ORM对象中，会报错
- 原理：**脏标记追踪**
  - 修改的对象标记为dirty
  - 提交事务时，检查所有dirty对象，生成update语句更新

#### 查
- 示例：[sql_alchemy_init.py:search_book](../basic_study/orm/sql_alchemy_init.py)
- 关键点:
  - `select().where()`封装查询语句，由`AsyncSession.execute()`执行,返回`Result`对象
  - 执行后的结果，再通过`Result.scalars()`转为模型对象，返回`ScalarResult`
  - `Result`获取结果的方法:
     - `Result.scalars().all()`: 获取所有结果,没有返回None
     - `Result.scalars().first()`: 获取第一个结果，没有返回None
     - `Result.scalars().one()`: 获取唯一结果，0条或多条数据会报错
     - `Result.scalar_one()`: 获取唯一结果，0条或多条数据会报错
     - `Result.scalar_one_or_none()`: 获取唯一结果，如果没有结果，返回None，如果由多条结果，异常
- 按主键查询
  - `AsyncSession.get(DelarativeMode, primary_key)`: 按主键查询，快速获取详情信息
  - `AsyncSession.query(DelarativeMode).filter(DelarativeMode.id == primary_key)`: 按主键查询，返回查询结果对象
- 条件查询
  - `==`,`!=`,`>`,`>=`,`<`,`<=`,`like`,`in_`,`not_in_`
  - `&`, `|`,`~`,逻辑运算符优先级高于`==`,`!=`,`>`等，因此在连接多个条件时，需要使用括号进行括号运算
  - `like`模糊查询通配符：`%`匹配任意字符，`_`匹配任意一个字符
- 聚合查询
  - `func.count()`,`func.sum()`,`func.avg()`,`func.max()`,`func.min()`
  - 示例: [sql_alchemy_init.py:book_statistics](../basic_study/orm/sql_alchemy_init.py)
- 分页查询
  - 关键参数：`offset`,`limit`, 和mysql的limit offset语法一致
  - `offset`计算：(page - 1) * page_size
  - 示例：[sql_alchemy_init.py:search_book](../basic_study/orm/sql_alchemy_init.py)

### 会话管理
- 代码示例：[db_conf.py](../daily_news_project/config/db_conf.py)
- `async_sessionmaker(expired_at_commit=xxx)`中参数`expired_at_commit`:
  - True：commit后，ORM对象所有属性标记为过期，所以ORM对象不可用，但仍在session的identify_map中
    - 如果访问过期ORM对象属性，SQLAlchemy会重新查询数据库，触发同步IO，但当在异步上下文中时触发同步IO，会报：`(sqlalchemy.exc.MissingGreenlet) greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? `
  - False: commit后，ORM对象可用，在session的identify_map中
- `await refresh(orm_obj)`：当ORM对象属性过期后，刷新ORM对象
