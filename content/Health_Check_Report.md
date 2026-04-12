# Wiki Health Check Report (2026-04-11)

## Executive Summary
The wiki has been successfully migrated to Quartz v4. The repository is mapped to GitHub, and the deployment pipeline is being stabilized. All 235 entities are successfully parsed during local builds.

## Structural Metrics
- **Total Entities:** 235
- **Bidirectional Link Coverage:** 100% (Calculated based on available relationship data)
- **Orphan Pages:** 0 (All entities are reachable from the Index or a Parent/Spouse link).
- **Integrity Check:** Resolved name collisions for James, Rex, and Karl Adrian to fix Graph View navigation.
- **Redundancy Check:** 0 (Clean)

## Data Gaps
### 1. Missing Metadata
The following YAML fields are empty across all files:
- `birth_date`
- `location`

### 2. Biographical Stubs
The following pages contain only generation boilerplate and require research to expand:
 - **Tan-Chua branch**: [[kathlene_tan]], [[karlene_tan]], [[kaylene_tan]], [[kashlee_tan]].
 - **Gaw branch**: [[alan_gaw_1]], [[andrew_gaw_2]], [[kathleen_gaw_3]].
 - **Desiree branch**: [[desiree]], [[desireehusband_bill]], [[james_2|James]].
 - **Lim Branch**: [[asuncion]] (Merged identity formerly known as Sionee).
 - **Haipin/Serrano Branch**: [[renee]], [[robert_ang]], [[glenn_paul_serrano]], [[jennifer_gwen_marie_serrano]], [[genevieve_jean_marie_serrano]].
 - **Ongjuco Branch**: [[rosanne_1]], [[madeleine_ongjuco|Madeleine Rose Ongjuco]].
 - **New Generations**: [[sean]], [[erin]], [[richard]], [[robin]], [[ralph]], [[renzo]], [[riley]], [[becca]], [[jaylen_randall_dy]], [[alaira_reese_dy]], [[juliana_ryanne_lim]], [[rania_nicole_lim]], [[alexa_rielle_lim]], [[ryden_isaac_lim]], [[imari_rafaielle_lim]], [[mikkel]], [[margaux]], [[caleb]], [[jadon]], [[cherry]], [[aileen]], [[ronald]], [[nathalia]], [[louise]], [[dale]], [[clark]], [[samantha_ashley_ang]], [[sean_aiden_ang]], [[sofia_ailison_ang]], [[bianco_go]], [[edward_go]], [[suzie|Susie Gamba]], [[edith_chua_sy|Edith Chua Sy]], [[may_ann_see|May Ann See]], [[geofredo_so|Geofredo So]], [[mannix]], [[geofredo_so_jr|Geofredo Jr.]], [[karl_adrian_2|Karl Adrian (Leo Branch)]], [[james_2|James (Desiree Branch)]].

### 3. Terminal Branches (No Descendants)
There are several significant individuals with no spouse or children linked, which may indicate missing data or the end of a lineage in the current record:
- [[juana]]
- [[clemente_ong_4]]
- [[sohun_ong_1]]
- [[huayteng_ong_4]]

## Recommendations
1. **Research Pass:** Prioritize filling `birth_date` and `location` for Generation 1 and 2 patriarchs/matriarchs to anchor the timeline.
2. **Narrative Expansion:** Use future journal entries or interview notes to replace "Member of the X generation" with specific life details.
3. **Linting:** Periodically run a check for any new links created in Chat that haven't been saved to the Index.
4. **Tool Integration:** Ensure the Relationship Finder is linked on the homepage for easy path tracing between the 235 entities.
5. **Sharing Strategy:** Evaluate **Obsidian Publish** or **Quartz** to provide a web-based, clickable interface for family members to explore the 227+ interlinked entities.

**Status:** HEALTHY (Maintenance Required)