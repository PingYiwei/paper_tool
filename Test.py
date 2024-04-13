import schedule
import time
import os

# 定义任务
def my_task():
    print("任务触发了！")

# 定义定时任务函数
def schedule_task(weekdays, hour, minute):
    # 将周几的列表转换为schedule模块需要的格式
    weekdays = [f"monday.{week}" for week in weekdays]

    # 创建定时任务
    for day in weekdays:
        schedule.every().day.at(f"{hour}:{minute}").do(my_task).tag(day)

# 示例：每周一、周三、周五的12点触发任务
schedule_task(["sat"], 17, 35)

os.environ["KIMI_API_KEY"] = "hello"
print(os.getenv("KIMI_API_KEY"))

# 持续运行直到手动停止
while True:
    # 检查定时任务是否需要执行
    schedule.run_pending()
    time.sleep(60)  # 每隔60秒检查一次