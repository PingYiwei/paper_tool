import json
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def extract_paper_data(paper_data_path):
    """
    从json中读取数据，并仅保留paper_id、paper_title、paper_abstract字段
    :param paper_data_path: 论文数据的地址
    :return: 论文数据
    """
    with open(paper_data_path, "r", encoding="utf-8") as f:
        paper_data = json.load(f)
    # 提取每篇文章的信息
    papers_info = []
    for category, subcategories in paper_data.items():
        for subcategory, papers in subcategories.items():
            for paper_id, paper_info in papers.items():
                article = {
                    "paper_id": paper_info["paper_id"],
                    "paper_title": paper_info["paper_title"],
                    "paper_abstract": paper_info["paper_abstract"]
                }
                papers_info.append(article)

    return papers_info


def update_judge_results(paper_data_path, judge_results):
    """
    更新筛选结果
    :param paper_data_path: 论文信息地址
    :param judge_results: 判别结果
    :return: none
    """
    judge_result_path = paper_data_path.replace(".json", "_judge_result.json")
    with open(judge_result_path, "w", encoding="utf-8") as f:
        json.dump(json.loads(judge_results.strip("```json")), f, ensure_ascii=False, indent=4)

    return judge_result_path


def judge_paper(paper_data_path, paper_number, judge_number=2, llm="openai"):
    """
    使用 Kimi 对论文进行筛选
    :param judge_number: 筛选得到的论文数量
    :param llm: 大模型选择
    :param paper_data_path: 论文数据的地址
    :return: 筛选后论文的id，并保存为文件
    """
    judge_result_path = paper_data_path.replace(".json", "_judge_result.json")
    if os.path.exists(judge_result_path):
        print("论文筛选结果已经存在，从本地文件中读取...")
        return judge_result_path

    # 从论文json中提取paper_id、paper_title、paper_abstract字段
    papers_info = extract_paper_data(paper_data_path)

    if llm == "moonshot":
        client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL"),
        )
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system",
                 "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"
                            "同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
                {"role": "user",
                 "content": f"{papers_info} \n " + f"从用户提供的论文列表中选择{judge_number}" + "篇适合非专业人士阅读的论文，只需要以[{\"paper_id\": ""}]的json格式返回论文的paper_id，不需要其他内容"}
            ],
            temperature=0,
        )
    else:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": ""},
                {"role": "user",
                 "content": f"{papers_info} \n " + f"从用户提供的论文列表中选择{judge_number}" + "篇适合非专业人士阅读的论文，只需要以[{\"paper_id\": ""}]的json格式返回论文的paper_id，不需要其他内容"}
            ],
            temperature=0,
        )
    judge_results = completion.choices[0].message.content
    judge_result_path = update_judge_results(paper_data_path, judge_results)
    print(f"论文筛选完成，从总共 {paper_number} 篇论文中保留了 {judge_number} 篇论文...")

    return judge_result_path


