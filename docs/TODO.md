# TIPS
> 记录问题和扩展知识，再统一整理到笔记中

## 20260731星期五深圳
- [X] 中间件怎么定义拦截规则？
- [X] hasattr(dispatch, '__name__')和getattr(current, 'dispatch', None)
- [X] 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？
- [X] 如何组合redis\mysql多个初始化操作为一个lifespan?写在一个lifespan函数即可
- [X] Enum 类型
- [X] refresh()
- [X] time和datetime区别？timedelta
- [X] 加__init__.py的作用是什么？不加也能正常导入
- [X] 依赖中的passlib[bcrypt]==1.7.4中的[]是什么?


## 20260801星期六深圳
- [X] 全局异常处理(事务)
- [X] 统一响应建模
   - 别名和populate_by_name
- [X] __pycache__是干嘛的？(编辑结构、不同python版本互不通用、自动被git忽略)
- [X] python异常捕获最佳实践和自定义异常
- [X] UserInfoResponse.model_validate(user)是干嘛的？必须开启from_attributes=True，如果没有配置，只能传字典。
- [X] 如果给ORM对象字段alias是怎样的？查询出来是别名还是字段名？保存的时候是操作别名还是字段名？适用什么场景？
- [X] 精简字段怎么查询。select时指定字段 
- [X] replace会改变原始字符串吗？split呢?
- [X] 怎么联合查询？
- [X] 时间用大于小于比较会有什么问题吗？
- [X] Alchemy的联合查询（左isouter=True、右isouter=True 、全外full=True）？联合查询多个连接条件？(and_)

## 20260802星期日深圳
- [X] `Pydantic`模型的`**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )`
- [X] `crypt_context.verify(content, hash_str)`
- [X] SQLAlchemy怎么做事务管理？
- [X] FastAPI多个依赖项执行顺序？从左至右、深度优先，缓存复用
- [X] 同一个方法的多个依赖项中有相同的依赖项，会缓存，只执行一次，比如`/user/password`中的获取session，且只有请求结束，才会关闭session
- [X] expire_on_commit=False的作用？commit后对象仍然identify_map中，只是一个是使用对象字段要重新查库，一个不需要。如果为True的情况下，commit后还使用对象会报：`(sqlalchemy.exc.MissingGreenlet) greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?`
      解决方法： 1. commit后db.refresh(obj) 2. 调整expire_on_commit=False
- [X] 游离态？关闭会话后，会话中的对象处于Detached状态；手动移除`session.expunge(obj)`;`session`作用域结束。即不存在于identify_map中的对象

## 20260803星期一深圳
- [X] SQLAlchemy设置唯一约束`UniqueConstraint` 
- [X] 连表查询获取多表字段，并且取别名,返回的是元组列表，元组推导式解构
- [X] typing中的List和list区别？以及typing这个包是干嘛的？
- [X] Redis使用流程,回顾装饰器原理，用装饰器实现旁路缓存，如果既要能够修饰普通函数，又要能够修饰async函数怎么做？
- [X] 怎么判断变量是不是一个类的实例还是简单数据类型
- [X] 回顾闭包和作用域
- [X] ORM对象无法序列化？通过jsonable_encoder()转化之后，变成了什么?jsonable_encoder支持哪些类型？为什么Java里的类可以直接序列化？
- [X] Redis客户端操作时，不同指令之间不要有; 否则会被当作key的一部分
- [X] 函数类型入参Callable[..., Any]类型注解
- [X] str的format语法，用途见CacheAside中从字段参数中解析key

## 20260804星期二深圳
- [X] //是干嘛的
- [X] Pydantic类的model_validate(orm_item).model_dump(mode="json", by_alias=False)
- [X] 回顾MRO
- [X] conversation review skill生成文件日期似乎不是按照当前时间，增加引用代码的显示
- [X] Cursor的BugBot怎么使用?


## 20260805星期三深圳
- [ ] （深入）为什么在异步IO上下文中触发同步IO会报错？greentlet的原理？
  - 上下文：在[users.py#change_password](../daily_news_project/crud/users.py)中如果将session的`expire_on_commit=True`,且手动`await db.commit()`后，再操作ORM对象，SQLAlchemy就会去数据库重新查询，触发同步IO，此时就会报错
- [ ] 解决FastAPI docs无法传入Authorization Header问题, 引入Oauth2方法，作为依赖项后，docs中有模拟登录接口，获取token。直接从请求头里获取Authorization,复制给依赖项中的token，接口传值一定要符合OAuth2规范，token必须有Bearer前缀，否则鉴权失败。本新项目前端没有遵守该规范
