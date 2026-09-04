# 1.3 Convolution, and a network that sees

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.3</span>
    <span class="notes-card-session">Session: Sept 3</span>
  </div>
  <p class="notes-card-lede">The same neuron from sections 1.1 and 1.2, wired to reuse its weights. Convolution arrived at from a moving average you already trust, then a worked case: a stock detector meeting a child on a scooter on a real Tampa street. This is the first page where the mechanism stops being an idea and starts being a thing that can be wrong.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Convolution_Kernels_Companion.html" target="_blank" rel="noopener">Convolution kernels &#8599;</a></li>
      <li><a href="../_static/companions/Scooter_Kid_CNN_Case.html" target="_blank" rel="noopener">A child on a scooter, seen by a stock CNN detector &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab3_image_embeddings.html">Lab 3 &mdash; Image embeddings with a deep CNN</a></li>
      </ul>
    </div>
  </div>
</div>

(convolution-kernels)=
## Convolution: the same neuron, wired to reuse its weights

Everything above took a short vector as input — a density, a $v/c$ ratio, a gap,
a speed. A single 1920 × 1080 camera frame is **6,220,800** numbers. Wiring one
neuron to all of them, the way every layer so far has been wired, would cost
6.2 million weights for one unit, and the unit would have to learn "bumper at
this pixel" separately from "bumper at the pixel next to it."

You already avoid that problem once a week without calling it anything. A
five-minute moving average of detector speeds is the weight vector
$[0.2, 0.2, 0.2, 0.2, 0.2]$ slid along a time series: five numbers, reused at
every time step. That is a convolution. In two dimensions the same move is a
small template slid over every position of a grid:

$$
y[i,j] \;=\; \sum_{a=-1}^{1}\ \sum_{b=-1}^{1}\ k[a,b]\ \cdot\ x[i+a,\,j+b]
$$

where $x$ is the image as brightness, $k$ is the **kernel** — nine numbers, also
called the filter or the template — and $y[i,j]$ is one output pixel: what the
template found at that position. The output is a **feature map**, and it is the
same size as the input less a border, because the window needs a neighbour on
every side. (Strictly this is cross-correlation rather than the flipped
convolution of a signals course. Deep learning calls it convolution, and the
sign convention makes no difference to a template that gets learned.)

What the nine numbers say is what the template wants: positive weights mean "I
want brightness here," negative weights mean "and darkness there." A negative
left column against a positive right column computes *light on the right minus
light on the left*, which is zero on a flat wall and large on a sign pole, a
mast arm or the side of a truck. Rotate it and you get the horizontal-edge
detector that finds bumpers, the stop bar and the shadow line under a vehicle.
Put a single 1 off centre and the template does not detect anything at all — it
**moves** the image by one pixel, exactly, with maximum difference $0.0$ against
a plain array shift. Hold onto that one: a translation in a time–space diagram
is what Newell's car-following model does, and Module 7 takes it up again.

**Why this wiring instead of a dense layer.** On a 384 × 241 frame — the size
used in the companion below — a 3 × 3 kernel is **9** weights covering
**91,298** output positions. A dense layer producing the same output would need
**8,449,082,112** weights, a factor of roughly **939 million**. The second half
of the argument matters more in the field: shift the frame by one pixel, the way
a camera on a mast arm does in wind, and **61.8%** of the flattened pixel vector
changes. The dense layer sees a different input. The feature map just slides —
correlation **1.000000** after realigning by that same pixel. The kernel does not
care where the bumper is, which is why it needs one copy of the bumper template
instead of one per location.

**A layer is a bank of these, and then depth.** Apply four kernels to the same
frame in parallel and the image is replaced by a stack of four answers, for
$4 \times 9 = 36$ weights. ReLU then keeps one polarity of each answer — on a
daylight frame it zeroes about **45%** of the vertical-edge map and about **52%**
of the horizontal-edge map, but **0.0%** of a blurring kernel's output, which has
no negative side to throw away and is a hint that blurring is not detection.
Pooling halves the grid. A second-layer filter then sees the *stack*, not the
pixels, and its weights say which combination to look for: one that averages the
vertical and horizontal channels together fires where both edge types coincide,
which is what a bumper, a licence plate, a sign face and a wheel arch all have.
One value after that second layer depends on an **8 × 8** patch of the original
frame. Stack it a dozen more times and the receptive field covers a whole
vehicle, and the thing being detected is a vehicle. That is the entire
architecture; everything else is bookkeeping.

