# Daliuren Knowledge Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the local 大六壬 knowledge base into three usable layers: 理法、象根、案例, then wire the agent to prefer the compiled layers when assembling analysis context.

**Architecture:** Keep the existing llm-wiki knowledge base as the source of truth and add curated compiled pages for 大六壬. The plan does not rewrite raw source extraction for the whole wiki; it only creates the 大六壬 layered pages, adds a clean modern-case derivation, and points the agent context at the compiled layers first.

**Tech Stack:** Existing llm-wiki markdown pages, local PDF/text extraction utilities, Python, pytest, and the current repo prompt/context assembly.

---

## File Structure

- Modify `/home/source/Documents/东玄知识库/wiki/topics/大六壬.md`: add layered navigation to 理法、象根、案例、现代案例.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-理法.md`: top-level理法 overview.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-象根.md`: top-level象根 overview.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-案例总览.md`: case index and reading order.
- Create `/home/source/Documents/东玄知识库/wiki/principles/daliuren/*.md`: principle pages distilled from《大六壬指南》.
- Create `/home/source/Documents/东玄知识库/wiki/images/daliuren/*.md`: symbol-root pages distilled from《五行大义》《六壬取象十二科》.
- Create `/home/source/Documents/东玄知识库/wiki/cases/daliuren/*.md`: structured case pages for邵彦和、牧夫占验、林烽.
- Create `/home/source/Documents/东玄知识库/wiki/sources/林烽-大六壬经典案例解析-clean.md`: source page for the clean modern case derivation.
- Create `/home/source/Documents/东玄知识库/raw/notes/derived_pdf/大六壬/林烽-大六壬经典案例解析-clean.pdf`: clean derived PDF used for indexing.
- Create `/home/source/Documents/东玄知识库/raw/notes/extracted/大六壬/林烽-大六壬经典案例解析-clean.txt`: extracted text from the clean modern PDF.
- Modify `daliuren_prompt.md`: add references to the compiled layers and require compiled-layer priority when available.
- Modify `daliuren_session.py`: include compiled-layer references in the emitted context payload.
- Modify `dongxuan_agent/rule_cards.py` or add a small knowledge loader: support layer-aware references in the context.
- Create/modify tests under `tests/test_prompt_policy.py`, `tests/test_session.py`, and any new knowledge-layer tests.

---

### Task 1: Audit Current 大六壬 Knowledge Pages

**Files:**
- Read: `/home/source/Documents/东玄知识库/wiki/topics/大六壬.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬指南-(2)-27c880de.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬古课考(1)-da74ca0d.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬心镜（整理版）-d868f798.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/五行大义-渊海子平-core-ocr-1e8c0e8e.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/林烽-大六壬经典案例解析-clean.md` once created

- [ ] **Step 1: Confirm the existing topic/source layout and identify which pages are already usable as compiled inputs**
- [ ] **Step 2: Identify which source pages are only raw summaries and which need new curated pages**
- [ ] **Step 3: Record the minimum set of pages needed to support the three-layer model**

### Task 2: Build 理法 Layer

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-理法.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/课体与三传.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/四课与类神.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/旺衰空亡与遁干.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/象理合参.md`

- [ ] **Step 1: Draft the top-level理法 page from《大六壬指南》**
- [ ] **Step 2: Split the理法 into small principle pages with one rule family per file**
- [ ] **Step 3: Add explicit source links and mark hard rules vs heuristics**

### Task 3: Build 象根 Layer

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-象根.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/十二天将象根.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/五行与十二支本义.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/类象边界.md`

- [ ] **Step 1: Extract symbol roots from《五行大义》and《六壬取象十二科》**
- [ ] **Step 2: Separate root meaning from later extended meaning**
- [ ] **Step 3: Add boundary notes that prevent fixed-symbol overreach**

### Task 4: Build Case Layer

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-案例总览.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/邵彦和-断案新编.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/牧夫占验.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/林烽-大六壬经典案例解析.md`

- [ ] **Step 1: Turn each book into an index page with major case themes**
- [ ] **Step 2: Create structured case cards with question, chart features, rationale, image, outcome, and technique**
- [ ] **Step 3: Mark direct exemplars vs analogy-only material**

### Task 5: Normalize the Modern Case PDF

**Files:**
- Read: `/home/source/Documents/东玄/大六壬/02.林烽-《大六壬经典案例解析》109页【666周易网：www.666zhouyi.com】.pdf`
- Read: `/home/source/Documents/东玄/大六壬/2433184671565302.林烽-《大六壬经典案例解析》109页.pdf`
- Create: `/home/source/Documents/东玄知识库/raw/notes/derived_pdf/大六壬/林烽-大六壬经典案例解析-clean.pdf`
- Create: `/home/source/Documents/东玄知识库/raw/notes/extracted/大六壬/林烽-大六壬经典案例解析-clean.txt`
- Create: `/home/source/Documents/东玄知识库/wiki/sources/林烽-大六壬经典案例解析-clean.md`

- [ ] **Step 1: Prefer the clean content-identical PDF as the indexing source**
- [ ] **Step 2: If needed, generate a dewatermarked derivative PDF from the cleanest available source**
- [ ] **Step 3: Extract text from the clean source only**
- [ ] **Step 4: Add a source page that records both archive and clean derivation paths**

### Task 6: Wire Compiled Layers Into Agent Context

**Files:**
- Modify: `daliuren_prompt.md`
- Modify: `daliuren_session.py`
- Modify: `dongxuan_agent/rule_cards.py` or a new loader module
- Create: tests for prompt/context parity

- [ ] **Step 1: Make compiled理法/象根/案例 pages the first-class runtime references**
- [ ] **Step 2: Keep raw source pages as fallback evidence**
- [ ] **Step 3: Make the emitted context surface the layer priority clearly**

---

## Self-Review

### Coverage Check

- 理法层 is covered by Task 2.
- 象根层 is covered by Task 3.
- 案例层 is covered by Task 4.
- Modern case normalization is covered by Task 5.
- Runtime wiring is covered by Task 6.

### Consistency Check

- Original PDFs stay intact.
- The clean modern case copy is used for indexing and extraction.
- The knowledge layers are separated by function, not by book title alone.

### Scope Check

This is one sub-project because all tasks serve the same runtime change: the 大六壬 agent should use layered knowledge rather than flat fixed象义.

