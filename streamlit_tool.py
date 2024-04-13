import datetime
import streamlit as st
import os

# 设置页面标题
st.title("论文自动化工具")

st.info("受版权限制，目前本工具仅支持Arxiv")
st.warning('因为Moonshot AI（kimi chat）每个人免费的API Key额度为15元，所以尽可能控制运行的频率，另外，免费账户的并发量有限，1分钟仅能发送3次，'
           '所以程序通常会在报告生成的时间前间隔运行，以确保能完成任务')

# region 添加侧边栏
# 添加侧边栏标题
st.sidebar.title('基本配置')

# 输入API Key
api_key = st.sidebar.text_input('Moonshot AI API Key', max_chars=100, help='输入Moonshot AI的API Key')

# 添加侧边栏中的复选框
checkbox_value = st.sidebar.checkbox('将论文信息发送至邮箱')

# 如果复选框被选中，则显示更多信息
if checkbox_value:
    st.sidebar.text_input('输入你的邮箱地址')

# 运行日
days_of_week = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

# 多选周几
selected_days = st.sidebar.multiselect("选择运行的频率", options=days_of_week)

# 运行时间
t = st.sidebar.time_input('每日生成报告的时间', datetime.time(9, 15), help="这是生成报告的时间，实际程序运行会在此之前")
st.sidebar.write('运行时间为：', t)

# 添加侧边栏中的运行按钮
if st.sidebar.button('运行', use_container_width=True):
    if not api_key:
        st.sidebar.error('请输入API Key')
    else:
        st.sidebar.success('开始执行...')

# endregion

# region 创建主题
st.subheader('创建主题')

topic = st.text_input('请输入主题', '')

options = st.multiselect(
    label='选择检索的对象',
    options=('全域', '标题', '作者', '摘要', '全文'),
    default=None,
    format_func=str,
    help='可以选择一个或多个需要检索的对象',
    placeholder=''
)

# 创建一个字典来存储每个选项的查询内容
queries = {}
queries_number = {}

# 根据选择的内容创建对应内容的输入框
for option in options:
    queries[option] = st.text_input(f'{option}检索关键词', queries.get(option, ''),
                                    placeholder='以英文逗号分隔输入英文关键词')

    # 统计字符串数量
    if queries[option]:
        # 使用逗号分割字符串，并去除首尾的空格
        strings = [s.strip() for s in queries[option].split(",")]
        # 计算字符串数量
        queries_number[option] = len(strings)
        # 显示统计结果
        st.write(f"{option} 输入的关键词数量为：{queries_number[option]}")

# endregion

# region 参数设置
st.subheader('参数设置')

max_results_per_query = st.number_input(
    label='论文检索数量',
    min_value=1,
    max_value=20,
    value=1,
    step=1,
    help='设置每个关键词的检索数量，不建议设置过大，容易被封ip',
)

judge_number = st.number_input(
    label='经大模型筛选后保留的论文数量',
    min_value=1,
    max_value=5,
    value=1,
    step=1,
    help='这一数量不能大于最大论文检索数量',
)

if judge_number:
    pass
# endregion


# 设置页面标题
st.subheader("文件保存路径")

# 默认文件保存路径
default_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper")

# 输入文件保存路径
file_path = st.text_input("请输入文件保存路径", value=default_file_path, help="输入文件保存路径")
