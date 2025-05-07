import inspect
import json
import re
from loguru import logger


category_motors_txt_path = "resources/category-motors.txt"
category_motors_json_path = "resources/category-motors.json"
category_England_txt_path = "resources/category-England.txt"
category_England_json_path = "resources/category-England.json"
category_Germany_txt_path = "resources/category-Germany.txt"
category_Germany_json_path = "resources/category-Germany.json"
category_us_txt_path = "resources/category-us.txt"
category_us_json_path = "resources/category-us.json"

with open(category_us_txt_path, 'r', encoding='utf-8') as f:
    category_list = f.read().splitlines()

with open(category_motors_txt_path, 'r', encoding='utf-8') as f:
    motors_category_list = f.read().splitlines()

with open(category_England_txt_path, 'r', encoding='utf-8') as f:
    England_category_list = f.read().splitlines()

with open(category_Germany_txt_path, 'r', encoding='utf-8') as f:
    Germany_category_list = f.read().splitlines()

with open(category_us_json_path, 'r', encoding='utf-8') as f:
    category_data = json.load(f)
with open(category_motors_json_path, 'r', encoding='utf-8') as f:
    for l, v in json.load(f).items():
        category_data[l].extend(v)

with open(category_England_json_path, 'r', encoding='utf-8') as f:
    for l, v in json.load(f).items():
        category_data[l].extend(v)

with open(category_Germany_json_path, 'r', encoding='utf-8') as f:
    for l, v in json.load(f).items():
        category_data[l].extend(v)




country_category_datas = {
    "100": motors_category_list,
    "0": category_list,
    "3": England_category_list,
    "77" : Germany_category_list

}

def match_category(result_content, country_id):
    try:
        print("最佳匹配的类目是:", json.dumps(result_content, ensure_ascii=False, indent=4))
        level_datas = category_data[str(len(re.findall('>', result_content)) + 1)]
        result_content_data = list(filter(lambda x: result_content in x, level_datas))
        print("选择的类目是:", result_content)
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