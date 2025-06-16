FROM python:3.11-slim

# Install system dependencies
RUN apt-get -y update && \
    apt-get -y install wget git bzip2 libcurl4-gnutls-dev nano

# Install MCP server
RUN git clone https://github.com/genepattern/genepattern-mcp.git /srv/genepattern-mcp
WORKDIR /srv/genepattern-mcp
RUN pip install -r requirements.txt

EXPOSE 3000
CMD python server.py