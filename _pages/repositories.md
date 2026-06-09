---
layout: page
permalink: /repositories/
title: Research Artifacts
description: Code, models, and datasets released alongside my research.
nav: true
nav_order: 4
---

## Code Releases

{% if site.data.repositories.github_repos %}
<div class="repositories-grid">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
{% endif %}

## Models & Datasets

{% if site.data.repositories.huggingface_artifacts %}
<div class="repositories-grid">
  {% for artifact in site.data.repositories.huggingface_artifacts %}
    {% include repository/artifact.liquid artifact=artifact %}
  {% endfor %}
</div>
{% endif %}
