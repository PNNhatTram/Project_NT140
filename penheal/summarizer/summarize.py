import openai
import requests

class Summarizer:
    def __init__(self, api_key, hf_api_key=None):
        self.api_key = api_key
        self.hf_api_key = hf_api_key

    def summarize(self, task, task_result):
        """
        Tóm tắt đầu ra từ Executor cho nhiệm vụ được giao.

        Parameters:
            task (dict): Thông tin về nhiệm vụ (bao gồm mô tả).
            task_result (dict): Kết quả từ Executor, bao gồm trạng thái và đầu ra.

        Returns:
            dict: Bản tóm tắt của kết quả nhiệm vụ.
        """
        # Tạo prompt để tóm tắt kết quả
        prompt = (
            f"The following is the result of a penetration testing task.\n\n"
            f"Task: {task['task']}\n"
            f"Description: {task['description']}\n"
            f"Result: {task_result['output']}\n\n"
            "Please provide a concise summary of this result. "
            "Focus on key findings, vulnerabilities, and any relevant details that could aid in decision-making."
        )
        openai.api_key = self.api_key
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a summarizer for penetration testing outputs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        # Lấy bản tóm tắt từ OpenAI
        summary = response.choices[0].message["content"].strip()

        # Nếu có Hugging Face API, bổ sung phân tích từ kết quả
        if self.hf_api_key:
            hf_analysis = self._analyze_summary_with_hf(task, task_result)
            summary += f"\n\n[Additional Insights from Hugging Face]:\n{hf_analysis}"

        # Tạo kết quả cuối cùng
        summarized_result = {
            "task": task["task"],
            "description": task["description"],
            "summary": summary,
            "result": task_result["status"]  # Bao gồm trạng thái của task (success, failed)
        }

        return summarized_result

    def _analyze_summary_with_hf(self, task, task_result):
        """
        Phân tích kết quả tóm tắt bằng Hugging Face API.

        Parameters:
            task (dict): Thông tin nhiệm vụ.
            task_result (dict): Kết quả từ nhiệm vụ.

        Returns:
            str: Phân tích bổ sung từ Hugging Face.
        """
        text = f"Task: {task['task']}\nDescription: {task['description']}\nResult: {task_result['output']}"
        url = "https://api-inference.huggingface.co/models/some-nlp-model"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": text}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get("summary", "No additional insights available.")
            else:
                return f"Hugging Face API returned status {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
