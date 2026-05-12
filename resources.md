# Open Mobility AI Ecosystem

<section class="resource-hero">
  <div class="resource-eyebrow">USF · AI Mobility Technologies</div>
  <h2>Open Mobility AI Ecosystem <span>Resource Hub</span></h2>
  <p>Curated tools, datasets, platforms, and agency-facing resources for practical AI applications in transportation and mobility.</p>
  <div class="resource-meta">
    <span>Graduate course resource</span>
    <span>Research-to-practice focus</span>
    <span>Last updated: May 2026</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>How to use this page.</strong> This hub is intentionally selective. It emphasizes public datasets, open-source mobility software, simulation platforms, V2X resources, and agency-relevant examples that connect AI methods with real transportation problems.</p>
</div>

<section class="resource-controls" aria-label="Resource search and filters">
  <label class="resource-search-label" for="resource-search">Search resources</label>
  <input id="resource-search" type="search" placeholder="Search by name, tag, category, or description" autocomplete="off">
  <div class="filter-row" aria-label="Category filters">
    <button type="button" class="filter-button is-active" data-filter="all">All</button>
    <button type="button" class="filter-button" data-filter="Dataset">Dataset</button>
    <button type="button" class="filter-button" data-filter="ADAS">ADAS</button>
    <button type="button" class="filter-button" data-filter="Simulation">Simulation</button>
    <button type="button" class="filter-button" data-filter="V2X">V2X</button>
    <button type="button" class="filter-button" data-filter="Traffic">Traffic</button>
    <button type="button" class="filter-button" data-filter="Agency">Agency</button>
    <button type="button" class="filter-button" data-filter="Advanced">Advanced</button>
  </div>
  <p class="resource-count" id="resource-count" aria-live="polite"></p>
</section>

<section class="resource-section" id="datasets">
  <div class="resource-section-header">
    <h2>Datasets & Benchmarks</h2>
    <span>8 resources</span>
  </div>
  <p class="section-intro">Public datasets are the fuel of AI mobility research. These resources support perception, prediction, naturalistic driving analysis, traffic flow modeling, and safety studies.</p>

  <h3 class="resource-subhead">Autonomous Driving Sensor Data</h3>
  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="waymo open dataset autonomous driving lidar camera tracking motion prediction perception benchmark dataset intermediate">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Waymo Open Dataset</h3>
      <p>Large-scale autonomous driving dataset with camera, LiDAR, tracking, motion prediction, and perception benchmarks.</p>
      <div class="tag-row"><span>LiDAR</span><span>Camera</span><span>Prediction</span><span>Benchmark</span></div>
      <a class="resource-link" href="https://waymo.com/open/" target="_blank" rel="noopener">waymo.com/open</a>
    </article>
    <article class="resource-card" data-resource data-search="nuscenes multimodal urban driving camera lidar radar maps object annotations dataset intermediate">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>nuScenes</h3>
      <p>Multimodal urban driving dataset with camera, LiDAR, radar, maps, and object annotations.</p>
      <div class="tag-row"><span>Multimodal</span><span>Radar</span><span>Urban Driving</span></div>
      <a class="resource-link" href="https://www.nuscenes.org/" target="_blank" rel="noopener">nuscenes.org</a>
    </article>
    <article class="resource-card" data-resource data-search="bdd100k driving video computer vision detection segmentation lane marking behavior dataset">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>BDD100K</h3>
      <p>Diverse driving video dataset for detection, segmentation, lane marking, and driving behavior analysis.</p>
      <div class="tag-row"><span>Video</span><span>Computer Vision</span><span>Segmentation</span></div>
      <a class="resource-link" href="https://bdd-data.berkeley.edu/" target="_blank" rel="noopener">bdd-data.berkeley.edu</a>
    </article>
    <article class="resource-card" data-resource data-search="comma2k19 comma ai highway driving camera vehicle signals can adas dataset advanced">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Comma2k19</h3>
      <p>Real-world highway driving dataset from comma.ai with camera, CAN bus, and vehicle signals.</p>
      <div class="tag-row"><span>ADAS</span><span>CAN</span><span>Real-World Driving</span></div>
      <a class="resource-link" href="https://github.com/commaai/comma2k19" target="_blank" rel="noopener">github.com/commaai/comma2k19</a>
    </article>
  </div>

  <h3 class="resource-subhead">Traffic Flow, Safety, and Naturalistic Driving</h3>
  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="ngsim usdot fhwa vehicle trajectories traffic flow car following lane change dataset">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>NGSIM</h3>
      <p>Foundational U.S. vehicle trajectory dataset for car-following, lane-change, and traffic flow modeling.</p>
      <div class="tag-row"><span>USDOT</span><span>Trajectories</span><span>Traffic Flow</span></div>
      <a class="resource-link" href="https://ops.fhwa.dot.gov/trafficanalysistools/ngsim.htm" target="_blank" rel="noopener">ops.fhwa.dot.gov/ngsim</a>
    </article>
    <article class="resource-card" data-resource data-search="highd exid round ind drone trajectory traffic safety naturalistic driving dataset">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>highD / exiD / rounD / inD</h3>
      <p>Drone-based naturalistic trajectory datasets for highways, exits, roundabouts, and intersections.</p>
      <div class="tag-row"><span>Trajectories</span><span>Drone</span><span>Safety</span></div>
      <a class="resource-link" href="https://levelxdata.com/highd-dataset/" target="_blank" rel="noopener">levelxdata.com</a>
    </article>
    <article class="resource-card" data-resource data-search="openacc adaptive cruise control empirical car following adas dataset advanced">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>OpenACC</h3>
      <p>Empirical car-following data from commercial adaptive cruise control vehicles, useful for ADAS impact studies.</p>
      <div class="tag-row"><span>ADAS</span><span>Car-Following</span><span>Empirical</span></div>
      <a class="resource-link" href="https://data.jrc.ec.europa.eu/dataset/9702c950-c80f-4d2f-982f-44d06ea0009f" target="_blank" rel="noopener">data.jrc.ec.europa.eu</a>
    </article>
    <article class="resource-card" data-resource data-search="citysim ucf drone trajectories florida safety surrogate measures traffic dataset">
      <div class="resource-card-top"><p class="resource-category">Dataset</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>CitySim Dataset</h3>
      <p>Drone trajectory dataset from Florida roadway sites with safety surrogate measure annotations.</p>
      <div class="tag-row"><span>Florida</span><span>Safety</span><span>Trajectories</span></div>
      <a class="resource-link" href="https://github.com/ozheng1993/UCF-SST-CitySim-Dataset" target="_blank" rel="noopener">github.com/ozheng1993/CitySim</a>
    </article>
  </div>
