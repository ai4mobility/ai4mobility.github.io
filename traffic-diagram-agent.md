(traffic-diagram-agent)=
# Traffic State Diagram Agent: Try It

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility &middot; Live research prototype</div>
  <h2>Traffic State Diagram Agent <span>from a short account to a kinematic-wave diagram</span></h2>
  <p>Describe a crash, a lane closure, a slow vehicle or a merge in a few sentences, the way you would report it to a traffic management center. The agent draws the fundamental diagram and the time-space diagram, gives the key numbers (when the queue forms, how far back it reaches, when it clears) and lists everything it assumed.</p>
  <div class="resource-meta">
    <span>Free to try, no sign-in</span>
    <span>Every diagram is checked against kinematic wave theory</span>
    <span>For teaching and research, not for operational decisions</span>
  </div>
</section>

<div class="cta-row resource-cta-row">
  <a class="cta-button" href="https://kw-diagram-agent.onrender.com/" target="_blank" rel="noopener">Open the agent in a new tab</a>
  <a class="cta-button cta-secondary" href="#kw-write">How to write your account</a>
  <a class="cta-button" href="#kw-examples">See six examples</a>
</div>

## Try it

Type your account in the box, or click one of the examples under it. A diagram usually takes one
to four minutes. If something essential is missing (how many lanes, how much of the road was blocked, for
how long), the agent asks you once; everything else it assumes and tells you.

<div class="companion-embed kw-embed">
  <div class="companion-embed-bar">
    <span>Traffic State Diagram Agent (live)</span>
    <a href="https://kw-diagram-agent.onrender.com/" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe id="kw-agent-frame" src="https://kw-diagram-agent.onrender.com/"
          title="Traffic State Diagram Agent" loading="lazy" style="height: 1150px;"></iframe>
</div>

<script>
(function () {
  // Size the frame to the agent's page, and pass on where the visitor came from (for example ?from=linkedin).
  var frame = document.getElementById("kw-agent-frame");
  if (!frame) return;
  try {
    var tag = new URLSearchParams(window.location.search).get("from");
    if (tag) frame.src = "https://kw-diagram-agent.onrender.com/?from=" + encodeURIComponent(tag.slice(0, 40));
  } catch (e) {}
  window.addEventListener("message", function (ev) {
    if (ev.origin !== "https://kw-diagram-agent.onrender.com") return;
    var d = ev.data || {};
    if (d.type === "kw-height" && typeof d.height === "number" && d.height > 300 && d.height < 20000) {
      frame.style.height = Math.ceil(d.height + 8) + "px";
    }
  });
})();
</script>

<div id="kw-write"></div>

## How to write your account

Write it the way you would tell a colleague at the TMC. Plain words, clock times and mile markers are all
fine. The more of the first three rows you give, the fewer questions the agent asks.

| Say... | For example | If you leave it out |
|---|---|---|
| **The road and how many lanes** in your direction | "I-75 northbound, three lanes" | The agent asks |
| **What happened and how much of the road it took** | "a crash blocks the right lane", "the bridge stops all traffic", "a load at 30 mph in the right lane" | The agent asks |
| **When it started and ended**, or how long | "from 4:40 to 5:10 PM", "for about 40 minutes" | The agent asks |
| **How much traffic** was coming | "about 5,200 veh/h", "heavy traffic", "the backup reached 2 miles" | Moderate traffic is assumed, or enough to cause the backup you report |
| The posted **speed limit** | "posted 65" | 75 mi/h is assumed |
| **Lane drops and ramps** nearby | "no lane changes nearby"; "half a mile past the SR 56 on-ramp, which brings about 700 veh/h" | None is assumed |
| **What you want to know** | "when is the road back to normal?", "compare midday with 3 to 4 PM" | The agent explains the whole diagram |

Two tips. A reported backup is useful: "the backup was about 2 miles when they reopened" lets the agent work
out how much traffic was coming, so it does not have to guess. And you can ask for a comparison in one
account ("with and without ramp metering"); the agent draws one diagram for each.

After the diagram appears, you can correct any assumption ("it was four lanes", "use 5,000 veh/h") and the
agent redraws.

<div id="kw-examples"></div>

## Six examples

Each example below is an account in the style of a traffic management center report, the diagram the agent
drew, and the key numbers. The accounts were written for testing; they are not real FDOT incidents.

The diagrams come from our test of November 21, 2026, in which a fresh copy of the agent (Claude Sonnet 5.5)
had only its skill and its tools, and no example of the same case. Every diagram passed the check against
kinematic wave theory, and each one matches the diagram we drew ourselves for the same account.

