---
permalink: /
title: "Welcome!"
author_profile: true
---

I'm Fabian Polnitzky, and I am an astrophysicist, currently doing my PhD at RWTH Aachen University. I have a passion for space exploration and the universe. My work focuses on the distribution of gas and dust in the Milky Way Galaxy and the timescales of protoplanetary disc evolution and dispersion. My methods are Bayesian inference and machine learning, and I am interested in all-sky observations.

If you have any questions, feel free to reach out to me!

{% if site.posts.size > 0 %}
{% include base_path %}

## From my blog

<div class="grid__wrapper">
{% for post in site.posts limit: 3 %}
    {% include archive-single.html type="grid" %}
{% endfor %}
</div>

<p><a href="{{ base_path }}/blog/">All posts &rarr;</a></p>
{% endif %}
