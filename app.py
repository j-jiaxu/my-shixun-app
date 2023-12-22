import streamlit as st
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题
import jieba 
import re  
from collections import Counter 
import csv
from pyecharts import options as opts 
from pyecharts.charts import WordCloud,Funnel
import streamlit_echarts as ste
import math
import pandas as pd
#############################################################################################################

# 获取html文本
def get_html(url):
    response=requests.get(url)
    # 获取编码方式
    response.encoding = response.apparent_encoding
    return response.text

# 查找body标签中的数据
def get_data(html):
    soup=BeautifulSoup(html, 'html.parser')
    a_tags=soup.find('body')
    return a_tags

# 将body标签中的数据写到txt文件中
def get_txt(a_tags):
    a_tags_ls=a_tags.replace("\n"," ")
    # 以utf-8编码写入txt文件
    with open(f'words.txt','w',encoding='utf-8') as f:
        f.write(a_tags_ls)
    return 'words.txt'

# 读取txt文件并进行分词
def a_tags_read(a_tags_txt):
    # 读取文本文件  
    with open(a_tags_txt, 'r',encoding='utf-8') as f:  
        text = f.read()
    # 去除文本中的空格  
    text = re.sub(r'\s+', '', text)  
    # 去除文本中的标点符号  
    text = re.sub(r'[^\w\s]', '', text)  # 使用正则表达式去除标点符号

    # 对文本分词,统计词频
    words = jieba.lcut(text)  # 使用jieba分词  
    word_counts = Counter(words)  # 使用Counter统计词频

    # 过滤长度为1或者词频为1的词
    filtered_word_counts = {word: count for word, count in word_counts.items() if len(word) > 1 and count > 1}

    return filtered_word_counts  #返回分词结果

# 将分词结果写入CSV文件
def a_tags_csv(word_counts):
    # 以写的方式打开CSV文件
    with open('words1.csv', 'w', encoding='utf-8', newline='') as csvfile:  
        writer = csv.writer(csvfile)  
        writer.writerow(['Word', 'Counts'])  # 写入CSV文件的标题行  
        for word, counts in word_counts.items():
            if len(word)>1 and counts>1:
                writer.writerow([word, counts])  # 写入CSV文件中的每一行数据

# 获取词频最高的前20个词
def a_tags_top(word_counts):
    word_count = dict(Counter(word_counts).most_common(20))
    return word_count
##############################################################################################################
def common():
    st.title('Web Scraping and Visualization App')
    # 输入URL
    url = st.text_input('Enter the URL:')

    if url:
        # 获取html文本
        html=get_html(url)
        # 获取数据
        a_tags=get_data(html)
        # 生成txt文本
        a_tags_txt=get_txt(a_tags.text)
        # 将词放入csv文件
        word_counts=a_tags_read(a_tags_txt)
        a_tags_csv(word_counts)
        return word_counts
    else:
        return False
##############################################################################################################

        
# 绘制折线图
def plot_line_chart(word_count):
    # 画布大小设置
    fig=plt.figure(figsize=(10, 6))
    # 标题
    plt.title("折线图")
    # x、y轴名称
    plt.xlabel("words")
    plt.ylabel("counts")
    # 调用函数绘制折线图
    plt.plot(word_count.keys(), word_count.values(), marker='o')
    # 显示画布
    st.pyplot(fig)

# 饼图
def plot_pie_chart(word_count):
    fig=plt.figure(figsize=(10, 6))
    plt.title("饼图")
    # 调用函数绘制饼图，autopct='%1.1f%%'显示饼图每一部分的百分比，startangle=140饼图的起始角度
    plt.pie(word_count.values(),labels=word_count.keys(),autopct='%1.1f%%', startangle=140)
    st.pyplot(fig)

# 柱状图
def plot_bar_chart(word_count):
    fig=plt.figure(figsize=(10, 6))
    plt.title('柱状图')
    plt.xlabel('words')
    plt.ylabel('counts')
     # 调用函数绘制柱状图
    plt.bar(word_count.keys(),word_count.values(),0.8,color='green')
    st.pyplot(fig)

    
