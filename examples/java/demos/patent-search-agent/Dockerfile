# Use an official Maven image with a JDK. Choose a version appropriate for your project.
FROM maven:3.8-openjdk-17 AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src

# Expose the port your application will listen on.
# Cloud Run will set the PORT environment variable, which your app should use.
EXPOSE 8080

# The command to run your application.
# TODO(Developer): Update the "adk.agents.source-dir" to the directory that contains your agents.
# You can have multiple agents in this directory and all of them will be available in the Dev UI.
ENTRYPOINT ["mvn", "compile", "exec:java", \
     "-Dexec.args=--server.port=${PORT} \
     --adk.agents.source-dir=src/main/java/agents \
     --logging.level.com.google.adk.dev=DEBUG \
     --logging.level.com.google.adk.demo.agents=DEBUG" \
    ]
