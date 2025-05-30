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
ENTRYPOINT ["mvn", "exec:java", \
    "-Dexec.mainClass=com.google.adk.web.AdkWebServer", \
    "-Dexec.classpathScope=compile", \
    "-Dexec.args=--server.port=${PORT} --adk.agents.source-dir=src/main/java" \
]