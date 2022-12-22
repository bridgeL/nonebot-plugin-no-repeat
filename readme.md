<div align="center">

# nonebot_plugin_no_repeat 不要复读

防止代码炸了在群里复读刷屏，让你写插件的时候更安全

</div>

## 配置（可选）

| 名称                | 值             | 意义                                                | 默认值/推荐值 |
| ------------------- | -------------- | --------------------------------------------------- | ------------- |
| no_repeat_mode      | use, not_use   | 白名单模式(use) or 黑名单模式(not_use)              | not_use       |
| no_repeat_groups    | [12345, 23456] | 群聊号                                              | []            |
| no_repeat_threshold | 3              | 发送重复语句达到3条后视为复读（第三条会被阻止发送） | 3             |
| no_repeat_gap       | 20             | 与上一条语句的发送间隔超过20s则不视为复读           | 20            |


白名单模式：仅在指定群内开启该功能

黑名单模式：仅在指定群内关闭该功能（比如你的机器人专用调试群），其他群均开启该功能

## 实现原理

https://v2.nonebot.dev/docs/next/advanced/runtime-hook#bot-api-%E8%B0%83%E7%94%A8%E9%92%A9%E5%AD%90

检测到异常复读情况后抛出`MockApiException`