def get_summary_from_moonshot(client, dir_path, paper_id):
    """
    从Moonshot AI获取论文总结
    :param client: 客户端
    :param dir_path: 保存目录
    :param paper_id: 论文id
    :return:
    """
    # 请求文件列表
    cloud_file_list = client.files.list().data  # 从服务端获取文件列表

    # 文件地址
    paper_pdf = os.path.join(dir_path, paper_id + ".pdf")

    # 使用列表解析来查找文件名，并提取对应的id
    result = [file.id for file in cloud_file_list if file.filename == (paper_id + ".pdf")]

    # 若云端已有该论文，则直接从云端提问，否则需要上传
    if result:
        file_content = client.files.content(file_id=result[0]).text

        # 调用kimi对论文进行摘要
        completion = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=[
                {"role": "system",
                 "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"
                            "同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
                {
                    "role": "system",
                    "content": file_content,
                },
                {
                    "role": "user",
                    "content": f"请用中文对{paper_id}.pdf进行总结归纳，不超过400字，并且列举2个创新点，以json格式返回,格式为"
                               + '{"summary": 在这里填写总结归纳内容, "keypoints_1": 在这里填写第一个创新点内容, '
                                 '"keypoints_2": 在这里填写第二个创新点内容}'
                }
            ],
            temperature=0,
        )
    else:
        # 文件对象
        file_object = client.files.create(file=Path(str(paper_pdf)), purpose="file-extract")
        file_content = client.files.content(file_id=file_object.id).text

        # 调用kimi对论文进行摘要
        completion = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=[
                {"role": "system",
                 "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"
                            "同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
                {
                    "role": "system",
                    "content": file_content,
                },
                {
                    "role": "user",
                    "content": f"请用中文对{paper_id}.pdf进行总结归纳，不超过400字，并且列举2个创新点，以json格式返回,格式为"
                               + '{"summary": 在这里填写总结归纳内容, "keypoints_1": 在这里填写第一个创新点内容, '
                                 '"keypoints_2": 在这里填写第二个创新点内容}'
                }
            ],
            temperature=0,
        )

    summary_content = json.loads(completion.choices[0].message.content.strip("```json"))

    return summary_content


def summary_paper(judge_result_path, root_paper_path, daily_dir):
    """
    对论文进行总结
    :param daily_dir: 每日信息保存目录
    :param root_paper_path: 论文根目录
    :param judge_result_path: 筛选后论文id的json文件
    :return: 无返回
    """
    # 读取json文件
    with open(judge_result_path, "r") as f:
        paper_id_dict_list = json.load(f)

    # 获取论文的id
    paper_id_list = [paper_id_dict["paper_id"] for paper_id_dict in paper_id_dict_list]

    # 初始化kimi引擎
    client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url=os.getenv("KIMI_BASE_URL"),
    )

    # 初始化summary_dict和current_paper_summary_dict
    # 前者是全部论文的总结，后者是当前任务论文的集合
    paper_summary_dict = dict()
    current_paper_summary_dict = dict()

    # 包含全部总结文件的路径
    total_summary_json_path = os.path.join(root_paper_path, "total_summary.json")

    for paper_id in paper_id_list:
        # 打开全部论文总结的json文件，如果不存在则创建，如果存在则查找是否有paper_id字段
        if not os.path.exists(os.path.join(root_paper_path, "total_summary.json")):
            with open(total_summary_json_path, "w", encoding="utf-8") as f:
                json.dump(paper_summary_dict, f, ensure_ascii=False, indent=4)
        else:
            with open(total_summary_json_path, "r", encoding="utf-8") as f:
                # 判断是否为空
                if os.path.getsize(os.path.join(root_paper_path, "total_summary.json")) != 0:
                    paper_summary_dict = json.load(f)
            # 检查是否存在 paper_id 字段
            if f"{paper_id}" in paper_summary_dict:
                print(f"论文 {paper_id} 已总结，从本地文件中拉取...")
                current_paper_summary_dict[paper_id] = paper_summary_dict[paper_id]
            else:
                print(f"论文 {paper_id} 未经总结，调用Moonshot AI总结...")
                summary_content = get_summary_from_moonshot(client, daily_dir, paper_id)
                current_paper_summary_dict[paper_id] = summary_content
                paper_summary_dict[paper_id] = summary_content
                with open(total_summary_json_path, "w", encoding='utf-8') as f:
                    json.dump(current_paper_summary_dict, f, ensure_ascii=False, indent=4)
                print(f"论文 {paper_id} 总结完成...")

    # 保存总结信息
    paper_summary_json_path = judge_result_path.replace("_judge_result.json", "_summary.json")
    with open(paper_summary_json_path, "w", encoding="utf-8") as f:
        json.dump(paper_summary_dict, f, ensure_ascii=False, indent=4)

    print("所有总结已完成...")


if __name__ == "__main__":
    # paper_data_path = "../paper/20240412130355.json"
    # judge_paper(paper_data_path, llm="kimi")
    # summary_paper("../paper/20240412130355_judge_result.json", dir_path="../paper")
    pass
