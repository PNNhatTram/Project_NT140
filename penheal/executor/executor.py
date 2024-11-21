import openai
import requests
import os

class Executor:
    def __init__(self, api_key, hf_api_key=None):
        self.api_key = api_key
        self.hf_api_key = hf_api_key

    def run_task(self, task_description):
        """
        Thực thi nhiệm vụ tấn công và xử lý đầu ra.
        
        Parameters:
            task_description (str): Mô tả nhiệm vụ cần thực hiện.
        
        Returns:
            dict: Kết quả nhiệm vụ, bao gồm trạng thái và thông tin đầu ra.
        """
        # Tạo lệnh từ mô tả nhiệm vụ
        command_prompt = (
            f"You are an expert pentester. Generate the best command or methodology "
            f"to execute the following task:\n\n{task_description}\n\n"
            "Output the command or methodology step-by-step."
        )
        openai.api_key = self.api_key
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a command generator for pentesting tasks."},
                {"role": "user", "content": command_prompt}
            ],
            max_tokens=150
        )

        # Lấy lệnh từ GPT
        command = response.choices[0].message["content"].strip()

        # Sử dụng Hugging Face API để kiểm tra hiệu quả hoặc bổ trợ
        if self.hf_api_key:
            hf_response = self._analyze_command_with_hf(command)
        else:
            hf_response = None

        # Trả kết quả
        task_result = {
            "command": command,
            "hf_analysis": hf_response,
            "status": "success" if hf_response else "pending"
        }
        return task_result

    def _analyze_command_with_hf(self, command):
        """
        Phân tích lệnh sử dụng Hugging Face API.
        
        Parameters:
            command (str): Lệnh cần phân tích.

        Returns:
            dict: Phân tích từ Hugging Face.
        """
        url = "https://api-inference.huggingface.co/models/some-nlp-model"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": command}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HF API returned status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
