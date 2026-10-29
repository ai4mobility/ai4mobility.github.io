# Labs

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility</div>
  <h2>Hands-On Labs <span>Every Notebook in the Course</span></h2>
  <p>One page for all the labs &mdash; what each one builds, what it actually proves, and what to compare it against before you believe the result. Everything runs in Google Colab; nothing needs a local install.</p>
  <div class="resource-meta">
    <span>8 notebooks available now</span>
    <span>7 more planned for Modules 2&ndash;7</span>
    <span>Open data throughout</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>How to use this page.</strong> The labs are where the reading turns into something you have done yourself, and together with the notebook exercises they carry 40% of the course grade. Each entry below names the section of the notes it belongs with, so you can read first and run second &mdash; or run first and read to find out why the result looked the way it did. Open a lab from this page, or use the rocket icon at the top right of any notebook to launch it straight into Colab. Labs that need hardware are marked; those use instructor-provided equipment listed on the <a href="hardware.html">Hardware for Class</a> page.</p>
</div>

<section class="resource-section" id="at-a-glance">
  <div class="resource-section-header">
    <h2>All Labs at a Glance</h2>
    <span>Modules 1&ndash;7</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th style="width:30%">Lab</th>
          <th style="width:15%">Module</th>
          <th style="width:40%">What it proves</th>
          <th style="width:15%">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><a href="module1/lab1.html">1 &mdash; Python and ML warmup</a></td><td>M1</td><td>You can run the supervised-learning pipeline end to end on traffic data</td><td>Available</td></tr>
        <tr><td><a href="module1/lab2_word_embeddings.html">2 &mdash; From Word2Vec to Road2Vec</a></td><td>M1</td><td>Representation learning is not about language &mdash; and a free baseline may match it</td><td>Available</td></tr>
        <tr><td><a href="module1/lab3_image_embeddings.html">3 &mdash; Image embeddings with a deep CNN</a></td><td>M1</td><td>Transfer learning in its simplest useful form</td><td>Available</td></tr>
        <tr><td><a href="module1/lab4_clip_vs_traditional_cv.html">4 &mdash; CLIP vs. traditional computer vision</a></td><td>M1</td><td>Why open-vocabulary perception matters for long-tail safety scenes</td><td>Available</td></tr>
        <tr><td><a href="module1/notes3-cnn.html#newell-lwr">Learning the CTM update</a></td><td>M1</td><td>A convolution kernel carries a reaction time and a wave speed</td><td>Companion available</td></tr>
        <tr><td>Cross-attention sanity check</td><td>M2</td><td>Attention heads route; they are not the tidy alignment maps papers suggest</td><td>In development</td></tr>
        <tr><td><a href="module3/lab5_graph_attention.html">5 &mdash; Attention on a road network</a></td><td>M3</td><td>Attention earns its parameters only where the weighting is unknown &mdash; and structure beats weighting</td><td>Available</td></tr>
        <tr><td><a href="module3/lab8_agency_graph.html">8 &mdash; Building a graph from agency documents</a></td><td>M3</td><td>A table already is an edge list; prose needs a model, and the model&rsquo;s edges need checks and a labeled sample</td><td>Available</td></tr>
        <tr><td><a href="module4/lab7_four_answers.html">7 &mdash; Four ways to predict the next 5 seconds</a></td><td>M4</td><td>Regression, a VAE, a translator and diffusion learn from the same pairs; squared error alone returns the average, and diffusion uses it to draw real futures</td><td>Available</td></tr>
        <tr><td>VAE on traffic state heatmaps</td><td>M4</td><td>What a narrow bottleneck chooses to keep, and what it throws away</td><td>In development</td></tr>
        <tr><td>From VAE to diffusion</td><td>M4</td><td>Diffusion as a response to measured VAE failures, not an assertion</td><td>In development</td></tr>
        <tr><td>Training the denoiser</td><td>M4</td><td>What the network predicts at each noise level, and why</td><td>In development</td></tr>
        <tr><td>An agent that tunes a signal plan</td><td>M5</td><td>What you show an agent in a tool's output changes how often it breaks the rules</td><td>In development</td></tr>
        <tr><td><a href="module6/lab6_vit_finetune.html">6 &mdash; Fine-tuning a vision transformer</a></td><td>M6</td><td>Where the accuracy in a fine-tune actually comes from &mdash; and how little of it survives sunset</td><td>Available</td></tr>
        <tr><td>Fine-tuning a small language model on crash narratives</td><td>M6</td><td>Whether LoRA beats prompting and retrieval on a split you can defend</td><td>In development</td></tr>
        <tr><td>Reviewing an agent&rsquo;s work</td><td>M7</td><td>Which agent failures a human reviewer would actually have caught</td><td>In development</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="resource-section" id="module1-labs">
  <div class="resource-section-header">
    <h2>Available Now</h2>
    <span>Modules 1, 3, 4 and 6</span>
  </div>
  <p class="section-intro">Eight notebooks, all runnable in Colab on open or synthetic data. Read each one alongside the notes section named on its card &mdash; the notebook shows the thing working, the section says why it works and where it stops working.</p>
  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>Lab 1 &mdash; Python and ML Warmup</h3>
      <p>Generate a synthetic traffic-flow dataset, plot the Greenshields fundamental diagram, then fit and evaluate a simple model on a held-out split. Light on purpose: it confirms your environment works and puts the supervised-learning pipeline &mdash; data &rarr; model &rarr; loss &rarr; optimization &rarr; evaluation &mdash; back in your hands on a curve you already know how to read.</p>
      <p><strong>Proves:</strong> you can execute the pipeline end to end. <strong>Check it against:</strong> the physics &mdash; does the fitted relationship behave sensibly at free flow and near jam density, or only on average?</p>
      <div class="tag-row"><span>Reads with 1.1, 1.2</span><span>numpy &middot; pandas &middot; scikit-learn</span><span>Synthetic data</span></div>
      <a class="resource-link" href="module1/lab1.html">Open Lab 1</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 2 &mdash; From Word2Vec to Road2Vec</h3>
      <p>Write skip-gram with negative sampling from scratch in numpy, train it on a small corpus and watch analogy structure appear &mdash; then hand the <em>same trainer</em> random walks over the real road network around USF Tampa. Intersection embeddings do recover functional class without ever seeing the labels.</p>
      <p><strong>Proves:</strong> representation learning is not about language. <strong>Check it against:</strong> plain latitude and longitude, which recover it just as well &mdash; because a uniform random walk mostly encodes <em>where</em> a place is, not <em>what it does</em>. Evaluating a representation against a free baseline is what the lab is really teaching.</p>
      <div class="tag-row"><span>Reads with 1.5</span><span>numpy &middot; matplotlib only</span><span>Runs offline</span></div>
      <a class="resource-link" href="module1/lab2_word_embeddings.html">Open Lab 2</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 3 &mdash; Image Embeddings with a Deep CNN</h3>
      <p>Load a pretrained ResNet-50, visualize what the layers respond to as depth increases &mdash; edges, then textures, then parts, then objects &mdash; extract 2048-dimensional embeddings for a handful of roadway images, and check that semantically similar scenes land near each other.</p>
      <p><strong>Proves:</strong> transfer learning in its simplest useful form &mdash; you are reusing a representation you did not pay to train. <strong>Check it against:</strong> the pairs you predicted would be closest before you ran it; the ones that surprise you are the finding.</p>
      <div class="tag-row"><span>Reads with 1.3, 1.4</span><span>torch &middot; torchvision &middot; scikit-learn</span><span>Downloads images</span></div>
      <a class="resource-link" href="module1/lab3_image_embeddings.html">Open Lab 3</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Lab 4 &mdash; CLIP vs. Traditional Computer Vision</h3>
      <p>Compare a closed-set classifier with a CLIP-style multimodal model on roadway and dashcam-style scenes. Run zero-shot recognition against open-vocabulary prompts &mdash; a flooded roadway, a construction work zone, a pedestrian crossing at night &mdash; then push on prompt phrasing until the model breaks.</p>
      <p><strong>Proves:</strong> why open-vocabulary perception matters for long-tail safety scenarios that never appear in an ImageNet-style label set &mdash; and how brittle prompt phrasing can be. <strong>Check it against:</strong> the closed-set classifier on the same images, including the scenes neither model has a label for.</p>
      <div class="tag-row"><span>Reads with 1.5</span><span>torch &middot; transformers</span><span>Bridge into Module 2</span></div>
      <a class="resource-link" href="module1/lab4_clip_vs_traditional_cv.html">Open Lab 4</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 3</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Lab 5 &mdash; Attention on a Road Network</h3>
      <p>Build one message-passing layer with six interchangeable aggregators and run it against two ground-truth traffic rules taken from flow theory. Four aggregators are generic; two of them encode what a traffic engineer already knows &mdash; that a queue backs up from downstream, that arriving flow comes from upstream. Those two are the real competition, and they cost no extra parameters.</p>
      <p><strong>Proves:</strong> attention wins only where the weighting is genuinely unknown &mdash; and even there, knowing <em>which</em> neighbours to listen to is worth more than learning <em>how much</em> to weight them. <strong>Check it against:</strong> not the mean aggregator, which anything beats, but the fixed aggregator carrying your own domain knowledge. On the spillback rule it ties attention at half the parameters and a third of the seed variance.</p>
      <div class="tag-row"><span>Reads with 3.6 and 3.7</span><span>numpy &middot; torch &middot; matplotlib</span><span>Runs offline &middot; ~3 min</span></div>
      <a class="resource-link" href="module3/lab5_graph_attention.html">Open Lab 5</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 3</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 8 &mdash; Building a Graph from Agency Documents</h3>
      <p>Turn two real hurricane documents into one typed graph: FDOT District 7&rsquo;s traffic-signal SOP (the plan) and Sarasota County&rsquo;s 2024 after-action report (what happened). Read the AAR&rsquo;s responsibility matrix straight into edges, merge the many names of one organization, split the SOP into steps by phase, and pull edges out of the prose twice: with a co-occurrence baseline and with Claude given a fixed schema. Every edge keeps its page and the exact quote behind it.</p>
      <p><strong>Proves:</strong> structure is cheap and prose is expensive. Claude finds 84% of the labeled links, and 79% of the links it reports are right, where the baseline is wrong more than half the time. Yet the automatic checks remove no wrong edge on the labeled pages: only a labeled sample tells you the reading is right. <strong>Check it against:</strong> the co-occurrence baseline, a 67-edge gold set on four pages, and a second, independent model run (the two share 138 of their 175 distinct edges).</p>
      <div class="tag-row"><span>Reads with 3.1</span><span>pdfplumber &middot; networkx &middot; pandas</span><span>Downloads 4 MB &middot; under a minute &middot; no API key</span></div>
      <a class="resource-link" href="module3/lab8_agency_graph.html">Open Lab 8</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 4</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 7 &mdash; Four Ways to Predict the Next 5 Seconds</h3>
      <p>A simulated intersection where each driver picks left, straight or right by a logit rule you can read, and a referee that re-runs every car 200 times from the same moment, so you know what really could happen next. Train regression, a conditional VAE, a word-by-word translator and diffusion on the same 20,000 trajectories with the same encoder design and the same training budget, and score all four on one card.</p>
      <p><strong>Proves:</strong> squared error alone returns the <em>average</em> future &mdash; 22.5% of regression&rsquo;s paths leave the pavement &mdash; while diffusion, trained with the same kind of loss plus a noisy draft of the answer as an extra input, draws futures that almost never do (0.2%). Run with a single pass, diffusion <em>is</em> regression. <strong>Check it against:</strong> constant velocity, a perfect model built from the referee, and the tuned VAE, which ties diffusion on the movement mix at one pass per future instead of 25 but leaves the road about ten times as often.</p>
      <div class="tag-row"><span>Reads with 4.6, 4.8</span><span>numpy &middot; torch &middot; matplotlib</span><span>Runs offline &middot; ~20 min on CPU, or load the 3.6 MB weights</span></div>
      <a class="resource-link" href="module4/lab7_four_answers.html">Open Lab 7</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 6</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 6 &mdash; Fine-tuning a Vision Transformer</h3>
      <p>2,949 snapshots from 494 FDOT traffic cameras around Tampa Bay, swept every 25 minutes straight through sunset. Turn the transfer dial you saw on the Sept 10 slides &mdash; head only, last block, last four blocks, everything &mdash; on a 5.5M-parameter ViT-Tiny, and watch what each setting costs and buys. The labels came from a detector, not a person, and the lab spends its last three sections on what that costs you.</p>
      <p><strong>Proves:</strong> a fine-tune's accuracy splits cleanly into what the pretrained features gave you for free and what you had to buy by unfreezing &mdash; and that an after-dark score can rise while the model gets worse, because the label source failed first. <strong>Check it against:</strong> twelve hand-written image statistics and a logistic regression, which scores 37.7% where the full fine-tune scores 71.2%.</p>
      <div class="tag-row"><span>Reads with 2.7, 6.1</span><span>torch &middot; timm &middot; scikit-learn &middot; matplotlib</span><span>Downloads 31 MB &middot; ~15 min on CPU</span></div>
      <a class="resource-link" href="module6/lab6_vit_finetune.html">Open Lab 6</a>
    </article>
  </div>
  <div class="placeholder-panel">
    <p><strong>Lab 4 is also the bridge into Module 2.</strong> It lives here because it is built from Module 1's embedding material, but the shared image&ndash;text space it constructs is what the vision-language section of <a href="module2/index.html">Module 2</a> assumes you already have. If you arrive at Module 2 without having run it, run it first.</p>
  </div>
