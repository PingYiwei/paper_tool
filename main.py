import datetime
import json
import arxiv
import os

from llm_tool import moonshot_tool
from llm_tool.gen_tool import print_with_timestamp

import schedule
import time
import markdown2


def get_authors(authors, first_author=False):
    """
    用于对文章作者进行处理
    :param authors: 作者列表
    :param first_author: 是否只需要第一作者
    :return: 作者名称
    """
    output = str()
    if not first_author:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output


def save_json_file(dir_name, topic_paper):
    """
    用于将检索的论文信息保存为json文件
    :param dir_name: 保存文件的目录
    :param topic_paper: 论文信息
    :return: 无返回
    """
    # 如果不存在目录就创建
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    # 以当前的时间点为文件名称
    file_name = os.path.join(dir_name, datetime.datetime.now().strftime("%Y%m%d")+".json")

    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump(topic_paper, f)

        print_with_timestamp(f"保存论文信息文件 {file_name} 完成...")
    else:
        print_with_timestamp(f"论文信息文件 {file_name} 已经存在...")

    return file_name


def download_paper(judge_result_path, dir_path):
    """
    下载论文
    :param dir_path: 保存论文pdf的路径
    :param judge_result_path: 论文id的json文件路径
    :return: 无返回
    """
    # 读取json文件
    with open(judge_result_path, "r") as f:
        paper_id_dict_list = json.load(f)

    if len(paper_id_dict_list) == 0:
        raise ValueError("筛选结果为空，没有需要下载的论文...")

    # 获取论文的id
    paper_id_list = [paper_id_dict["paper_id"] for paper_id_dict in paper_id_dict_list]

    for paper_id in paper_id_list:
        # 对论文进行检测是否存在
        if not os.path.exists(os.path.join(dir_path, paper_id+".pdf")):
            print_with_timestamp(f"开始下载 {paper_id}.pdf...")
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            paper.download_pdf(filename=paper_id+".pdf", dirpath=dir_path)
            print_with_timestamp(f"下载 {paper_id}.pdf 完成...")
        else:
            print_with_timestamp(f"{paper_id}.pdf 已经存在，无需下载...")


