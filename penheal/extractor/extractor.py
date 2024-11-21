import openai
import requests

class Extractor:
    def __init__(self, openai_api_key, hf_api_key=None):
        self.openai_api_key = openai_api_key
        self.hf_api_key = hf_api_key

    def extract_vulnerabilities(self, attack_history):
        """
        Trích xuất thông tin lỗ hổng từ lịch sử nhiệm vụ.

        Parameters:
            attack_history (str): Lịch sử các nhiệm vụ và kết quả thực hiện.

        Returns:
            list[dict]: Danh sách các lỗ hổng được trích xuất.
        """
        # Tạo prompt để OpenAI API phân tích lịch sử tấn công
        openai_prompt = (
            f"The following is the history of a penetration testing engagement:\n\n{attack_history}\n\n"
            "Please extract a list of vulnerabilities identified. For each vulnerability, include the following details: "
            "1. Exploited vulnerability, 2. Description, 3. Impact, 4. Recommended remediation."
        )
        openai.api_key = self.openai_api_key
        openai_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at extracting vulnerabilities from penetration testing reports."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=500
        )

        openai_results = self._parse_openai_response(openai_response.choices[0].message["content"])

        # Nếu có Hugging Face API, phân tích sâu hơn
        if self.hf_api_key:
            hf_results = self._analyze_with_hf(attack_history)
            return self._merge_results(openai_results, hf_results)

        return openai_results

    def _analyze_with_hf(self, text):
        """
        Phân tích lịch sử nhiệm vụ bằng Hugging Face API.

        Parameters:
            text (str): Văn bản lịch sử nhiệm vụ.

        Returns:
            list[dict]: Kết quả phân tích từ Hugging Face.
        """
        url = "https://api-inference.huggingface.co/models/some-nlp-model"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": text}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()  # Parse và trả kết quả
            else:
                return []
        except Exception as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return []

    def _parse_openai_response(self, response_text):
        """
        Phân tích kết quả từ OpenAI API.

        Parameters:
            response_text (str): Văn bản đầu ra từ GPT.

        Returns:
            list[dict]: Danh sách các lỗ hổng được trích xuất.
        """
        vulnerabilities = []
        for line in response_text.split("\n"):
            if line.strip():
                parts = line.split(":")
                if len(parts) == 2:
                    key, value = parts
                    vulnerabilities.append({key.strip(): value.strip()})
        return vulnerabilities

    def _merge_results(self, openai_results, hf_results):
        """
        Kết hợp kết quả từ OpenAI và Hugging Face.

        Parameters:
            openai_results (list): Kết quả từ OpenAI.
            hf_results (list): Kết quả từ Hugging Face.

        Returns:
            list[dict]: Kết quả kết hợp.
        """
        merged = openai_results.copy()
        for hf_item in hf_results:
            if hf_item not in merged:
                merged.append(hf_item)
        return merged