</section>

<section class="resource-section" id="stacks">
  <div class="resource-section-header">
    <h2>ADAS & Autonomous Mobility Software</h2>
    <span>5 resources</span>
  </div>
  <p class="section-intro">Open-source autonomy stacks expose the perception, planning, control, vehicle interface, and evaluation code behind modern mobility AI systems.</p>

  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="openpilot open-source driver assistance system production vehicles adas can edge ai advanced">
      <div class="resource-card-top"><p class="resource-category">ADAS</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>openpilot</h3>
      <p>Open-source driver assistance system for production vehicles. Useful for ADAS, CAN bus, controls, and real-world driving research.</p>
      <div class="tag-row"><span>ADAS</span><span>CAN</span><span>Edge AI</span></div>
      <a class="resource-link" href="https://github.com/commaai/openpilot" target="_blank" rel="noopener">github.com/commaai/openpilot</a>
    </article>
    <article class="resource-card" data-resource data-search="sunnypilot openpilot fork adas production vehicles customization advanced">
      <div class="resource-card-top"><p class="resource-category">ADAS</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>sunnypilot</h3>
      <p>Community-enhanced openpilot fork with additional customization options for experimental ADAS research.</p>
      <div class="tag-row"><span>ADAS</span><span>Open Source</span><span>Production Vehicles</span></div>
      <a class="resource-link" href="https://github.com/sunnypilot/sunnypilot" target="_blank" rel="noopener">github.com/sunnypilot/sunnypilot</a>
    </article>
    <article class="resource-card" data-resource data-search="autoware ros autonomous driving perception planning localization control advanced">
      <div class="resource-card-top"><p class="resource-category">Autonomy Stack</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Autoware</h3>
      <p>ROS-based open-source autonomous driving software stack for perception, planning, localization, and control.</p>
      <div class="tag-row"><span>ROS</span><span>Planning</span><span>Perception</span></div>
      <a class="resource-link" href="https://autoware.org/" target="_blank" rel="noopener">autoware.org</a>
    </article>
    <article class="resource-card" data-resource data-search="apollo auto autonomous driving platform perception planning control simulation advanced">
      <div class="resource-card-top"><p class="resource-category">Autonomy Stack</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Apollo Auto</h3>
      <p>Open autonomous driving platform with modules for perception, planning, control, and simulation.</p>
      <div class="tag-row"><span>Full Stack</span><span>Planning</span><span>Simulation</span></div>
      <a class="resource-link" href="https://apollo.auto/" target="_blank" rel="noopener">apollo.auto</a>
    </article>
    <article class="resource-card" data-resource data-search="ultralytics yolo object detection tracking computer vision mobility safety">
      <div class="resource-card-top"><p class="resource-category">Perception Tool</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Ultralytics YOLO</h3>
      <p>Practical object detection and tracking framework for roadway video analytics, safety studies, and AI dashcam projects.</p>
      <div class="tag-row"><span>Detection</span><span>Tracking</span><span>Computer Vision</span></div>
      <a class="resource-link" href="https://github.com/ultralytics/ultralytics" target="_blank" rel="noopener">github.com/ultralytics</a>
    </article>
  </div>
