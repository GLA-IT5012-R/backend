
# 外键关系总结（1-N N-1 N-M）
| 父表                    | 子表                    | 关系类型 | 说明                         |
| --------------------- | --------------------- | ---- | -------------------------- |
| `users`               | `customisations`      | 1–N  | 一个用户可有多条定制配置               |
| `users`               | `cart`                | 1–N  | 一个用户可有多个购物车项               |
| `users`               | `orders`              | 1–N  | 一个用户可有多个订单                 |
| `users`               | `review`              | 1–N  | 一个用户可对多个产品评论               |
| `products`            | `customisations`      | 1–N  | 一个产品可被多条定制引用               |
| `products`            | `product_asset_links` | 1–N  | 套装产品可关联多个单品资源              |
| `product_assets`      | `product_asset_links` | 1–N  | 单品资源可被多个套装引用               |
| `product_asset_links` | N/A                   | N–M  | 套装 ↔ 单品资源 多对多关系            |
| `customisations`      | `cart`                | 1–N  | 一个定制可对应多个购物车项              |
| `customisations`      | `order_items`         | 1–N  | 一个定制可对应多个订单项               |
| `orders`              | `order_items`         | 1–N  | 一个订单可包含多个订单项               |
| `review`              | N/A                   | 1–N  | 产品可有多个评价（通过 product_id 关联） |
| `site_content`        | N/A                   | 1–1  | 内容独立，无外键                   |

# 所有表

| 表名                    | 字段                  | 含义       | 关系 / 外键                | 备注                                             |
| --------------------- | ------------------- | -------- | ---------------------- | ---------------------------------------------- |
| `users`               | `id`                | 主键       | PK                     | 用户唯一标识                                         |
|                       | `email`             | 邮箱，登录用   | UNIQUE                 | 登录凭证                                           |
|                       | `verification_code` | 邮箱验证码    |                        | 可保存当前有效验证码和过期时间                                |
|                       | `address`           | 用户默认收货地址 |                        | 初始化为空，可修改                                      |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |
| `product_assets`      | `id`                | 主键       | PK                     | 单品资源唯一标识                                       |
|                       | `type`              | 类型       |                        | 例如: 雪板/眼镜/衣服/鞋子/固定器                            |
|                       | `type_id`           | 类型编号     |                        | 固定编号: SB-001, G-001 等                          |
|                       | `type_name`         | 类型名称     |                        | 便于显示                                           |
|                       | `name`              | 商品名称     |                        | 用户理解的名称                                        |
|                       | `desc`              | 商品描述     |                        | 几句话介绍                                          |
|                       | `size`              | 尺寸       |                        | 例如 "140,160,180" 或 0（无尺寸）                      |
|                       | `texture_urls`      | JSON 数组  |                        | 预设纹理路径，例如 {"SB-001": ["front.png","back.png"]} |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |
| `products`            | `id`                | 主键       | PK                     | 套装或单品唯一标识                                      |
|                       | `name`              | 产品名称     |                        | 前端显示名称                                         |
|                       | `type`              | 类型       |                        | 1=单品, 2=套装                                     |
|                       | `status`            | 上架/下架    |                        | 布尔值                                            |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |
| `product_asset_links` | `id`                | 主键       | PK                     | N–M 关联表唯一标识                                    |
|                       | `product_id`        | 套装 ID    | FK → products.id       | 套装关联单品                                         |
|                       | `asset_id`          | 单品 ID    | FK → product_assets.id | 套装包含的单品                                        |
|                       | `quantity`          | 套装中单品数量  |                        | 默认为 1                                          |
| `customisations`      | `id`                | 主键       | PK                     | 用户自定义配置唯一标识                                    |
|                       | `user_id`           | 用户 ID    | FK → users.id          | 对应用户                                           |
|                       | `product_id`        | 产品 ID    | FK → products.id       | 用户定制的套装或单品                                     |
|                       | `custom_data`       | JSON     |                        | 存储用户选择的尺寸/纹理等信息                                |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
| `cart`                | `id`                | 主键       | PK                     | 购物车项唯一标识                                       |
|                       | `user_id`           | 用户 ID    | FK → users.id          | 对应用户                                           |
|                       | `design_id`         | 定制 ID    | FK → customisations.id | 用户选择的定制配置                                      |
|                       | `quantity`          | 数量       |                        | 默认为 1，用户可修改                                    |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |
| `orders`              | `id`                | 主键       | PK                     | 订单唯一标识                                         |
|                       | `user_id`           | 用户 ID    | FK → users.id          | 关联用户                                           |
|                       | `order_status`      | 状态       |                        | Pending / Confirmed / Shipped / Completed      |
|                       | `total_price`       | 总价       |                        | 自动计算                                           |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |
| `order_items`         | `id`                | 主键       | PK                     | 订单项唯一标识                                        |
|                       | `order_id`          | 订单 ID    | FK → orders.id         | 所属订单                                           |
|                       | `design_id`         | 定制 ID    | FK → customisations.id | 对应用户定制配置                                       |
|                       | `quantity`          | 数量       |                        | 与购物车一致                                         |
|                       | `unit_price`        | 单价       |                        | 对应设计单价                                         |
| `review`              | `id`                | 主键       | PK                     | 评论唯一标识                                         |
|                       | `user_id`           | 用户 ID    | FK → users.id          | 评论者                                            |
|                       | `product_id`        | 产品 ID    | FK → products.id       | 评论的产品                                          |
|                       | `rating`            | 评分       |                        | 1-5 星                                          |
|                       | `comment`           | 评论内容     |                        | 文本，不包含图片                                       |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
| `site_content`        | `id`                | 主键       | PK                     | 网站内容节点唯一标识                                     |
|                       | `section_name`      | 内容板块     |                        | 如 Brand Story / Customer Service               |
|                       | `content_json`      | JSON     |                        | 存储标题/段落/可展开状态等                                 |
|                       | `created_at`        | 创建时间     |                        | 自动生成                                           |
|                       | `updated_at`        | 更新时间     |                        | 自动生成                                           |

