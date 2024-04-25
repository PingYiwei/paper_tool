# 📚论文自动化工具
**开发者：中建八局工程研究院绿色低碳技术研究所**  
  
本工具用于监测[Arxiv](https://arxiv.org/)上最新论文的动态，并根据用户设定的主题、关键词等进行自动化检索、下载、筛选、总结分析并形成简报，其中筛选和总结分析采用了Moonshot AI的大模型[Kimi Chat](https://kimi.moonshot.cn/)。

## 🚀使用说明
  
**1-从git上clone项目**  

```
git clone https://github.com/PingYiwei/paper_tool.git
```
  
**2-配置环境**  
  
使用Anaconda或者其他工具部署python基本环境，在当前环境下切换到git库目录，进行库的安装

```
// 切换到目录
cd git仓库的目录下

// 安装必要的库
pip install -r requirements.txt
```
  
**3-启动工具**  
  
在仓库目录下，使用如下命令启动

```
streamlit run .\streamlit_tool.py
```

当看到下列字样，代表启动成功
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://xx.xx.xx.xx:8501
```
  
**4-工具配置**  
  
在打开的网页界面中，对各个参数进行设置，其中API Key请在[Moonshot AI](https://platform.moonshot.cn/)的开发者中心-->用户中心-->API Key管理中创建（每个人的免费额度为15元，会根据使用额度消耗）

**5-运行任务**  
  
点击界面左侧【保存配置文件】按钮后，点击【运行任务】即可开始运行论文自动化任务，当在命令行界面中看到如下字样则代表任务启动成功  
```
2024-04-25 14:05:50 任务启动...
2024-04-25 14:06:00 任务运行中...
```
  
## 📜注意事项
- arXiv目前支持英文检索，在填写关键词时请输入英文
- 设置的定时时间例如为9:00，则系统将在8:40启动任务，确保有20分钟时间能执行完成
- 单次建议不要监测很大数量的论文，容易触发arXiv的ip封禁，同时也会消耗更多的大模型token额度
- 
 

![image](https://github.com/PingYiwei/paper_tool/assets/68776067/b38de1fc-1702-4b6d-bba7-3ba5220839a7)