</section>

<section class="resource-section" id="simulation-v2x">
  <div class="resource-section-header">
    <h2>Simulation, V2X & Connected Vehicles</h2>
    <span>4 resources</span>
  </div>
  <p class="section-intro">Simulation and connected-vehicle platforms help bridge controlled experiments, field deployment, and agency operations.</p>

  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="carla high fidelity autonomous driving simulator perception planning reinforcement learning safety testing simulation">
      <div class="resource-card-top"><p class="resource-category">Simulation</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>CARLA</h3>
      <p>High-fidelity autonomous driving simulator for perception, planning, reinforcement learning, and safety testing.</p>
      <div class="tag-row"><span>Simulation</span><span>Autonomous Driving</span><span>Safety</span></div>
      <a class="resource-link" href="https://carla.org/" target="_blank" rel="noopener">carla.org</a>
    </article>
    <article class="resource-card" data-resource data-search="sumo eclipse microscopic traffic simulation signal control operations connected vehicles simulation traffic">
      <div class="resource-card-top"><p class="resource-category">Simulation</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>SUMO</h3>
      <p>Open-source microscopic traffic simulator used for traffic operations, connected vehicles, and AI-based signal control.</p>
      <div class="tag-row"><span>Traffic</span><span>Operations</span><span>Signal Control</span></div>
      <a class="resource-link" href="https://www.eclipse.org/sumo/" target="_blank" rel="noopener">eclipse.org/sumo</a>
    </article>
    <article class="resource-card" data-resource data-search="v2x mobile applications platform usdot fhwa connected vehicle infrastructure v2x agency">
      <div class="resource-card-top"><p class="resource-category">V2X</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>V2X Mobile Applications Platform</h3>
      <p>USDOT FHWA open-source V2X mobile application platform for connected vehicle and infrastructure applications.</p>
      <div class="tag-row"><span>V2X</span><span>Connected Vehicles</span><span>USDOT</span></div>
      <a class="resource-link" href="https://github.com/usdot-fhwa-stol/v2x-mobile-app" target="_blank" rel="noopener">github.com/usdot-fhwa-stol</a>
    </article>
    <article class="resource-card" data-resource data-search="usdot its codehub intelligent transportation systems software connected vehicle tools v2x agency">
      <div class="resource-card-top"><p class="resource-category">V2X</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>USDOT ITS CodeHub</h3>
      <p>USDOT resource for open-source intelligent transportation systems software and connected vehicle tools.</p>
      <div class="tag-row"><span>USDOT</span><span>ITS</span><span>Open Source</span></div>
      <a class="resource-link" href="https://its.dot.gov/code/" target="_blank" rel="noopener">its.dot.gov/code</a>
    </article>
  </div>
</section>

<section class="resource-section" id="agency">
  <div class="resource-section-header">
    <h2>Agency & Practice Resources</h2>
    <span>5 resources</span>
  </div>
  <p class="section-intro">These resources help connect AI mobility projects to public-sector operations, safety programs, standards, and deployment contexts.</p>

  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="usdot its joint program office connected vehicles automation data intelligent infrastructure agency">
      <div class="resource-card-top"><p class="resource-category">Agency</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>USDOT ITS Joint Program Office</h3>
      <p>Federal ITS program resource for connected vehicles, automation, data, and intelligent infrastructure.</p>
      <div class="tag-row"><span>USDOT</span><span>ITS</span><span>Connected Vehicles</span></div>
      <a class="resource-link" href="https://www.its.dot.gov/" target="_blank" rel="noopener">its.dot.gov</a>
    </article>
    <article class="resource-card" data-resource data-search="fhwa federal highway administration operations safety infrastructure innovation agency traffic">
      <div class="resource-card-top"><p class="resource-category">Agency</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>FHWA</h3>
      <p>Federal Highway Administration resources on roadway operations, safety, infrastructure, and innovation.</p>
      <div class="tag-row"><span>Safety</span><span>Infrastructure</span><span>Operations</span></div>
      <a class="resource-link" href="https://highways.dot.gov/" target="_blank" rel="noopener">highways.dot.gov</a>
    </article>
    <article class="resource-card" data-resource data-search="nhtsa vehicle safety automation adas crash data regulation agency">
      <div class="resource-card-top"><p class="resource-category">Agency</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>NHTSA</h3>
      <p>Federal agency resource for vehicle safety, automation, ADAS, and crash data.</p>
      <div class="tag-row"><span>Vehicle Safety</span><span>ADAS</span><span>Crash Data</span></div>
      <a class="resource-link" href="https://www.nhtsa.gov/" target="_blank" rel="noopener">nhtsa.gov</a>
    </article>
    <article class="resource-card" data-resource data-search="sae international standards vehicle automation mobility transportation technologies agency">
      <div class="resource-card-top"><p class="resource-category">Standards</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>SAE International</h3>
      <p>Standards and technical resources for vehicle automation, mobility, and transportation technologies.</p>
      <div class="tag-row"><span>Standards</span><span>Automation</span><span>Vehicle Technology</span></div>
      <a class="resource-link" href="https://www.sae.org/" target="_blank" rel="noopener">sae.org</a>
    </article>
    <article class="resource-card" data-resource data-search="florida 511 traffic operations incidents roadway conditions florida agency">
      <div class="resource-card-top"><p class="resource-category">Operations</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Florida 511</h3>
      <p>Florida traveler information system with traffic, incident, and roadway condition information.</p>
      <div class="tag-row"><span>Florida</span><span>Traffic Operations</span><span>Incidents</span></div>
      <a class="resource-link" href="https://fl511.com/" target="_blank" rel="noopener">fl511.com</a>
    </article>
  </div>
