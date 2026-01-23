# Changelog

## [1.4.0](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.3.0...v1.4.0) (2026-01-23)


### Features

* add GitHub Action for automatic code formatting via /lint_code command ([#598](https://github.com/openfoodfacts/taxonomy-editor/issues/598)) ([92912a5](https://github.com/openfoodfacts/taxonomy-editor/commit/92912a532ce131478608373ecac034fd403b4661))
* implement smart Dependabot dependency grouping to reduce PR noise ([#583](https://github.com/openfoodfacts/taxonomy-editor/issues/583)) ([0822286](https://github.com/openfoodfacts/taxonomy-editor/commit/08222864ecb983789e52388f4bd7fd05a0a83040))


### Bug Fixes

* Fix typo in PR dialog text ([#580](https://github.com/openfoodfacts/taxonomy-editor/issues/580)) ([9bf3187](https://github.com/openfoodfacts/taxonomy-editor/commit/9bf31877bc5a4c8faea45af5db5f0ba767869e0d))
* Fix typo in TLDR section of README ([#601](https://github.com/openfoodfacts/taxonomy-editor/issues/601)) ([83ccbfd](https://github.com/openfoodfacts/taxonomy-editor/commit/83ccbfddb0982ad6649c8ed08b6cc0d891f625df))
* Rename dependabot-groups.MD to DEPENDABOT_GROUPS.md ([b99cb60](https://github.com/openfoodfacts/taxonomy-editor/commit/b99cb60ec60615001518c8d4ad78496bf9efe971))
* Rename dependabot-groups.md to dependabot-groups.MD ([2b47c74](https://github.com/openfoodfacts/taxonomy-editor/commit/2b47c74740e28bfc050c329a1643cf36cce25479))

## [1.3.0](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.2.0...v1.3.0) (2025-05-15)


### Features

* add Beauty ingredients taxonomy ([#571](https://github.com/openfoodfacts/taxonomy-editor/issues/571)) ([b914696](https://github.com/openfoodfacts/taxonomy-editor/commit/b9146964472ec6556e68033d0e0a12c6398bb9cd))


### Bug Fixes

* do not account for stopwords for ids ([#579](https://github.com/openfoodfacts/taxonomy-editor/issues/579)) ([03112a8](https://github.com/openfoodfacts/taxonomy-editor/commit/03112a815264a90e4d77e47bcaa017ec317eb0da)), closes [#540](https://github.com/openfoodfacts/taxonomy-editor/issues/540)
* newly added then deleted node should not be exported ([#576](https://github.com/openfoodfacts/taxonomy-editor/issues/576)) ([1b5ef0d](https://github.com/openfoodfacts/taxonomy-editor/commit/1b5ef0d6053ca594235a85710708a59a7cb9d352)), closes [#561](https://github.com/openfoodfacts/taxonomy-editor/issues/561)
* Update README.md with design promo ([40f1eff](https://github.com/openfoodfacts/taxonomy-editor/commit/40f1eff08da758f20ca5dbe9bb6b796f85c5389f))

## [1.2.0](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.1.0...v1.2.0) (2024-12-20)


### Features

* first beauty and product taxonomies ([#559](https://github.com/openfoodfacts/taxonomy-editor/issues/559)) ([e66db34](https://github.com/openfoodfacts/taxonomy-editor/commit/e66db34213dd449a351d2948a427107d0a1c9194))
* more readable default project names ([#557](https://github.com/openfoodfacts/taxonomy-editor/issues/557)) ([4036188](https://github.com/openfoodfacts/taxonomy-editor/commit/4036188278b142b58aea1e7cf2beddb3d6b9069e))
* taxonomy patch instead of re-generating ([#554](https://github.com/openfoodfacts/taxonomy-editor/issues/554)) ([928dfd0](https://github.com/openfoodfacts/taxonomy-editor/commit/928dfd0e7b27d62425ef47ed2f969b3db3596c09))
* wip on: ([b5bcefc](https://github.com/openfoodfacts/taxonomy-editor/commit/b5bcefc2a22d4f0257868db9f357a866aabe8f90))


### Bug Fixes

* bad tables dom on errors and search results ([#556](https://github.com/openfoodfacts/taxonomy-editor/issues/556)) ([31243c7](https://github.com/openfoodfacts/taxonomy-editor/commit/31243c7ecbc26986bb5e04df2126cd529e510670))

## [1.1.0](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.0.2...v1.1.0) (2024-07-26)


### Features

* make taxonomy more robust ([#524](https://github.com/openfoodfacts/taxonomy-editor/issues/524)) ([49d8e46](https://github.com/openfoodfacts/taxonomy-editor/commit/49d8e46ea30d7c8ca6b6edc73842005603058d1e))

## [1.0.2](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.0.1...v1.0.2) (2024-07-24)


### Bug Fixes

* add a space after line identifier ([#520](https://github.com/openfoodfacts/taxonomy-editor/issues/520)) ([51f7b43](https://github.com/openfoodfacts/taxonomy-editor/commit/51f7b43c73b7a1f8504ce203c98627583cb31097))
* avoid altering original entries at parsing time ([#519](https://github.com/openfoodfacts/taxonomy-editor/issues/519)) ([5fbaba9](https://github.com/openfoodfacts/taxonomy-editor/commit/5fbaba991ad3d37ccd48ce22f19014ac9d418b4f))
* less transformations on comment lines and others ([#523](https://github.com/openfoodfacts/taxonomy-editor/issues/523)) ([d366218](https://github.com/openfoodfacts/taxonomy-editor/commit/d3662181e139243c8c709dffbe48124bb100b7fa))

## [1.0.1](https://github.com/openfoodfacts/taxonomy-editor/compare/v1.0.0...v1.0.1) (2024-07-17)


### Bug Fixes

* avoid confusing language prefixes and property names ([#513](https://github.com/openfoodfacts/taxonomy-editor/issues/513)) ([e0053b6](https://github.com/openfoodfacts/taxonomy-editor/commit/e0053b6213b7f3584fcb860eb7f577baebb34520))
* language order as we dump taxonomies ([#512](https://github.com/openfoodfacts/taxonomy-editor/issues/512)) ([2bc56e6](https://github.com/openfoodfacts/taxonomy-editor/commit/2bc56e621829dd1676660a1a6a4407c5e036eb40))

## 1.0.0 (2024-07-12)


### Features

* add a button to add translations for langs with no translations ([#179](https://github.com/openfoodfacts/taxonomy-editor/issues/179)) ([ee1fa5a](https://github.com/openfoodfacts/taxonomy-editor/commit/ee1fa5abbef06ce1eb94c176258369c456d5be74))
* Add advanced search API ([#438](https://github.com/openfoodfacts/taxonomy-editor/issues/438)) ([9c87d1b](https://github.com/openfoodfacts/taxonomy-editor/commit/9c87d1b3b3fc9a40483265008147feae3c919d59))
* add automatic client SDK generation ([#405](https://github.com/openfoodfacts/taxonomy-editor/issues/405)) ([7751319](https://github.com/openfoodfacts/taxonomy-editor/commit/7751319716f2f47d741d5554d86b659160937a8e))
* Add CRUD features for entries and root nodes ([#41](https://github.com/openfoodfacts/taxonomy-editor/issues/41)) ([038a1a6](https://github.com/openfoodfacts/taxonomy-editor/commit/038a1a6df162e74969e41de4fd88f095f0ee01d9))
* add error logs to parser ([#37](https://github.com/openfoodfacts/taxonomy-editor/issues/37)) ([2e8e49f](https://github.com/openfoodfacts/taxonomy-editor/commit/2e8e49fb7e9ca56ac5ff195dde00a6992f435c5c))
* Add export functionality in frontend ([#120](https://github.com/openfoodfacts/taxonomy-editor/issues/120)) ([63dbf17](https://github.com/openfoodfacts/taxonomy-editor/commit/63dbf17222bf077fca06aa1e1d00400854d53466))
* Add GET paths for parents and children + fix: Update Neo4J query ([#35](https://github.com/openfoodfacts/taxonomy-editor/issues/35)) ([44025da](https://github.com/openfoodfacts/taxonomy-editor/commit/44025da3b204ee7209554b1447d4669507ec3b13))
* Add home screen ([#42](https://github.com/openfoodfacts/taxonomy-editor/issues/42)) ([d94954c](https://github.com/openfoodfacts/taxonomy-editor/commit/d94954c27fcbe3adcdf6af3cb96fce78ff0770a6))
* add link to the Taxonomy Editor project in PR description ([#472](https://github.com/openfoodfacts/taxonomy-editor/issues/472)) ([b2a7b43](https://github.com/openfoodfacts/taxonomy-editor/commit/b2a7b4339d336023755d010d3e1612c5bf28f6fc))
* add new user with USER_GID parameter & replace root user ([#113](https://github.com/openfoodfacts/taxonomy-editor/issues/113)) ([6fb1b4c](https://github.com/openfoodfacts/taxonomy-editor/commit/6fb1b4c6e898212a515b01c96d525bf8c2485e6a)), closes [#63](https://github.com/openfoodfacts/taxonomy-editor/issues/63)
* Add parent order determinism ([#337](https://github.com/openfoodfacts/taxonomy-editor/issues/337)) ([5762d0c](https://github.com/openfoodfacts/taxonomy-editor/commit/5762d0c59fbe80832aedaf9cda649e97f8727c83))
* add property filter to search API ([#456](https://github.com/openfoodfacts/taxonomy-editor/issues/456)) ([0b26030](https://github.com/openfoodfacts/taxonomy-editor/commit/0b26030d96588692a8dcb65ebaf8f0b06f04f17a))
* add taxonomy file upload endpoint ([#196](https://github.com/openfoodfacts/taxonomy-editor/issues/196)) ([115c76d](https://github.com/openfoodfacts/taxonomy-editor/commit/115c76d46d234295336b4359be5e0b679e85d27d))
* add tests for importing taxonomies ([#225](https://github.com/openfoodfacts/taxonomy-editor/issues/225)) ([bad3f6a](https://github.com/openfoodfacts/taxonomy-editor/commit/bad3f6ae87431a6eba0cd3e73b8f6470b88a91bb))
* added autocomplete for language codes ([#117](https://github.com/openfoodfacts/taxonomy-editor/issues/117)) ([7d8863a](https://github.com/openfoodfacts/taxonomy-editor/commit/7d8863a902627d26ecc32f93391c442dda004ce0))
* Added functions for reopening projects and fetching closed projects ([#152](https://github.com/openfoodfacts/taxonomy-editor/issues/152)) ([a714cf4](https://github.com/openfoodfacts/taxonomy-editor/commit/a714cf48d0c8a9511e67d9cda7555857399802bd))
* added typescript ([#191](https://github.com/openfoodfacts/taxonomy-editor/issues/191)) ([ff85a0a](https://github.com/openfoodfacts/taxonomy-editor/commit/ff85a0a250956201cf9fa89cf4ecc0e1f91b693d))
* All entries page + Navbar ([#43](https://github.com/openfoodfacts/taxonomy-editor/issues/43)) ([3eb9149](https://github.com/openfoodfacts/taxonomy-editor/commit/3eb91493f9e70180d7c212360e61ebfca5ad8755))
* CI formatter ([#172](https://github.com/openfoodfacts/taxonomy-editor/issues/172)) ([7d43499](https://github.com/openfoodfacts/taxonomy-editor/commit/7d4349976f1b74f5a10278af003c5b50654e7d89))
* Decouple parsing the taxonomy and writing the taxonomy to the database ([#317](https://github.com/openfoodfacts/taxonomy-editor/issues/317)) ([71b34be](https://github.com/openfoodfacts/taxonomy-editor/commit/71b34be697047ba5c33d76c0b2cc3dc6386ffba7))
* Delete projects when their Github PR is merged ([#385](https://github.com/openfoodfacts/taxonomy-editor/issues/385)) ([1304822](https://github.com/openfoodfacts/taxonomy-editor/commit/1304822b1c65a565548caca59497c8c6f2d39dc4))
* Delete taxonomy project ([#237](https://github.com/openfoodfacts/taxonomy-editor/issues/237)) ([d0a15cb](https://github.com/openfoodfacts/taxonomy-editor/commit/d0a15cb262e3db24bccf11a9b41f62716c6cc425)), closes [#139](https://github.com/openfoodfacts/taxonomy-editor/issues/139)
* Display parents and children of an entry ([#47](https://github.com/openfoodfacts/taxonomy-editor/issues/47)) ([d71da9c](https://github.com/openfoodfacts/taxonomy-editor/commit/d71da9c341aebff00433e31d4625b79e30fe0804))
* Edit synonyms, stopwords page ([#46](https://github.com/openfoodfacts/taxonomy-editor/issues/46)) ([be2da15](https://github.com/openfoodfacts/taxonomy-editor/commit/be2da15deb1a209767d77d0172a3fe67a08caf9b))
* expand/collapse languages ([3ba69ec](https://github.com/openfoodfacts/taxonomy-editor/commit/3ba69eca5cc2d40961cd7d346ae12f4f1f7b9627))
* **frontend,backend:** Add a owner to a project ([#409](https://github.com/openfoodfacts/taxonomy-editor/issues/409)) ([2c508cb](https://github.com/openfoodfacts/taxonomy-editor/commit/2c508cb392caa2ff1f702d43a782147ec0d59dcd))
* **frontend:** enable advanced research ([#463](https://github.com/openfoodfacts/taxonomy-editor/issues/463)) ([20ca2e4](https://github.com/openfoodfacts/taxonomy-editor/commit/20ca2e46406aeed0a7ed2193d709f53b72eac232))
* **frontend:** make language selection for translations more intuitive ([#461](https://github.com/openfoodfacts/taxonomy-editor/issues/461)) ([4119aed](https://github.com/openfoodfacts/taxonomy-editor/commit/4119aedf501fbd0c7ad2c04cc0a219f66e709caf))
* **frontend:** Reword export message ([#428](https://github.com/openfoodfacts/taxonomy-editor/issues/428)) ([f2b13dc](https://github.com/openfoodfacts/taxonomy-editor/commit/f2b13dc946ab30e7d60014d8bea8ecfe4f7b0ea3))
* hide all languages by default in the UI ([#175](https://github.com/openfoodfacts/taxonomy-editor/issues/175)) ([3ba69ec](https://github.com/openfoodfacts/taxonomy-editor/commit/3ba69eca5cc2d40961cd7d346ae12f4f1f7b9627))
* hide synonyms and stopwords in the root nodes page ([#187](https://github.com/openfoodfacts/taxonomy-editor/issues/187)) ([177b60e](https://github.com/openfoodfacts/taxonomy-editor/commit/177b60e7587f40287d39f87e8f87eb1657c4ff1c))
* improve errors page ([#341](https://github.com/openfoodfacts/taxonomy-editor/issues/341)) ([674e3c1](https://github.com/openfoodfacts/taxonomy-editor/commit/674e3c1e14e0ff366966c72e35140aaaf19dbf43))
* improve node creation performance ([74d0083](https://github.com/openfoodfacts/taxonomy-editor/commit/74d0083717feb6c3e1851971a925e4d90ec69f90))
* Improve node creation performance ([#338](https://github.com/openfoodfacts/taxonomy-editor/issues/338)) ([74d0083](https://github.com/openfoodfacts/taxonomy-editor/commit/74d0083717feb6c3e1851971a925e4d90ec69f90))
* Improve parser performance ([#318](https://github.com/openfoodfacts/taxonomy-editor/issues/318)) ([78fdffc](https://github.com/openfoodfacts/taxonomy-editor/commit/78fdffc978af64f79b124c3d758f37906cfdb5f0))
* improve translations editing ([#324](https://github.com/openfoodfacts/taxonomy-editor/issues/324)) ([453ff89](https://github.com/openfoodfacts/taxonomy-editor/commit/453ff8937004c18c11adc32e1055668207c002e4))
* Initialize edit entry page ([#44](https://github.com/openfoodfacts/taxonomy-editor/issues/44)) ([87c23e0](https://github.com/openfoodfacts/taxonomy-editor/commit/87c23e051b7a87415283b74c71a2dc2c1f9a9940))
* List all properties of an entry ([#45](https://github.com/openfoodfacts/taxonomy-editor/issues/45)) ([f6f8bc2](https://github.com/openfoodfacts/taxonomy-editor/commit/f6f8bc28cfa529ebb7f4f2032ca5d4fa46b143e5))
* New paths for API ([#76](https://github.com/openfoodfacts/taxonomy-editor/issues/76)) ([2901cf7](https://github.com/openfoodfacts/taxonomy-editor/commit/2901cf765aa50f3734dcac7d4094a8cb7a2b1dfb)), closes [#38](https://github.com/openfoodfacts/taxonomy-editor/issues/38) [#75](https://github.com/openfoodfacts/taxonomy-editor/issues/75)
* New paths for backend API ([#26](https://github.com/openfoodfacts/taxonomy-editor/issues/26)) ([d5891fe](https://github.com/openfoodfacts/taxonomy-editor/commit/d5891fe691d2270df53aba29e1c8d930b8937710))
* new UX for submitting changes ([#224](https://github.com/openfoodfacts/taxonomy-editor/issues/224)) ([8525351](https://github.com/openfoodfacts/taxonomy-editor/commit/852535143e16df36fef337cfcfc9d52e2e9fc636))
* **parser,backend,frontend:** enable extended taxonomies ([#429](https://github.com/openfoodfacts/taxonomy-editor/issues/429)) ([230bdbf](https://github.com/openfoodfacts/taxonomy-editor/commit/230bdbffc7f5f1e7c295fc16a14a7f9d5020ed5b))
* **parser,frontend,backend:** conserve comments order and sort properties at export ([#364](https://github.com/openfoodfacts/taxonomy-editor/issues/364)) ([780ad2a](https://github.com/openfoodfacts/taxonomy-editor/commit/780ad2af6eeb95c588f18b84a95e6e3522c3726f))
* **parser:** handle duplicate ID errors during parsing ([#408](https://github.com/openfoodfacts/taxonomy-editor/issues/408)) ([e5720bf](https://github.com/openfoodfacts/taxonomy-editor/commit/e5720bf04eeed8ffd30c8029eb85f30925be1f08))
* parsing error endpoint ([#163](https://github.com/openfoodfacts/taxonomy-editor/issues/163)) ([1f38d0f](https://github.com/openfoodfacts/taxonomy-editor/commit/1f38d0f2c302aa36672b8fb036f64e93fb5b8afe))
* parsing errors page ([#186](https://github.com/openfoodfacts/taxonomy-editor/issues/186)) ([68b64ec](https://github.com/openfoodfacts/taxonomy-editor/commit/68b64ece9401325f31dd9fcd8a93fb10bc380642))
* Search functionality - Backend ([#91](https://github.com/openfoodfacts/taxonomy-editor/issues/91)) ([3317fae](https://github.com/openfoodfacts/taxonomy-editor/commit/3317fae1cc8e20c00744429c51b50f6e4b3086dc))
* Search functionality - Frontend ([#92](https://github.com/openfoodfacts/taxonomy-editor/issues/92)) ([154f50f](https://github.com/openfoodfacts/taxonomy-editor/commit/154f50f3dfda329ae68a9e54f9c04b9b945a1b4a))
* select shown languages in UI ([#180](https://github.com/openfoodfacts/taxonomy-editor/issues/180)) ([50403e8](https://github.com/openfoodfacts/taxonomy-editor/commit/50403e88533e45b0d9d820d673ec9ab97bd08cd8))
* Setup basic FastAPI project ([#10](https://github.com/openfoodfacts/taxonomy-editor/issues/10)) ([1d1e789](https://github.com/openfoodfacts/taxonomy-editor/commit/1d1e789055d74dee2bceda3042c5c0a2dd1a44a5))
* setup fastapi tests ([#223](https://github.com/openfoodfacts/taxonomy-editor/issues/223)) ([6e24698](https://github.com/openfoodfacts/taxonomy-editor/commit/6e2469854d5d90f9ed5c36a603b431cdbf6cf856))
* Show feedback when special characters are entered in branch name ([#229](https://github.com/openfoodfacts/taxonomy-editor/issues/229)) ([2b19c72](https://github.com/openfoodfacts/taxonomy-editor/commit/2b19c72d42bb80e1f0b3408f26650caf52825728))
* store languages marked as visible by user in localstorage ([#185](https://github.com/openfoodfacts/taxonomy-editor/issues/185)) ([5c9df2e](https://github.com/openfoodfacts/taxonomy-editor/commit/5c9df2e7118d574f2c526be81cee6fdb4317b5fc))
* store raw stopwords and rewrite them at export ([#358](https://github.com/openfoodfacts/taxonomy-editor/issues/358)) ([444f76d](https://github.com/openfoodfacts/taxonomy-editor/commit/444f76d1f1954473829bf71f9c7e2268d2e0a9c5))
* support new folders structure ([#434](https://github.com/openfoodfacts/taxonomy-editor/issues/434)) ([7180f5c](https://github.com/openfoodfacts/taxonomy-editor/commit/7180f5ca69e22208c455b1378a9b1652d26346ca))
* taxonomy parser library ([#18](https://github.com/openfoodfacts/taxonomy-editor/issues/18)) ([6b3461a](https://github.com/openfoodfacts/taxonomy-editor/commit/6b3461ade913202aedb4796f506c549c7c80c938))
* **taxonomy-editor-frontend:** loading animation ([#283](https://github.com/openfoodfacts/taxonomy-editor/issues/283)) ([2746f7f](https://github.com/openfoodfacts/taxonomy-editor/commit/2746f7f3bd2a6a6370977ef7ad13a36dc01eedf5))
* Update GitHub functions ([#368](https://github.com/openfoodfacts/taxonomy-editor/issues/368)) ([3fefb1d](https://github.com/openfoodfacts/taxonomy-editor/commit/3fefb1d8eac5efb32c8ec0860c6e11595c5964cd))
* Update parser to add a neo4j parsing errors node ([#132](https://github.com/openfoodfacts/taxonomy-editor/issues/132)) ([8ec5331](https://github.com/openfoodfacts/taxonomy-editor/commit/8ec533160125596cb6f985d00000b1286b9888ea))
* Update Project List ([#443](https://github.com/openfoodfacts/taxonomy-editor/issues/443)) ([ca0512c](https://github.com/openfoodfacts/taxonomy-editor/commit/ca0512c35ff54c8e2a69f1f129f7f2d6f3c5c4ea))


### Bug Fixes

* [#184](https://github.com/openfoodfacts/taxonomy-editor/issues/184) sorted the language selection menu alphabetically ([#218](https://github.com/openfoodfacts/taxonomy-editor/issues/218)) ([25e494c](https://github.com/openfoodfacts/taxonomy-editor/commit/25e494cef9b4d2294742fd6a70c00c010f3ef18e))
* [#203](https://github.com/openfoodfacts/taxonomy-editor/issues/203) added scrollbar in the table for small screen sizes ([#221](https://github.com/openfoodfacts/taxonomy-editor/issues/221)) ([63e29d3](https://github.com/openfoodfacts/taxonomy-editor/commit/63e29d319d8dfee3bd6cfb4858736c30de1b1885))
* add camel cased types to the frontend ([d5d5944](https://github.com/openfoodfacts/taxonomy-editor/commit/d5d5944aed2613aadb47dedbaf8668551d55f83a))
* Add camelCased aliases to Pydantic models ([#436](https://github.com/openfoodfacts/taxonomy-editor/issues/436)) ([d5d5944](https://github.com/openfoodfacts/taxonomy-editor/commit/d5d5944aed2613aadb47dedbaf8668551d55f83a))
* Add multiple labels in backend, import and export ([#101](https://github.com/openfoodfacts/taxonomy-editor/issues/101)) ([a40b9fd](https://github.com/openfoodfacts/taxonomy-editor/commit/a40b9fd69b046823e871c577ac2f696b46058382)), closes [#83](https://github.com/openfoodfacts/taxonomy-editor/issues/83)
* Add score &gt; 0 condition for search ([#102](https://github.com/openfoodfacts/taxonomy-editor/issues/102)) ([23b9b5e](https://github.com/openfoodfacts/taxonomy-editor/commit/23b9b5e5dfa1473732ac7dfea1a12c49611e4cc2))
* Add snake case to taxonomy name for link ([c8a9e0a](https://github.com/openfoodfacts/taxonomy-editor/commit/c8a9e0a7f060bb38bd1a3a46f1c3db02b0c3da27))
* Add UUIDs after fetching node ([#100](https://github.com/openfoodfacts/taxonomy-editor/issues/100)) ([3bafa54](https://github.com/openfoodfacts/taxonomy-editor/commit/3bafa540ee1ab6f4fa333e1a13a0ff0b789a1c9f))
* added requested changes ([7d8863a](https://github.com/openfoodfacts/taxonomy-editor/commit/7d8863a902627d26ecc32f93391c442dda004ce0))
* App bar fixes ([#392](https://github.com/openfoodfacts/taxonomy-editor/issues/392)) ([3deaa57](https://github.com/openfoodfacts/taxonomy-editor/commit/3deaa579a2defa2de613961b9eba67c7feb5c61c))
* **backend,parser:** remove stopwords from normalized tags on node update ([#369](https://github.com/openfoodfacts/taxonomy-editor/issues/369)) ([24be684](https://github.com/openfoodfacts/taxonomy-editor/commit/24be684b1415e7131476af1cb16b884f26dbf412))
* **backend:** error on node creation from root nodes ([#445](https://github.com/openfoodfacts/taxonomy-editor/issues/445)) ([d94376c](https://github.com/openfoodfacts/taxonomy-editor/commit/d94376c5c22b176026b007e4a9a9de05a226308f))
* **backend:** fix create_node function ([#393](https://github.com/openfoodfacts/taxonomy-editor/issues/393)) ([40a3208](https://github.com/openfoodfacts/taxonomy-editor/commit/40a3208a7a5e1075ef5fc5d1216800942f399dd3))
* Broken link while starting new project ([#217](https://github.com/openfoodfacts/taxonomy-editor/issues/217)) ([c8a9e0a](https://github.com/openfoodfacts/taxonomy-editor/commit/c8a9e0a7f060bb38bd1a3a46f1c3db02b0c3da27))
* Change routes for including branch and taxonomy names ([#110](https://github.com/openfoodfacts/taxonomy-editor/issues/110)) ([3d7ff93](https://github.com/openfoodfacts/taxonomy-editor/commit/3d7ff930d8377b884c156f0a8d35b819e6319582))
* Change session to transactions ([#97](https://github.com/openfoodfacts/taxonomy-editor/issues/97)) ([21d05e5](https://github.com/openfoodfacts/taxonomy-editor/commit/21d05e5f9b0a080a9034afead8de846fa812e122))
* Changed JSON according to spec ([#19](https://github.com/openfoodfacts/taxonomy-editor/issues/19)) ([9133a70](https://github.com/openfoodfacts/taxonomy-editor/commit/9133a7013de609db76751e4b37d1b2cfe1190c37))
* clean duplicate title ([3cba2c9](https://github.com/openfoodfacts/taxonomy-editor/commit/3cba2c9700af7fcc2cfecfb23cc71314348ab7e7))
* clean duplicate title in project list ([#415](https://github.com/openfoodfacts/taxonomy-editor/issues/415)) ([3cba2c9](https://github.com/openfoodfacts/taxonomy-editor/commit/3cba2c9700af7fcc2cfecfb23cc71314348ab7e7))
* Creation and relationship building using normalized node ID ([#128](https://github.com/openfoodfacts/taxonomy-editor/issues/128)) ([ca574b3](https://github.com/openfoodfacts/taxonomy-editor/commit/ca574b35a536532c22d1b3234046ecc129c13cb3))
* error when adding child to node with no children ([#447](https://github.com/openfoodfacts/taxonomy-editor/issues/447)) ([f74cfdf](https://github.com/openfoodfacts/taxonomy-editor/commit/f74cfdf7f01fa2814b0772ec701eeedab52d6dce))
* Error while updating a node (backend) ([#74](https://github.com/openfoodfacts/taxonomy-editor/issues/74)) ([f24ff83](https://github.com/openfoodfacts/taxonomy-editor/commit/f24ff8328c3007b61cd6a62b6f023ca01740f78f))
* fix backwards compatibility for is:not:external search ([#455](https://github.com/openfoodfacts/taxonomy-editor/issues/455)) ([dbedfb9](https://github.com/openfoodfacts/taxonomy-editor/commit/dbedfb937a5b5c9912d1f3c2a5ea766014dff2bb))
* fix bug in parser ([0c7427e](https://github.com/openfoodfacts/taxonomy-editor/commit/0c7427eed640c8a023f70b30753475643ca9d0eb))
* fix export to local file ([#352](https://github.com/openfoodfacts/taxonomy-editor/issues/352)) ([b18ac03](https://github.com/openfoodfacts/taxonomy-editor/commit/b18ac038fcf20ffbd202e87460f0d354199bd56d))
* frontend fixes ([#492](https://github.com/openfoodfacts/taxonomy-editor/issues/492)) ([6003639](https://github.com/openfoodfacts/taxonomy-editor/commit/60036397b508e278f8d30fd4db6512f7a706b4a2))
* **frontend:** enable child creation even if no children in entry ([#406](https://github.com/openfoodfacts/taxonomy-editor/issues/406)) ([3562e7d](https://github.com/openfoodfacts/taxonomy-editor/commit/3562e7d6fa73de2404fc1b23812023c53cddd89a))
* **frontend:** Enhance Edition of Properties for a Node ([#362](https://github.com/openfoodfacts/taxonomy-editor/issues/362)) ([9d765d0](https://github.com/openfoodfacts/taxonomy-editor/commit/9d765d09cd96bf0435ef1a8a605b49e79876dce8))
* **frontend:** enhance property edition ([#394](https://github.com/openfoodfacts/taxonomy-editor/issues/394)) ([7bfcb71](https://github.com/openfoodfacts/taxonomy-editor/commit/7bfcb7153520171e773a2251c8b17c7d331844b2))
* **frontend:** fix children and parents overflow ([#411](https://github.com/openfoodfacts/taxonomy-editor/issues/411)) ([eb0f36a](https://github.com/openfoodfacts/taxonomy-editor/commit/eb0f36acbe019568cf17116829c6c3e30feaf423))
* **frontend:** fix root nodes page infinite loading when project exported ([#413](https://github.com/openfoodfacts/taxonomy-editor/issues/413)) ([ee90d96](https://github.com/openfoodfacts/taxonomy-editor/commit/ee90d960f43d3c777b30064e33273c5105acc410))
* **frontend:** handle no error case on errors page ([054cf8c](https://github.com/openfoodfacts/taxonomy-editor/commit/054cf8c42b95d3e992a0f88ac9a47b6f5796101e))
* **frontend:** Handle no error case on errors page ([#378](https://github.com/openfoodfacts/taxonomy-editor/issues/378)) ([054cf8c](https://github.com/openfoodfacts/taxonomy-editor/commit/054cf8c42b95d3e992a0f88ac9a47b6f5796101e))
* **frontend:** Handle xx language for translations edition ([#354](https://github.com/openfoodfacts/taxonomy-editor/issues/354)) ([b189e2e](https://github.com/openfoodfacts/taxonomy-editor/commit/b189e2e2946ad08bf1ad2a680f2caa15f0c99cd1))
* **frontend:** Prevent users from navigating to child with unsaved changes ([#468](https://github.com/openfoodfacts/taxonomy-editor/issues/468)) ([6391abb](https://github.com/openfoodfacts/taxonomy-editor/commit/6391abb6eed563a33be1e06d8ca97971260fbadb))
* **frontend:** Remove Countries and Languages from editable taxonomies ([#377](https://github.com/openfoodfacts/taxonomy-editor/issues/377)) ([fdde28c](https://github.com/openfoodfacts/taxonomy-editor/commit/fdde28c4896611dc3327b59361b60985d0bd0c5a))
* **frontend:** Replace white spaces in branch name proposition and allow dashes in owner name ([#466](https://github.com/openfoodfacts/taxonomy-editor/issues/466)) ([7170d84](https://github.com/openfoodfacts/taxonomy-editor/commit/7170d84095b2e9cd9d00392556681d361d4b9db2))
* Makefile unable to detect parser directory in Windows 11 ([#178](https://github.com/openfoodfacts/taxonomy-editor/issues/178)) ([e2a6e8e](https://github.com/openfoodfacts/taxonomy-editor/commit/e2a6e8e7bcdb721f78a48857b1cee4f9e9656472))
* nginx config allows app page reload ([#141](https://github.com/openfoodfacts/taxonomy-editor/issues/141)) ([ebc772b](https://github.com/openfoodfacts/taxonomy-editor/commit/ebc772bf116f66af8efc67be55a34cb121d90986))
* node update and display ([#497](https://github.com/openfoodfacts/taxonomy-editor/issues/497)) ([012de09](https://github.com/openfoodfacts/taxonomy-editor/commit/012de098da1f79e90c77ad6943c47378f6abcc86))
* Normalising Children and New Nodes ([#111](https://github.com/openfoodfacts/taxonomy-editor/issues/111)) ([118a60f](https://github.com/openfoodfacts/taxonomy-editor/commit/118a60f88d403d3a6ce3f72368dea7dea7c7aa59))
* Normalize '-' characters + Convert to snake_case ([d9198ef](https://github.com/openfoodfacts/taxonomy-editor/commit/d9198ef014ba1b70b7b298c52571f111aa536e9d))
* Normalize '-' characters + fix: Convert to snake_case ([#137](https://github.com/openfoodfacts/taxonomy-editor/issues/137)) ([d9198ef](https://github.com/openfoodfacts/taxonomy-editor/commit/d9198ef014ba1b70b7b298c52571f111aa536e9d))
* Remove end slashes from URL in frontend ([#143](https://github.com/openfoodfacts/taxonomy-editor/issues/143)) ([39aa0e5](https://github.com/openfoodfacts/taxonomy-editor/commit/39aa0e5153b12db41207a27adbe01eb78ac8240f))
* simplify wording ([5d835e4](https://github.com/openfoodfacts/taxonomy-editor/commit/5d835e4c021bc4a9f78854c052514b13fcc83e03))
* simplify wording in error page ([#417](https://github.com/openfoodfacts/taxonomy-editor/issues/417)) ([5d835e4](https://github.com/openfoodfacts/taxonomy-editor/commit/5d835e4c021bc4a9f78854c052514b13fcc83e03))
* sort languages in search filters ([#498](https://github.com/openfoodfacts/taxonomy-editor/issues/498)) ([669755b](https://github.com/openfoodfacts/taxonomy-editor/commit/669755b98afbea7473b499e5d6d7cf9496ab1080))
* **taxonomy-editor-frontend:** redirect user to node editor when clicking from nodes page ([#284](https://github.com/openfoodfacts/taxonomy-editor/issues/284)) ([089df89](https://github.com/openfoodfacts/taxonomy-editor/commit/089df8971e447e38d322867840e11f3d23ffb344))
* update logo link to default / ([#422](https://github.com/openfoodfacts/taxonomy-editor/issues/422)) ([f010f31](https://github.com/openfoodfacts/taxonomy-editor/commit/f010f311d368efb176422e1e51b38026e830b851))
* Update requirements.txt for backend ([#103](https://github.com/openfoodfacts/taxonomy-editor/issues/103)) ([17150d9](https://github.com/openfoodfacts/taxonomy-editor/commit/17150d9637dee93a647a8531e8e9315d59932a62))
* use async neo4j + neo4j updgrade  ([#182](https://github.com/openfoodfacts/taxonomy-editor/issues/182)) ([3182980](https://github.com/openfoodfacts/taxonomy-editor/commit/318298041663fc966ce7f1a8260304a8836babc9)), closes [#181](https://github.com/openfoodfacts/taxonomy-editor/issues/181)
* Using Neo4J transactions ([#93](https://github.com/openfoodfacts/taxonomy-editor/issues/93)) ([bbab8d3](https://github.com/openfoodfacts/taxonomy-editor/commit/bbab8d3f8335ddeb1a6a03029ac4f46e1c178c24))
* wording in export ([#418](https://github.com/openfoodfacts/taxonomy-editor/issues/418)) ([ffaecb7](https://github.com/openfoodfacts/taxonomy-editor/commit/ffaecb7dfd6312c68b8ed2f7da9f86e60a86f93f))