</section>

<section class="resource-section" id="coming-later">
  <div class="resource-section-header">
    <h2>Coming Later in the Course</h2>
    <span>Modules 2&ndash;7</span>
  </div>
  <p class="section-intro">These are described on each module page and released as the semester reaches them. They are listed here so you can see the arc &mdash; and so that if one of them is close to your capstone, you can start early rather than waiting for the week it is assigned.</p>
  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 2</p><span class="status-tag status-closed">In development</span></div>
      <h3>Transformers, LLMs, and Multimodal Models</h3>
      <p><strong>Cross-attention sanity check.</strong> Build a small cross-attention model on paired mobility data, then run a three-tier check: does the model learn the task, does attention concentrate where the physics says it should, and does that interpretation survive a control condition? Useful corrective before you read your next attention visualization.</p>
      <a class="resource-link" href="module2/index.html">Module 2</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 4</p><span class="status-tag status-closed">In development</span></div>
      <h3>Deep Generative Models</h3>
      <p><strong>VAE on traffic state heatmaps</strong> &mdash; read the latent space of a model trained on cell-transmission speed fields. <strong>From VAE to diffusion</strong> &mdash; measure where the VAE breaks on that same data before reaching for diffusion. <strong>Training the denoiser</strong> &mdash; build it in numpy and answer what the network is really predicting at each noise level.</p>
      <a class="resource-link" href="module4/index.html">Module 4</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 5</p><span class="status-tag status-closed">In development</span></div>
      <h3>Understanding AI Agents</h3>
      <p><strong>An agent that tunes a signal plan.</strong> Build a small agent loop that adjusts the timing of one intersection through SUMO tools. Run it with and without the timing limits shown in the tool&rsquo;s output, count the plans that break them, then add a checkpoint before any plan is applied.</p>
      <a class="resource-link" href="module5/index.html">Module 5</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 6</p><span class="status-tag status-closed">In development</span></div>
      <h3>Evaluation and Fine-Tuning</h3>
      <p><strong>Fine-tuning a small language model on crash narratives.</strong> Use LoRA to teach a small open model to turn crash narratives into structured fields, and compare it with prompting alone and with retrieval on a split you can defend.</p>
      <a class="resource-link" href="module6/index.html">Module 6</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 7</p><span class="status-tag status-closed">In development</span></div>
      <h3>Agents and People in an Agency</h3>
      <p><strong>Reviewing an agent&rsquo;s work.</strong> Work through recorded agent runs on transportation tasks, find the failures, decide which a human reviewer would have caught, and design where the approvals go. The runs are recorded in advance, so nothing needs an API key.</p>
      <a class="resource-link" href="module7/index.html">Module 7</a>
    </article>
  </div>
