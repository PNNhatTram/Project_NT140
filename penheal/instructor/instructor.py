import openai
import requests
import json

class Instructor:
    def __init__(self, openai_api_key, knowledge_base_file, hf_api_key=None):
        self.openai_api_key = openai_api_key
        self.hf_api_key = hf_api_key
        self.knowledge_base = self._load_knowledge_base(knowledge_base_file)

    def _load_knowledge_base(self, file_path):
        """
        Tải cơ sở dữ liệu kiến thức từ file JSON.
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return {}

    def query_knowledge_base(self, query):
        """
        Truy vấn cơ sở dữ liệu kiến thức bằng OpenAI và Hugging Face.

        Parameters:
            query (str): Truy vấn cần tìm kiếm.

        Returns:
            str: Kết quả từ cơ sở dữ liệu hoặc phân tích từ OpenAI/HF.
        """
        # Tìm kiếm trực tiếp trong cơ sở dữ liệu
        results = [entry for entry in self.knowledge_base if query.lower() in entry["content"].lower()]
        if results:
            return f"Results from knowledge base:\n" + "\n".join([res["content"] for res in results])

        # Nếu không tìm thấy, sử dụng OpenAI API
        openai_prompt = (
            f"The following is a query related to penetration testing:\n\n{query}\n\n"
            "Search the knowledge base and provide detailed information or suggestions."
        )
        openai.api_key = self.openai_api_key
        openai_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledge base assistant for pentesting queries."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=200
        )
        openai_result = openai_response.choices[0].message["content"].strip()

        # Nếu có Hugging Face API, bổ sung kết quả từ phân tích
        if self.hf_api_key:
            hf_result = self._analyze_with_hf(query)
            return f"{openai_result}\n\n[Additional Insights from Hugging Face]:\n{hf_result}"

        return openai_result

    def _analyze_with_hf(self, query):
        """
        Sử dụng Hugging Face để phân tích truy vấn.

        Parameters:
            query (str): Truy vấn cần phân tích.

        Returns:
            str: Kết quả từ Hugging Face API.
        """
        url = "https://api-inference.huggingface.co/models/some-nlp-model"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": query}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get("output", "No additional insights available.")
            else:
                return f"Hugging Face API returned status {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
