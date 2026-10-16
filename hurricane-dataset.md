(hurricane-dataset)=
# Course Dataset: Florida Hurricane Transportation Posts

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility &middot; Course dataset</div>
  <h2>Hurricane Transportation Posts <span>Helene and Milton, 2024</span></h2>
  <p>2,425 real posts from X (Twitter) about roads, bridges, evacuation traffic, fuel, transit and airports during Hurricanes Helene and Milton, each with the images its author attached. Two views of the same moment, the words and the pixels, for text models, image models and models that combine the two.</p>
  <div class="resource-meta">
    <span>2,425 posts &middot; 3,348 images</span>
    <span>Download on Canvas only</span>
    <span>Last updated: October 2026</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>Where to get it.</strong> The data files are <strong>not</strong> on this website. Students enrolled in CGN 6933 download <code>hurricane_transport_posts_v2.zip</code> (177&nbsp;MB) from the course Canvas site, which needs a USF login. This page describes what is in the zip, how it was built, and what to watch out for before you model it.</p>
</div>

When Hurricanes Helene and Milton hit Florida in the fall of 2024, residents, cities, FDOT, transit
agencies and newsrooms posted about closed bridges, flooded roads, evacuation traffic and empty gas
pumps, and they usually attached a picture. This dataset collects **2,425 of those posts**, each with
the images its author attached.

Every post gives you **two views of the same moment: the words and the pixels**. That is what you
need to try a text encoder (BERT, {doc}`2.5 <module2/notes5-bert>`), an image encoder (ViT, CLIP,
{doc}`2.7 <module2/notes7-vision>`), and models that combine the two on the same items
({doc}`2.9 <module2/notes9-cross-attention>`), and to ask
a question an agency would care about: *when does the picture tell you something the words do not?*

```{figure} _static/figures/HT_Dataset_Examples.jpg
:alt: Eight example posts, each with its image, post ID, storm, time window and automatic image label, and the start of its text. Top row, four photos: a gas pump with a sign saying 87 and 89 octane are out (HT0109); Manasota Key Road washed out beside the beach (HT0628); a traffic camera on northbound I-75 during the Milton evacuation (HT1501); a traffic camera on I-275 at the Howard Frankland Bridge with construction barges moored for the storm (HT1629). Bottom row: a "Traffic light out? Treat it as a 4-way stop" graphic (HT0470); a "Tolls suspended" graphic from the Tampa Hillsborough Expressway Authority (HT1084); a Jacksonville Transportation Authority bus with a "Detour" banner (HT2048); and an FDOT/511 map of a closed section of Dunlawton Avenue with its detour (HT2204), which the automatic label wrongly calls a graphic.
:width: 100%

Eight of the 2,425 posts. Some images show what the text says, many repeat the text as a graphic,
and some add what the text never mentions.
```

<section class="resource-section" id="at-a-glance">
  <div class="resource-section-header">
    <h2>At a Glance</h2>
    <span>Sept 20 &ndash; Oct 26, 2024</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr><th style="width:24%">Count</th><th>What it is</th></tr>
      </thead>
      <tbody>
        <tr><td><strong>2,425</strong> posts</td><td>Original posts (no reposts or replies), each with 1&ndash;4 images</td></tr>
        <tr><td><strong>3,348</strong> images</td><td>Resized to at most 512 px on the long side, metadata removed</td></tr>
        <tr><td><strong>1,146</strong> accounts</td><td>Residents, cities and counties, FDOT, transit agencies, airports, newsrooms</td></tr>
        <tr><td><strong>1,039</strong> / <strong>1,386</strong></td><td>Posts directly / indirectly about transportation (<code>transport_relevance</code>)</td></tr>
      </tbody>
    </table>
  </div>
</section>

<div class="placeholder-panel">
  <p><strong>Terms of use.</strong> Use the files only for CGN 6933 coursework (exercises, assignments and your class project), on your own device, your own Google Drive or Colab. Do not redistribute them: no public GitHub, Kaggle, Hugging Face or shared drives &mdash; publish your code and results, not the data. These were public posts, but their authors did not write them for this class: do not search for the original posts or try to identify anyone. If you find anything that looks like personal information or inappropriate content, stop and tell the instructor. Delete your copy at the end of the semester.</p>
</div>

## Getting started

Unzip the file from Canvas and you get one folder:

```text
hurricane_transport_posts/
  posts.csv      one row per post, 2,425 rows, 29 columns
  images/        HT0001_1.jpg ... HT2425_1.jpg  (3,348 images)
  index.html     open in your browser to scroll and filter every post with its images
  README.md      the full data card: every column, how the data was built, every caveat
```