**What a trained network actually put in those nine numbers.** The first layer of
a trained ResNet-18 holds 64 filters of 7 × 7 × 3, **9,408** weights. Split each
one into the part all three colour channels agree on — a pure shape detector,
which is what a hand-typed kernel is — and the part they disagree on, **41 of the
56 live filters** are shape-dominant. Gradient descent, given nothing but
photographs and a loss, arrived at oriented edge detectors. The other **15** are
colour-opponent detectors that fire on a colour boundary where brightness is
flat: useful for photographs of objects, and not obviously what a night-time
roadside camera needs.

The remaining **8 of the 64 are dead**. Their largest weight is $5.7 \times
10^{-6}$ or less, against a median largest weight of **0.432** across the live
ones — five orders of magnitude down. They are not weak detectors; they output
zero on every input. **12.5%** of the first layer of one of the most-downloaded
checkpoints in computer vision does nothing at all, and no accuracy number
reports it. This is the dead-unit failure mode from the training section above,
shipped.

**Where the wiring stops being the right answer.** The whole construction assumes
the pattern is *local* and means the same thing everywhere. A shockwave can start
anywhere on a corridor, so a kernel fits. A bottleneck at a fixed milepost is a
property of that location, and a translation-invariant filter is built to ignore
precisely that — ask "would this pattern mean the same thing fifty pixels to the
left?" before reaching for a convolution. And a kernel measures contrast, not
importance: on equal-sized crops the vertical-edge kernel's mean response is
**45.85** on a night frame against **18.56** on a daylight one, 2.5 times larger,
because headlights and their wet reflections are enormous edges. The pedestrian
is the low-contrast shape between them.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Convolution kernels: how a network learns to see shape</span>
    <a href="../_static/companions/Convolution_Kernels_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Convolution_Kernels_Companion.html"
          title="Convolution kernels: how a network learns to see shape" loading="lazy"></iframe>
</div>

Type the nine numbers yourself on the first tab, click any output pixel to see
the nine multiplications behind it, then stack the kernels into a layer and
finally page through the 64 real filters — the dead ones included — on the third.

(scooter-kid-case)=
## A worked case: a child on a scooter, seen by a stock detector

Everything above is machinery. Here is thirteen seconds of it doing a real job,
on footage from this course rather than from a benchmark.

The clip is the forward camera of a Tesla driving under FSD on a residential
street in Florida — 1928 × 1208 pixels, 20 frames per second, **263 frames**,
recorded by the instructor. A child on a kick scooter comes toward the car. The
detector is `fasterrcnn_resnet50_fpn` with COCO weights, exactly as it downloads:
a ResNet-50 backbone of the kind you just took apart, a feature pyramid, a
region-proposal stage, and a head that picks one of **80** object classes. No
fine-tuning, no transportation data, no dashcam data, nothing about children. It
is the honest version of what an agency or a consultant reaches for first,
because it is free and it is five lines of code.

**What it got right, which is most of it.** It found the child at a box height of
36 pixels — roughly 74 m out — and held her for **111 consecutive frames with
zero gaps**, until she left the frame at a box height of 277 pixels. Its
confidence went from 0.65 at first sight past 0.90 within **3** frames. It found
both pedestrians standing on the shoulder. All **84** of its `fire hydrant`
detections are real hydrants. Judged as an object detector on video it had never
seen, this is a good result, and you should expect a good result: this is the
task the model was built for.

**What it did not give you is the whole lesson.** Three failures, none of them
bugs, all of them consequences of a vocabulary chosen years ago by people
solving a different problem.

The first is that **the word "child" does not exist in this model.** The output
is `person`, at a confidence of **1.00**. A five-year-old and a construction
flagger are the same output. Every property that would change a driving decision
— small, unpredictable, cannot be expected to yield, may accelerate into the lane
without looking — is invisible, and has to be supplied by whoever uses the model.
Notice that the score is no help here. A confident, correct, decision-irrelevant
label is more dangerous than an uncertain one, because it passes every threshold
check you would think to write.

The second is that **the scooter came out a skateboard**, in 17 detections up to
**0.93**, with the box correctly placed on the scooter. COCO's nearest words are
`skateboard`, `bicycle` and `motorcycle`; there is no `scooter`. The model is not
confused — it is answering the only question it was ever asked, which is which of
its 80 words fits best. And this near-miss turns out to be the *only* signal in
the model's output that separates the rider from an ordinary pedestrian, which is
a thin thread: the two shoulder pedestrians grow *larger* in the frame than the
child does, because the car drives past them, so "take the biggest track" picks
the wrong person.

