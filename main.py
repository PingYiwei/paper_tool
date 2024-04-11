import datetime
import requests
import json
import arxiv
import os


# 根据关键词获取论文信息
def get_paper(topic, query="", max_results=2):
    """
    检索论文
    :param topic:
    :param query:
    :param max_results:
    :return:
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

    for result in results:
        print(result.title)


if __name__ == '__main__':
    topic = "quantum"
    query = "quantum"
    get_paper(topic, query)


