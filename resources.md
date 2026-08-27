# Open Mobility AI Ecosystem

<section class="resource-hero">
  <div class="resource-eyebrow">USF · AI for Mobility</div>
  <h2>Open Mobility AI Ecosystem <span>Resource Hub</span></h2>
  <p>Curated tools, datasets, platforms, and agency-facing resources for practical AI applications in transportation and mobility.</p>
  <div class="resource-meta">
    <span>Graduate course resource</span>
    <span>Research-to-practice focus</span>
    <span>Last updated: August 2026</span>
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
    <button type="button" class="filter-button" data-filter="Hardware">Hardware</button>
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

<section class="resource-section" id="dotpilot">
  <div class="resource-section-header">
    <h2>Course Baseline Platform: DoTPilot</h2>
    <span>MOTIF Lab project</span>
  </div>
  <p class="section-intro">DoTPilot is the MOTIF Lab's own open-source platform, built by forking sunnypilot (itself a fork of comma.ai's openpilot) and adding an LLM-based agent layer for transportation-agency use cases. It is the baseline repository for this course: rather than building vehicle sensing and control from scratch, students fork DoTPilot and add new agency-facing functions on top of it.</p>

  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="dotpilot motif lab agency transportation fleet sunnypilot openpilot fork road damage inspection road asset inspection travel advisory advisories fl511 work zone workzone data exchange ai dashcam llm agent v2x traffic adas agency advanced">
      <div class="resource-card-top"><p class="resource-category">Agency Platform</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>DoTPilot</h3>
      <p>MOTIF Lab's open-source agency fork of sunnypilot/openpilot for state and county transportation fleets — the course's baseline repository for capstone projects.</p>
      <div class="tag-row"><span>Agency</span><span>AI Dashcam</span><span>Course Baseline</span></div>
      <a class="resource-link" href="https://github.com/HaoZhouGT/DoTPilot" target="_blank" rel="noopener">github.com/HaoZhouGT/DoTPilot</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>What's implemented today.</strong> Three branches carry the active features: <code>llm-agent</code> runs a managed on-device agent that sends forward-camera crops to a vision model and flags pavement defects, flooding, blocked drainage, debris, shoulder erosion, faded markings, sign or signal damage, guardrail issues, bridge issues, and work zones as onroad findings; <code>v2x-traffic-advisor-f511</code> fetches public Florida 511 event data and filters it on-device by GPS position, vehicle heading, and route corridor to surface travel advisories, closures, incidents, and construction; and the fleet-log-export branches add a Wi-Fi-only, route-grouped Dropbox uploader for agency review. Every feature publishes advisory findings or warnings to the driver — none of them takes control of steering, throttle, or braking.</p>
    <p><strong>How to build on it.</strong> Fork the repository and branch from whichever feature is closest to your project — <code>llm-agent</code> for a new hazard or road-asset class, <code>v2x-traffic-advisor-f511</code> for a new advisory source. Capstone teams are encouraged to extend the platform with additional inspection categories, new agency data feeds beyond FL511, alternate upload destinations, or a standards-based work-zone data exchange (e.g., <a href="https://ops.fhwa.dot.gov/wz/wzdx/index.htm" target="_blank" rel="noopener">WZDx</a>) rather than rebuilding the vehicle sensing and driver-assist stack underneath it.</p>
  </div>
</section>