</section>

<section class="resource-section" id="running-a-lab">
  <div class="resource-section-header">
    <h2>Running a Lab</h2>
    <span>Setup, and what you are expected to know</span>
  </div>
  <div class="placeholder-panel">
    <p><strong>In Colab, there is nothing to install.</strong> Open any notebook page and use the rocket icon at the top right to launch it in Google Colab, or download the <code>.ipynb</code> and run it locally. Running locally means installing the packages each lab names in its first setup cell; the notebooks keep those lists short and each one states its dependencies before it uses them.</p>
    <p><strong>Two of the four run without a network.</strong> Lab 1 generates its own data and Lab 2 needs only numpy and matplotlib. Labs 3 and 4 download pretrained model weights and sample images, so run them where you have a connection.</p>
    <p><strong>You are not expected to write code unaided.</strong> The prerequisite is being able to read Python, run a cell, and say what the output means &mdash; not writing a training loop from memory. Where you use an AI assistant on lab code, the course's expectation is the one in the <a href="syllabus.html">syllabus</a>: you can explain every line you hand in. The <a href="prerequisites.html">prerequisites</a> page has the setup details and the refresher material.</p>
    <p><strong>Hardware is for projects.</strong> No lab on the current schedule needs hardware. Capstone projects that do use instructor-provided equipment &mdash; Jetsons, cameras, and the comma devices on the <a href="hardware.html">Hardware for Class</a> page. No personal vehicle is used for any lab or project, and any project that collects identifiable data needs IRB approval before collection starts.</p>
  </div>
