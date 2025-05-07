import torch
from sentence_transformers import SentenceTransformer
from category_matching import match_category

class SemanticMatcher:
    def __init__(self, country_id='0',categories=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device} ({'CUDA加速可用' if torch.cuda.is_available() else 'CPU模式'})")
        model_name = {
            '77':'T-Systems-onsite/german-roberta-sentence-transformer-v2',
        }
        self.model = SentenceTransformer(model_name.get(country_id, 'paraphrase-multilingual-mpnet-base-v2'))
        self.model = self.model.to(self.device)
        if categories is None:
            self.categories = self.load_categories(country_id)
        else:
            self.categories = categories
        self.embeddings = self.model.encode(self.categories, convert_to_tensor=True, device=self.device)
        self.model.half()

    def load_categories(self, country_id):
        from category_matching import country_category_datas
        return country_category_datas.get(country_id, [])

    def match_category_json(self, target_category: str, ai_product_info: dict, country: str):
        country_ids = {'Germany':'77', 'eaby-motors':'100'}
        return match_category(target_category, ai_product_info, country_ids.get(country, '0'))

    def find_similar(self, queries: list, top_n: int = 5, batch_size: int = 32):
        results = []
        with torch.no_grad():
            for i in range(0, len(queries), batch_size):
                batch = queries[i:i+batch_size]
                query_embeddings = self.model.encode(batch, convert_to_tensor=True, device=self.device).half()
                similarities = torch.nn.functional.cosine_similarity(
                    query_embeddings.unsqueeze(1),
                    self.embeddings.unsqueeze(0),
                    dim=2
                )
                top_similarities = torch.topk(similarities, k=top_n, dim=1)
                for j in range(len(batch)):
                    results.append([
                        (self.categories[idx], val.item()) 
                        for idx, val in zip(top_similarities.indices[j], top_similarities.values[j])
                    ])
        return results

    # 添加上下文管理协议方法
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if torch.cuda.is_available():
            del self.model
            del self.embeddings
            torch.cuda.empty_cache()
    
    # 修改main函数使用with语句
    def main():
        with SemanticMatcher() as matcher:
            # 批量测试
            test_queries = [
                "Home & Kitchen›Household Cleaning Tools & Vacuums›Carpet Washers",
            ]
            
            results = matcher.find_similar(test_queries)
            
            for query, matches in zip(test_queries, results):
                print(f"匹配结果 '{query}':")
                for category, score in matches:
                    print(f"{category}: {score:.4f}")
                print("\n")
            print("测试完成")


if __name__ == "__main__":
    SemanticMatcher.main()