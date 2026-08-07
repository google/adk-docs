# Advanced setup

This page provides detailed installation and configuration instructions for ADK across supported languages. For a guided introduction, start with the [quickstart for your language](/get-started/).

**Create & activate virtual environment**

We recommend creating a virtual Python environment using [venv](https://docs.python.org/3/library/venv.html):

```shell
python3 -m venv .venv
```

Now, you can activate the virtual environment using the appropriate command for your operating system and environment:

```text
# Mac / Linux
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1
```

**Install ADK**

```bash
pip install google-adk
```

(Optional) Verify your installation:

```bash
pip show google-adk
```

**Install ADK and ADK DevTools**

```bash
npm install @google/adk @google/adk-devtools
```

**Prerequisites:** Go 1.25 or later is required for ADK Go v2.0.0.

**Create a new Go module**

If you are starting a new project, you can create a new Go module:

```shell
go mod init example.com/my-agent
```

**Install ADK Go v2.0.0**

To add ADK Go v2.0.0 to your project, run the following command:

```shell
go get google.golang.org/adk/v2
```

This will add ADK Go v2.0.0 as a dependency to your `go.mod` file.

(Optional) Verify your installation by checking your `go.mod` file for the `google.golang.org/adk/v2` entry.

Still using ADK Go v1.x?

If you are not yet ready to upgrade to v2.0.0, you can continue using the v1.x release line:

```shell
go get google.golang.org/adk@v1
```

See the [ADK 2.0 release page](/2.0/) for upgrade guidance, including breaking changes and migration steps for ADK Go 1.x projects.

You can either use maven or gradle to add the `google-adk` and `google-adk-dev` package.

`google-adk` is the core Java ADK library. Java ADK also comes with a pluggable example SpringBoot server to run your agents seamlessly. This optional package is present as part of `google-adk-dev`.

If you are using maven, add the following to your `pom.xml`:

pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example.agent</groupId>
    <artifactId>adk-agents</artifactId>
    <version>1.0-SNAPSHOT</version>

    <!-- Specify the version of Java you'll be using -->
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- The ADK core dependency -->
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk</artifactId>
            <version>1.6.0</version>
        </dependency>
        <!-- The ADK dev web UI to debug your agent -->
        <dependency>
            <groupId>com.google.adk</groupId>
            <artifactId>google-adk-dev</artifactId>
            <version>1.6.0</version>
        </dependency>
    </dependencies>

</project>
```

Here's a [complete pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) file for reference.

If you are using gradle, add the dependency to your build.gradle:

build.gradle

```text
dependencies {
    implementation 'com.google.adk:google-adk:1.6.0'
    implementation 'com.google.adk:google-adk-dev:1.6.0'
}
```

You should also configure Gradle to pass `-parameters` to `javac`. (Alternatively, use `@Schema(name = "...")`).

**Use ADK Kotlin on the JVM**

For Kotlin on the JVM, add the ADK core library and the KSP annotation processor to your `build.gradle.kts`:

build.gradle.kts

```kotlin
plugins {
    kotlin("jvm") version "2.1.20"
    id("com.google.devtools.ksp") version "2.1.20-2.0.1"
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.5.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.5.0")
}
```

The KSP processor generates code for the `@Tool` annotation used to register function tools. See the [Kotlin Quickstart](/get-started/kotlin/) for a complete project setup.
