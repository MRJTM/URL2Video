def print_sorted_dict_with_percentage(data, head="", k_name="", value_name="", top=10):
    print('\n---------------- {} ----------------'.format(head))
    # 按照字典的值从大到小排序
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)

    # 计算总数
    total = sum(data.values())

    # 打印排序后的字典和每个类别的占比
    index = 0
    if len(k_name) == 0:
        k_name = "Category"
    if len(value_name) == 0:
        value_name = "Value"

    acc_percentage = 0
    for k, v in sorted_data:
        if index < top:
            percentage = (v / total) * 100
            acc_percentage += percentage
            print(
                f"top {index + 1:2}: {k_name}: {k:5}, {value_name}: {v:5}, Per: {percentage:7.4f}%, acc_per: {acc_percentage:7.4f}%")
        index += 1


# 用matplotlib绘制柱状图
import matplotlib.pyplot as plt


def plot_bar_chart(data_list, labels, title, xlabel, ylabel, min_x=None, max_x=None):
    # 创建图形
    x_num = len(data_list[0])
    plt.figure(figsize=(int(1 * x_num), 6))

    # 为每个数据集绘制柱状图
    for data, label in zip(data_list, labels):
        # 将dict转化为list_pair
        pairs = [(k, v) for k, v in data.items()]
        # 统计value之和，再计算占比
        total = sum(v for _, v in pairs)
        pairs = [(k, v, float(v) / total) for k, v in pairs]

        # 如果key是数字，那么按照key从小到大排列
        if all(isinstance(key, int) for key, _, _ in pairs):
            pairs = sorted(pairs, key=lambda x: x[0])
        if all(isinstance(key, float) for key, _, _ in pairs):
            pairs = sorted(pairs, key=lambda x: x[0])

        # 获取x, y, 和百分比
        x = [k for k, _, _ in pairs]
        y = [v for _, v, _ in pairs]
        y_percentage = [p * 100.0 for _, _, p in pairs]

        # 设置横坐标范围为横坐标最大值，去掉数量占比top 1%的极端最大值
        if max_x is None:
            if isinstance(x[0], int):
                max_sum_per = 0
                # x从大到小排序
                x.sort(reverse=True)
                for k in x:
                    max_sum_per += float(data[k]) / total * 100
                    if max_sum_per > 3:
                        max_x = k
                        break
            else:
                max_x = -1
        if min_x is None:
            min_x = -1

        # 过滤数据大于max_x的数据
        if max_x > 0:
            pairs = [(k, v, p) for k, v, p in pairs if k <= max_x]
            x = [k for k, _, _ in pairs]
            y = [v for _, v, _ in pairs]
            y_percentage = [p * 100 for _, _, p in pairs]

        # 绘制柱状图，并显示具体的值和占比
        print("\n[{}]".format(title))
        print("x:", x)
        print("y:", y)
        print("label:", label)
        # x=[str[k] for k in x]
        # plt.bar(x, y, label=str(label))  # 为每个数据集指定一个标签
        # 绘制折线图
        plt.plot(x, y, marker='o', label=str(label))
        for k, v, per in zip(x, y, y_percentage):
            plt.text(k, v + 1, f"{v}\n({per:.2f}%)", ha='center', va='bottom')

    # 设置横坐标范围
    if max_x > 0:
        plt.xlim(min_x, max_x)

    # 设置标题和轴标签
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # 添加图例
    plt.legend()

    # 保存图片
    plt.savefig(f"figures/{title}.png")
    # plt.show()
