# Hardware You Can Access in This Class

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility</div>
  <h2>Course Hardware <span>Loaner Equipment</span></h2>
  <p>Devices the course owns and can lend you for labs and capstone projects &mdash; what each one actually does, what it cannot do, and the projects worth proposing with it.</p>
  <div class="resource-meta">
    <span>Instructor-provided equipment</span>
    <span>Labs and capstone projects</span>
    <span>Last updated: August 2026</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>How to use this page.</strong> Everything listed here is instructor-provided equipment under the syllabus hardware policy: no personal vehicles, and any project collecting identifiable data needs IRB approval <em>before</em> collection starts. Each entry states plainly what the device can and cannot do &mdash; read the limits before you write a proposal that depends on one, and check availability with the instructor early, because most of these are shared and a semester has fewer usable weeks than you think. For open datasets, software, and simulation platforms rather than physical equipment, see the <a href="resources.html">Open Mobility AI Ecosystem</a> page.</p>
</div>

<section class="resource-section" id="stackchan">
  <div class="resource-section-header">
    <h2>M5Stack StackChan</h2>
    <span>Desktop AI robot &middot; 2 units</span>
  </div>
  <p class="section-intro">A palm-sized open-source robot that makes the last mile of an AI workflow physical: speech in, speech out, a face that turns toward you, and a tool-calling client that can reach whatever data source you expose to it.</p>

  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>M5Stack StackChan</h3>
      <p>ESP32-S3, camera, dual microphones, speaker, 9-axis IMU, and a two-servo pan/tilt head, with a wake-word voice agent and an MCP client in the stock firmware. Two units on hand.</p>
      <div class="tag-row"><span>Edge AI</span><span>Voice Agent</span><span>MCP</span><span>Embodied Interface</span></div>
      <a class="resource-link" href="https://docs.m5stack.com/en/StackChan" target="_blank" rel="noopener">docs.m5stack.com/en/StackChan</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>What is inside.</strong> An M5Stack CoreS3 head &mdash; ESP32-S3 dual-core at 240 MHz, 16 MB flash, 8 MB PSRAM &mdash; driving a 2.0-inch 320&times;240 capacitive touch LCD that renders the robot&rsquo;s face. Sensing: a 640&times;480 (0.3 MP) camera, two microphones with an ES7210 codec, a 1 W speaker, a 9-axis IMU (accelerometer, gyroscope, magnetometer), a proximity and ambient-light sensor, NFC, and infrared. The body adds a 360&deg; continuous pan servo and a 90&deg; tilt servo, both with position feedback, plus 12 addressable RGB LEDs. Wi-Fi and Bluetooth LE, USB-C, a microSD slot, a 550 mAh battery, and three Grove ports for adding M5Stack units such as GPS, time-of-flight ranging, radar, or environmental sensors. Stock firmware runs a wake-word voice agent (&ldquo;Hi, StackChan&rdquo;) that is also an <strong>MCP client</strong>, so it can call external tools; M5Stack ships a Home Assistant integration as the worked example. You can reflash it from UiFlow2, Arduino IDE, PlatformIO, or ESP-IDF.</p>
    <p><strong>Read it as an interface, not a sensor.</strong> An ESP32-S3 with a 0.3 MP fixed-focus camera will not run a real object detector at video rate, and it will not read a license plate. Its value sits at the other end of the pipeline. StackChan is the cheapest way to make the <em>output</em> of an AI workflow physical, and in a course that spends most of its time on models and data, this is the piece that shows what the last mile to a human actually looks like &mdash; which is where most agency AI projects succeed or fail.</p>
  </div>

  <h3 class="resource-subhead">Project Ideas</h3>
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
        <tr><td>Voice front end for agency data</td><td>An MCP server wrapping a live feed &mdash; FL511 events, signal cabinet status, work-zone permits &mdash; that StackChan calls when you ask a spoken question, then answers out loud</td><td>The stock firmware is already an MCP client; you swap the shipped Home Assistant example for your own server</td></tr>
        <tr><td>Alert embodiment in a TMC</td><td>Stream an incident or queue-detection feed to the robot so it turns toward the operator and speaks the event, then compare operator response against a screen-only alarm</td><td>Whether embodiment reduces alarm fatigue is an open human-factors question with a measurable outcome, not a demo</td></tr>
        <tr><td>Ride-quality and harsh-event logger</td><td>Log the 9-axis IMU to microSD in a moving vehicle, add a Grove GPS unit, and classify hard braking, lateral jerk, and pavement roughness proxies by location</td><td>Same principle as the smartphone-IMU roughness screening agencies already use; the onboard sensing is sufficient for this one</td></tr>
        <tr><td>Miniature PTZ and active sensing</td><td>Close the loop from a detection to the pan and tilt servos so the camera points at the event; measure slew time, overshoot, and target reacquisition</td><td>A bench model of how a real CCTV PTZ behaves, with the control latency exposed and instrumented</td></tr>
        <tr><td>Edge-AI budget lab</td><td>Quantize a small classifier, run it on the ESP32-S3, and measure accuracy, frames per second, and power draw against the same model on a laptop GPU</td><td>The constraint is the lesson: you find out empirically where edge inference stops being viable (Module 5)</td></tr>
        <tr><td>In-vehicle assistant proxy for HMI studies</td><td>Mount it on the dash in the driving simulator and script takeover requests or advisory messages delivered by an anthropomorphic voice and face</td><td>A cheap, repeatable stimulus for trust-calibration and takeover-response studies without building a custom HMI</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>Know the limits before you propose one.</strong> The camera is 0.3 MP and fixed focus, so useful vision ends a couple of meters out. On-device inference means tiny quantized models at low frame rates &mdash; plan for that, do not discover it in week 10. The stock voice agent streams audio to a vendor cloud server, which is a real procurement and data-governance blocker for anything an agency would deploy; self-hosting the agent backend is the interesting fix and a legitimate project in itself. There is no GPS unless you add a Grove module, no weatherproofing, and roughly an hour of battery. And there are two units, so treat them as one shared interface station that several teams connect to rather than hardware each team keeps.</p>
  </div>
