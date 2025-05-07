from typing import Dict
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel
from semantic_matcher import SemanticMatcher
import uvicorn
from category_matching import match_category
import requests
import json
import re
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache


app = FastAPI()
model_cache: Dict[str, SemanticMatcher] = {}
with open('open-webui.key', 'r', encoding='utf-8') as f:
    open_webui_key = f.read().strip()
class MatchRequest(BaseModel):
    queries: list[str]
    country: str = 'Germany'
    top_n: int = 5

class MatchAIRequest(BaseModel):
    category: str
    title: str
    country: str = 'Germany'
    top_n: int = 10

class MatchResult(BaseModel):
    categoryId: str
    categoryText: str
    cateSeqId: str
    score: float

@app.post("/match/{country_id}")
async def match_country(country_id: str, request: MatchRequest):
    try:
        if country_id not in model_cache:
            model_cache[country_id] = SemanticMatcher(country_id=country_id)
        
        matcher = model_cache[country_id]
        results = matcher.find_similar(request.queries, top_n=request.top_n)
        datas = []
        for result in results:
            logger.info(f"匹配结果: {result}")
            data = match_category(result[0][0], country_id)
            datas.append(data)
        return datas
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Country categories not found")
    except Exception as e:
        logger.error(f"匹配失败: {e} {e.__traceback__.tb_lineno}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match/list/{country_id}")
async def match_country(country_id: str, request: MatchAIRequest):
    try:
        if country_id not in model_cache:
            model_cache[country_id] = SemanticMatcher(country_id=country_id)
        matcher = model_cache[country_id]
        results = matcher.find_similar([request.category], top_n=request.top_n)
        result = results[0]
        logger.info(f"匹配结果: {result}")
        init_datas = [match_category(i[0], country_id) for i in result]
        select_list = [i[1] for i in init_datas]
        select_dict = dict(zip(select_list, init_datas))
        product_category = request.category
        product_title = request.title
        product_name = get_product_name(product_category, product_title)
        finally_select_list = {
            "product-title": product_title,
            "product-name": product_name,
            "product-category": product_category,
            "select-list": select_list
        }
        ai_select_result = get_ai_select_product_category(json.dumps(finally_select_list))
        if ai_select_result in select_list:
            end_result = ai_select_result
        else:
            # 相似度 匹配 ai_select_result 和 select_list 中的每个元素 使用 显卡 计算相似度
            model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            model.to('cuda')
            cosine_scores = util.cos_sim(model.encode(ai_select_result), model.encode(select_list))[0]
            end_result = select_list[cosine_scores.argmax()]
        return [select_dict[end_result]]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Country categories not found")
    except Exception as e:
        logger.error(f"匹配失败: {e} {e.__traceback__.tb_lineno}")
        raise HTTPException(status_code=500, detail=str(e))

def get_product_name(product_category,product_title):
    ai_data = {
        "model": "product-get-name",
        "messages": [{"role": "user", "content": "\n".join([product_category, product_title])}],
        "stream": False,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {open_webui_key}"
    }
    response = requests.post(f"http://localhost:8080/api/chat/completions", json=ai_data, headers=headers)
    result = response.json()["choices"][0]["message"]["content"]
    return re.findall(r"<content>(.*?)</content>", result)[0]

@lru_cache(maxsize=1000)
def get_ai_select_product_category(content):
    ai_data = {
        "model": "category-select",
        "messages": [{"role": "user", "content": "\n".join([content, """Output Format:XML\n<content>xxx</content>"""])}],
        "stream": False,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {open_webui_key}"
    }
    response = requests.post(f"http://localhost:8080/api/chat/completions", json=ai_data, headers=headers)
    result = response.json()["choices"][0]["message"]["content"]
    return re.findall(r"<content>(.*?)</content>", result)[0]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)