# ER图绘画要求
| 形状   | 代表含义       | 你的项目用法       |
| ---------- | ------------------- | -------- |
| 矩形 ▭	| 实体（对应数据库的表）	|   users products orders 等｜
| 椭圆 ○	| 属性（表里的字段）	   |  只标 PK 主键 + 1 个核心业务属性｜
| 菱形 ◇	| 关系（表之间的业务动作）	|  写动词（如 Creates/Owns/Places）+ 基数｜
| 连线 →	| 关联方向	从主表指向从表|  （如 users → customisations）｜


## 第一页 ER Diagram（用户端核心流程）

| 实体（矩形框）                 | 主键                   | 外键关系 / 备注                                                                           |
| ----------------------- | -------------------- | ----------------------------------------------------------------------------------- |
| **users**               | PK: user_id          | 1 → N → customisations（user_id）<br>1 → N → cart（user_id）<br>1 → N → orders（user_id） |
| **customisations**      | PK: customisation_id | 1 ← N ← users（user_id）<br>1 ← N ← products（product_id）用于记录用户定制选择                    |
| **cart**                | PK: cart_id          | 1 ← N ← users（user_id）<br>1 ← N ← customisations（design_id）存储用户加入购物车的定制商品           |
| **orders**              | PK: order_id         | 1 ← N ← users（user_id）<br>1 → N → order_items（order_id）存储订单下的每个商品                   |
| **order_items**         | PK: order_item_id    | 1 ← N ← orders（order_id）<br>1 ← N ← customisations（design_id）记录每个商品/定制内容及数量         |
| **products**            | PK: product_id       | 1 → N → customisations（product_id）<br>N–M → product_asset_links（套装关联单品资源）           |
| **product_asset_links** | PK: link_id          | N–M 连接 products（product_id，套装）和 product_assets（asset_id，单品）                         |

## 第二页 ER Diagram（后台/管理/扩展功能）

| 实体（矩形框）                 | 主键                   | 外键关系 / 备注                                                          |
| ----------------------- | -------------------- | ------------------------------------------------------------------ |
| **products**            | PK: product_id       | N–M → product_asset_links（套装↔单品资源）                                 |
| **product_assets**      | PK: asset_id         | N–M → product_asset_links（单品被套装引用）                                 |
| **product_asset_links** | PK: link_id          | N–M 连接 products ↔ product_assets                                   |
| **orders**              | PK: order_id         | 1 → N → order_items（order_id）<br>1 ← N ← users（user_id）用于管理员查看订单状态 |
| **order_items**         | PK: order_item_id    | 1 ← N ← orders（order_id）<br>1 ← N ← customisations（design_id）      |
| **customisations**      | PK: customisation_id | 1 ← N ← products（product_id）用于后台统计定制数据                             |
| **site_content**        | PK: content_id       | 可独立管理网站静态内容，供管理员修改品牌故事、客服信息等                                       |
