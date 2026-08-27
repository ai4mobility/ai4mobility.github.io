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
  <p><strong>How to use this page.</strong> Everything listed here is instructor-provided equipment under the syllabus hardware policy: no personal vehicles, and any project collecting identifiable data needs IRB approval <em>before</em> collection starts. Each entry states plainly what the device can and cannot do &mdash; read the limits before you write a proposal that depends on one, and check availability with the instructor early, because most of these are single units and a semester has fewer usable weeks than you think. For open datasets, software, and simulation platforms rather than physical equipment, see the <a href="resources.html">Open Mobility AI Ecosystem</a> page.</p>
</div>

<section class="resource-section" id="at-a-glance">
  <div class="resource-section-header">
    <h2>What Is Available</h2>
    <span>Everything on this page</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr>
          <th>Device</th>
          <th>What It Is</th>
          <th>Units</th>
          <th>Best For</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Raspberry Pi 5</td><td>Linux single-board computer, quad Cortex-A76, dual MIPI camera ports</td><td>1</td><td>Classic CV, data logging, sensor nodes, orchestration</td></tr>
        <tr><td>Jetson Orin Nano</td><td>Entry NVIDIA edge AI board, 40 TOPS (67 in Super Mode)</td><td>1</td><td>Real-time detection, small models, first Jetson project</td></tr>
        <tr><td>Jetson Orin NX</td><td>Higher-tier Jetson module, 100 TOPS (157 in Super Mode)</td><td>1</td><td>Multi-stream video, larger models, vision-language models</td></tr>
        <tr><td>Pi Camera Module 3</td><td>12 MP autofocus CSI camera (Sony IMX708)</td><td>2</td><td>Bench rigs and window-mounted counters, paired with the Pi 5</td></tr>
        <tr><td>Automotive cameras</td><td>GMSL / FPD-Link serialized cameras over coax</td><td>8</td><td>Multi-camera intersection and surround-view rigs on a Jetson</td></tr>
        <tr><td>M5Stack StackChan</td><td>Desktop AI robot with voice agent and MCP client</td><td>2</td><td>Making the output of an AI workflow physical</td></tr>
        <tr><td>comma 3X / comma four</td><td>In-vehicle openpilot computers with CAN access</td><td>Shared</td><td>Production ADAS evaluation, naturalistic driving data</td></tr>
        <tr><td>chestnut</td><td>eGPU dock for comma four</td><td>Shared</td><td>Compute-scaling experiments at 10 W versus 100 W</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section class="resource-section" id="edge-ai">
  <div class="resource-section-header">
    <h2>Edge AI Computers</h2>
    <span>Raspberry Pi 5 &middot; Jetson Orin Nano &middot; Jetson Orin NX</span>
  </div>
  <p class="section-intro">Three Linux computers spanning a wide compute range. The same model can be made to run on all three, which turns &ldquo;what does this cost in latency and watts&rdquo; into something you measure rather than argue about.</p>

  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>Raspberry Pi 5</h3>
      <p>Broadcom BCM2712, 2.4 GHz quad-core Cortex-A76, VideoCore VII GPU, LPDDR4X. Two 4-lane MIPI CSI/DSI connectors, 2&times; USB 3.0 and 2&times; USB 2.0, Gigabit Ethernet with PoE+ via HAT, PCIe 2.0 &times;1 for NVMe, USB-C PD power. No AI accelerator.</p>
      <div class="tag-row"><span>Linux SBC</span><span>CSI Cameras</span><span>Classic CV</span></div>
      <a class="resource-link" href="https://www.raspberrypi.com/products/raspberry-pi-5/" target="_blank" rel="noopener">raspberrypi.com/products/raspberry-pi-5</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-intermediate">Intermediate</span></div>
      <h3>Jetson Orin Nano</h3>
      <p>NVIDIA Ampere GPU with tensor cores plus a six-core Arm CPU. 40 sparse TOPS (20 dense) on the 8 GB module, rising to 67 sparse / 33 dense in Super Mode under JetPack 6.2. Power configurable from 7 W to 25 W.</p>
      <div class="tag-row"><span>Edge AI</span><span>TensorRT</span><span>Real-Time Inference</span></div>
      <a class="resource-link" href="https://developer.nvidia.com/embedded/jetson-modules" target="_blank" rel="noopener">developer.nvidia.com/embedded/jetson-modules</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Jetson Orin NX</h3>
      <p>The step up: 100 sparse TOPS (50 dense) on the 16 GB module, 157 sparse / 78 dense in Super Mode, with a 40 W mode and high-speed interfaces for multiple concurrent camera streams. The board to reach for when one Jetson has to feed several cameras or a larger model.</p>
      <div class="tag-row"><span>Edge AI</span><span>Multi-Camera</span><span>VLM Capable</span></div>
      <a class="resource-link" href="https://developer.nvidia.com/embedded/jetson-modules" target="_blank" rel="noopener">developer.nvidia.com/embedded/jetson-modules</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>A compute ladder, on purpose.</strong> These three are not redundant. The Pi 5 has no AI accelerator at all &mdash; everything runs on four Cortex-A76 cores, which is plenty for classic computer vision, data logging, sensor fusion, and orchestration, and painful for anything neural at video rate. The Orin Nano adds an Ampere GPU with tensor cores and TensorRT, which is where real-time detection becomes possible. The Orin NX roughly doubles that again and adds the interface bandwidth to drive several camera streams at once. Having all three in one lab means you can hold the model fixed and vary the hardware, which is the experiment almost nobody bothers to run and everybody cites.</p>
    <p><strong>Two numbers to read carefully.</strong> First, headline TOPS figures are <em>sparse</em>; dense throughput is half. Compare like with like, and say which one you are quoting. Second, &ldquo;Super Mode&rdquo; is a software change, not new silicon: JetPack 6.2 raises GPU clocks (625 to 1020 MHz on Orin Nano, up to 1173 MHz on Orin NX), bumps CPU clocks, and adds new 25 W / 40 W and MAXN SUPER power modes, which is where the 40&rarr;67 and 100&rarr;157 TOPS jumps come from. NVIDIA reports roughly 1.3&times; to 2&times; on generative models. That a firmware release can nearly double a device&rsquo;s advertised AI performance is itself worth a slide in your presentation &mdash; it tells you how much these numbers depend on the power and clock envelope rather than the chip.</p>
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
        <tr><td>Roadside detection and counting node</td><td>A Pi 5 or Orin Nano with one camera watching an intersection or corridor, classifying and counting road users by movement and writing a clean time-series</td><td>The single most common agency ask, and the whole pipeline fits on one board and one camera</td></tr>
        <tr><td>Same-model compute ladder</td><td>Run one detector across Pi 5, Orin Nano, and Orin NX, with Super Mode on and off, and report accuracy, frame rate, latency percentiles, and watts</td><td>Turns &ldquo;which device should we buy&rdquo; into a measured answer instead of a vendor claim &mdash; and you have all three boards</td></tr>
        <tr><td>Quantization and precision study</td><td>Take a detector down through FP16 and INT8 with TensorRT and plot exactly what accuracy you lost against what latency you bought</td><td>The tradeoff is invisible until you plot it, and the tooling already ships with JetPack</td></tr>
        <tr><td>On-device hazard description with a VLM</td><td>Run a small vision-language model on the Orin NX that <em>describes</em> a road scene &mdash; flooding, debris, a blocked sidewalk &mdash; rather than only classifying it</td><td>Chases the DoTPilot inspection use case, but on-device, which is the version an agency can afford to run at fleet scale</td></tr>
        <tr><td>Multi-camera intersection rig</td><td>Drive several of the automotive cameras from one Jetson, time-align the frames, and build a multi-view analysis of a single intersection</td><td>The lab has eight cameras; the interesting geometry problems start at four</td></tr>
        <tr><td>Bandwidth and backhaul budget</td><td>Measure what it costs to send full video versus compressed clips versus events-only metadata from a roadside node, then design the on-device filter that makes it affordable</td><td>Backhaul cost is the actual reason edge inference exists, and it is almost never quantified in student work</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>Know the limits before you propose one.</strong> The Pi 5 has no inference accelerator &mdash; plan for classic CV, logging, and orchestration, and expect single-digit frame rates for anything neural at useful resolution. (An AI HAT or USB accelerator would change that; ask if your project needs one.) Super Mode requires JetPack 6.2 and a re-flash with the super device-kit configuration, and it raises power draw, so budget the supply and the cooling before you assume the higher number. All three are development kits, not field hardware: no enclosure, no weatherproofing, active cooling, and a real power requirement &mdash; anything mounted outdoors needs a housing, a power plan, and permission you should start asking about in week 3, not week 12. Video fills storage far faster than students expect, so put the Pi 5 on NVMe over its PCIe lane rather than logging to an SD card. And there is exactly one of each board, so coordinate early if two teams both want a Jetson.</p>
  </div>
