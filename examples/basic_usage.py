"""
Mrliouword Agent SDK - 基本使用範例
"""
import asyncio
from mrliouword_agents.agents.data_analyzer import MrliouwordDataAnalyzer
from mrliouword_agents.agents.code_reviewer import MrliouwordCodeReviewer
from mrliouword_agents.core.logger import get_logger

logger = get_logger(__name__)


async def example_data_analysis():
    """範例: 數據分析"""
    print("\n" + "=" * 50)
    print("範例 1: 數據分析")
    print("=" * 50 + "\n")

    analyzer = MrliouwordDataAnalyzer()

    # 分析 CSV 檔案
    async for message in analyzer.analyze_file(
        file_path="data/input/sample_sales.csv", full_analysis=True
    ):
        print(message)


async def example_code_review():
    """範例: 程式碼審查"""
    print("\n" + "=" * 50)
    print("範例 2: 程式碼審查")
    print("=" * 50 + "\n")

    reviewer = MrliouwordCodeReviewer()

    # 審查 Python 檔案
    async for message in reviewer.review_code(
        file_path="mrliouword_agents/core/base_agent.py", strict_mode=False
    ):
        print(message)


async def example_generate_report():
    """範例: 生成分析報告"""
    print("\n" + "=" * 50)
    print("範例 3: 生成報告")
    print("=" * 50 + "\n")

    analyzer = MrliouwordDataAnalyzer()

    # 生成完整報告
    async for message in analyzer.generate_report(
        file_path="data/input/sample_sales.csv",
        output_path="data/output/sales_analysis_report.md",
    ):
        print(message)


async def main():
    """執行所有範例"""
    logger.info("✓ Mrliouword Agent SDK 範例開始")

    try:
        # 執行範例
        await example_data_analysis()
        await example_code_review()
        await example_generate_report()

        logger.info("✓ 所有範例執行完成")

    except Exception as e:
        logger.error(f"✗ 執行錯誤: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