def process_keywords(keywords):
    """
    用于对关键词进行处理
    :param keywords:
    :return:
    """
    query_list = []
    for i in range(len(keywords) // 4):
        key = f'k-{i}-'
        # 检查每组四个关键词，组合成所需的字符串
        all_str_parts = []
        for j in range(4):
            keyword = keywords[key + str(j)]
            if keyword:
                if j == 0:
                    all_str_parts.append(f'all:\"{keyword}\"')
                elif j == 1:
                    all_str_parts.append(f'ti:\"{keyword}\"')
                elif j == 2:
                    all_str_parts.append(f'au:\"{keyword}\"')
                elif j == 3:
                    all_str_parts.append(f'abs:\"{keyword}\"')
        query_list.append(" AND ".join(all_str_parts))
    return query_list


def output_md_and_pdf(paper_data_path, topic, query_list):
    """
    用于生成markdown文件和pdf文件
    :return: none
    """
    print_with_timestamp("开始生成markdown文件和pdf文件...")

    # 提取所有论文信息
    paper_info = moonshot_tool.extract_paper_data(paper_data_path)

    # 总结文件
    summary_json = paper_data_path.replace(".json", "_summary.json")
    # md文件
    md_file = paper_data_path.replace(".json", ".md")

    # 时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(md_file, "w+", encoding='utf-8') as f:
        pass

    with open(md_file, "a+", encoding='utf-8') as m:

        # 标题
        m.write("## 论文自动化结果\n")
        # 更新时间
        m.write(f"### 更新时间：{current_time}\n\n")
        # 主题
        m.write(f"### 主题：{topic}\n")
        # 关键词
        for query in query_list:
            m.write(f"#### 关键词：{query}\n")

        m.write(f"\n\n")

        with open(summary_json, "r", encoding='utf-8') as f:
            summary_data = json.load(f)
            # 总论文数量
            m.write(f"#### 共总结论文数量：{len(summary_data)}\n")

            paper_num = 1
            # 各论文详细情况
            for paper_id, paper_summary in summary_data.items():
                # 在paper_info数组中找到paper_id一致的项
                current_paper = next((item for item in paper_info if item["paper_id"] == paper_id), None)
                # print(current_paper)

                if current_paper is None:
                    continue

                # 论文序号
                m.write(f"#### 论文序号：{paper_num}\n")
                # 论文标题
                m.write(f"**论文标题**：{current_paper['paper_title']}\n\n")
                # 论文作者
                m.write(f"**论文作者**：{current_paper['paper_authors']}\n\n")
                # 论文发表时间
                m.write(f"**论文发表时间**：{current_paper['paper_published_time']}\n\n")
                # 论文总结
                m.write(f"**论文总结**：{paper_summary['summary']}\n\n")
                # 论文关键点1
                m.write(f"**论文关键点1**：{paper_summary['keypoints_1']}\n\n")
                # 论文关键点2
                m.write(f"**论文关键点2**：{paper_summary['keypoints_2']}\n\n")
                # 论文地址
                m.write(f"**论文地址**：{current_paper['paper_entry_id']}")
                # 空行
                m.write(f"\n\n")

                paper_num += 1

    with open(md_file, "r", encoding='utf-8') as f:
        html = markdown2.markdown(f.read())

    # 保存HTML到文件
    with open(md_file.replace(".md", ".html"), "w", encoding="utf-8") as f:
        f.write(html)

    print_with_timestamp("生成markdown文件完成...")


def get_query_paper(query="", max_results=2):
    """
    根据关键词获取论文信息
    :param query: 关键词
    :param max_results: 最大数量
    :return: 检索结果
    """
    # 构造客户端
    client = arxiv.Client()

    # 发送请求，获取论文信息
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = client.results(search)

    # 存放信息的字典
    paper_content = dict()

    for result in results:

        paper_title = result.title  # 文章标题
        paper_entry_id = result.entry_id  # URL
        paper_authors = get_authors(result.authors)  # 作者
        """
        包括了这些类型
        Computer Science, 
        Economics, 
        Electrical Engineering and Systems Science, 
        Mathematics, 
        Physics, 
        Quantitative Biology, 
        Quantitative Finance, 
        Statistics
        """
        paper_primary_category = result.primary_category  # 所属的主要分类
        paper_published_time = result.published.date().strftime("%Y-%m-%d")  # 首次出版时间
        paper_abstract = result.summary.replace('\n', " ")  # 论文的摘要

        # paper的id，用于识别唯一性
        paper_id = result.get_short_id()

        paper_content[paper_id] = {
            "paper_id": paper_id,
            "paper_title": paper_title,
            "paper_entry_id": paper_entry_id,
            "paper_authors": paper_authors,
            "paper_primary_category": paper_primary_category,
            "paper_published_time": paper_published_time,
            "paper_abstract": paper_abstract,
        }

    print_with_timestamp(f"关键词 {query} 检索到 {max_results} 个结果...")

    return paper_content


def get_topic_paper(topic, query_list=None, max_results=2):
    """
    根据主题对论文进行检索
    :param topic: 主题
    :param query_list: 关键词列表
    :param max_results: 单关键词最大论文数量
    :return: 检索结果
    """
    # 如果没有提供query，则返回，并报错
    if query_list is None:
        raise ValueError("没有提供关键词列表...")

    topic_paper = dict()

    for query in query_list:
        paper_content = get_query_paper(query, max_results)
        topic_paper[query.strip('"')] = paper_content

    return {topic: topic_paper}


def paper_process(
        topic: str,
        query_list: list,
        max_results_per_query: int,
        judge_number: int,
        root_dir: str,
        is_free_account=True
):
    """
    论文主函数
    :return: 无返回
    """

    print_with_timestamp('开始执行主题为："' + topic + '"的论文自动化任务')

    # 判断目录是否存在
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    current_dir = root_dir

    # 建立当日任务的保存目录
    daily_dir_name = os.path.join(current_dir, 'paper', datetime.datetime.now().strftime("%Y%m%d"))

    # 获取主题的论文信息
    topic_paper = get_topic_paper(topic, query_list, max_results=max_results_per_query)

    # 保存论文信息
    paper_data_path = save_json_file(dir_name=daily_dir_name, topic_paper=topic_paper)

    # 通过llm选取论文
    judge_result_path = moonshot_tool.judge_paper(paper_data_path=paper_data_path, paper_number=max_results_per_query,
                                                  judge_number=judge_number, llm="moonshot")

    # 下载论文
    download_paper(judge_result_path=judge_result_path, dir_path=daily_dir_name)

    # 对论文进行总结
    moonshot_tool.summary_paper(judge_result_path=judge_result_path,
                                root_paper_path=os.path.join(current_dir, 'paper'),
                                daily_dir=daily_dir_name,
                                is_free_account=is_free_account)

    # 输出md和html
    output_md_and_pdf(paper_data_path, topic, query_list)


if __name__ == '__main__':
    # 主题与关键词
    topic = "Green and Low-carbon"
    query_list = ["\"low carbon\"", "\"green building\""]
    max_results_per_query = 1
    paper_number = len(query_list) * max_results_per_query
    judge_number = 2
    if judge_number > paper_number:
        raise ValueError("筛选论文的数量不能大于总论文数量...")

    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 建立当日任务的保存目录
    daily_dir_name = os.path.join(current_dir, 'paper', datetime.datetime.now().strftime("%Y%m%d"))

    # 获取主题的论文信息
    topic_paper = get_topic_paper(topic, query_list, max_results=max_results_per_query)

    # 保存论文信息
    paper_data_path = save_json_file(dir_name=daily_dir_name, topic_paper=topic_paper)

    # 通过llm选取论文
    judge_result_path = moonshot_tool.judge_paper(paper_data_path=paper_data_path, paper_number=paper_number,
                                                  judge_number=judge_number, llm="moonshot")

    # 下载论文
    download_paper(judge_result_path=judge_result_path, dir_path=daily_dir_name)

    # 对论文进行总结
    moonshot_tool.summary_paper(judge_result_path=judge_result_path, root_paper_path=os.path.join(current_dir, 'paper'),
                                daily_dir=daily_dir_name)

    print_with_timestamp("任务启动...")
    # 读取配置文件
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 执行主函数
    os.environ["KIMI_API_KEY"] = config["api_key"]
    os.environ["KIMI_BASE_URL"] = "https://api.moonshot.cn/v1"

    # 中文到英文的周几映射
    weekday_mapping = {
        "周一": "mon",
        "周二": "tue",
        "周三": "wed",
        "周四": "thu",
        "周五": "fri",
        "周六": "sat",
        "周日": "sun"
    }

    # 对关键词进行处理
    query_list = process_keywords(config["keyword"])

    # 定义定时任务函数
    def schedule_task(chinese_weekdays, hour, minute):
        # 将中文周几列表转换为英文缩写列表
        weekdays = [weekday_mapping[wd] for wd in chinese_weekdays]

        # 创建定时任务
        for day in weekdays:
            schedule.every().day.at(f"{hour}:{minute}").do(
                lambda: paper_process(
                    topic=config["topic"],
                    query_list=query_list,
                    max_results_per_query=config["max_results_per_query"],
                    judge_number=config["judge_number"],
                    root_dir=config["root_dir"],
                    is_free_account=config["is_free_account"]
                )
            ).tag(day)


    # 提早20分钟触发任务
    schedule_task(config["selected_days"], config["daily_time"][0], config["daily_time"][1])

    # 持续运行直到手动停止
    while True:
        # 检查定时任务是否需要执行
        schedule.run_pending()
        time.sleep(10)  # 每隔60秒检查一次
        print_with_timestamp("任务运行中...")