**Look before you model.** Open `index.html` from the unzipped folder. Filter by storm, time window,
image kind and relevance, or search the text for *bridge*, *I-75*, *fuel* or *bus*. Ten minutes of
browsing will tell you more about this data than any summary table.

**Load it in Colab.** Put the zip in your Google Drive once, then:

```ipython
from google.colab import drive
drive.mount('/content/drive')
!unzip -q "/content/drive/MyDrive/hurricane_transport_posts_v2.zip" -d /content

import pandas as pd
from PIL import Image
folder = "/content/hurricane_transport_posts/"
df = pd.read_csv(folder + "posts.csv")
row = df.iloc[0]
print(row.text)
images = [Image.open(folder + p) for p in row.image_files.split(";")]   # all images of the post
Image.open(folder + row.image_file)                                     # show the first one
```

On your own laptop, skip the first three lines and set `folder` to wherever you unzipped it.

## What is in it

Helene made landfall near Perry around 11:10 p.m. EDT on September 26; Milton near Siesta Key around
8:30 p.m. EDT on October 9. Each post falls in one time window:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:44%">Storm, window</th><th>Posts</th><th>Photos</th><th>Graphics</th><th>Maps</th></tr>
    </thead>
    <tbody>
      <tr><td>Helene, pre-landfall (Sept 20&ndash;25)</td><td>285</td><td>51</td><td>88</td><td>146</td></tr>
      <tr><td>Helene, landfall and after (Sept 26 &ndash; Oct 1)</td><td>457</td><td>192</td><td>143</td><td>122</td></tr>
      <tr><td>Milton, pre-landfall (Oct 2&ndash;8)</td><td>872</td><td>191</td><td>326</td><td>355</td></tr>
      <tr><td>Milton, landfall and after (Oct 9&ndash;17)</td><td>762</td><td>331</td><td>268</td><td>163</td></tr>
      <tr><td>Milton, late aftermath (Oct 18&ndash;26)</td><td>49</td><td>23</td><td>20</td><td>6</td></tr>
      <tr><td><strong>All</strong></td><td><strong>2,425</strong></td><td><strong>788</strong></td><td><strong>845</strong></td><td><strong>792</strong></td></tr>
    </tbody>
  </table>
</div>

Photo / graphic / map is an automatic guess on each post's first image (column `image_kind_auto`).
Windows are calendar days in UTC.

<h3 class="resource-subhead">The columns you will use most</h3>

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:36%">Column</th><th>What it holds</th></tr>
    </thead>
    <tbody>
      <tr><td><code>post_id</code></td><td><code>HT0001</code>&ndash;<code>HT2425</code>, in time order</td></tr>
      <tr><td><code>storm</code>, <code>window</code></td><td>Helene or Milton; <code>pre_landfall</code>, <code>landfall_and_after</code> or <code>late_aftermath</code></td></tr>
      <tr><td><code>hours_from_landfall</code>, <code>before_landfall</code></td><td>Exact timing against that storm's landfall (negative = before)</td></tr>
      <tr><td><code>text</code></td><td>The post, with <code>@USER</code> and <code>HTTPURL</code> in place of account handles and links</td></tr>
      <tr><td><code>image_file</code>, <code>image_files</code></td><td>The first image, and all images separated by <code>;</code></td></tr>
      <tr><td><code>image_kind_auto</code></td><td><code>photo</code>, <code>graphic</code> or <code>map</code>: a CLIP guess, not checked by a person</td></tr>
      <tr><td><code>transport_relevance</code>, <code>relevance_source</code></td><td><code>direct</code> or <code>indirect</code>, and how that was judged (see below)</td></tr>
      <tr><td><code>author_id</code>, <code>lookalike_group</code></td><td>A random code per account, and a shared code for posts whose images look nearly identical. Use both when you split train and test</td></tr>
    </tbody>
  </table>
</div>

The README in the zip describes all 29 columns, including engagement counts, keyword topics and
Brandwatch's sentiment label.

## How it was built

