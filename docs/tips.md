# TIPS
> 记录注意点和思考

## 中间件
2. 中间件怎么定义拦截规则？
3. 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？

## 生命周期
1. 如何组合redis\mysql多个初始化操作为一个lifespan?

## SQLAlchemy
1. 数据库异步引擎在io时会让出cpu去执行，这样会很容易让连接池耗尽吗？
2. Enum 类型
3. refresh()
4. time和datetime区别？timedelta
5. 加__init__.py的作用是什么？不加也能正常导入
6. 依赖中的passlib[bcrypt]==1.7.4中的[]是什么?