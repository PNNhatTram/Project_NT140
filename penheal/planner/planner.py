import openai
import requests

class Planner:
    def __init__(self, target_ip, openai_api_key, hf_api_key=None):
        self.target_ip = target_ip
        self.openai_api_key = openai_api_key
        self.hf_api_key = hf_api_key
        self.executor = None  # Sẽ được khởi tạo trong main
        self.summarizer = None  # Sẽ được khởi tạo trong main
        self.completed_tasks = []

    def generate_plan(self):
        """
        Tạo kế hoạch pentest cho mục tiêu.
        """
        # Tạo prompt để lập kế hoạch với OpenAI API
        prompt = (
            f"You are tasked with creating a penetration testing plan for the target IP: {self.target_ip}. "
            "Generate a step-by-step plan, including reconnaissance, scanning, exploitation, and reporting phases."
        )
        openai.api_key = self.openai_api_key
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a pentesting plan generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        # Lấy kế hoạch từ OpenAI
        plan = response.choices[0].message["content"].strip()

        # Nếu Hugging Face API được cấu hình, cải thiện kế hoạch bằng phân tích bổ sung
        if self.hf_api_key:
            hf_analysis = self._analyze_plan_with_hf(plan)
            plan += f"\n\n[Additional Insights from Hugging Face]:\n{hf_analysis}"

        return plan

    def execute_plan(self, plan):
        """
        Thực thi kế hoạch pentest từng bước.
        """
        for step in plan.split("\n"):
            if step.strip():
                print(f"Executing: {step}")
                result = self.executor.run_task(step)
                self.completed_tasks.append({
                    "task": step,
                    "description": result.get("command", "No description"),
                    "status": result.get("status", "Unknown")
                })

    def run(self):
        """
        Chạy toàn bộ quy trình pentest.
        """
        plan = self.generate_plan()
        print("Generated Plan:\n", plan)
        self.execute_plan(plan)

    def _analyze_plan_with_hf(self, plan):
        """
        Phân tích kế hoạch bằng Hugging Face API.

        Parameters:
            plan (str): Kế hoạch pentest.

        Returns:
            str: Phân tích bổ sung từ Hugging Face.
        """
        url = "https://api-inference.huggingface.co/models/some-nlp-model"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": plan}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json().get("analysis", "No additional insights available.")
            else:
                return f"Hugging Face API returned status {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