The source is a Brandwatch export of Florida-located X posts. Each step kept fewer posts:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:70%">Step</th><th>Posts left</th></tr>
    </thead>
    <tbody>
      <tr><td>All unique posts, Sept 20 &ndash; Oct 26</td><td>969,867</td></tr>
      <tr><td>Originals only (no reposts, replies or quotes)</td><td>129,911</td></tr>
      <tr><td>&hellip; with at least one image</td><td>45,106</td></tr>
      <tr><td>&hellip; whose text has a transportation word (road, bridge, I-##, traffic, evacuat-, fuel, airport, bus, FDOT, &hellip;)</td><td>3,573</td></tr>
      <tr><td>Repeated images and identical texts removed; images no longer online dropped; sexual or spam content removed</td><td>3,419</td></tr>
      <tr><td><strong>Read and judged to be about transportation</strong></td><td><strong>2,425</strong></td></tr>
    </tbody>
  </table>
</div>

The last step matters. The keyword filter alone let in a lot that has nothing to do with
transportation: high-school teams playing *on the road*, a *donation drive*, a *long road to
recovery*, automated river warnings named after the highway bridge where the gauge sits. So every
post's text was read and labeled `direct`, `indirect` or `not` about transportation, and the 994
`not` posts were removed. **That reading was done by an AI model (Claude), from the text only.** An
independent second pass on 100 posts agreed on 85 of the labels. The 196 posts marked
`relevance_source = text_and_image` were also reviewed with their images and are the most carefully
labeled subset.

Account handles became `@USER`, links became `HTTPURL`, author names became random codes, and images
were shrunk to 512 px with their metadata removed. No links to the original posts are included.

## Six things that will bite you

1. **The labels are weak.** `transport_relevance` is an AI's reading of the text, `image_kind_auto`
   is CLIP's guess, `bw_sentiment` is Brandwatch's own text model. They are good enough to filter on
   or to start with. They are not ground truth, and a model that "beats" them may only have learned
   their mistakes.
2. **A few accounts post a lot.** One account has 68 posts, two others 40 and 35, and agencies reuse
   the same templates. **Split train and test by `author_id`** and keep each `lookalike_group` on one
   side, or your test set will be full of near-copies of your training set.
3. **The window is not the landfall.** The "landfall and after" window starts the day before
   landfall: 246 of Helene's 457 and 310 of Milton's 762 posts in that window were written *before*
   landfall. If your question is before vs. after, use `before_landfall`.
4. **Most images are not photos.** About two thirds are graphics or maps, and many graphics are the
   post's text again, rendered as pixels. A model that can read printed words (CLIP) will look much
   smarter on these than one that cannot (a ViT trained on ImageNet). Report photos and graphics
   separately.
5. **A picture is not proof.** Old photos from earlier storms, photos from other states, screenshots
   of TV and apps, and memes all appear. The image is what the author chose to attach.
6. **This is not a sample of hurricane Twitter.** It is a keyword-filtered slice of an export that was
   capped near 50,000 posts per time block. Never quote a percentage from it as a fact about how
   Floridians posted during the storms.

## What you can do with it

You may use this dataset in this course's exercises and in your class project. A few questions it can
answer, matched to what the course covers:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:22%">Course topic</th><th>Try this</th></tr>
    </thead>
    <tbody>
      <tr><td>Tokens</td><td><code>bert-base-uncased</code> splits <em>impassable</em> into <code>imp</code> &middot; <code>##ass</code> &middot; <code>##able</code> and <em>#HurricaneMilton</em> into <code>#</code> &middot; <code>hurricane</code> &middot; <code>##mi</code> &middot; <code>##lton</code>. What happens to <em>I-275</em>, <em>SR-60</em> or <em>Howard Frankland</em>, and does a tokenizer trained on tweets do better?</td></tr>
      <tr><td>BERT on text</td><td>Predict <code>before_landfall</code> or <code>transport_relevance</code> from the text alone. Run a TF-IDF + logistic regression baseline first, split by author.</td></tr>
      <tr><td>ViT and CLIP on images</td><td>Embed the images with a ViT trained on ImageNet and with CLIP's image encoder. Pick a flooded-road photo and compare its nearest neighbours in the two spaces. Which one groups images by object, and which by event?</td></tr>
      <tr><td>Multimodal fusion</td><td>Does adding the image improve a text-only classifier? Check photos and graphics separately, because the answer is probably different.</td></tr>
      <tr><td>Cross-attention</td><td>Hide the pairing and ask a model to find each post's own image among 100. Compare a dual encoder (CLIP) with a model whose words cross-attend to the image patches (BLIP).</td></tr>
      <tr><td>Class project</td><td>A triage tool that flags posts reporting a road condition (flooding, closure, debris, signals out) for a traffic management center, evaluated on an author-and-lookalike split. For bigger questions, see the <a href="#hurricane-research-directions">five research directions</a> below.</td></tr>
    </tbody>
  </table>
</div>

(hurricane-research-directions)=
## Five research directions

The table above lists exercises. These five directions are bigger. Each one asks a question the
research literature has not settled, is small enough for a class project, and could become a
conference or journal paper if the results hold up. Each card gives the key question, a first look
at the data, why the answer matters beyond this course, and what it would take to turn the project
into a paper. Treat them as starting points and reshape them to fit your team.

```{figure} _static/figures/HT_Research_Directions.png
:alt: A six-stage agency pipeline drawn left to right. Posts and images; About a road? (classification); What, and how bad? (classification); Where, exactly? (extraction); New, and real? (retrieval); Send crews, inform public (judgment). Below it, five numbered research directions, each linked to the stage it studies. 1, What does the picture add? (affect vs. severity; fusion, cross-attention) links to the road filter and the severity stage. 2, A general model, or our labels? (transport damage types; CLIP, VLM, ViT) links to the severity stage. 3, Where on the road network? (place names to roads; NER, LLM, OSM) links to the location stage. 4, Worth monitoring? (posts vs. NWS reports; lead time, coverage) links to the verification stage. 5, Do agencies answer in time? (the messaging gap; BERTweet, LLM labels) links to the action stage.
:width: 100%

Where each direction sits. The numbers match the cards below.
```

<div class="notes-card">
  <div class="notes-card-head"><span class="notes-card-eyebrow">Direction 1 &middot; What does the picture add?</span><span class="notes-card-session">Text + image &middot; fusion &middot; cross-attention</span></div>
  <p class="notes-card-lede"><strong>Key question.</strong> Does the image tell you how severe a transportation impact is when the text does not, and does combining text and image help mainly when the caption is short or neutral?</p>
  <p class="notes-card-lede"><strong>A first look.</strong> HT2348's text mentions sand on a barrier-island street; only the photo shows how much. HT1982's text names a damaged road but not what happened to it, and the AI relevance review judged it not about transportation; the photo shows power poles down across the road. Brandwatch's text-based label calls photo posts negative about twice as often as graphics (19.5% vs. 8.9%), but that may only mean photos come from people on the scene.</p>
  <div class="notes-card-cols" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><h4>Why it matters</h4><ul>
      <li>Multimodal crisis datasets such as <a href="https://crisisnlp.qcri.org/crisismmd" target="_blank" rel="noopener">CrisisMMD</a> label whether a post is informative, its humanitarian category and its damage severity. Their labels do not separate how the author feels from how bad the situation is, and they do not ask whether a road is passable, which is what an agency acts on.</li>
      <li>CrisisMMD labeled each post's text and image separately, and fusion studies on it often keep only the posts where the two labels agree. That drops exactly the cases where one modality adds something. Labeling the same posts with and without the image measures what each modality contributes instead of assuming it.</li>
    </ul></div>
    <div><h4>Toward a paper</h4><ul>
      <li>Two labels per post, author affect and impact severity (with passability), each assigned once from the text alone and once with the image, on about 400 photo posts, by two people, with agreement reported.</li>
      <li>Text-only, image-only, late-fusion and cross-attention (BLIP) models on an author-and-lookalike split, with photos and graphics reported separately.</li>
      <li>Show where fusion helps, by caption length and by how neutral the text is.</li>
    </ul></div>
  </div>
  <p class="notes-card-lede" style="font-size:0.88rem;margin:0.7rem 0 0.2rem"><strong>Beyond the zip:</strong> only your labels. <strong>Course tools:</strong> BERT, CLIP, BLIP (Module 2). <strong>Possible venues:</strong> Transportation Research Part C; Computer-Aided Civil and Infrastructure Engineering; ISCRAM.</p>
</div>

<div class="notes-card">
  <div class="notes-card-head"><span class="notes-card-eyebrow">Direction 2 &middot; A general model, or our labels?</span><span class="notes-card-session">Images &middot; CLIP &middot; VLMs &middot; ViT fine-tuning</span></div>
  <p class="notes-card-lede"><strong>Key question.</strong> How well do general-purpose vision-language models recognize transportation-specific hurricane impacts (flooded lanes, trees or debris across a road, downed lines, damaged signals, washouts and sand overwash, closed bridges, fuel outages) with no training, and how many labeled examples does a small fine-tuned model need to beat them?</p>
  <p class="notes-card-lede"><strong>A first look.</strong> In HT2199 the wind has spun traffic signal heads to face the wrong way. The text calls them street lights and Brandwatch calls the post neutral; nothing in the words matches how an agency would log it, as signal damage. 788 posts have a photo as their first image (by the automatic guess), so there is plenty to label.</p>
  <div class="notes-card-cols" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><h4>Why it matters</h4><ul>
      <li>General crisis taxonomies put roads, bridges, power lines and buildings into one &ldquo;infrastructure damage&rdquo; class. Agencies dispatch crews by asset type and by whether a road is passable.</li>
      <li>A label-efficiency curve (no labels, then 10, 50 and 200 per class) answers a practical question every agency faces: use an off-the-shelf model, or invest in labeling? It is a clean test of this course's recurring question, when a general model needs domain adaptation.</li>
    </ul></div>
    <div><h4>Toward a paper</h4><ul>
      <li>A transportation impact taxonomy grounded in what an agency's damage assessment teams record, with a written codebook.</li>
      <li>About 600 photos labeled by two people. Zero-shot CLIP and an open vision-language model with several prompt wordings, against linear probes and a fine-tuned ViT at each label budget.</li>
      <li>An error analysis of what gets confused and why, such as a flooded road against a flooded parking lot.</li>
    </ul></div>
  </div>
  <p class="notes-card-lede" style="font-size:0.88rem;margin:0.7rem 0 0.2rem"><strong>Beyond the zip:</strong> your labels; optionally CrisisMMD's images for extra training data. <strong>Course tools:</strong> CLIP zero-shot (Module 2), ViT fine-tuning (Lab 6). <strong>Possible venues:</strong> Transportation Research Record; Journal of Infrastructure Systems; Computer-Aided Civil and Infrastructure Engineering.</p>
</div>

<div class="notes-card">
  <div class="notes-card-head"><span class="notes-card-eyebrow">Direction 3 &middot; Where on the road network?</span><span class="notes-card-session">Text &middot; tokens &middot; entity extraction &middot; OSM</span></div>
  <p class="notes-card-lede"><strong>Key question.</strong> How precisely can a road-impact post be placed on the road network from its text (route numbers, street names, bridges, cross streets), its image (signs, landmarks) and the author's city, and what share of posts can be placed precisely enough to send a crew?</p>
  <p class="notes-card-lede"><strong>A first look.</strong> A simple pattern finds a named route, street or bridge in only about 1 post in 10, and in about 1 in 5 road-impact photos from the four days after landfall. 690 posts have no city at all. Location, not detection, may be what limits an agency's use of these posts.</p>
  <div class="notes-card-cols" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><h4>Why it matters</h4><ul>
      <li>Geotagged posts are rare, so location has to be read from the content. General named-entity recognizers are built for people, organizations and cities, not for &ldquo;I-275 northbound at the Howard Frankland&rdquo; or &ldquo;SR-60&rdquo;, and tokenizers break those names into pieces (the Tokens exercise above).</li>
      <li>Linking the extracted names to OpenStreetMap or a state road inventory is entity linking adapted to transportation, with an accuracy measure an agency understands: right road, right segment, within so many meters.</li>
    </ul></div>
    <div><h4>Toward a paper</h4><ul>
      <li>About 300 posts geocoded by hand (road, segment, point) as ground truth.</li>
      <li>A gazetteer-and-rules baseline against a general named-entity model, a fine-tuned BERT token classifier and an LLM extractor. Report the share placed on the right road and within 0.5 km.</li>
      <li>A test of whether the image (a sign, a landmark) adds anything to the text.</li>
    </ul></div>
  </div>
  <p class="notes-card-lede" style="font-size:0.88rem;margin:0.7rem 0 0.2rem"><strong>Beyond the zip:</strong> OpenStreetMap roads for Florida (public). <strong>Course tools:</strong> tokenization, BERT token classification, LLM extraction. <strong>Possible venues:</strong> Transportation Research Record; Transactions in GIS; ISCRAM.</p>
</div>

<div class="notes-card">
  <div class="notes-card-head"><span class="notes-card-eyebrow">Direction 4 &middot; Worth monitoring?</span><span class="notes-card-session">Posts vs. official reports &middot; lead time</span></div>
  <p class="notes-card-lede"><strong>Key question.</strong> For road flooding and closures during Helene and Milton, how often did a post appear before the matching official report, and how often was there no official report at all?</p>
  <p class="notes-card-lede"><strong>A first look.</strong> 51 posts are automated relays of National Weather Service storm reports, and a few of those official reports name a social media post as their own source. The official record already leans on the public; the question is by how much, and how early.</p>
  <div class="notes-card-cols" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><h4>Why it matters</h4><ul>
      <li>The amount of posting tracks damage at the level of whole areas (<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4803483" target="_blank" rel="noopener">Kryvasheyeu et al., 2016</a>, Hurricane Sandy). Whether individual posts add timely, locatable road information that official channels miss is still open, and it is the question that decides whether an agency should pay for monitoring.</li>
      <li>A lead time and a coverage rate are numbers a traffic management center can weigh against analyst hours.</li>
    </ul></div>
    <div><h4>Toward a paper</h4><ul>
      <li>NWS Local Storm Reports for Florida, Sept 20 &ndash; Oct 26 2024, from the public <a href="https://mesonet.agron.iastate.edu/request/gis/lsrs.phtml" target="_blank" rel="noopener">Iowa Environmental Mesonet archive</a>.</li>
      <li>Posts matched to reports by impact type, place and time (Direction 3 gives you the places), giving a lead time and the share of reports a post anticipated.</li>
      <li>False alarms per hour reported as the cost side.</li>
    </ul></div>
  </div>
  <p class="notes-card-lede" style="font-size:0.88rem;margin:0.7rem 0 0.2rem"><strong>Beyond the zip:</strong> NWS reports (public); closure logs from FL511 or a traffic management center would make it stronger, so ask the instructor. <strong>Watch out:</strong> the capped export undercounts posts, so coverage numbers are lower bounds. <strong>Possible venues:</strong> Natural Hazards Review; International Journal of Disaster Risk Reduction; Transportation Research Record.</p>
</div>

<div class="notes-card">
  <div class="notes-card-head"><span class="notes-card-eyebrow">Direction 5 &middot; Do agencies answer in time?</span><span class="notes-card-session">Text &middot; BERTweet &middot; LLM labels with validation</span></div>
  <p class="notes-card-lede"><strong>Key question.</strong> For each transportation concern (fuel, evacuation routes and traffic, closures, tolls, transit, re-entry), when do residents raise it relative to landfall, when do agencies and media address it, and where are the gaps?</p>
  <p class="notes-card-lede"><strong>A first look.</strong> Among posts that mention fuel or gas stations, the median post by an individual comes about 6 hours before landfall and the median post by an organisation about 39 hours after (45 and 34 posts). Is that a slow response, or two groups talking about different things, empty pumps during the evacuation against reopened stations afterwards? Telling those apart is the project.</p>
  <div class="notes-card-cols" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
    <div><h4>Why it matters</h4><ul>
      <li>Crisis-communication studies usually measure public sentiment or agency messaging, rarely the two aligned on the same topic and the same hour. Aligning them turns sentiment analysis into a measurable gap that a public information officer can act on.</li>
      <li>Positive or negative is the wrong unit. Brandwatch calls 92% of organisation posts neutral and misses sarcasm (it labels HT0645 positive). Concern types such as frustration, uncertainty or a need for information, fear, and trust in the agency are closer to what an agency can respond to.</li>
    </ul></div>
    <div><h4>Toward a paper</h4><ul>
      <li>A codebook of concern types, and about 500 posts labeled by two people with Cohen's &kappa; reported.</li>
      <li>A fine-tuned BERTweet or an LLM labeler, checked against those labels before you trust it on the rest.</li>
      <li>Curves by topic, hours from landfall and account type, with confidence intervals and both storms pooled, and a lead&ndash;lag test between individual concern and organisational response.</li>
    </ul></div>
  </div>
  <p class="notes-card-lede" style="font-size:0.88rem;margin:0.7rem 0 0.2rem"><strong>Beyond the zip:</strong> only your labels. <strong>Watch out:</strong> compare shares, never volumes (the export cap), and only 1,384 posts are from individuals. <strong>Possible venues:</strong> Transportation Research Record; International Journal of Disaster Risk Reduction; Natural Hazards Review.</p>
</div>

<div class="resource-callout">
  <p><strong>Heading toward a paper?</strong> Talk to the instructor early. The posts cannot be released with a paper, so publish your code, codebook and aggregate results. Paraphrase posts rather than quoting them, because an exact quote can be searched back to its author. Ask whether your study needs an IRB determination before you submit.</p>
</div>

<div class="resource-callout">
  <p><strong>Questions about the data?</strong> Post them on the course discussion board in Canvas so everyone sees the answer, or bring them to office hours (Tuesdays 3&ndash;5 pm, CUTR 231). If something in the files looks wrong, note the <code>post_id</code>.</p>
</div>
