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
    implementation("com.google.adk:google-adk-kotlin-core:0.1.0")
    implementation("com.google.adk:google-adk-kotlin-webserver:0.1.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.1.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
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
