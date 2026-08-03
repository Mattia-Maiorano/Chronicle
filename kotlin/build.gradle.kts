plugins {
    kotlin("jvm") version "1.9.22"
    application
}

group = "com.uzumaki"
version = "1.0.4"

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
}

application {
    mainClass.set("ExampleKt")
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions.jvmTarget = "17"
}
