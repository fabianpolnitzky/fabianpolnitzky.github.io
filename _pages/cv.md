---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

<a href="{{ base_path }}/files/CV.pdf" class="btn btn--primary" target="_blank" rel="noopener">Download CV as PDF</a>

Scientific Summary
======
I am working on **Bayesian inference** and **machine learning** methods and their applications in Astrophyics. Currently, I work on the **distribution of gas and dust** and their correlation in the **Milky Way** as part of the [mw-atlas](https://mw-atlas.eu/) project, where I am using methods of **Information Field Theory** to reconstruct the spatial structure of our home galaxy. Furthermore, I work on the timescales of **protoplanetary disc evolution and dispersion**. From the observational side, I have experience with **all-sky observations** from optical, infrared to radio surveys.

Education
======
* **PhD** at RWTH Aachen University<br>
  Supervised by *Philipp Mertsch*<br>
  10.2025 - 

* **Master Astronomy** at the University of Vienna<br> 
  Master Thesis *Disk evolution in a single star forming region* supervised by *João Alves*, passed with honours<br>
  10.2023 - 08.2025

* **Bachelor Astronomy** at the University of Vienna<br>
  Bachelor Thesis *Revisiting the ages of circumstellar disks* supervised by *João Alves*, passed with honours<br>
  10.2019 - 07.2023

* **Bachelor Physics** at the University of Vienna<br>
  Bachelor Thesis *Simulation and optimisation of microstrip antennas for propagating spin wave spectroscopy* supervised by *Andrii Chumak*, passed with honours<br>
  10.2019 - 09.2023

Work experience
======
* **Research Assistant** at RWTH Aachen University in the group of *Philipp Mertsch*<br>
  10.2025 - 

* **Research Internship** at the European Southern Observatory<br>
  Automatic classification of young stellar objects' light curves under the supervision of *Amelia Bayo* and *Paula Sánchez Sáez*<br>
  03.2025 - 05.2025

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>

Skills
======
* **Programming**
  * **Python** - Proficient
  * **Bash** - Intermediate
  * **HPC** and **Slurm Workload Manager** - Intermediate
  * **Git** - Intermediate
  * **SQL** - Intermediate
  * **TopCat** - Intermediate
  * **Aladin, SAOImage DS9** - Beginner

* **Language**
  * **German** - Native
  * **English** - B2
  * **Spanish** - A1
  * **Japanese** - A1

* **Observations**<br>
  Approved operator of the **Vienna Little Telescope** of the Department of Astrophysics, University of Vienna
  
Talks and Posters
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html  %}
  {% endfor %}</ul>

Summer Schools
======
* **ESO Summer School: Writing and Communicating your Science** in Munich, Germany, from 20th to 24th of July 2026
  
Teaching
======
  {% for post in site.teaching reversed %}
  <div class="archive__item">
    <h2 class="archive__item-title teaching__item-title">{{ post.title }}</h2>
    <p class="archive__item-excerpt">{{ post.type }}, {{ post.venue }}, {{ post.location }}</p>
    <div class="archive__item-body">
      {{ post.content | markdownify }}
    </div>
  </div>
{% endfor %}
  
Scholarships
======
**Merit Scholarship** of the University of Vienna awarded every year from 2020 to 2025

Extracurricular Experience
======
**Elected student representative** for Astronomy at the University of Vienna from July 2021 to June 2025