# Sử dụng Ubuntu làm nền tảng
FROM ubuntu:22.04

# Đặt môi trường không có giao diện người dùng để tránh yêu cầu nhập tay
ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt các công cụ cần thiết cho pentest và phát triển Python
RUN apt-get update && \
    apt-get install -y \
    sudo curl netcat \
    build-essential python3 python3-pip python3-venv \
    nmap sqlmap nikto hydra \
    && rm -rf /var/lib/apt/lists/*

# Tạo một user không phải root để đảm bảo an toàn
ARG USERNAME=pentester
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Cài đặt thư viện Python cần thiết cho các module của bạn
USER $USERNAME
WORKDIR /home/$USERNAME

# Tạo môi trường ảo và cài đặt thư viện Python
RUN python3 -m venv venv
ENV PATH="/home/$USERNAME/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install openai requests  # Thêm các thư viện cần thiết khác vào đây nếu cần

# Copy mã nguồn của bạn vào container
COPY . /home/$USERNAME/app
WORKDIR /home/$USERNAME/app

# Khởi động container và chạy chương trình chính
CMD ["python3", "main.py"]
