FROM python:3.9.9

WORKDIR /usr/src/app

# Download Postgres
RUN apt-get update && apt-get install -y postgresql-client

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # Install Prisma CLI and Knex CLI
# RUN npm install -g prisma@6.0.1 
# RUN npm install -g knex@3.1.0

# Bundle app source
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Ensure migrate.sh is executable
RUN chmod +x script/migrate.sh

ARG VCS_REF=unspecified
LABEL vcs_ref=$VCS_REF
ARG SOURCE_BRANCH=unspecified
LABEL source_branch=$SOURCE_BRANCH
ARG BUILD_DATE=unspecified
LABEL build_date=$BUILD_DATE

EXPOSE 5000
ENTRYPOINT ["script/migrate.sh"]
# Start the server using the production build

RUN export FLASK_APP=app.py

CMD [ "flask", "run" ]
