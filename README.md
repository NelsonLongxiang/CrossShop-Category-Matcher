### 项目详细介绍

#### 项目概述
这个项目主要致力于实现英语和德语环境下，各大电商平台之间产品类目的精准匹配。通过语义匹配技术，结合预训练的语言模型，将产品准确归类到合适的电商类目下。`category_matching.py` 文件在整个项目中承担着重要角色，主要负责读取不同国家或平台的产品类目数据，并根据匹配结果获取对应的类目 ID、类目文本和类目顺序 ID。

#### 文件功能详解：`category_matching.py`
1. **数据文件路径定义**：
    ```python
    category_motors_txt_path = "resources/category-motors.txt"
    category_motors_json_path = "resources/category-motors.json"
    # 其他国家类目文件路径...
    ```
    这里定义了多个不同国家或平台的产品类目数据文件的路径，包括 `.txt` 和 `.json` 格式的文件，用于存储类目信息。

2. **数据读取**：
    ```python
    with open(category_us_txt_path, 'r', encoding='utf-8') as f:
        category_list = f.read().splitlines()
    
    with open(category_us_json_path, 'r', encoding='utf-8') as f:
        category_data = json.load(f)
    # 其他国家类目数据读取...
    ```
    通过 `open` 函数读取 `.txt` 文件并将其按行分割存储到列表中，读取 `.json` 文件并将其解析为 Python 字典。同时，将不同国家或平台的类目数据合并到 `category_data` 中。

3. **国家类目数据映射**：
    ```python
    country_category_datas = {
        "100": motors_category_list,
        "0": category_list,
        "3": England_category_list,
        "77" : Germany_category_list
    }
    ```
    定义了一个字典 `country_category_datas`，将国家或平台的 ID 映射到对应的类目列表，方便根据国家 ID 获取相应的类目数据。

4. **类目匹配函数**：
    ```python
    def match_category(result_content, country_id):
        try:
            print("最佳匹配的类目是:", json.dumps(result_content, ensure_ascii=False, indent=4))
            level_datas = category_data[str(len(re.findall('>', result_content)) + 1)]
            result_content_data = list(filter(lambda x: result_content in x, level_datas))
            result = result_content_data[0][result_content][-1]
            select_categoryId = result["categoryId"]
            select_categoryText = "-->".join([i["categoryStr"] for i in result_content_data[0][result_content]])
            select_cateSeqId = result["cateSeqId"]
            print("选择的类目ID是:", select_categoryId)
            print("选择的类目文本是:", select_categoryText)
            print("选择的类目顺序ID是:", select_cateSeqId)
            return select_categoryId, select_categoryText, select_cateSeqId
        except Exception as e:
            logger.error(f"ai错误 {inspect.currentframe()} {e} : {e.__traceback__.tb_lineno} country_id {country_id}")
    ```
    `match_category` 函数接受匹配到的类目内容 `result_content` 和国家 ID `country_id` 作为参数。首先根据类目内容中的 `>` 数量确定类目级别，然后从 `category_data` 中获取相应级别的数据。接着，筛选出包含匹配类目内容的数据，并从中提取类目 ID、类目文本和类目顺序 ID 并返回。如果出现异常，使用 `loguru` 记录错误信息。

### 项目衍生用途

#### 商品搬运（从亚马逊搬运到沃尔玛）
在将商品从亚马逊搬运到沃尔玛时，由于两个平台的产品类目体系可能存在差异，需要将亚马逊上的产品准确归类到沃尔玛的类目下。该项目的类目匹配功能可以帮助实现这一目标，具体步骤如下：
1. **获取亚马逊商品信息**：通过亚马逊的 API 或爬虫技术，获取商品的标题、描述、类别等信息。
2. **类目匹配**：将获取到的亚马逊商品类目信息作为输入，调用 `SemanticMatcher` 类的 `find_similar` 方法，找到与之最相似的沃尔玛类目。
3. **确定沃尔玛类目**：将匹配到的类目信息传递给 `match_category` 函数，获取对应的沃尔玛类目 ID、类目文本和类目顺序 ID。
4. **商品上架**：使用沃尔玛的 API 将商品信息和匹配到的类目信息上传到沃尔玛平台，完成商品搬运。

#### 多平台商品管理
当商家在多个电商平台销售商品时，需要对商品进行统一管理。该项目可以帮助商家将不同平台的商品类目进行统一映射，方便对商品进行分类、统计和分析。例如，商家可以根据匹配结果，将所有平台上的服装类商品归为一类，进行库存管理和销售分析。

#### 跨境电商商品分类
在跨境电商业务中，不同国家的电商平台类目体系差异较大。该项目可以帮助商家将商品准确归类到不同国家平台的类目下，提高商品的曝光率和销售转化率。例如，将中国的商品出口到德国时，使用该项目将商品类目从中文体系转换为德语的德国电商平台类目体系。