</section>

<section class="resource-section" id="evaluating">
  <div class="resource-section-header">
    <h2>Before You Trust a Lab Result</h2>
    <span>The habit every lab is built around</span>
  </div>
  <p class="section-intro">Every notebook in this course produces something that looks like a result. The point of the lab is not the number &mdash; it is whether the number survives three questions, the same three that decide whether you would put a system on a pole or in front of a review board.</p>
  <div class="placeholder-panel">
    <p><strong>What is the baseline?</strong> Not "no model" &mdash; the cheap, tuned, classical thing a colleague would do instead. Latitude and longitude in Lab 2. A Webster or properly tuned actuated plan in the SUMO agent lab. Prompting alone in the crash-narrative fine-tuning lab. A result that does not beat its baseline is a finding, and worth reporting as one.</p>
    <p><strong>How was the data split, and is that split honest?</strong> Random splits flatter models on data with structure &mdash; consecutive frames of the same video, repeated days at the same station, trips by the same driver. Ask whether anything in your test set could have been memorized from your training set.</p>
    <p><strong>What happens on the ugly cases?</strong> Night, rain, occlusion, work zones, the scene with no label for it. Aggregate accuracy hides exactly the cases that matter for safety, and those are the ones a vendor demo will not show you.</p>
  </div>
</section>