</section>

<section class="resource-section" id="practice">
  <div class="resource-section-header">
    <h2>Research-to-Practice Examples</h2>
    <span>Course project lens</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th>Practical Problem</th>
          <th>AI/Mobility Solution</th>
          <th>Relevant Tools</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Signal outage assessment</td><td>AI dashcam damage detection and geotagged reporting</td><td>YOLO, OpenCV, Survey123, GIS</td></tr>
        <tr><td>Lane keeping evaluation</td><td>Production-vehicle ADAS data analysis</td><td>openpilot, CAN data, OpenLKA</td></tr>
        <tr><td>Post-storm generator deployment</td><td>Dynamic routing and replanning</td><td>SUMO, GIS, optimization</td></tr>
        <tr><td>Near-miss detection</td><td>Video-based conflict and behavior analysis</td><td>VLMs, object detection, tracking</td></tr>
        <tr><td>Connected vehicle safety</td><td>V2X mobile and infrastructure applications</td><td>USDOT V2X mobile app, ITS CodeHub</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>MOTIF Lab / AI4Mobility datasets.</strong> Future course and lab datasets will be listed here, including resources related to OpenLKA, ADAS evaluation, AI dashcams, and mobility safety applications.</p>
  </div>
</section>

## Contribute a Resource

<section class="contribute-panel">
  <p>This page should evolve with the AI4Mobility community. Students, researchers, practitioners, and agency partners are encouraged to suggest tools, datasets, tutorials, project examples, agency problem statements, benchmark tasks, and student project outcomes.</p>
  <div class="cta-row resource-cta-row">
    <a class="cta-button" href="https://github.com/ai4mobility/ai4mobility.github.io/issues/new?title=Resource%20suggestion" target="_blank" rel="noopener">Submit a Resource</a>
    <a class="cta-button cta-secondary" href="https://github.com/ai4mobility/ai4mobility.github.io/issues/new?title=Mobility%20problem%20suggestion" target="_blank" rel="noopener">Suggest a Mobility Problem</a>
    <a class="cta-button" href="https://github.com/ai4mobility/ai4mobility.github.io" target="_blank" rel="noopener">View GitHub Repository</a>
  </div>
</section>

<script>
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("resource-search");
  const cards = Array.from(document.querySelectorAll("[data-resource]"));
  const buttons = Array.from(document.querySelectorAll(".filter-button"));
  const count = document.getElementById("resource-count");
  let activeFilter = "all";

  function updateResources() {
    const query = (searchInput.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach(function (card) {
      const haystack = (card.getAttribute("data-search") || "").toLowerCase();
      const matchesSearch = !query || haystack.includes(query);
      const matchesFilter = activeFilter === "all" || haystack.includes(activeFilter.toLowerCase());
      const show = matchesSearch && matchesFilter;
      card.hidden = !show;
      if (show) visible += 1;
    });

    count.textContent = visible + " resource" + (visible === 1 ? "" : "s") + " shown";
  }

  searchInput.addEventListener("input", updateResources);
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      activeFilter = button.getAttribute("data-filter");
      buttons.forEach(function (item) { item.classList.remove("is-active"); });
      button.classList.add("is-active");
      updateResources();
    });
  });

  updateResources();
});
</script>
