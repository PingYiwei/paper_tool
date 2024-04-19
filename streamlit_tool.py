import datetime
import subprocess

import streamlit as st
import os
import json

# 设置页面标题
st.title("论文自动化工具")
st.info("受版权限制，目前本工具仅支持Arxiv")

# region 添加侧边栏
# 添加侧边栏标题
st.sidebar.title('基本配置')
st.sidebar.warning('因为Moonshot AI（kimi chat）每个人免费的API Key额度为15元，所以尽可能控制运行的频率，另外，免费账户的并发量有限，1分钟仅能发送3次，'
                   '所以程序通常会在报告生成的时间前间隔运行，以确保能完成任务')

# 输入API Key
api_key = st.sidebar.text_input('Moonshot AI API Key', help='输入Moonshot AI的API Key', placeholder="请输入API Key")

# 是否为免费账户
is_free_account = st.sidebar.checkbox('是否是免费账户', help='以是否充值过50元以上为判断条件', value=True)

# 添加侧边栏中的复选框
# checkbox_value = st.sidebar.checkbox('将论文信息发送至邮箱')

# 如果复选框被选中，则显示更多信息
# if checkbox_value:
#     st.sidebar.text_input('输入你的邮箱地址')

# 运行日
days_of_week = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

# 多选周几
selected_days = st.sidebar.multiselect("选择运行的频率", options=days_of_week, placeholder="选择运行频率")

# 运行时间
daily_time = st.sidebar.time_input('每日生成报告的时间', datetime.time(9, 15), help="这是生成报告的时间，实际程序运行会在此之前")
st.sidebar.write('运行时间为：', daily_time)

# endregion

# region 创建主题
st.subheader('创建主题')

topic = st.text_input('请输入主题', '')

keyword_number = st.session_state['keyword_number'] if 'keyword_number' in st.session_state else 1
# 增加关键词组合的容器
if st.button('添加关键词组合'):
    if keyword_number < 2:
        keyword_number += 1
        st.session_state['keyword_number'] = keyword_number
    else:
        st.toast('关键词组合数量不能超过2个', icon="⚠️")

# 关键词类型
keyword_type = ['全域', '标题', '作者', '摘要']
# 创建关键词组合
keyword = dict()
for i in range(keyword_number):
    with st.container(border=True):
        st.markdown("**关键词组合%d**" % (i+1))
        cols = st.columns(4)
        for j, col in enumerate(cols):
            keyword[f"k-{i}-{j}"] = col.text_input(f'{keyword_type[j]}', '', key=f'k-{i}-{j}')
# endregion
# print(keyword)

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
root_dir = st.text_input("请输入文件保存路径", value=default_file_path, help="输入文件保存路径")

# 保存配置文件
if st.sidebar.button('保存配置文件', use_container_width=True):
    # 将时间转换为datetime.datetime对象
    current_datetime = datetime.datetime.combine(datetime.datetime.today(), daily_time)
    # 将时间提早20分钟
    adjusted_datetime = current_datetime - datetime.timedelta(minutes=20)
    # 构造配置参数的字典
    config = {
        'api_key': api_key,
        'is_free_account': is_free_account,
        'selected_days': selected_days,
        'daily_time': [str(adjusted_datetime.hour).zfill(2), str(adjusted_datetime.minute).zfill(2)],
        'topic': topic,
        'keyword': keyword,
        'max_results_per_query': max_results_per_query,
        'judge_number': judge_number,
        'root_dir': root_dir,
    }

    # 保存配置文件, json格式
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    st.toast('配置文件已保存', icon="✅")
# 添加侧边栏中的运行按钮
if st.sidebar.button('运行定时任务', use_container_width=True, type="primary"):
    if not os.path.exists('./config.json'):
        st.toast('请先保存配置文件', icon="⚠️")
    else:
        st.sidebar.success('开始执行...')
        subprocess.Popen(["python", "main.py"])

