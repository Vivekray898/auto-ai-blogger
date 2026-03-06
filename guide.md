You are a **professional AI software engineer** tasked with designing and implementing a **fully automated multi-agent AI blogging system** in Python. Build it as if you are producing production-grade code for a professional SEO content automation platform. The system must be **fully modular, maintainable, scalable, and distributed**, with proper failover mechanisms. It should integrate **free or low-cost AI models**, **free image APIs**, **WordPress publishing**, and modern SEO best practices.  

The system should have the following **agents and responsibilities**:

1. **Scraper & Outline Agent**
   - Scrape topics and competitor URLs from DuckDuckGo, Reddit, Quora.
   - Extract headings, bullet points, and FAQs.
   - Convert messy scraped content into a **structured outline** with H1, H2, H3.
   - Model: OpenAI o3-mini / o1-mini (Reasoning-focused)
   - Handle noisy input gracefully.

2. **Writer Agent**
   - Generate **long-form content** for each section of the outline.
   - Use **distributed AI models** to avoid hitting free usage limits:
       - Primary: Gemini 1.5 Pro / Flash
       - Secondary/Fallback: Cerebrium GPT OSS 120B
   - Maintain consistency and coherence with the outline and research notes.
   - Section-based generation for large context support.

3. **Content Gap & SEO Agent**
   - Compare the draft with top competitor content.
   - Detect missing information, FAQs, or relevant points.
   - Optimize content for **RankMath SEO fields**:
       - Focus keyword, meta description, slug, internal links, FAQ schema.
   - Models: Llama 3.3 70B / Qwen 3 32B (Groq) or Cohere Command R as alternative.

4. **AI Detection / Rewrite Agent**
   - Scan the draft to detect AI-generated patterns.
   - Rewrites unnatural/robotic sentences into **human-like language**.
   - Ensure content is **plagiarism-free, readable, and natural**.
   - Model: GPT-4.1 / GPT-5-chat.

5. **Image & Publisher Agent**
   - Fetch **contextual images** from free APIs (Unsplash / Pexels) for each section and featured image.
   - Automatically post the blog to WordPress via REST API.
   - Include SEO metadata, featured image, categories, and tags.
   - Model: Llama 3.1 8B (Groq) for fast automation tasks.

---

### System Requirements:

- **Programming Language:** Python 3.11+
- **Pipeline:** Modular, JSON-based data passing between agents.
- **Distributed Execution:** Each agent can run independently; failover if a model or API fails.
- **Error Handling:** Automatic retries for failed API calls or model failures.
- **Parallelization:** Section-based content generation in parallel where possible.
- **Scalability:** Able to handle 20–50 posts per day.
- **SEO:** Generate RankMath-compatible metadata automatically.
- **Content Safety:** Includes AI-detection avoidance and plagiarism minimization.
- **Logging & Monitoring:** Track each agent’s execution and errors for debugging.

---

### Implementation Instructions for AI:

1. Create **separate Python modules/files** for each agent (scraper, writer, SEO, rewrite, image/publisher).  
2. Implement a **main orchestrator script** that:
   - Collects scraped data
   - Passes it through the pipeline
   - Handles distributed agent execution
   - Manages fallbacks and retries
   - Publishes the final blog post to WordPress  
3. Use **modern Python practices**: type hints, modular functions, docstrings, exception handling.
4. Include **examples for configuration** (API keys, endpoints, model selection).  
5. Use **section-based AI calls** to handle large articles efficiently.  
6. Provide **fallback logic** for every agent:
   - If primary AI fails → secondary AI → fallback static template or log warning.  
   - If image API fails → try alternative API.
7. Provide **async or threading support** to allow parallel section generation for speed.
8. Include **logging**, so each step can be monitored.
9. Provide **sample output** in HTML for WordPress with headings, paragraphs, images, and SEO metadata ready to be inserted.
10. Add **configurable parameters** for:
    - Number of posts per day
    - API keys / tokens
    - List of distributed AI agents
    - Scraping depth / number of competitor pages

---

### Output Requirements:

- Provide a **full folder structure**, e.g.:


auto_ai_blogger/
│
├── agents/
│ ├── scraper_outline.py
│ ├── writer_agent.py
│ ├── content_gap_seo.py
│ ├── rewrite_agent.py
│ ├── image_publisher.py
│
├── orchestrator.py
├── config.py
├── utils.py
├── requirements.txt
└── README.md


- Each module must be **self-contained** with functions, reusable, and documented.
- Include **example usage** in orchestrator.py that runs **one full blog cycle**.
- The code should **run without errors**, using free-tier models/APIs, and simulate agent fallback logic.

---

### Extra Instructions:

- Use **DuckDuckGo scraping instead of Google SERP** to avoid paid API limits.
- Use **section-based distributed AI writing** to reduce per-agent token usage.
- Include **content gap detection logic** using embeddings (sentence-transformers or open-source alternatives).
- Integrate **RankMath SEO fields** in WordPress post automatically.
- Make sure **final content is human-readable**, well-formatted, and passes basic AI-detection tools.

---

**Goal:** At the end of execution, the orchestrator should take scraped topics and competitor pages and output a **fully polished, SEO-optimized, human-like blog post with images**, published automatically to WordPress, with **distributed AI models and full failover logic** built in.  

**Do not skip any agent or step. Use modern methods, distributed AI, fallbacks, and SEO best practices. Output code and folder structure in one go as a professional developer would.**