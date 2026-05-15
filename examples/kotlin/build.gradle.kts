import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "2.1.0"
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
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
}

kotlin {
    jvmToolchain(17)
}

ktlint {
    android.set(false)
    ignoreFailures.set(false)
    reporters {
        reporter(org.jlleitschuh.gradle.ktlint.reporter.ReporterType.PLAIN)
    }
    kotlinScriptAdditionalPaths {
        include(fileTree("scripts"))
    }
    filter {
        exclude("**/generated/**")
    }
}

// Ensure ktlint uses Google style by setting the property
// Alternatively, this can be done via .editorconfig which is more robust for Google Style

sourceSets {
    main {
        kotlin {
            setSrcDirs(listOf("snippets", "build/generated/ksp/main/kotlin"))
        }
    }
}
