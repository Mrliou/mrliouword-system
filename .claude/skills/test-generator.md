# Test Generator Skill

## 描述

測試生成 Agent - 自動為程式碼生成單元測試。

## 功能

- 單元測試生成
- 整合測試生成
- 端對端測試生成
- 測試覆蓋率分析
- Mock 物件建立

## 使用方式

```python
from mrliouword_agents.agents import MrliouwordTestGenerator

generator = MrliouwordTestGenerator()
async for msg in generator.generate_tests("app.py", test_type="unit"):
    print(msg)
```
