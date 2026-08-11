plugins {
    kotlin("jvm") version "2.1.20"
    id("com.google.devtools.ksp") version "2.1.20-2.0.1"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.2"
}

group = "com.google.adk"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    google()
    maven { url = uri("https://oss.sonatype.org/content/repositories/snapshots") }
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.7.0")
    implementation("com.google.adk:google-adk-kotlin-webserver:0.7.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.7.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
    // The Vertex AI session and memory services expose Ktor's HttpClient as a
    // defaulted constructor parameter, so any snippet naming them needs Ktor on
    // the COMPILE classpath, not just at runtime. Version matches what
    // adk-kotlin 0.7.0 already resolves to.
    implementation("io.ktor:ktor-client-core:2.3.13")
    implementation("io.ktor:ktor-client-java:2.3.13")
    // A2A. The a2a artifact publishes the A2A SDK as runtime-only, but A2AAgent's
    // httpClient parameter defaults to JdkA2AHttpClient(), so the client artifact
    // is needed on the COMPILE classpath too. Version matches adk-kotlin 0.7.0's
    // own catalog; the spec and jsonrpc transport arrive transitively.
    implementation("com.google.adk:google-adk-kotlin-a2a:0.7.0")
    implementation("org.a2aproject.sdk:a2a-java-sdk-client:1.0.0.Final")
    implementation("com.google.cloud:google-cloud-storage:2.48.2")
    implementation("io.opentelemetry:opentelemetry-sdk:1.56.0")
    implementation("io.opentelemetry:opentelemetry-exporter-otlp:1.56.0")
}

kotlin {
    jvmToolchain(17)
}

ktlint {
    android.set(false)
    ignoreFailures.set(true)
    reporters {
        reporter(org.jlleitschuh.gradle.ktlint.reporter.ReporterType.PLAIN)
    }
    kotlinScriptAdditionalPaths {
        include(fileTree("scripts"))
    }
    filter {
        exclude("**/build/**")
        exclude("build/**")
    }
}

// Ensure ktlint uses Google style by setting the property
// Alternatively, this can be done via .editorconfig which is more robust for Google Style

sourceSets {
    main {
        kotlin {
            setSrcDirs(listOf("snippets"))
        }
    }
}
