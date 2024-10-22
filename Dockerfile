# Start from the latest Python image
FROM python:3.10.15-bullseye

# Set the working directory in the container
WORKDIR /main

# Install necessary packages including Open vSwitch
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    wget \
    openvswitch-switch && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /main/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/iwaseyusuke/python-ovs-vsctl.git

# Copy the main script
COPY ovs_mirror_monitor_v3.py /main/

# Set the command to execute the main script
CMD ["python", "ovs_mirror_monitor_v3.py"]