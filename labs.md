# Labs

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility</div>
  <h2>Hands-On Labs <span>Every Notebook in the Course</span></h2>
  <p>One page for all the labs &mdash; what each one builds, what it actually proves, and what to compare it against before you believe the result. Everything runs in Google Colab; nothing needs a local install.</p>
  <div class="resource-meta">
    <span>4 notebooks available now</span>
    <span>15 more planned for Modules 2&ndash;8</span>
    <span>Open data throughout</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>How to use this page.</strong> The labs are where the reading turns into something you have done yourself, and together with the notebook exercises they carry 40% of the course grade. Each entry below names the section of the notes it belongs with, so you can read first and run second &mdash; or run first and read to find out why the result looked the way it did. Open a lab from this page, or use the rocket icon at the top right of any notebook to launch it straight into Colab. Labs that need hardware are marked; those use instructor-provided equipment listed on the <a href="hardware.html">Hardware for Class</a> page.</p>
</div>

<section class="resource-section" id="at-a-glance">
  <div class="resource-section-header">
    <h2>All Labs at a Glance</h2>
    <span>Modules 1&ndash;8</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th style="width:30%">Lab</th>
          <th style="width:15%">Module &amp; session</th>
          <th style="width:40%">What it proves</th>
          <th style="width:15%">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><a href="module1/lab1.html">1 &mdash; Python and ML warmup</a></td><td>M1 &middot; Sept 3</td><td>You can run the supervised-learning pipeline end to end on traffic data</td><td>Available</td></tr>
        <tr><td><a href="module1/lab2_word_embeddings.html">2 &mdash; From Word2Vec to Road2Vec</a></td><td>M1 &middot; Sept 10</td><td>Representation learning is not about language &mdash; and a free baseline may match it</td><td>Available</td></tr>
        <tr><td><a href="module1/lab3_image_embeddings.html">3 &mdash; Image embeddings with a deep CNN</a></td><td>M1 &middot; Sept 3 &amp; 10</td><td>Transfer learning in its simplest useful form</td><td>Available</td></tr>
        <tr><td><a href="module1/lab4_clip_vs_traditional_cv.html">4 &mdash; CLIP vs. traditional computer vision</a></td><td>M1 &middot; Sept 10</td><td>Why open-vocabulary perception matters for long-tail safety scenes</td><td>Available</td></tr>
        <tr><td>Cross-attention sanity check</td><td>M2 &middot; Sept 17</td><td>Attention heads route; they are not the tidy alignment maps papers suggest</td><td>In development</td></tr>
        <tr><td>VAE on traffic state heatmaps</td><td>M3 &middot; Sept 24</td><td>What a narrow bottleneck chooses to keep, and what it throws away</td><td>In development</td></tr>
        <tr><td>From VAE to diffusion</td><td>M3 &middot; Sept 24</td><td>Diffusion as a response to measured VAE failures, not an assertion</td><td>In development</td></tr>
        <tr><td>Training the denoiser</td><td>M3 &middot; Nov 19</td><td>What the network predicts at each noise level, and why</td><td>In development</td></tr>
        <tr><td>A retrieval assistant over transportation documents</td><td>M4 &middot; Oct 1</td><td>When a RAG answer is wrong, retrieval usually failed &mdash; not the model</td><td>In development</td></tr>
        <tr><td>An agentic workflow for a recurring task</td><td>M4 &middot; Oct 8</td><td>An agent is only as good as the verification step you designed</td><td>In development</td></tr>
        <tr><td>Vehicle detection and tracking</td><td>M5 &middot; Oct 15</td><td>Count error against manual ground truth, not mAP</td><td>In development</td></tr>
        <tr><td>Deploy it to the edge <em>(hardware)</em></td><td>M5 &middot; Oct 22</td><td>What quantization costs in accuracy and buys in latency and power</td><td>In development</td></tr>
        <tr><td>Reading a production driving stack <em>(hardware)</em></td><td>M6 &middot; Oct 29</td><td>What a deployed ADAS is doing, and how you would know if it were doing it badly</td><td>In development</td></tr>
        <tr><td>A lane-keeping policy from camera images</td><td>M6 &middot; Oct 29</td><td>The failure cases that look fine on aggregate metrics</td><td>In development</td></tr>
        <tr><td>Learning the CTM update</td><td>M7 &middot; Nov 5</td><td>A convolution kernel carries a reaction time and a wave speed</td><td>Companion available</td></tr>
        <tr><td>RL signal control in SUMO</td><td>M7 &middot; Nov 5</td><td>The tuned actuated baseline is the comparison that deflates the result</td><td>In development</td></tr>
        <tr><td>Sensor simulation in CARLA</td><td>M7 &middot; Nov 5</td><td>What a simulator systematically fails to represent</td><td>In development</td></tr>
        <tr><td>Surrogate safety from video</td><td>M8 &middot; Nov 12</td><td>What would have to be true for TTC and PET to predict crashes here</td><td>In development</td></tr>
        <tr><td>An agency document workflow</td><td>M8 &middot; Nov 12</td><td>End-to-end time including your verification, against doing it by hand</td><td>In development</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="resource-section" id="module1-labs">
  <div class="resource-section-header">
    <h2>Available Now</h2>
    <span>Module 1 &middot; Foundations and Representation Learning</span>
  </div>
  <p class="section-intro">Four notebooks, all runnable in Colab on open or synthetic data. Read them alongside the Module 1 sections named on each card &mdash; the notebook shows the thing working, the section says why it works and where it stops working.</p>
  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1 &middot; Sept 3</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>Lab 1 &mdash; Python and ML Warmup</h3>
      <p>Generate a synthetic traffic-flow dataset, plot the Greenshields fundamental diagram, then fit and evaluate a simple model on a held-out split. Light on purpose: it confirms your environment works and puts the supervised-learning pipeline &mdash; data &rarr; model &rarr; loss &rarr; optimization &rarr; evaluation &mdash; back in your hands on a curve you already know how to read.</p>
      <p><strong>Proves:</strong> you can execute the pipeline end to end. <strong>Check it against:</strong> the physics &mdash; does the fitted relationship behave sensibly at free flow and near jam density, or only on average?</p>
      <div class="tag-row"><span>Reads with 1.1, 1.2</span><span>numpy &middot; pandas &middot; scikit-learn</span><span>Synthetic data</span></div>
      <a class="resource-link" href="module1/lab1.html">Open Lab 1</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1 &middot; Sept 10</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 2 &mdash; From Word2Vec to Road2Vec</h3>
      <p>Write skip-gram with negative sampling from scratch in numpy, train it on a small corpus and watch analogy structure appear &mdash; then hand the <em>same trainer</em> random walks over the real road network around USF Tampa. Intersection embeddings do recover functional class without ever seeing the labels.</p>
      <p><strong>Proves:</strong> representation learning is not about language. <strong>Check it against:</strong> plain latitude and longitude, which recover it just as well &mdash; because a uniform random walk mostly encodes <em>where</em> a place is, not <em>what it does</em>. Evaluating a representation against a free baseline is what the lab is really teaching.</p>
      <div class="tag-row"><span>Reads with 1.5</span><span>numpy &middot; matplotlib only</span><span>Runs offline</span></div>
      <a class="resource-link" href="module1/lab2_word_embeddings.html">Open Lab 2</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1 &middot; Sept 3 &amp; 10</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Lab 3 &mdash; Image Embeddings with a Deep CNN</h3>
      <p>Load a pretrained ResNet-50, visualize what the layers respond to as depth increases &mdash; edges, then textures, then parts, then objects &mdash; extract 2048-dimensional embeddings for a handful of roadway images, and check that semantically similar scenes land near each other.</p>
      <p><strong>Proves:</strong> transfer learning in its simplest useful form &mdash; you are reusing a representation you did not pay to train. <strong>Check it against:</strong> the pairs you predicted would be closest before you ran it; the ones that surprise you are the finding.</p>
      <div class="tag-row"><span>Reads with 1.3, 1.4</span><span>torch &middot; torchvision &middot; scikit-learn</span><span>Downloads images</span></div>
      <a class="resource-link" href="module1/lab3_image_embeddings.html">Open Lab 3</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 1 &middot; Sept 10</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Lab 4 &mdash; CLIP vs. Traditional Computer Vision</h3>
      <p>Compare a closed-set classifier with a CLIP-style multimodal model on roadway and dashcam-style scenes. Run zero-shot recognition against open-vocabulary prompts &mdash; a flooded roadway, a construction work zone, a pedestrian crossing at night &mdash; then push on prompt phrasing until the model breaks.</p>
      <p><strong>Proves:</strong> why open-vocabulary perception matters for long-tail safety scenarios that never appear in an ImageNet-style label set &mdash; and how brittle prompt phrasing can be. <strong>Check it against:</strong> the closed-set classifier on the same images, including the scenes neither model has a label for.</p>
      <div class="tag-row"><span>Reads with 1.5</span><span>torch &middot; transformers</span><span>Bridge into Module 2</span></div>
      <a class="resource-link" href="module1/lab4_clip_vs_traditional_cv.html">Open Lab 4</a>
    </article>
  </div>
  <div class="placeholder-panel">
    <p><strong>Lab 4 is also the bridge into Module 2.</strong> It lives here because it is built from Module 1's embedding material, but the shared image&ndash;text space it constructs is what the vision-language section of <a href="module2/index.html">Module 2</a> assumes you already have. If you arrive at Module 2 without having run it, run it first.</p>
  </div>