<section class="resource-section" id="hardware">
  <div class="resource-section-header">
    <h2>Hardware You Can Access in This Class</h2>
    <span>Loaner equipment</span>
  </div>
  <p class="section-intro">Devices the course owns and can lend you for labs and capstone projects. All of it is instructor-provided equipment under the syllabus hardware policy — no personal vehicles, and any project that collects identifiable data needs IRB approval <em>before</em> collection starts. Check availability with the instructor before you write a project proposal that depends on a specific device.</p>

  <h3 class="resource-subhead">M5Stack StackChan &mdash; Desktop AI Robot</h3>
  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="stackchan stack-chan m5stack cores3 esp32-s3 desktop ai robot hardware loaner edge ai voice agent wake word mcp model context protocol servo pan tilt camera imu microphone speaker grove embodied interface agency traffic beginner">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>M5Stack StackChan</h3>
      <p>Palm-sized open-source AI desktop robot: ESP32-S3, camera, dual microphones, speaker, 9-axis IMU, and a two-servo pan/tilt head, with a wake-word voice agent and an MCP client in the stock firmware. Two units on hand.</p>
      <div class="tag-row"><span>Edge AI</span><span>Voice Agent</span><span>MCP</span><span>Embodied Interface</span></div>
      <a class="resource-link" href="https://docs.m5stack.com/en/StackChan" target="_blank" rel="noopener">docs.m5stack.com/en/StackChan</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>What is inside.</strong> An M5Stack CoreS3 head — ESP32-S3 dual-core at 240 MHz, 16 MB flash, 8 MB PSRAM — driving a 2.0-inch 320&times;240 capacitive touch LCD that renders the robot&rsquo;s face. Sensing: a 640&times;480 (0.3 MP) camera, two microphones with an ES7210 codec, a 1 W speaker, a 9-axis IMU (accelerometer, gyroscope, magnetometer), a proximity and ambient-light sensor, NFC, and infrared. The body adds a 360&deg; continuous pan servo and a 90&deg; tilt servo, both with position feedback, plus 12 addressable RGB LEDs. Wi-Fi and Bluetooth LE, USB-C, a microSD slot, a 550 mAh battery, and three Grove ports for adding M5Stack units such as GPS, time-of-flight ranging, radar, or environmental sensors. Stock firmware runs a wake-word voice agent (&ldquo;Hi, StackChan&rdquo;) that is also an <strong>MCP client</strong>, so it can call external tools; M5Stack ships a Home Assistant integration as the worked example. You can reflash it from UiFlow2, Arduino IDE, PlatformIO, or ESP-IDF.</p>
    <p><strong>Read it as an interface, not a sensor.</strong> An ESP32-S3 with a 0.3 MP fixed-focus camera will not run a real object detector at video rate, and it will not read a license plate. Its value sits at the other end of the pipeline. StackChan is the cheapest way to make the <em>output</em> of an AI workflow physical: speech in, speech out, a face that turns toward you, and an MCP client that can call whatever data source you expose to it. In a course that spends most of its time on models and data, this is the piece that shows what the last mile to a human actually looks like — which is where most agency AI projects succeed or fail.</p>
  </div>

  <h3 class="resource-subhead">StackChan Project Ideas</h3>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th>Project Idea</th>
          <th>What You Would Build</th>
          <th>Why It Is Realistic</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Voice front end for agency data</td><td>An MCP server wrapping a live feed — FL511 events, signal cabinet status, work-zone permits — that StackChan calls when you ask a spoken question, then answers out loud</td><td>The stock firmware is already an MCP client; you swap the shipped Home Assistant example for your own server</td></tr>
        <tr><td>Alert embodiment in a TMC</td><td>Stream an incident or queue-detection feed to the robot so it turns toward the operator and speaks the event, then compare operator response against a screen-only alarm</td><td>Whether embodiment reduces alarm fatigue is an open human-factors question with a measurable outcome, not a demo</td></tr>
        <tr><td>Ride-quality and harsh-event logger</td><td>Log the 9-axis IMU to microSD in a moving vehicle, add a Grove GPS unit, and classify hard braking, lateral jerk, and pavement roughness proxies by location</td><td>Same principle as the smartphone-IMU roughness screening agencies already use; the onboard sensing is sufficient for this one</td></tr>
        <tr><td>Miniature PTZ and active sensing</td><td>Close the loop from a detection to the pan and tilt servos so the camera points at the event; measure slew time, overshoot, and target reacquisition</td><td>A bench model of how a real CCTV PTZ behaves, with the control latency exposed and instrumented</td></tr>
        <tr><td>Edge-AI budget lab</td><td>Quantize a small classifier, run it on the ESP32-S3, and measure accuracy, frames per second, and power draw against the same model on a laptop GPU</td><td>The constraint is the lesson: you find out empirically where edge inference stops being viable (Module 5)</td></tr>
        <tr><td>In-vehicle assistant proxy for HMI studies</td><td>Mount it on the dash in the driving simulator and script takeover requests or advisory messages delivered by an anthropomorphic voice and face</td><td>A cheap, repeatable stimulus for trust-calibration and takeover-response studies without building a custom HMI</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>Know the limits before you propose one.</strong> The camera is 0.3 MP and fixed focus, so useful vision ends a couple of meters out. On-device inference means tiny quantized models at low frame rates — plan for that, do not discover it in week 10. The stock voice agent streams audio to a vendor cloud server, which is a real procurement and data-governance blocker for anything an agency would deploy; self-hosting the agent backend is the interesting fix and a legitimate project in itself. There is no GPS unless you add a Grove module, no weatherproofing, and roughly an hour of battery. And there are two units, so treat them as one shared interface station that several teams connect to rather than hardware each team keeps.</p>
  </div>

  <h3 class="resource-subhead">comma Devices &mdash; In-Vehicle ADAS Platform</h3>
  <div class="resource-grid">
    <article class="resource-card" data-resource data-search="comma 3x comma three x openpilot adas hardware loaner snapdragon 845 ox03c10 hdr camera driver monitoring can fd panda lane keeping acc alc lka dotpilot sunnypilot in-vehicle agency advanced">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>comma 3X</h3>
      <p>Windshield-mounted openpilot computer: Snapdragon 845, 128 GB storage, three OX03C10 140 dB HDR cameras (wide road, narrow road, driver-facing), 6-inch 2160&times;1080 OLED, LTE and Wi-Fi, and an integrated CAN-FD panda.</p>
      <div class="tag-row"><span>ADAS</span><span>CAN Bus</span><span>Naturalistic Data</span></div>
      <a class="resource-link" href="https://blog.comma.ai/comma3X/" target="_blank" rel="noopener">blog.comma.ai/comma3X</a>
    </article>
    <article class="resource-card" data-resource data-search="comma four comma 4 openpilot adas hardware loaner snapdragon 845 max oled triple camera 360 usb 3.1 chestnut egpu lane centering acc dotpilot sunnypilot in-vehicle agency advanced">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>comma four</h3>
      <p>Current-generation device: Snapdragon 845 MAX with a cooling design built for sustained turbo behind a hot windshield, the same triple-camera 360&deg; suite in roughly one-fifth the volume, and a 1.9-inch 300 PPI OLED. Supports 300+ cars and the chestnut eGPU path.</p>
      <div class="tag-row"><span>ADAS</span><span>Edge Compute</span><span>eGPU Ready</span></div>
      <a class="resource-link" href="https://blog.comma.ai/comma-four/" target="_blank" rel="noopener">blog.comma.ai/comma-four</a>
    </article>
    <article class="resource-card" data-resource data-search="chestnut egpu external gpu dock usb4 pcie gen4 asm2464pd open source firmware tinygrad radeon rx 9060 comma four model scaling flops parameters hardware loaner edge compute advanced">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>chestnut (eGPU)</h3>
      <p>USB4-to-PCIe Gen4 &times;4 bridge on the ASM2464PD with open-source firmware, letting a full desktop GPU run driving models off a comma four. Moves the inference budget from roughly 10 W on-SoC to about 100 W on the external card.</p>
      <div class="tag-row"><span>eGPU</span><span>Model Scaling</span><span>Open Firmware</span></div>
      <a class="resource-link" href="https://comma.ai/shop/chestnut" target="_blank" rel="noopener">comma.ai/shop/chestnut</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>How the three fit together.</strong> comma 3X and comma four are the same idea one generation apart: a windshield-mounted computer that reads the car&rsquo;s CAN bus through an integrated panda, watches the road and the driver with a triple-camera 360&deg; suite, and runs openpilot to provide adaptive cruise control, automated lane centering, forward collision warning, and lane departure warning on 300+ supported cars. The 3X launched in 2023; the comma four keeps its compute and sensor suite but packs it into about a fifth of the volume behind the mirror. Both remain supported by openpilot and its forks &mdash; but forks ship <em>separate release tracks per device</em>, so confirm which device your branch targets before you flash anything.</p>
    <p><strong>What chestnut changes.</strong> This is the newest piece and the most interesting one pedagogically. Because it hangs a desktop GPU off the device over USB4, it is the rare case where you can run the same workload at a 10 W budget and a 100 W budget <em>in the same vehicle on the same drive</em>. comma reports that the first chestnut-class driving model has 30&times; the parameters and 100&times; the FLOPs of the latest on-device model, with image warping and driver monitoring staying on the Qualcomm SoC. Pricing is $249 for the bare dock or $899 for the ready-to-drive kit with an AMD Radeon RX 9060 8 GB, power adapters, and mounting hardware. If you have ever wanted to measure the accuracy-versus-latency-versus-power tradeoff instead of arguing about it, this is the setup.</p>
    <p><strong>Where to start.</strong> openpilot documentation and the supported-car list live at <a href="https://docs.comma.ai/" target="_blank" rel="noopener">docs.comma.ai</a>, with source at <a href="https://github.com/commaai/openpilot" target="_blank" rel="noopener">github.com/commaai/openpilot</a>. For course projects, do not start from upstream openpilot &mdash; fork <a href="#dotpilot">DoTPilot</a>, the MOTIF Lab agency platform described in the section above, which already carries the road-inspection agent, the FL511 advisory filter, and the fleet log export.</p>
  </div>

  <h3 class="resource-subhead">comma Device Project Ideas</h3>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th>Project Idea</th>
          <th>What You Would Build</th>
          <th>Why It Is Realistic</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Production ADAS lane-keeping evaluation</td><td>Log CAN and camera data on instrumented corridors, then quantify lane-centering error, disengagements, and failure onset against curvature, marking quality, weather, and lighting</td><td>The device gives you the actual control signals and driver takeovers, which no external dashcam can recover</td></tr>
        <tr><td>New road-asset or hazard class</td><td>Extend DoTPilot&rsquo;s inspection agent with one new category &mdash; blocked inlets, sign retroreflectivity, sidewalk obstruction, shoulder erosion &mdash; and score it against a field-verified sample</td><td>The capture, inference, and upload path already exist; you add one class and its evaluation rather than a whole system</td></tr>
        <tr><td>Corridor advisory beyond FL511</td><td>Add a second feed to the on-device advisory filter &mdash; WZDx work zones, weather, transit signal priority status &mdash; geofiltered by position, heading, and route</td><td>These feeds are public and standards-based, and the on-device filtering logic is already written</td></tr>
        <tr><td>Edge versus eGPU model-scaling study</td><td>Run the same perception or driving model on comma four alone and on comma four plus chestnut; measure accuracy, latency, frame rate, and power at each budget</td><td>Chestnut makes the compute budget an experimental variable instead of a fixed constraint</td></tr>
        <tr><td>Driver attention and takeover behavior</td><td>Pair the driver-facing camera with disengagement logs to characterize where and why drivers take over, and how long the transition takes</td><td>Grounds in-vehicle HMI and trust-calibration research in real trips rather than simulator sessions</td></tr>
        <tr><td>Naturalistic conflict and near-miss mining</td><td>Mine fleet logs for hard braking and lane-departure events, pull the matching video, and build a geolocated surrogate-safety hot-spot map</td><td>Converts routine agency driving into a safety dataset without waiting for crashes to accumulate</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>Rules and limits &mdash; read these before you propose.</strong> These devices go in a moving vehicle, which raises the bar on everything. The harness is car-specific, so bring the vehicle to the instructor before anything is installed, and the syllabus rule stands: instructor-provided vehicles only, never a personal car. openpilot and its forks are <em>driver assistance, not automation</em> &mdash; everything DoTPilot adds is advisory, and nothing in it touches steering, throttle, or braking; do not propose a project that changes that. Any project recording the driver-facing camera, or road video containing faces or license plates, needs IRB approval before the first drive plus a written retention and de-identification plan. Chestnut needs its own power supply and a physical mounting spot such as under a seat or in the passenger footwell, so treat it as a bench and pilot-vehicle instrument rather than something you hand to a fleet. Finally, these are shared units and only one project can have a device installed at a time &mdash; claim your data-collection window early, because a semester has fewer good weather weeks than you think.</p>
  </div>

  <div class="placeholder-panel">
    <p><strong>More hardware will be listed here</strong> as it becomes available. If your capstone needs a device the course does not own, raise it early &mdash; sometimes it can be borrowed or purchased in time, but not in the last three weeks of the semester.</p>
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
        <tr><td>Running a larger driving model in-vehicle</td><td>Offloading inference from the on-device SoC to an external GPU on a ~100 W budget</td><td>comma four, chestnut, tinygrad, openpilot</td></tr>
        <tr><td>Road damage inspection, travel advisories, work zone data</td><td>Agency-facing AI dashcam + advisory platform, forked and extended</td><td>DoTPilot, OpenAI Vision API, FL511</td></tr>
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
