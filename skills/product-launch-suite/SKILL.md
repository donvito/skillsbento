---
name: product-launch-suite
description: "Generate a comprehensive product launch document suite. Use when the user wants to create launch materials, go-to-market plans, business strategy documents, competitive analysis, product roadmaps, partnership strategies, sales decks, or case study templates. Triggers on keywords like: product launch, go-to-market, GTM, launch plan, business strategy, competitive analysis, market sizing, TAM SAM SOM, sales deck, pitch deck, product roadmap, partnership strategy, case studies, launch suite, launch documents, launch kit. The user provides the product/company name and description; the skill produces 4 professional documents covering strategy, competitive analysis, roadmap, and sales materials."
---

# Product Launch Suite

Generate a complete set of product launch documents: Business Strategy, Competitive Analysis, Product Roadmap, and Sales Deck.

## Overview

This skill produces **4 documents** for any product launch:

| # | Document | Format | Description |
|---|----------|--------|-------------|
| 1 | Business & Market Strategy | .docx | Market sizing, personas, GTM, pricing, KPIs |
| 2 | Competitive Landscape & Feasibility | .docx | Competitors, SWOT, feasibility, risks |
| 3 | Product Roadmap & Partnerships | .docx | Roadmap, priorities, partnerships, integrations |
| 4 | Sales Deck & Case Studies | .pptx | Problem/solution, demo flow, case studies, CTA |

## Workflow

### Step 1: Gather Product Information

Collect from the user (ask if not provided):
- **Product/Company Name**: The name of the product being launched
- **Product Description**: What it does, who it's for, core value proposition
- **Target Market**: Industry, geography, customer segment
- **Stage**: Pre-launch, MVP, growth, expansion
- **Competitors** (optional): Known competitors to analyze
- **Pricing** (optional): Existing pricing or pricing ideas

If the user provides a URL, use `web_fetch` to pull product details from their website.

### Step 2: Research Phase

Conduct web research to gather real market data. This is critical for producing high-quality, data-backed documents rather than generic filler.

**Market Research:**
```
{product_category} market size 2024 2025
{product_category} TAM SAM SOM market sizing
{product_category} industry trends forecast
{target_market} buyer persona demographics
```

**Competitive Research:**
```
{product_category} competitors comparison
{competitor_name} pricing features reviews
{product_category} market share leaders
{competitor_name} strengths weaknesses
```

**Industry Research:**
```
{product_category} industry analysis
{product_category} barriers to entry
{product_category} trends technology
```

Use `web_search` for each query and `web_fetch` to read detailed pages. Aim for 8-15 searches to build a solid research foundation. Store findings in a structured research file before generating documents.

### Step 3: Generate Documents

Generate all 4 documents using the research gathered. Follow the detailed templates in the `references/` directory for each document.

**Document generation order:**
1. Business & Market Strategy (.docx) — foundational; informs the other documents
2. Competitive Landscape & Feasibility (.docx) — builds on market data
3. Product Roadmap & Partnerships (.docx) — uses competitive insights
4. Sales Deck & Case Studies (.pptx) — synthesizes everything into a pitch

**For Documents 1-3 (Word docs):**
- Read `/mnt/skills/public/docx/SKILL.md` for docx creation best practices
- Use `npm install -g docx` and JavaScript to generate
- Apply professional formatting: TOC, headers, tables, proper styling
- Use the document templates in `references/` for section structure and content guidance

**For Document 4 (Sales Deck):**
- Read `/mnt/skills/public/pptx/SKILL.md` and the pptxgenjs guide for slide creation
- Use `npm install -g pptxgenjs` and JavaScript to generate
- Apply bold, visually engaging design — NOT boring bullet slides
- Follow the slide template in `references/` for slide structure

### Step 4: Quality Assurance

**For .docx files:**
```bash
python /mnt/skills/public/docx/scripts/office/validate.py output.docx
```

**For .pptx file:**
```bash
python -m markitdown output.pptx  # Check content
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide  # Visual inspection
```

### Step 5: Deliver

Copy all 4 files to `/mnt/user-data/outputs/` and present them to the user.

Name files consistently:
- `{product_name}_Business_Strategy.docx`
- `{product_name}_Competitive_Analysis.docx`
- `{product_name}_Product_Roadmap.docx`
- `{product_name}_Sales_Deck.pptx`

---

## Document Templates

Detailed section-by-section templates for each document are in the `references/` directory:

| Template File | Document |
|---------------|----------|
| `references/doc1-business-strategy.md` | Business & Market Strategy |
| `references/doc2-competitive-analysis.md` | Competitive Landscape & Feasibility |
| `references/doc3-product-roadmap.md` | Product Roadmap & Partnerships |
| `references/doc4-sales-deck.md` | Sales Deck & Case Studies |

**Always read the relevant template before generating each document.**

---

## Styling Guidelines

### Word Documents (Docs 1-3)

- **Font**: Arial (body 11pt, headings 14-18pt)
- **Colors**: Use a professional accent color for headings and table headers (e.g., `2E5090` navy blue)
- **Tables**: Include shaded header rows, alternating row colors for readability
- **Spacing**: 1.15 line spacing, 6pt after paragraphs
- **Page setup**: US Letter, 1" margins
- **Structure**: Title page → Table of Contents → Sections with H1/H2/H3 hierarchy
- **Page numbers**: Footer with page numbers

### Sales Deck (Doc 4)

- **Layout**: 16:9 widescreen
- **Design**: Bold, modern — dark title slide, clean content slides
- **Color palette**: Choose colors that match the product's brand or industry
- **Typography**: Strong header font (e.g., Arial Black or Trebuchet MS) with clean body (Calibri)
- **Visuals**: Every slide needs a visual element — charts, icons, stat callouts, comparison tables
- **Slides**: 12-16 slides covering all sections

---

## Content Quality Standards

- **Use real data** from web research wherever possible (market sizes, growth rates, competitor info)
- **Be specific** — avoid vague statements; include numbers, percentages, timelines
- **Tailor to the product** — every section should reference the specific product, not read as generic
- **Provide actionable insights** — recommendations, priorities, next steps
- **Include placeholders clearly marked** with `[PLACEHOLDER: description]` for information that requires the user's specific input (e.g., internal financials, proprietary data)

---

## Single Document Mode

If the user asks for only one of the four documents, generate just that document. Follow the same research → generate → QA → deliver workflow but scoped to the single document.

---

## Dependencies

- `npm install -g docx` — Word document generation
- `npm install -g pptxgenjs` — PowerPoint generation
- `pip install "markitdown[pptx]" --break-system-packages` — Content verification
- LibreOffice — PDF conversion for visual QA
- Web search — Market and competitive research
