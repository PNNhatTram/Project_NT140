import openai
import os
from dotenv import load_dotenv
from executor.executor import Executor
from extractor.extractor import Extractor
from planner.planner import Planner
from summarizer.summarize import Summarizer
from instructor.instructor import Instructor

def main():
    # Yêu cầu người dùng nhập IP mục tiêu
    target_ip = input("Nhập IP mục tiêu để bắt đầu pentest: ")
    load_dotenv()
    
    # API key cho OpenAI và Hugging Face
    openai_api_key = os.getenv("OPENAI_API_KEY")
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not openai_api_key or not hf_api_key:
        print("Vui lòng cung cấp API key cho cả OpenAI và Hugging Face trong file .env")
        return
    
    # Khởi tạo các module cần thiết
    planner_instance = Planner(target_ip, openai_api_key)
    executor_instance = Executor(openai_api_key)
    summarizer_instance = Summarizer(openai_api_key, hf_api_key)
    extractor_instance = Extractor(openai_api_key, hf_api_key)
    instructor_instance = Instructor(openai_api_key, "knowledge_base.json")

    # Thiết lập các module phụ trợ cho planner
    planner_instance.executor = executor_instance
    planner_instance.summarizer = summarizer_instance
    
    # Bắt đầu chạy pentest
    print("Đang chạy pentest...")
    planner_instance.run()
    
    # Tạo lịch sử tấn công từ các nhiệm vụ đã hoàn thành
    attack_history = "\n".join(
        [f"Task: {task['task']}, Result: {task['description']}, Status: {task['status']}" 
         for task in planner_instance.completed_tasks]
    )

    # Sử dụng Extractor để trích xuất thông tin lỗ hổng
    vulnerabilities = extractor_instance.extract_vulnerabilities(attack_history)

    # Hiển thị kết quả trích xuất
    print("\nKết quả trích xuất các lỗ hổng đã khai thác:")
    for vulnerability in vulnerabilities:
        print(f"Exploited: {vulnerability['exploited']}")
        print(f"Description: {vulnerability['description']}")
        print(f"Impact: {vulnerability['impact']}")
        print(f"Remediation: {vulnerability['remediation']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
