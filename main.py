import datetime
import requests
import json
import arxiv
import os

from llm_tool import moonshot_tool


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

        print(f"保存论文信息文件 {file_name} 完成...")
    else:
        print(f"论文信息文件 {file_name} 已经存在...")

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

    # 获取论文的id
    paper_id_list = [paper_id_dict["paper_id"] for paper_id_dict in paper_id_dict_list]

    for paper_id in paper_id_list:
        # 对论文进行检测是否存在
        if not os.path.exists(os.path.join(dir_path, paper_id+".pdf")):
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            paper.download_pdf(filename=paper_id+".pdf", dirpath=dir_path)
            print(f"下载 {paper_id}.pdf 完成...")
        else:
            print(f"{paper_id}.pdf 已经存在，无需下载...")


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

    print(f"关键词 {query} 检索到 {max_results} 个结果...")

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