**How to read a diagram.** The left panel is the fundamental diagram: each dot is a traffic state (flow
against density), and the slope of a line between two dots is the speed of the wave between them. The right
panel is the time-space diagram: time runs left to right, distance in the direction of travel runs bottom to
top, and each colored region is one traffic state. Yellow, orange and red regions are queues (the darker, the
denser; red is stopped traffic), and green regions are traffic leaving a queue. The assumptions are printed
under each figure.

### 1. A crash, with everything given

> I-4 eastbound at mile marker 14. A crash at 4:40 PM blocked the two right lanes of four. All lanes were
> open again at 5:10 PM. The detector upstream was reading about 5,200 vehicles an hour before the crash. The
> speed limit there is 65. Show me how the queue builds and when the road is back to normal.

*What it shows:* a complete account. The agent asked only whether the number of lanes changes nearby
(answer: "No, it is four lanes for several miles on either side"); the live page now assumes it does not
unless you say so.

```{figure} _static/figures/KWA_Crash_Two_Of_Four.png
:alt: Fundamental diagram and time-space diagram for a crash that blocks two of four lanes from 16:40 to 17:10. Behind the crash a queue (orange, state U) grows upstream; when the lanes reopen, discharge at capacity (state C) runs back through the queue and meets its back at 17:28, about 4.5 miles upstream.
:width: 100%

Key numbers: a queue first forms at 16:40. It is longest at 17:28, just as it clears: its back is then
4.5 mi upstream of the crash. The queue is gone by 17:28.
```

### 2. A one-line report

> Vehicle fire on I-75 southbound at MM 262. The right lane is closed and traffic is backing up.

*What it shows:* a short report is enough to start. The agent asked one round of questions. The answer was:
"Three lanes, no lane drop nearby. It started around 2:10 PM and fire rescue reopened the lane at 2:50. I
don't have a count, but the backup was about 2 miles long when they reopened. Posted speed is 70." The agent
then worked out the arriving traffic (about 4,140 veh/h) from the reported backup instead of guessing it.

```{figure} _static/figures/KWA_Vehicle_Fire.png
:alt: Fundamental diagram and time-space diagram for a vehicle fire that closes one of three lanes from 14:10 to 14:50. The queue behind the fire grows upstream; after the lane reopens, discharge at capacity meets the back of the queue at 15:00.
:width: 100%

Key numbers: a queue first forms at 14:10. It is longest at 15:00, just as it clears: its back is then
2.5 mi upstream of the fire. The queue is gone by 15:00.
```

### 3. A drawbridge on an arterial, twice

> We have a drawbridge on a four-lane arterial, two lanes northbound, posted 35 mph, no lane changes on the
> approach. On Saturday the bridge opens for boat traffic at 11:00 and again at 11:30, and each opening stops
> traffic for 6 minutes. Northbound volume on Saturdays is about 1,400 veh/h. Does the queue from the first
> opening clear before the second one? Draw the northbound approach.

*What it shows:* full stops (a jam behind the bridge, an empty road ahead of it), a repeated event, and a
yes-or-no question. Answer: yes, the first queue is gone by 11:09, well before the second opening.

```{figure} _static/figures/KWA_Drawbridge.png
:alt: Fundamental diagram and time-space diagram for a drawbridge that stops two northbound lanes from 11:00 to 11:06 and from 11:30 to 11:36. Each opening creates a stopped queue (red, state J) and an empty road ahead (state O); each queue discharges at capacity and is gone a few minutes after the bridge closes.
:width: 100%

Key numbers: a queue first forms at 11:00. At its longest, at 11:09, its back is 0.84 mi upstream of the
bridge. The second queue is gone by 11:39.
```

### 4. A slow oversize load

> A permitted oversize load will move on I-75 northbound tomorrow. It enters at MM 240 at 10:00 AM and leaves
> at MM 250, travelling 30 mph in the right lane. Three lanes, posted 70, no lane changes on that stretch.
> Midday volume there is about 4,300 veh/h. What does traffic look like behind it, and how long after it exits
> before things are back to normal?

*What it shows:* a moving bottleneck. The queue travels with the load; when the load exits, the queue
discharges and is gone four minutes later.

```{figure} _static/figures/KWA_Oversize_Load.png
:alt: Fundamental diagram and time-space diagram for an oversize load moving at 30 mph in one of three lanes from mile 240 to mile 250. A queue (state U) follows the load and grows; ahead of the load, lighter traffic (state D) runs at free speed; after the load exits at 10:20 the queue discharges at capacity and clears by 10:24.
:width: 100%

Key numbers: a queue first forms at 10:00. The queue moves with the load and is longest at 10:20: about
2.7 mi long. The queue is gone by 10:24.
```

