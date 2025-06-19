FROM docker.1panel.live/library/python:3.12-bookworm

RUN rm -f /etc/apt/sources.list && \
    rm -f /etc/apt/sources.list.d/debian.sources
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/  bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/  bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security  bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

RUN apt update -y
RUN apt install -y --no-install-recommends curl ca-certificates supervisor

ENV WORKDIR_PATH="/data/apps/fastapi-template"
ENV UV_VERSION=0.7.13
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/" \
    VENV_PATH="$WORKDIR_PATH/.venv" \
    # ensure deps real file, not link
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

ENV PATH="$VENV_PATH/bin:$PATH"

RUN mkdir -p "$WORKDIR_PATH" /data/applogs
WORKDIR $WORKDIR_PATH

RUN pip install "uv==$UV_VERSION" --no-cache-dir

COPY uv.lock pyproject.toml .python-version ./
RUN uv sync --frozen --no-install-project --no-dev --no-cache && rm -rf ~/.cache

COPY . $WORKDIR_PATH

COPY devops/supervisor.conf /etc/supervisor/conf.d/main.conf

EXPOSE 8000

RUN chmod +x devops/entry.sh
CMD bash devops/entry.sh