# 散点图
def plot_scatter_chart(word_count):
    if st.button("Re-run"):
        fig=plt.figure(figsize=(10, 6))
        plt.title('散点图')
        plt.xlabel('words')
        plt.ylabel('counts')
        plt.scatter(word_count.keys(),word_count.values())
        st.pyplot(fig)

# 直方图
def plot_plotly_chart(word_count):
    if st.button("Re-run"):
        fig=plt.figure(figsize=(10, 6))
        plt.title('直方图')
        plt.xlabel('words')
        plt.ylabel('counts')
        plt.hist(word_count.values(),bins=len(word_count),color='yellow')
        st.pyplot(fig)

# 雷达图
def plot_leida_chart(word_count):
    words=list(word_count.keys())
    counts=list(word_count.values())
    n = len(counts)
    angles = [i * 2 * math.pi / n for i in range(n)]
    angles.append(angles[0])
    counts.append(counts[0])
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, counts)
    ax.fill(angles, counts, alpha=0.3)
    ax.set_thetagrids([a * 180 / math.pi for a in angles[:-1]], words)
    ax.grid(True)
    ax.plot(angles, counts, 'o', linewidth=2)
    ax.plot(angles, counts, color='r', linewidth=2)
    st.pyplot(fig)
    



# 漏斗图
def plot_ld_charts(word_count):
    wf = Funnel()
    wf.add('漏斗图',[list(z) for z in zip(word_count.keys(), word_count.values())])
    ste.st_pyecharts(wf)

##############################################################################################################
# 词云
def plot_ciyun_chart(word_count,shape_mask):
    plt.title('词云图')
    # 将字典转为列表的形式
    ls=list(word_count.items())
    # 创建一个WordCloud类实例
    wordcloud = (  
        WordCloud()  
    .add("", ls, word_size_range=[30, 30+len(word_count)],shape=shape_mask)  
    .set_global_opts(title_opts=opts.TitleOpts(title="词云图")))

    # 保存为html文件
    wordcloud.render("wordcloud.html")

     # 读取 HTML 文件内容
    with open('wordcloud.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    # 在页面中显示 HTML 内容
    st.components.v1.html(html_content, height=500,width=900)

##############################################################################################################

def get_word():
    word_counts=common()
    if word_counts:
        # 上传 CSV 文件
        uploaded_file = st.file_uploader("words1.csv", type=['csv'])

        if uploaded_file is not None:
            # 读取上传的 CSV 文件
            data = pd.read_csv(uploaded_file)
            # 将 CSV 文件内容以表格形式显示在页面上
            st.cache_data(data)

def Visualization():
    #侧边栏选项
    list_baidu_project= ['折线图', '饼图', '柱形图','直方图','散点图','雷达图','漏斗图']
    selected_option = st.sidebar.selectbox("请选择图形类型",list_baidu_project)

    word_counts=common()
    # 获得词频最高的20个词
    word_count=a_tags_top(word_counts)
    # st.write(word_counts)

    if word_count:
        # 根据侧边栏选择显示不同的内容
        if selected_option == "折线图":
            plot_line_chart(word_count)
        elif selected_option == "饼图":
            plot_pie_chart(word_count)
        elif selected_option == "柱形图":
            plot_bar_chart(word_count)
        elif selected_option == "直方图":
            plot_plotly_chart(word_count)
        elif selected_option == "散点图":
            plot_scatter_chart(word_count)
        elif selected_option == "漏斗图":
            plot_ld_charts(word_count)
        elif selected_option == "雷达图":
            plot_leida_chart(word_count)


    
    
# 词云
def ciyun():
    word_counts=common()
    # 获得词频最高的20个词
    word_count=a_tags_top(word_counts)
    # 读取多个形状图片
    shape_images = {'circle','rect','roundRect','triangle','diamond','pinwheel','snowflake','heart','star'}
    shape_mask = st.sidebar.selectbox("shape",shape_images)

    if word_count!=None:
        plot_ciyun_chart(word_count,shape_mask)

##############################################################################################################


def main():
    # 创建侧边栏选项来切换页面
    page = st.sidebar.radio("选择页面", ("word_count", "Visualization","ciyun"))

    if page=="word_count":
        get_word()
    elif page=="Visualization":
        Visualization()
    elif page=="ciyun":
        ciyun()

   

    
    
    
    

if __name__=='__main__':
    main()