</section>

<section class="resource-section" id="comma">
  <div class="resource-section-header">
    <h2>comma Devices</h2>
    <span>In-vehicle ADAS platform</span>
  </div>
  <p class="section-intro">Windshield-mounted computers that read the car&rsquo;s CAN bus, watch the road and the driver, and run openpilot. This is the course&rsquo;s route to real vehicle data &mdash; actual control signals and driver takeovers, not just video from a dashcam.</p>

  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>comma 3X</h3>
      <p>Snapdragon 845, 128 GB storage, three OX03C10 140 dB HDR cameras (wide road, narrow road, driver-facing), 6-inch 2160&times;1080 OLED, LTE and Wi-Fi, and an integrated CAN-FD panda.</p>
      <div class="tag-row"><span>ADAS</span><span>CAN Bus</span><span>Naturalistic Data</span></div>
      <a class="resource-link" href="https://blog.comma.ai/comma3X/" target="_blank" rel="noopener">blog.comma.ai/comma3X</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>comma four</h3>
      <p>Current generation: Snapdragon 845 MAX with a cooling design built for sustained turbo behind a hot windshield, the same triple-camera 360&deg; suite in roughly one-fifth the volume, and a 1.9-inch 300 PPI OLED. Supports 300+ cars and the chestnut eGPU path.</p>
      <div class="tag-row"><span>ADAS</span><span>Edge Compute</span><span>eGPU Ready</span></div>
      <a class="resource-link" href="https://blog.comma.ai/comma-four/" target="_blank" rel="noopener">blog.comma.ai/comma-four</a>
    </article>
    <article class="resource-card">
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
    <p><strong>Where to start.</strong> openpilot documentation and the supported-car list live at <a href="https://docs.comma.ai/" target="_blank" rel="noopener">docs.comma.ai</a>, with source at <a href="https://github.com/commaai/openpilot" target="_blank" rel="noopener">github.com/commaai/openpilot</a>. For course projects, do not start from upstream openpilot &mdash; fork <a href="resources.html#dotpilot">DoTPilot</a>, the MOTIF Lab agency platform on the resources page, which already carries the road-inspection agent, the FL511 advisory filter, and the fleet log export.</p>
  </div>

  <h3 class="resource-subhead">Project Ideas</h3>
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
</section>

<section class="resource-section" id="requests">
  <div class="resource-section-header">
    <h2>Requesting Hardware</h2>
    <span>Plan early</span>
  </div>

  <div class="placeholder-panel">
    <p><strong>How to reserve a device.</strong> Bring the request to the instructor when you scope your project, not when you start building. Say which device, which weeks you need it, and what you intend to collect &mdash; and if the project touches a vehicle or records people, start the IRB conversation in the same meeting. Devices are handed out for a stated window and returned at the end of it.</p>
    <p><strong>More hardware will be listed here</strong> as it becomes available. If your capstone needs a device the course does not own, raise it early &mdash; sometimes it can be borrowed or purchased in time, but not in the last three weeks of the semester.</p>
  </div>
</section>
