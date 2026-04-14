---
title: Wiki Maintenance Prompts
tags: documentation
---
# Wiki Maintenance Prompts

**Instruction for AI**: Reference this file and follow the numbered steps whenever a **Keyword** listed below is used in a query.

Use these prompts to interact with Gemini Code Assist for consistent wiki management. 

## 1. Update entity (The "Match First" Protocol)
**Use this when you have a list of names and want to ensure they match existing records before making changes.**
**Keyword:** `update entity`
> I am going to provide a list of names. Please process them using the following steps:
> 1. **Identification**: Search the wiki (including titles, aliases, and nicknames) for matching entities. Identify any ambiguities or potential new people.
> 2. **Verification**: Show me a table of matches (Proposed Name -> Existing Entity ID) and ask for confirmation before proceeding.
> 3. **Ripple Effect**: Once confirmed, update the filename, the YAML title, and the Wiki Index.
> 4. **Bidirectional Integrity**: Refactor all relationship links (parents, spouse, children, siblings) in other Markdown files to point to the new ID.
> **Note for Steps 3 & 4**: Absolutely exclude `.json` files from these updates, as they are handled by the automation script.

## 2. General Health Check & Linting
**Use this for periodic maintenance to find broken links or missing data.**
**Keyword:** `health check`
> Please run a health check on the wiki. Identify broken links, orphan pages, or inconsistencies where the YAML frontmatter does not match the relationship links in the page body. Provide a summary of found issues and ask for permission to fix them.

## 3. Data Ingestion
**Use this when you add a new file to the `/raw/` folder.**
**Keyword:** `ingest source`
> I have added a new source file to the `/raw/` folder named `[FILENAME]`. Please process this according to the `gemini.md` schema: create a source summary, update/create entity pages, update the index, and log the operation.

## 4. Relationship Tracing
**Use this to verify connections between two specific people.**
**Keyword:** `trace relationship`
> Trace the relationship path between `[[Person A]]` and `[[Person B]]`. Identify the common ancestor and define the relationship term (e.g., First Cousin Once Removed) based on the rules in the `relationship-guide.md`.

## 5. Batch Metadata Updates
**Use this to fill in missing `birth_date` or `location` fields.**
**Keyword:** `batch metadata`
> I have biographical details for several people. Please update the YAML frontmatter and "Biographical Data" sections for the following list:
> - [Name]: Birth Date [Date], Location [Place]
> - [Name]: Birth Date [Date], Location [Place]

## 6. Name Refactoring (Ripple Effects)
**Use this if a person was recorded with the wrong name or spelling.**
**Keyword:** `refactor name`
> Please rename the entity `[[Old Name]]` to `[[New Name]]`. Ensure you apply the "Ripple Effect" rule: update the filename, the title in frontmatter, the Wiki Index, and all parent/child/spouse/sibling links in other files that reference this person.
> **Note**: Absolutely exclude `.json` files from these updates.
 
## 7. Genealogical Branch Expansion
**Use this to add a spouse and children to an existing person.**
**Keyword:** `expand branch`
> I want to expand the branch for `[[Person Name]]`. 
> Spouse: [Spouse Name]
> Children: [Child 1], [Child 2]
> Please create any missing files and ensure all bidirectional links (parents to children and children to parents) are established.

## 8. Deployment Preparation
**Use this before pushing changes to GitHub.**
**Keyword:** `prepare deployment`
> I am ready to deploy. Please verify that the Wiki Index is alphabetized, all new entities have a `title` field in their frontmatter, and the `Health_Check_Report.md` is updated with the latest metrics.