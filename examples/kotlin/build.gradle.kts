import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "2.1.10"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.2"
}

group = "com.google.adk"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    maven { url = uri("https://oss.sonatype.org/content/repositories/snapshots") }
}

dependencies {
    implementation("com.google.adk:google-adk:1.2.0")
    // If there is a Kotlin specific artifact, it would be here.
    // For now, using the Java one as it seems to contain what's needed.
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
tasks.withType<KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs = listOf("-Xjsr305=strict")
        jvmTarget = "17"
    }
}

sourceSets {
    main {
        kotlin {
            setSrcDirs(listOf("snippets"))
        }
    }
}