The third matters most for agency work. A red-circle regulatory sign at the end
of the clip is reported as `stop sign` **35** times, peaking at **0.97**. There
is no stop sign anywhere in this clip. `stop sign` is COCO's only sign class —
no speed limit, no yield, no warning — so anything red and sign-shaped receives
the one available word, confidently. Run this pipeline over a fleet's video to
build a sign inventory and you have recorded a stop sign at a location that has
none, at 0.97, with no flag of any kind. The failure is silent, it is systematic
rather than random, and no accuracy number computed on COCO would surface it.

**And it gives you no distance.** A detector outputs a box and a word. Range,
closing speed and lane position — the three quantities a braking decision
actually needs — are not in the output. They can be *inferred* from the box, and
the companion does so, but only through

$$
Z \;=\; f \cdot H / h_{\text{px}}
$$

where $h_{\text{px}}$ is the measured box height, $f$ is the focal length in
pixels and $H$ is the object's true height. Neither $f$ nor $H$ is measured here,
so both are stated assumptions — a 50° field of view and a 1.30 m child — and
every distance scales linearly with the assumed height. Worse, the error is
worst where you need it most: at the far end **one pixel of box height is 2.05 m
of range**, and at the near end 0.035 m. That single fact is the whole argument
for radar, lidar or a stereo pair, and the reason a camera-only stack has to
learn a size prior for every class it cares about.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — A child on a scooter, seen by a stock CNN detector</span>
    <a href="../_static/companions/Scooter_Kid_CNN_Case.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Scooter_Kid_CNN_Case.html"
          title="A child on a scooter, seen by a stock CNN detector" loading="lazy"></iframe>
</div>

Step through the clip on the first tab and move the score threshold while you
watch — every detection above 0.05 was stored, so the slider filters results
rather than re-running anything. The second tab opens the backbone on one frame
of this footage: the same five stages, with the receptive field growing from 7
pixels to **267** and the share of values ReLU sets to zero rising from
**12.8%** to **78.4%**. In the first two rows you can still see the child; by
layer 2 the picture is gone and what remains is a handful of lit cells in
roughly the right place. Nothing in the network ever sees a child. Losing the
picture is the point — a representation that kept every pixel would have learned
nothing.

One last thing, because it is a habit worth forming. The camera is bolted to the
car, so the whole background slides sideways when the car turns, and phase
correlation between consecutive frames recovers that motion. After subtracting a
0.75 s moving average to remove the road's own curvature, the clip contains
exactly one real steering excursion — **3.82 °/s at frame 146**, while the child
was about 32 m ahead. The instructor's own account of driving it is that the car
"shook its direction laterally a little bit" as it passed her, and the
measurement is consistent with that account. It does not *prove* it. Image motion
cannot separate a steering command from a road crown, a pothole, a gust, or a
hand on the wheel, and the log that could settle it belongs to the manufacturer.
Keeping those two things apart — what you measured, and what you were told — is
most of what makes an analysis worth reading.

The detection machinery itself — proposals, non-maximum suppression, the
precision/recall trade-off, multi-camera tracking — is the Sept 10 session. This
case is here because it is the first place the convolution you just built stops
being an idea.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For "did anything move" on a fixed camera, the baseline
is frame differencing against a median background: no training, no GPU, no
labels. For counting and speed at a point, it is the loop or radar detector you
already have, which needs a calibration rather than a training set. A CNN earns
its keep when the question needs the *appearance* of the object, not its
presence.

**How was the data split, and why is that honest?** Frames from one clip are not
independent observations — consecutive frames five per second apart are nearly
the same picture. Split by clip, by site and by lighting condition, and say which
sites the model never saw. Two of the four frames in the companion are not US
roads, and the page says so rather than letting them stand as evidence.

**What does it do on the ugly cases?** Report the response on night, rain and
glare separately, not pooled. Count the dead filters. And check that a large
response means the right thing — the night frame above scores higher on edge
energy than the daylight one, and it is the harder scene.
:::

---

Next: {doc}`notes4-cnn-in-practice` &mdash; which architecture to pick, what it costs, and what a heat map does not prove.