</section>

<section class="resource-section" id="coming-later">
  <div class="resource-section-header">
    <h2>Coming Later in the Course</h2>
    <span>Modules 2&ndash;8</span>
  </div>
  <p class="section-intro">These are described on each module page and released as the semester reaches them. They are listed here so you can see the arc &mdash; and so that if one of them is close to your capstone, you can start early rather than waiting for the week it is assigned.</p>
  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 2 &middot; Sept 17</p><span class="status-tag status-closed">In development</span></div>
      <h3>Transformers, LLMs, and Multimodal Models</h3>
      <p><strong>Cross-attention sanity check.</strong> Build a small cross-attention model on paired mobility data, then run a three-tier check: does the model learn the task, does attention concentrate where the physics says it should, and does that interpretation survive a control condition? Useful corrective before you read your next attention visualization.</p>
      <a class="resource-link" href="module2/index.html">Module 2</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 3 &middot; Sept 24, Nov 19</p><span class="status-tag status-closed">In development</span></div>
      <h3>Generative AI and World Models</h3>
      <p><strong>VAE on traffic state heatmaps</strong> &mdash; read the latent space of a model trained on cell-transmission speed fields. <strong>From VAE to diffusion</strong> &mdash; measure where the VAE breaks on that same data before reaching for diffusion. <strong>Training the denoiser</strong> &mdash; build it in numpy and answer what the network is really predicting at each noise level.</p>
      <a class="resource-link" href="module3/index.html">Module 3</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 4 &middot; Oct 1, Oct 8</p><span class="status-tag status-closed">In development</span></div>
      <h3>Adapting and Orchestrating Models</h3>
      <p><strong>A retrieval assistant over transportation documents</strong> &mdash; build a RAG pipeline over a design manual or a set of agency reports, and measure retrieval quality on its own before judging the answers. <strong>An agentic workflow for a recurring task</strong> &mdash; decompose a monthly analysis into tool calls, with a verification step you designed rather than one the agent reports on itself.</p>
      <a class="resource-link" href="module4/index.html">Module 4</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 5 &middot; Oct 15, Oct 22</p><span class="status-tag status-closed">In development &middot; hardware</span></div>
      <h3>Mobility Sensing and Edge AI</h3>
      <p><strong>Vehicle detection and tracking</strong> &mdash; train a YOLO detector on a public traffic-camera dataset, extract counts and turning movements with ByteTrack, and report count error against manual ground truth rather than mAP. <strong>Deploy it to the edge</strong> &mdash; quantize that detector, run it on a Jetson, and measure what you lost and gained before deciding whether you would put it on a pole.</p>
      <a class="resource-link" href="module5/index.html">Module 5</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 6 &middot; Oct 29</p><span class="status-tag status-closed">In development &middot; hardware</span></div>
      <h3>Autonomous Driving and Connectivity</h3>
      <p><strong>Reading a production driving stack</strong> &mdash; work through the Openpilot longitudinal and lateral control paths and examine CAN traces from a vehicle running it. <strong>A lane-keeping policy from camera images</strong> &mdash; train a small CNN policy, evaluate it in simulation, and analyze the failures that look fine in aggregate.</p>
      <a class="resource-link" href="module6/index.html">Module 6</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 7 &middot; Nov 5</p><span class="status-tag status-open">Companion available</span></div>
      <h3>Simulation, Digital Twins, and Operations</h3>
      <p><strong>Learning the CTM update</strong> &mdash; fit a convolution kernel to a Newell platoon, read the reaction time off its peak, then train a residual conv block on CTM fields and measure the wave speeds it learned. Runs in the browser, nothing to install. <strong>RL signal control in SUMO</strong> and <strong>sensor simulation in CARLA</strong> follow.</p>
      <a class="resource-link" href="module7/index.html">Module 7</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Module 8 &middot; Nov 12</p><span class="status-tag status-closed">In development</span></div>
      <h3>Safety, Agency Practice, and Responsible Use</h3>
      <p><strong>Surrogate safety from video</strong> &mdash; extract trajectories from an intersection video, compute TTC and PET distributions, then state what would have to be true for those numbers to predict crashes at that location and check whether it is. <strong>An agency document workflow</strong> &mdash; build one, design its verification step, and time it honestly against doing the task by hand.</p>
      <a class="resource-link" href="module8/index.html">Module 8</a>
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
    <p><strong>Hardware labs are different.</strong> The Module 5 and Module 6 labs marked <em>hardware</em> use instructor-provided equipment &mdash; Jetsons, cameras, and the comma devices on the <a href="hardware.html">Hardware for Class</a> page. No personal vehicle is used for any lab, and any project that collects identifiable data needs IRB approval before collection starts.</p>
  </div>
</section>

<section class="resource-section" id="evaluating">
  <div class="resource-section-header">
    <h2>Before You Trust a Lab Result</h2>
    <span>The habit every lab is built around</span>
  </div>
  <p class="section-intro">Every notebook in this course produces something that looks like a result. The point of the lab is not the number &mdash; it is whether the number survives three questions, the same three that decide whether you would put a system on a pole or in front of a review board.</p>
  <div class="placeholder-panel">
    <p><strong>What is the baseline?</strong> Not "no model" &mdash; the cheap, tuned, classical thing a colleague would do instead. Latitude and longitude in Lab 2. A properly tuned actuated controller in the SUMO lab. Manual counts in the detection lab. A result that does not beat its baseline is a finding, and worth reporting as one.</p>
    <p><strong>How was the data split, and is that split honest?</strong> Random splits flatter models on data with structure &mdash; consecutive frames of the same video, repeated days at the same station, trips by the same driver. Ask whether anything in your test set could have been memorized from your training set.</p>
    <p><strong>What happens on the ugly cases?</strong> Night, rain, occlusion, work zones, the scene with no label for it. Aggregate accuracy hides exactly the cases that matter for safety, and those are the ones a vendor demo will not show you.</p>
  </div>
</section>
