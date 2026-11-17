"""
Mrliouword CLI 工具
"""

import asyncio
import click
from pathlib import Path

from ..core.config import config
from ..core.logger import get_logger
from ..agents.data_analyzer import MrliouwordDataAnalyzer
from ..agents.code_reviewer import MrliouwordCodeReviewer

logger = get_logger(__name__)


@click.group()
@click.version_option(version=config.version)
def cli():
    """Mrliouword Agent SDK - 命令列工具"""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--full", is_flag=True, help="執行完整分析")
@click.option("--output", "-o", help="輸出報告路徑")
def analyze(file_path: str, full: bool, output: str):
    """分析數據檔案"""

    async def run():
        analyzer = MrliouwordDataAnalyzer()
        if output:
            async for msg in analyzer.generate_report(file_path, output):
                click.echo(msg)
        else:
            async for msg in analyzer.analyze_file(file_path, full):
                click.echo(msg)

    asyncio.run(run())


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="嚴格模式審查")
def review(file_path: str, strict: bool):
    """審查程式碼"""

    async def run():
        reviewer = MrliouwordCodeReviewer()
        async for msg in reviewer.review_code(file_path, strict):
            click.echo(msg)

    asyncio.run(run())


@cli.command()
@click.argument("project_path", type=click.Path())
def init(project_path: str):
    """初始化 Mrliouword 專案"""
    project_dir = Path(project_path)
    project_dir.mkdir(parents=True, exist_ok=True)

    # 建立 .claude 目錄結構
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    (claude_dir / "skills").mkdir(exist_ok=True)
    (claude_dir / "commands").mkdir(exist_ok=True)

    # 建立 README.md
    readme_content = """# Mrliouword AI Agent

這是使用 Mrliouword Agent SDK 建立的專案。

## 可用功能

- 數據分析
- 程式碼審查
- 測試生成
- 文件撰寫

## 開始使用

```bash
mrliouword analyze data.csv
mrliouword review code.py
```
"""
    (claude_dir / "README.md").write_text(readme_content, encoding="utf-8")

    click.echo(f"✓ Mrliouword 專案已初始化在: {project_path}")
    click.echo(f"✓ 配置目錄: {claude_dir}")


@cli.command()
def cost():
    """查看 API 使用成本"""
    from ..core.cost_tracker import CostTracker

    tracker = CostTracker()
    report = tracker.generate_report()
    click.echo(report)


if __name__ == "__main__":
    cli()
