/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.adk.kt.examples.skills

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.skills.Frontmatter
import com.google.adk.kt.skills.NewFileSystemSource
import com.google.adk.kt.skills.SkillSource
import com.google.adk.kt.skills.SkillSourceException
import com.google.adk.kt.tools.SkillToolset

// --8<-- [start:get_started]
// NewFileSystemSource discovers every skill directory under the base directory,
// so there is no per-skill load call.
val mySkillToolset = SkillToolset(NewFileSystemSource("skills"))

val skillUserAgent =
    LlmAgent(
        name = "skill_user_agent",
        model = Gemini(name = "gemini-flash-latest"),
        description = "An agent that can use specialized skills.",
        instruction =
            Instruction("You are a helpful assistant that can leverage skills to perform tasks."),
        // A SkillToolset contributes only the skill tools. Any other tool the agent
        // needs is passed separately in `tools`.
        toolsets = listOf(mySkillToolset),
    )
// --8<-- [end:get_started]

// --8<-- [start:inline_skill]

/**
 * ADK Kotlin does not provide a standard [SkillSource] for skills defined in code, so implement the
 * interface yourself to serve them from memory.
 */
class StaticSkillSource : SkillSource {
    private val greetingSkill =
        Frontmatter(
            name = "greeting-skill",
            description = "A friendly greeting skill that can say hello to a specific person.",
        )

    private val instructions =
        "Step 1: Read the 'references/hello_world.txt' file to understand how to greet the " +
            "user. Step 2: Return a greeting based on the reference."

    private val resources =
        mapOf(
            "references/hello_world.txt" to "Hello! So glad to have you here!",
            "references/example.md" to "This is an example reference.",
        )

    private fun notFound(skillName: String) = SkillSourceException("Skill $skillName not found.")

    override suspend fun listFrontmatters(): Result<List<Frontmatter>> =
        Result.success(listOf(greetingSkill))

    override suspend fun loadFrontmatter(skillName: String): Result<Frontmatter> =
        if (skillName == greetingSkill.name) {
            Result.success(greetingSkill)
        } else {
            Result.failure(notFound(skillName))
        }

    override suspend fun loadInstructions(skillName: String): Result<String> =
        if (skillName == greetingSkill.name) {
            Result.success(instructions)
        } else {
            Result.failure(notFound(skillName))
        }

    override suspend fun listResources(
        skillName: String,
        resourceDirectoryPath: String,
    ): Result<List<String>> {
        if (skillName != greetingSkill.name) return Result.failure(notFound(skillName))
        val prefix = resourceDirectoryPath.removePrefix("./").removeSuffix("/")
        if (prefix.isEmpty() || prefix == ".") return Result.success(resources.keys.toList())
        // Skill resources live only under references/, assets/ and scripts/.
        if (prefix.substringBefore("/") !in SkillSource.VALID_RESOURCE_DIRS) {
            return Result.failure(
                SkillSourceException("Invalid resource path: $resourceDirectoryPath"),
            )
        }
        return Result.success(resources.keys.filter { it.startsWith("$prefix/") })
    }

    override suspend fun loadResource(
        skillName: String,
        resourcePath: String,
    ): Result<ByteArray> {
        if (skillName != greetingSkill.name) return Result.failure(notFound(skillName))
        val content =
            resources[resourcePath]
                ?: return Result.failure(
                    SkillSourceException("Resource $resourcePath not found in skill $skillName."),
                )
        return Result.success(content.encodeToByteArray())
    }
}

val inlineSkillAgent =
    LlmAgent(
        name = "greeting_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("Greet the user by following the greeting skill."),
        toolsets = listOf(SkillToolset(StaticSkillSource())),
    )
// --8<-- [end:inline_skill]

// --8<-- [start:filesystem_skill]
// Every immediate subdirectory of "skills" that contains a SKILL.md is exposed as
// a skill, so individual skills are discovered rather than named one by one.
val filesystemSource = NewFileSystemSource("skills")

val filesystemSkillToolset = SkillToolset(filesystemSource)
// --8<-- [end:filesystem_skill]