### 5. A work zone: which time of day?

> We are planning bridge joint repair on I-275 southbound: the right lane closed for 1.5 miles starting at the
> Bearss Ave overpass. Three lanes there, posted 55, no other lane changes nearby. We can do it midday, 10 AM
> to 2 PM, when volume is about 3,000 veh/h, or we can take one hour from 3 to 4 PM when volume is about
> 4,000. Which one backs up, and how bad is it?

*What it shows:* a what-if comparison, drawn as two diagrams. Two open lanes carry about 3,536 veh/h. At
midday 3,000 veh/h arrive, so nothing is held back and that diagram shows no queue at all. From 3 to 4 PM,
4,000 veh/h arrive and a queue builds; this is the diagram below.

```{figure} _static/figures/KWA_Work_Zone_PM.png
:alt: Fundamental diagram and time-space diagram for a lane closure from 15:00 to 16:00 with 4,000 veh/h arriving. A queue grows upstream of the overpass; after the lane reopens at 16:00 the discharge meets the back of the queue at 16:17, about 4.2 miles upstream.
:width: 100%

The 3 to 4 PM option. Key numbers: a queue first forms at 15:00. It is longest at 16:17, just as it clears:
its back is then 4.2 mi upstream of the overpass. The queue is gone by 16:17. (Midday option: no queue
forms.)
```

### 6. A crash just past an on-ramp

> Crash on I-75 northbound about half a mile past the SR 56 on-ramp, one of three lanes blocked from 7:15 to
> 7:45 AM. The mainline was carrying about 4,000 veh/h and the ramp about 700. Posted 70, no lane changes
> nearby. Does the backup get to the ramp, and what happens to the ramp traffic and to the mainline behind it?

*What it shows:* a merge. The backup reaches the ramp about four minutes after the crash; from then on the
ramp and the mainline take turns (the zipper rule, assumed because the account did not say who has priority),
so both queue. The lower panels show the merge and the ramp's own flow.

```{figure} _static/figures/KWA_Crash_Past_On_Ramp.png
:alt: Fundamental diagram, time-space diagram, merge diagram and ramp flow for a crash half a mile past an on-ramp, one of three lanes blocked from 7:15 to 7:45. The queue from the crash reaches the merge, after which the mainline queue (states U1, U2, U3) grows upstream of the merge and the ramp flow drops below its demand; the queue is gone at 8:19.
:width: 100%

Key numbers: a queue first forms at 07:15. At its longest, at 08:00, its back is 3.9 mi upstream of the
crash. The queue is gone by 08:19.
```

## What it can and cannot draw

**Can:** crashes and lane closures, full stops and traffic signals, a slow vehicle, a lane drop, a
speed-limit zone, on-ramps (zipper merge or ramp priority) and off-ramps, an arriving volume that changes in
steps, and with-and-without comparisons.

**Cannot (yet):** stop-and-go waves that grow by themselves, speed limits switched on along a stretch during
an incident, networks of several roads, and totals such as delay or travel time. It uses a triangular
fundamental diagram, and it does not consider a capacity drop unless you mention one.

## How it works

The agent is an AI model (Claude Sonnet 5.5) that follows a **skill**: Prof. Hao Zhou's procedure for drawing
traffic state diagrams, written down step by step (see {doc}`Module 6 on skills <module6/index>` and
{doc}`Transportation Skills <skills>`). The model does the reasoning: which traffic states appear, and on which
side of each wave. **Tools** do everything that must be exact: the states on the fundamental diagram, wave
speeds, where waves meet, and the drawing.

Before you see a diagram, a final tool checks it against kinematic wave theory, including an independent
numerical solution of the same problem. If the model cannot get a diagram through that check, a stronger
model (Claude Opus 5.5) starts again; if that also fails, the tools' own solver draws the diagram and the page
says so. A diagram that fails the check is never shown as an answer.

## Credits and contact

Built on Prof. Hao Zhou's procedure for drawing traffic state diagrams, with examples from *Traffic Flow
Theory* by Prof. Jorge Laval at Georgia Tech.

**What is stored.** The account you type, the diagram and answer, your feedback, the time, and the
approximate network address of your visit. We use them to improve the agent. Please do not enter personal
information.

**Contact.** Hao Zhou, Ph.D., Assistant Professor, CEE Department, University of South Florida,
<a href="mailto:haozhou1@usf.edu">haozhou1@usf.edu</a>. Lab website:
<a href="https://www.motiflab.net" target="_blank" rel="noopener">www.motiflab.net</a>.