</section>

<section class="resource-section" id="cameras">
  <div class="resource-section-header">
    <h2>Cameras and Imaging</h2>
    <span>Pi Camera Module 3 &middot; 8 automotive cameras</span>
  </div>
  <p class="section-intro">Two very different camera families: a couple of Raspberry Pi camera modules for quick tethered work, and eight automotive-grade serialized cameras for multi-camera rigs. They are not interchangeable, and which one you pick decides how hard your project is.</p>

  <div class="resource-grid">
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-beginner">Beginner</span></div>
      <h3>Raspberry Pi Camera Module 3</h3>
      <p>12 MP back-illuminated Sony IMX708 (4608&times;2592, 1.4 &micro;m pixels) with phase-detect autofocus and HDR mode. 75&deg; standard or 120&deg; wide diagonal field of view, 1080p50 video, 200 mm ribbon into the Pi 5&rsquo;s MIPI connectors. Two units.</p>
      <div class="tag-row"><span>CSI Camera</span><span>Autofocus</span><span>Pairs with Pi 5</span></div>
      <a class="resource-link" href="https://www.raspberrypi.com/products/camera-module-3/" target="_blank" rel="noopener">raspberrypi.com/products/camera-module-3</a>
    </article>
    <article class="resource-card">
      <div class="resource-card-top"><p class="resource-category">Hardware</p><span class="level-badge level-advanced">Advanced</span></div>
      <h3>Automotive Cameras (GMSL / FPD-Link)</h3>
      <p>Eight serialized automotive cameras. Video, control, and power all travel over a single coax, which is why production vehicles use them &mdash; long runs, one thin cable per camera, and many cameras on one host. Requires a deserializer to reach a Jetson.</p>
      <div class="tag-row"><span>Automotive</span><span>Multi-Camera</span><span>Coax Serialized</span></div>
      <a class="resource-link" href="https://docs.nvidia.com/jetson/archives/r35.4.1/DeveloperGuide/text/SD/CameraDevelopment/JetsonVirtualChannelWithGmslCameraFramework.html" target="_blank" rel="noopener">NVIDIA GMSL camera framework guide</a>
    </article>
  </div>

  <div class="placeholder-panel">
    <p><strong>The Pi cameras are the easy path.</strong> Camera Module 3 units are CSI ribbon cameras that go straight onto the Pi 5&rsquo;s MIPI connectors and work within minutes. Autofocus and HDR make them good for close and mid-range work &mdash; a bench rig, a tripod, a window-mounted counter. The supplied ribbon is 200 mm, so design the mount around the board rather than the other way round, and do not expect them to substitute for a road camera at distance.</p>
    <p><strong>The automotive cameras need a capture path, and that is the real constraint.</strong> A GMSL or FPD-Link camera does <em>not</em> plug into a Jetson development kit. The camera carries a serializer; you need the matching deserializer on a GMSL carrier board or capture card, and then device-tree work on the Jetson so the cameras enumerate. Bring-up follows a fixed order &mdash; power and link lock, then the I2C tunnel to the camera, then per-camera address assignment, then sensor initialization, then MIPI lane configuration &mdash; and skipping a step produces errors that point at the wrong layer. Budget a week to first light, not an afternoon. <strong>Before you scope a project around these eight cameras, ask the instructor which capture hardware the lab has.</strong> The deserializer path, not the cameras, decides whether your project is possible.</p>
    <p><strong>Why they are worth the trouble anyway.</strong> Eight synchronized automotive cameras is an uncommon teaching asset. It is the hardware behind surround-view, multi-view conflict analysis, and camera-to-camera handoff along a corridor &mdash; problems you simply cannot study with one webcam, and problems agencies are actively paying consultants to solve.</p>
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
        <tr><td>Multi-view intersection conflict analysis</td><td>Four or more cameras covering one intersection from different angles, frame-synchronized, with trajectories reconstructed to compute post-encroachment time and other surrogate safety measures</td><td>Multi-view is what makes conflict measurement defensible; single-camera studies get argued with in review</td></tr>
        <tr><td>Camera handoff and re-identification</td><td>Track a vehicle across overlapping fields of view and measure how often identity survives the handoff, and what breaks it</td><td>The quiet failure mode that undermines corridor-level analytics, and it needs exactly this hardware to study</td></tr>
        <tr><td>Surround-view rig on a test vehicle</td><td>Four cameras on a vehicle feeding one Jetson, time-aligned and logged with position, to reproduce how a production ADAS actually receives its inputs</td><td>Mirrors the real sensor architecture instead of approximating it with a dashcam</td></tr>
        <tr><td>Bench counter with a classic-versus-neural baseline</td><td>Pi 5 and Camera Module 3 on a tripod or window, counting and classifying road users with a background-subtraction baseline and a neural baseline side by side</td><td>The simplest complete pipeline in the lab and an honest place to start &mdash; the classic baseline often wins, which is the lesson</td></tr>
        <tr><td>Calibration and error budget</td><td>Intrinsic and extrinsic calibration of both camera types, then convert pixel measurements into real-world speeds and distances with a documented uncertainty at each step</td><td>The step everyone skips and every reviewer asks about; doing it properly makes every other camera project defensible</td></tr>
        <tr><td>Low-light and weather degradation study</td><td>Characterize how detection quality falls off at dusk, at night, in rain, and against low sun angles for each camera type</td><td>Florida-relevant, inexpensive to run, and reported honestly far less often than it should be</td></tr>
      </tbody>
    </table>
  </div>

  <div class="placeholder-panel">
    <p><strong>Know the limits before you propose one.</strong> The automotive cameras are gated on the deserializer and driver path described above &mdash; confirm what the lab has before you plan around them. Pi camera ribbons are short, and longer ribbons degrade signal, so a camera far from its board wants a USB camera or a second board instead. Neither family is weatherproof as supplied: outdoor work needs an enclosure, a power plan, and, on public right-of-way, permission from whoever owns the pole or the property. Recording public space that contains identifiable faces or license plates means IRB approval before collection plus a written de-identification and retention plan &mdash; start that in the proposal, not after you have the footage. And image quality is the easiest thing in a pipeline to get wrong and the hardest to fix later: check exposure, focus, and mounting geometry on real target scenes before you collect a semester of unusable video.</p>
  </div>
</section>

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
