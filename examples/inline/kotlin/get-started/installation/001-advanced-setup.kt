plugins {
    kotlin("jvm") version "2.1.20"
    id("com.google.devtools.ksp") version "2.1.20-2.0.1"
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.8.0")
    ksp("com.google.adk:google-adk-kotlin-processor:0.8.0")
}