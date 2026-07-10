<h1 align="center">Hi, I'm Chen (KedoKudo) 👋</h1>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=17&duration=3200&pause=900&center=true&vCenter=true&repeat=true&width=640&height=28&color=F0F6FC&lines=Computational+Scientist+%40+Oak+Ridge+National+Laboratory;Neutron+Scattering+%C2%B7+AI+Research+%C2%B7+Scientific+Software;This+README+maintains+itself+with+an+agentic+AI+pipeline" />
    <img alt="Computational Scientist @ Oak Ridge National Laboratory — Neutron Scattering · AI Research · Scientific Software" src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=17&duration=3200&pause=900&center=true&vCenter=true&repeat=true&width=640&height=28&color=1F2328&lines=Computational+Scientist+%40+Oak+Ridge+National+Laboratory;Neutron+Scattering+%C2%B7+AI+Research+%C2%B7+Scientific+Software;This+README+maintains+itself+with+an+agentic+AI+pipeline" />
  </picture>
</p>

I work at the intersection of **neutron scattering science**, **AI research**, and **scientific software engineering** — building the software that turns raw neutron events into physics, and exploring how AI can accelerate the way we do science.

## 🔭 What I Do

- 🧲 **Neutron scattering** — data reduction and analysis software for neutron imaging and diffraction instruments at ORNL
- 🧠 **AI research** — applying foundation models and agentic systems to scientific workflows, from data reduction to automated analysis
- 🛠️ **Software engineering** — production scientific software in Python and C++, from detector event streams to user-facing analysis tools

## 🤖 Currently Exploring

<!-- AI-HIGHLIGHT:START -->
- Most of my energy right now is going into [NEREIDS](https://github.com/ornlneutronimaging/NEREIDS), where I'm building out neutron transmission fitting features like a bounded multiplicative baseline model, physics-complete Ikeda-Carpenter calibration, and TIFF preprocessing.
- I'm hardening the imaging pipeline's robustness — tackling dead-pixel detection for intermittent/hot pixels and chasing down subtle issues like baseline `E_ref` being computed on the full grid instead of the active fit window.
- I've been refining fitter flexibility, adding per-parameter freezing and support for joint `fit_energy_scale` and `fit_temperature` fitting with better `calibrate_energy` performance.
- On the maintenance side, I'm keeping [HyperCTui](https://github.com/ornlneutronimaging/HyperCTui) and [timepix_geometry_correction](https://github.com/ornlneutronimaging/timepix_geometry_correction) secure by triaging Grype CVE findings for Python 3.12.
<!-- AI-HIGHLIGHT:END -->

<sub>✨ This section is written by <a href="https://www.anthropic.com/claude">Claude</a> (`anthropic/claude-opus-4.8` via <a href="https://openrouter.ai">OpenRouter</a>), which reviews my recent public GitHub activity on a schedule and summarizes what I've been working on. See <a href="#%EF%B8%8F-how-this-profile-works">how this profile works</a>.</sub>

## 🚀 Featured Projects

**Neutron scattering**

- [Mantid](https://github.com/mantidproject/mantid) – Collaborative neutron and muon scattering analysis suite with global contributors.
- [iMars3D](https://github.com/ornlneutronimaging/iMars3D) – Neutron imaging reconstruction workflow powering instrument operations at ORNL.
- [mcpevent2hist](https://github.com/ornlneutronimaging/mcpevent2hist) – Transforms raw MCP detector events into analysis-ready histograms.
- [iBeatles](https://github.com/ornlneutronimaging/iBeatles) – Utility collection that streamlines neutron imaging beamline experiments.

**AI for science**

- [PLEIADES](https://github.com/lanl/PLEIADES) – LANL/ORNL research on scalable, AI-enhanced experimental workflows.
- [NEREIDS](https://github.com/ornlneutronimaging/NEREIDS) – MCP-enabled neutron imaging analysis with new resolution models for AI-assisted workflows.

## 🛠️ Toolbox

![](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![](https://img.shields.io/badge/C++-00599C?style=flat&logo=cplusplus&logoColor=white)
![](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)
![](https://img.shields.io/badge/CMake-064F8C?style=flat&logo=cmake&logoColor=white)
![](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)
![](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)
![](https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white)

![](https://img.shields.io/badge/Claude_Code-D97757?style=flat&logo=claude&logoColor=white)
![](https://img.shields.io/badge/OpenRouter-6566F1?style=flat&logoColor=white)
![](https://img.shields.io/badge/uv-DE5FE9?style=flat&logo=uv&logoColor=white)
![](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)

## 📊 GitHub Stats

<p align="center">
  <img src="assets/stats.svg" alt="GitHub snapshot showing followers, repository and star counts plus top languages." />
</p>

<p><sub>Last sync: Friday, July 10, 2026 at 7:10 AM CDT · 38 followers · 220 repos tracked (194 public) · 67 stars · Top languages: C++ (31.6%), Python (30.5%), HTML (24.8%), IGOR Pro (4.9%), Rust (2.4%), TypeScript (1.7%)</sub></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/KedoKudo/KedoKudo/output/github-snake-dark.svg" />
    <img alt="Snake animation eating my GitHub contribution graph" src="https://raw.githubusercontent.com/KedoKudo/KedoKudo/output/github-snake.svg" />
  </picture>
</p>

<p align="center"><sub>🐍 regenerated daily from my contribution graph by <a href="https://github.com/Platane/snk">Platane/snk</a></sub></p>

## ⚙️ How This Profile Works

This README is not edited by hand — it's the output of a small agentic pipeline that lives in this repo:

1. A scheduled **GitHub Action** runs [`scripts/update_profile.py`](scripts/update_profile.py) via [`uv`](https://docs.astral.sh/uv/) (zero-setup Python with [PEP 723](https://peps.python.org/pep-0723/) inline dependencies) to pull live stats from the GitHub API and render this page from a template.
2. On a weekly cadence, [`scripts/ai_highlight.py`](scripts/ai_highlight.py) feeds my recent public activity to **Claude** through [OpenRouter](https://openrouter.ai) (model-agnostic — one env var swaps the LLM) and lets it write the *Currently Exploring* section above.
3. The pipeline itself was built and is maintained with [**Claude Code**](https://claude.com/claude-code) — the same agentic tooling I use day-to-day for scientific software development.

## 📫 Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/chen-z-5a081725/)
[![Google Scholar](https://img.shields.io/badge/Google%20Scholar-Profile-blue?style=flat&logo=google-scholar)](https://scholar.google.com/citations?user=aPdsom8AAAAJ&hl=en)
[![ORNL](https://img.shields.io/badge/ORNL-Profile-orange?style=flat&logo=atom)](https://www.ornl.gov/staff-profile/chen-zhang)
[![ORCID](https://img.shields.io/badge/ORCID-Profile-green?style=flat&logo=orcid)](https://orcid.org/0000-0001-8374-4467)

<sub>Last updated on Friday, July 10, 2026 at 7:10 AM CDT.</sub>
